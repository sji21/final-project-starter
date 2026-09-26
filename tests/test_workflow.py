import copy
import time
from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi.testclient import TestClient

from app.errors import AppError
from app.main import create_app
from app.models import DecisionRequest, RunRequest
from app.providers import DemoProvider
from app.store import Store


def finish(client, request, key=None):
    response = client.post(
        "/api/runs", json=request, headers={"Idempotency-Key": key} if key else {}
    )
    assert response.status_code == 202, response.text
    run_id = response.json()["id"]
    for _ in range(200):
        run = client.get("/api/runs/" + run_id).json()
        if run["status"] not in {"queued", "running"}:
            return run
        time.sleep(0.01)
    pytest.fail("Workflow did not finish")


@pytest.mark.parametrize("pack_id,count", [("requirements-review", 6), ("cs-quality", 3)])
def test_both_packs_complete_same_pipeline(client, pack_id, count):
    example = client.get("/api/packs/" + pack_id + "/example").json()
    run = finish(client, example)
    assert run["status"] == "awaiting_review", run
    assert len(run["items"]) == count
    assert [event["stage"] for event in run["trace"]] == [
        "normalize",
        "extract",
        "retrieve",
        "review",
        "critic",
    ]
    assert all(not event["billable_model_call"] for event in run["trace"])
    assert run["provenance"]["demo_is_not_model_quality"] is True
    assert not any(item["validation_issues"] for item in run["items"])


def test_fixture_does_not_analyze_modified_documents(client, example):
    example["documents"][1]["content"] += "\nchanged"
    result = client.post("/api/runs", json=example)
    assert result.status_code == 422
    assert result.json()["error"]["code"] == "DEMO_INPUT_CHANGED"
    assert client.get("/api/runs").json()["runs"] == []


def test_model_mode_requires_configuration(client, example):
    example["mode"] = "model"
    assert client.post("/api/runs", json=example).status_code == 409


def test_invalid_input_rejected_before_queue(client, example):
    example["documents"][1]["id"] = example["documents"][0]["id"]
    assert client.post("/api/runs", json=example).status_code == 422


def test_duplicate_request_reuses_run_and_conflicts_on_changed_input(client, example):
    first = finish(client, example, "retry-key")
    second = client.post("/api/runs", json=example, headers={"Idempotency-Key": "retry-key"})
    assert second.json()["id"] == first["id"]
    assert len(client.get("/api/runs").json()["runs"]) == 1
    example["title"] = "Different title"
    assert (
        client.post("/api/runs", json=example, headers={"Idempotency-Key": "retry-key"}).status_code
        == 409
    )


def test_review_edits_persist_with_audit_and_report(client, example, settings):
    run = finish(client, example)
    for index, item in enumerate(run["items"]):
        response = client.post(
            "/api/runs/" + run["id"] + "/decisions",
            json={
                "revision": run["revision"],
                "criterion_id": item["criterion_id"],
                "actor": "PM",
                "action": "edit" if index == 0 else "accept",
                "note": "검토 완료",
                "edited_suggestion": "확인 후 문구를 수정했습니다." if index == 0 else None,
            },
        )
        assert response.status_code == 200, response.text
        run = response.json()
    assert run["status"] == "completed"
    assert len(run["audit"]) == 6
    persisted = Store(settings.data_dir / "workspace.sqlite3").get(run["id"])
    assert persisted["items"][0]["decision"]["edited_suggestion"] == "확인 후 문구를 수정했습니다."
    report = client.get("/api/runs/" + run["id"] + "/report.md")
    assert "확인 후 문구를 수정했습니다." in report.text
    assert "모델 성능 평가 결과가 아닙니다" in report.text
    metrics = client.get("/api/runs/" + run["id"] + "/metrics").json()
    assert metrics["decided_count"] == 6
    assert metrics["model_quality_measured"] is False
    assert metrics["cost"] is None


def test_stale_revision_and_missing_edit_reason_are_rejected(client, example):
    run = finish(client, example)
    payload = {
        "revision": run["revision"],
        "criterion_id": "REQ-01",
        "actor": "PM",
        "action": "accept",
        "note": "",
    }
    path = "/api/runs/" + run["id"] + "/decisions"
    assert client.post(path, json=payload).status_code == 200
    assert client.post(path, json=payload).status_code == 409
    payload["action"] = "edit"
    assert client.post(path, json=payload).status_code == 422


def test_atomic_revision_protects_concurrent_review(client, app, example):
    run = finish(client, example)
    decision = DecisionRequest(
        revision=run["revision"], criterion_id="REQ-01", actor="PM", action="accept"
    )

    def write():
        try:
            app.state.store.decide(run["id"], decision)
            return "saved"
        except AppError as exc:
            return exc.code

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(lambda _: write(), range(2)))
    assert sorted(results) == ["REVISION_CONFLICT", "saved"]
    assert len(app.state.store.get(run["id"])["audit"]) == 1


def test_cross_origin_and_unknown_pack_are_rejected(client, example):
    assert (
        client.post(
            "/api/runs", json=example, headers={"Origin": "https://foreign.example"}
        ).status_code
        == 403
    )
    example["pack_id"] = "unknown-pack"
    assert client.post("/api/runs", json=example).status_code == 404


def test_failed_model_output_persists_error_without_fake_results(settings):
    class BrokenProvider:
        def call(self, stage, payload, schema):
            raise AppError("MODEL_INVALID_OUTPUT", "모델 출력 오류", 502)

    app = create_app(settings, provider_factory=lambda request, pack: BrokenProvider())
    with TestClient(app) as client:
        example = client.get("/api/packs/cs-quality/example").json()
        run = finish(client, example)
        assert run["status"] == "failed"
        assert run["items"] == []
        assert run["error"]["code"] == "MODEL_INVALID_OUTPUT"


def test_invalid_citations_are_downgraded_and_critic_can_flag(settings):
    def provider(request, pack):
        altered = copy.deepcopy(pack)
        altered.responses["review"]["findings"][0]["evidence"][0]["quote"] = "없는 문장"
        altered.responses["critic"]["issues"] = [{"criterion_id": "REQ-03", "reason": "추가 확인"}]
        return DemoProvider(altered, request.documents)

    app = create_app(settings, provider_factory=provider)
    with TestClient(app) as client:
        run = finish(client, client.get("/api/packs/requirements-review/example").json())
        assert run["status"] == "awaiting_review"
        by_id = {item["criterion_id"]: item for item in run["items"]}
        assert by_id["REQ-01"]["verdict"] == "needs_review"
        assert by_id["REQ-01"]["evidence"] == []
        assert by_id["REQ-03"]["verdict"] == "needs_review"


def test_restart_marks_unfinished_work_interrupted(client, app, example, settings):
    request = RunRequest.model_validate(example)
    pack = app.state.registry.get(request.pack_id)
    store = app.state.store
    queued, _ = store.create(request, pack, "interrupted-job", "sample-hash")
    restored = Store(settings.data_dir / "workspace.sqlite3")
    restored.recover_interrupted()
    assert restored.get(queued["id"])["error"]["code"] == "INTERRUPTED"


def test_static_ui_and_openapi_are_served(client):
    assert client.get("/").status_code == 200
    assert "frame-ancestors 'none'" in client.get("/").headers["Content-Security-Policy"]
    assert client.get("/assets/app.js").status_code == 200
    assert "/api/runs" in client.get("/openapi.json").json()["paths"]

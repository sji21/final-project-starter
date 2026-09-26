import json
import shutil

import httpx
from fastapi.testclient import TestClient

from app.config import ROOT, Settings
from app.main import create_app
from app.providers import ModelProvider
from tests.test_workflow import finish


def test_new_pack_is_discovered_without_core_changes(tmp_path):
    packs = tmp_path / "custom-packs"
    folder = packs / "custom-topic"
    shutil.copytree(ROOT / "packs" / "requirements-review", folder)
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    manifest.update(id="custom-topic", name="새 업무")
    manifest["labels"]["conflict"] = "새 업무의 충돌"
    (folder / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    example = json.loads((folder / "example.json").read_text(encoding="utf-8"))
    example["pack_id"] = "custom-topic"
    (folder / "example.json").write_text(json.dumps(example), encoding="utf-8")
    app = create_app(Settings(data_dir=tmp_path / "db", packs_dir=packs))
    with TestClient(app) as client:
        assert client.get("/api/packs").json()["packs"][0]["id"] == "custom-topic"
        run = finish(client, example)
        assert run["status"] == "awaiting_review"
        assert run["pack"]["labels"]["conflict"] == "새 업무의 충돌"
        assert "새 업무의 충돌" in client.get("/api/runs/" + run["id"] + "/report.md").text


def test_model_mode_three_role_http_contract(settings):
    settings.model_base_url = "https://mock-model.example/v1"
    settings.model_name = "fake-base-for-contract-test"
    settings.stage_models = {"review": "fake-trained-adapter-for-contract-test"}
    calls = []

    def factory(request, pack):
        def handle(http_request):
            body = json.loads(http_request.content)
            stage = body["response_format"]["json_schema"]["name"]
            calls.append((stage, body["model"]))
            return httpx.Response(
                200,
                json={
                    "choices": [
                        {
                            "message": {
                                "content": json.dumps(pack.responses[stage], ensure_ascii=False)
                            },
                            "finish_reason": "stop",
                        }
                    ],
                    "usage": {"prompt_tokens": 10, "completion_tokens": 5},
                },
            )

        return ModelProvider(settings, pack, httpx.MockTransport(handle))

    app = create_app(settings, provider_factory=factory)
    with TestClient(app) as client:
        example = client.get("/api/packs/requirements-review/example").json()
        example["mode"] = "model"
        run = finish(client, example)
        assert run["status"] == "awaiting_review"
        assert calls == [
            ("extract", "fake-base-for-contract-test"),
            ("review", "fake-trained-adapter-for-contract-test"),
            ("critic", "fake-base-for-contract-test"),
        ]
        metrics = client.get("/api/runs/" + run["id"] + "/metrics").json()
        assert metrics["prompt_tokens"] == 30
        assert metrics["completion_tokens"] == 15
        assert metrics["cost"] is None

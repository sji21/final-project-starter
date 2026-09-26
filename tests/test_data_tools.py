import copy

import pytest

from app.dataset import export_train, inspect_records
from app.errors import AppError
from app.evaluation import evaluate
from app.packs import digest
from tests.test_workflow import finish


def record(identifier="a", group="source-a", split="train", text="입력 원문", status="approved"):
    return {
        "id": identifier,
        "group_id": group,
        "split": split,
        "pack_id": "sample",
        "source": "synthetic-test",
        "license_note": "test-authored",
        "review_status": status,
        "messages": [
            {"role": "user", "content": text},
            {"role": "assistant", "content": "검토 결과"},
        ],
    }


def test_groups_and_normalized_inputs_cannot_leak():
    rows = [
        record(),
        record("b", "source-a", "test", "다른 입력"),
        record("c", "source-c", "validation", "입력  원문"),
    ]
    _, report = inspect_records(rows)
    assert report["valid"] is False
    assert "group_leakage:source-a" in report["errors"]
    assert "duplicate_input_across_splits:c" in report["errors"]


def test_export_only_approved_train_and_keep_manifest(tmp_path):
    rows = [record(), record("b", "source-b", "test", "보지 않은 입력")]
    target = tmp_path / "train.jsonl"
    result = export_train(rows, target)
    assert result["exported_ids"] == ["a"]
    assert len(target.read_text(encoding="utf-8").splitlines()) == 1
    assert (tmp_path / "train.jsonl.manifest.json").exists()
    with pytest.raises(FileExistsError):
        export_train(rows, target)


def test_draft_data_is_not_exported_as_reviewed_training(tmp_path):
    with pytest.raises(ValueError, match="approved"):
        export_train([record(status="draft")], tmp_path / "train.jsonl")


def test_empty_dataset_and_existing_manifest_are_rejected(tmp_path):
    _, report = inspect_records([])
    assert report["valid"] is False
    output = tmp_path / "train.jsonl"
    manifest = tmp_path / "train.jsonl.manifest.json"
    manifest.write_text("existing evidence", encoding="utf-8")
    with pytest.raises(FileExistsError):
        export_train([record()], output)
    assert not output.exists()
    assert manifest.read_text(encoding="utf-8") == "existing evidence"


def test_demo_metrics_never_claim_model_quality(client, example):
    run = finish(client, example)
    gold = {
        "pack_id": example["pack_id"],
        "dataset_id": "unit",
        "human_reviewed": True,
        "documents_hash": digest(example["documents"]),
        "items": [
            {"criterion_id": item["criterion_id"], "verdict": item["verdict"]}
            for item in run["items"]
        ],
    }
    result = evaluate(run, gold)
    assert result["label_agreement"] == 1
    assert result["model_quality_measured"] is False
    assert result["metric_name"] == "fixture_or_draft_label_agreement"
    changed = copy.deepcopy(gold)
    changed["documents_hash"] = "wrong"
    with pytest.raises(AppError, match="버전"):
        evaluate(run, changed)


def test_missing_predictions_count_as_incorrect(client, example):
    run = finish(client, example)
    gold = {
        "pack_id": example["pack_id"],
        "documents_hash": digest(example["documents"]),
        "items": [
            {"criterion_id": "REQ-01", "verdict": "partial"},
            {"criterion_id": "UNSEEN", "verdict": "missing"},
        ],
    }
    result = evaluate(run, gold)
    assert result["label_agreement"] == 0.5
    assert result["missing_predictions"] == ["UNSEEN"]
    assert result["confusion"]["missing"]["not_predicted"] == 1

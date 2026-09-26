"""Offline evaluation; fixture agreement must not be presented as model accuracy."""

from app.errors import AppError
from app.packs import digest

LABELS = ("covered", "partial", "missing", "conflict", "needs_review")


def evaluate(run, gold):
    if run["status"] not in {"awaiting_review", "completed"}:
        raise AppError("INCOMPLETE_RUN", "완료된 실행만 평가할 수 있습니다.")
    if gold.get("pack_id") != run["request"]["pack_id"]:
        raise AppError("DATASET_MISMATCH", "평가셋과 실행의 업무 팩이 다릅니다.")
    document_hash = digest(run["request"]["documents"])
    if gold.get("documents_hash") != document_hash:
        raise AppError("DATASET_MISMATCH", "평가셋과 입력 문서 버전이 다릅니다.")
    entries = gold.get("items", [])
    ids = [entry.get("criterion_id") for entry in entries]
    if not entries or len(ids) != len(set(ids)):
        raise AppError("INVALID_GOLD", "정답 항목이 비어 있거나 ID가 중복되었습니다.")
    if any(entry.get("verdict") not in LABELS for entry in entries):
        raise AppError("INVALID_GOLD", "정답의 판정 값이 유효하지 않습니다.")
    expected = {entry["criterion_id"]: entry for entry in entries}
    predicted = {item["criterion_id"]: item for item in run["items"]}
    correct = 0
    per_label = {}
    confusion = {label: {other: 0 for other in (*LABELS, "not_predicted")} for label in LABELS}
    for key, entry in expected.items():
        prediction = predicted.get(key, {}).get("verdict", "not_predicted")
        confusion[entry["verdict"]][prediction] += 1
        correct += prediction == entry["verdict"]
    for label in LABELS:
        tp = sum(
            key in expected and expected[key]["verdict"] == label and value["verdict"] == label
            for key, value in predicted.items()
        )
        predicted_count = sum(value["verdict"] == label for value in predicted.values())
        support = sum(value["verdict"] == label for value in expected.values())
        precision = tp / predicted_count if predicted_count else 0.0
        recall = tp / support if support else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        per_label[label] = {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "support": support,
            "predicted": predicted_count,
        }
    # Evaluate retrieval separately from the subset the model chose to cite.
    retrieved_hits = 0
    expected_evidence = 0
    for key, entry in expected.items():
        required = set(entry.get("evidence_chunk_ids", []))
        retrieved = set(run["retrieval"].get(key, {}).get("chunk_ids", []))
        retrieved_hits += len(required & retrieved)
        expected_evidence += len(required)
    usable_quality = run["request"]["mode"] == "model" and gold.get("human_reviewed") is True
    return {
        "run_id": run["id"],
        "dataset_id": gold.get("dataset_id"),
        "documents_hash": document_hash,
        "mode": run["request"]["mode"],
        "purpose": gold.get("purpose", "development"),
        "human_reviewed_gold": gold.get("human_reviewed") is True,
        "model_quality_measured": usable_quality,
        "metric_name": "label_accuracy" if usable_quality else "fixture_or_draft_label_agreement",
        "label_agreement": correct / len(expected),
        "macro_f1_supported_labels": sum(
            value["f1"] for value in per_label.values() if value["support"]
        )
        / sum(bool(value["support"]) for value in per_label.values()),
        "per_label": per_label,
        "confusion": confusion,
        "missing_predictions": sorted(set(expected) - set(predicted)),
        "unexpected_predictions": sorted(set(predicted) - set(expected)),
        "gold_evidence_recall_in_presented_context": retrieved_hits / expected_evidence
        if expected_evidence
        else None,
        "note": (
            "고정 정답셋에 대한 측정입니다. 데이터 대표성·누출 여부와 표본 수는 별도 검토해야 합니다."
            if usable_quality
            else "데모 또는 미검수 정답과의 일치도입니다. 모델 성능으로 해석하지 마세요."
        ),
    }

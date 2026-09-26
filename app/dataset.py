"""Validate independently reviewed SFT records and prevent obvious split leakage."""

import json
import re
from pathlib import Path
from typing import Literal

from pydantic import Field

from app.models import StrictModel
from app.packs import digest


class Message(StrictModel):
    role: Literal["system", "user", "assistant"]
    content: str = Field(min_length=1)


class TrainingRecord(StrictModel):
    id: str = Field(min_length=1)
    group_id: str = Field(min_length=1)
    split: Literal["train", "validation", "test"]
    pack_id: str = Field(min_length=1)
    source: str = Field(min_length=1)
    license_note: str = Field(min_length=1)
    review_status: Literal["draft", "approved"]
    messages: list[Message] = Field(min_length=2)


def normalized_input(record):
    # Exclude assistant labels: changing the answer must not hide duplicated input.
    text = "\n".join(message.content for message in record.messages if message.role == "user")
    return re.sub(r"\s+", "", text).casefold()


def inspect_records(rows):
    records = [TrainingRecord.model_validate(row) for row in rows]
    errors = [] if records else ["empty_dataset"]
    ids = set()
    groups = {}
    input_splits = {}
    for record in records:
        if record.id in ids:
            errors.append(f"duplicate_id:{record.id}")
        ids.add(record.id)
        if record.messages[-1].role != "assistant" or not any(
            message.role == "user" for message in record.messages
        ):
            errors.append(f"invalid_message_order:{record.id}")
        previous = groups.setdefault(record.group_id, record.split)
        if previous != record.split:
            errors.append(f"group_leakage:{record.group_id}")
        content_key = digest(normalized_input(record))
        previous_split = input_splits.setdefault(content_key, record.split)
        if previous_split != record.split:
            errors.append(f"duplicate_input_across_splits:{record.id}")
    return records, {
        "valid": not errors,
        "records": len(records),
        "splits": {
            split: sum(record.split == split for record in records)
            for split in ("train", "validation", "test")
        },
        "approved": sum(record.review_status == "approved" for record in records),
        "errors": errors,
        "dataset_hash": digest(rows),
        "limitation": "정규화된 동일 입력과 문서 그룹 누출을 검사합니다. 의미상 유사 사례·정답의 진실성·라이선스는 사람이 검토해야 합니다.",
    }


def export_train(rows, output: Path):
    records, report = inspect_records(rows)
    if not report["valid"]:
        raise ValueError("데이터 분할 또는 중복 검사 실패: " + ", ".join(report["errors"]))
    selected = [record for record in records if record.split == "train"]
    if not selected:
        raise ValueError("train 레코드가 없습니다.")
    if any(record.review_status != "approved" for record in selected):
        raise ValueError("train 레코드는 모두 사람이 검토한 approved 상태여야 합니다.")
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest_path = Path(str(output) + ".manifest.json")
    if manifest_path.exists():
        raise FileExistsError(manifest_path)
    with output.open("x", encoding="utf-8") as stream:
        for record in selected:
            stream.write(
                json.dumps(
                    {"messages": [message.model_dump() for message in record.messages]},
                    ensure_ascii=False,
                )
                + "\n"
            )
    manifest = report | {
        "exported_train_records": len(selected),
        "exported_ids": [record.id for record in selected],
    }
    with manifest_path.open("x", encoding="utf-8") as stream:
        json.dump(manifest, stream, ensure_ascii=False, indent=2)
    return manifest

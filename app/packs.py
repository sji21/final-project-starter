import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from app.models import Manifest, RunRequest


def digest(value):
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


@dataclass(frozen=True)
class Pack:
    manifest: Manifest
    example: RunRequest
    responses: dict
    prompts: dict[str, str]
    fingerprint: str

    def public(self):
        return {**self.manifest.model_dump(), "fingerprint": self.fingerprint}


class PackRegistry:
    def __init__(self, directory: Path):
        self.packs = {}
        for path in sorted(directory.glob("*/manifest.json")):
            manifest = Manifest.model_validate_json(path.read_text(encoding="utf-8"))
            folder = path.parent
            if folder.name != manifest.id or manifest.id in self.packs:
                raise ValueError("팩 디렉터리와 ID가 일치하고 고유해야 합니다.")
            example = RunRequest.model_validate_json(
                (folder / "example.json").read_text(encoding="utf-8")
            )
            if example.pack_id != manifest.id or example.mode != "demo":
                raise ValueError("예제의 pack_id 또는 실행 모드를 확인하세요.")
            responses = json.loads((folder / "demo-responses.json").read_text(encoding="utf-8"))
            prompts = {
                name: (folder / "prompts" / f"{name}.md").read_text(encoding="utf-8")
                for name in ("extract", "review", "critic")
            }
            fingerprint = digest({"manifest": manifest.model_dump(), "prompts": prompts})
            self.packs[manifest.id] = Pack(manifest, example, responses, prompts, fingerprint)
        if not self.packs:
            raise ValueError("설치된 업무 팩이 없습니다.")

    def get(self, pack_id: str):
        if pack_id not in self.packs:
            raise KeyError("업무 팩을 찾을 수 없습니다.")
        return self.packs[pack_id]

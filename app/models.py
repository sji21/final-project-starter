from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

Identifier = Annotated[str, Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")]
Verdict = Literal["covered", "partial", "missing", "conflict", "needs_review"]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Document(StrictModel):
    id: Identifier
    title: str = Field(min_length=1, max_length=160)
    version: str = Field(min_length=1, max_length=40)
    role: Literal["basis", "target"]
    content: str = Field(min_length=1, max_length=30000)
    complete: bool = True


class RunRequest(StrictModel):
    pack_id: Identifier
    mode: Literal["demo", "model"] = "demo"
    title: str = Field(default="새 검토", min_length=1, max_length=160)
    documents: list[Document] = Field(min_length=2, max_length=8)

    @model_validator(mode="after")
    def valid_documents(self):
        ids = [doc.id for doc in self.documents]
        if len(set(ids)) != len(ids):
            raise ValueError("문서 ID가 중복되었습니다.")
        if {doc.role for doc in self.documents} != {"basis", "target"}:
            raise ValueError("기준 문서와 검토 대상 문서가 모두 필요합니다.")
        if sum(len(doc.content) for doc in self.documents) > 60000:
            raise ValueError("전체 입력은 60,000자 이하여야 합니다.")
        return self


class Citation(StrictModel):
    chunk_id: str = Field(min_length=1, max_length=100)
    quote: str = Field(min_length=1, max_length=2000)


class Criterion(StrictModel):
    id: Identifier
    title: str = Field(min_length=1, max_length=300)
    description: str = Field(min_length=1, max_length=3000)
    source: Citation


class Extraction(StrictModel):
    criteria: list[Criterion] = Field(min_length=1, max_length=30)

    @model_validator(mode="after")
    def unique_criteria(self):
        if len({item.id for item in self.criteria}) != len(self.criteria):
            raise ValueError("검토 기준 ID가 중복되었습니다.")
        return self


class Finding(StrictModel):
    criterion_id: Identifier
    verdict: Verdict
    reason: str = Field(min_length=1, max_length=3000)
    evidence: list[Citation] = Field(max_length=20)
    suggestion: str | None = Field(default=None, max_length=3000)


class Findings(StrictModel):
    findings: list[Finding] = Field(min_length=1, max_length=30)

    @model_validator(mode="after")
    def unique_findings(self):
        if len({item.criterion_id for item in self.findings}) != len(self.findings):
            raise ValueError("판정 기준 ID가 중복되었습니다.")
        return self


class CriticIssue(StrictModel):
    criterion_id: Identifier
    reason: str = Field(min_length=1, max_length=1500)


class Critique(StrictModel):
    issues: list[CriticIssue] = Field(max_length=30)


class DecisionRequest(StrictModel):
    revision: int = Field(ge=1)
    criterion_id: Identifier
    action: Literal["accept", "reject", "edit"]
    actor: str = Field(min_length=1, max_length=80)
    note: str = Field(default="", max_length=3000)
    edited_suggestion: str | None = Field(default=None, max_length=3000)

    @model_validator(mode="after")
    def decision_details(self):
        if self.action in {"reject", "edit"} and not self.note:
            raise ValueError("반려 또는 수정 사유를 입력하세요.")
        if self.action == "edit" and not self.edited_suggestion:
            raise ValueError("수정할 제안을 입력하세요.")
        return self


class Manifest(StrictModel):
    id: Identifier
    name: str = Field(min_length=1, max_length=80)
    version: str = Field(min_length=1, max_length=40)
    description: str = Field(min_length=1, max_length=500)
    basis_label: str
    target_label: str
    task: str
    training_task: str
    accent: str = Field(pattern=r"^#[0-9a-fA-F]{6}$")
    labels: dict[Verdict, str]

    @model_validator(mode="after")
    def all_labels(self):
        if set(self.labels) != {"covered", "partial", "missing", "conflict", "needs_review"}:
            raise ValueError("모든 공통 판정 라벨의 표시 이름이 필요합니다.")
        return self

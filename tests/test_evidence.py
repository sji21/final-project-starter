import pytest

from app.errors import AppError
from app.models import Citation, Criterion, Document, Extraction, Finding, Findings
from app.retrieval import chunk_documents, retrieve
from app.validation import validate_extraction, validate_findings


def inputs(count=1, complete=True):
    documents = [
        Document(id="B", title="기준", version="v1", role="basis", content="접수 경로를 안내한다."),
        Document(
            id="T",
            title="대상",
            version="v1",
            role="target",
            complete=complete,
            content="\n\n".join(f"대상 문단 {i}: 접수 정보" for i in range(count)),
        ),
    ]
    chunks = chunk_documents(documents)
    criterion = Criterion(
        id="C1",
        title="접수 안내",
        description="접수 경로 안내",
        source=Citation(chunk_id="B:p1", quote="접수 경로를 안내한다."),
    )
    return documents, chunks, [criterion]


@pytest.mark.parametrize(
    "count,complete,verdict",
    [(31, True, "needs_review"), (1, False, "needs_review"), (1, True, "missing")],
)
def test_missing_requires_entire_complete_scope(count, complete, verdict):
    documents, chunks, criteria = inputs(count, complete)
    findings = Findings(
        findings=[Finding(criterion_id="C1", verdict="missing", reason="찾지 못함", evidence=[])]
    )
    result = validate_findings(findings, criteria, chunks, retrieve(criteria, chunks), documents)
    assert result[0]["verdict"] == verdict


def test_basis_cannot_be_used_as_target_evidence():
    documents, chunks, criteria = inputs()
    findings = Findings(
        findings=[
            Finding(
                criterion_id="C1",
                verdict="covered",
                reason="확인",
                evidence=[Citation(chunk_id="B:p1", quote="접수 경로를 안내한다.")],
            )
        ]
    )
    result = validate_findings(findings, criteria, chunks, retrieve(criteria, chunks), documents)
    assert result[0]["verdict"] == "needs_review"
    assert not result[0]["evidence"]


def test_unquoted_criterion_and_unknown_output_fail():
    documents, chunks, criteria = inputs()
    criteria[0].source.quote = "가짜 원문"
    with pytest.raises(AppError, match="원문 근거"):
        validate_extraction(Extraction(criteria=criteria), chunks)
    findings = Findings(
        findings=[Finding(criterion_id="UNKNOWN", verdict="missing", reason="없음", evidence=[])]
    )
    with pytest.raises(AppError, match="모든 검토 기준"):
        validate_findings(findings, criteria, chunks, retrieve(criteria, chunks), documents)


def test_long_paragraphs_retain_exact_source_and_version():
    doc = Document(id="D", title="Long", version="v7", role="target", content="가" * 2500)
    chunks = chunk_documents([doc])
    assert len(chunks) == 3
    assert "".join(chunk["text"] for chunk in chunks) == doc.content
    assert all(chunk["document_version"] == "v7" for chunk in chunks)

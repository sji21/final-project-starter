from app.errors import AppError


def check_citation(citation, chunks, role=None, allowed=None):
    chunk = chunks.get(citation.chunk_id)
    if not chunk or (role and chunk["role"] != role):
        return False
    if allowed is not None and citation.chunk_id not in allowed:
        return False
    return citation.quote in chunk["text"]


def validate_extraction(extraction, chunks):
    by_id = {chunk["id"]: chunk for chunk in chunks}
    for criterion in extraction.criteria:
        if not check_citation(criterion.source, by_id, role="basis"):
            raise AppError(
                "INVALID_CRITERION_SOURCE", "추출한 기준의 원문 근거가 일치하지 않습니다.", 422
            )


def validate_findings(findings, criteria, chunks, retrieval, documents):
    expected = {criterion.id for criterion in criteria}
    if {finding.criterion_id for finding in findings.findings} != expected:
        raise AppError("INCOMPLETE_FINDINGS", "모든 검토 기준에 하나씩 결과가 필요합니다.", 422)
    by_id = {chunk["id"]: chunk for chunk in chunks}
    complete = all(doc.complete for doc in documents if doc.role == "target")
    output = []
    for finding in findings.findings:
        result = finding.model_dump()
        issues = []
        scope = retrieval[finding.criterion_id]
        valid = [
            citation
            for citation in finding.evidence
            if check_citation(citation, by_id, "target", scope["chunk_ids"])
        ]
        if len(valid) != len(finding.evidence):
            issues.append("원문에 없거나 전달되지 않은 근거를 제거했습니다.")
        if finding.verdict in {"covered", "partial", "conflict"} and not valid:
            issues.append("이 판정에는 확인 가능한 대상 문서 근거가 필요합니다.")
        if finding.verdict == "missing" and (
            not complete or not scope["all_target_chunks_presented"]
        ):
            issues.append("전체 문서 범위를 확인하지 못해 누락을 확정할 수 없습니다.")
        if issues:
            result["verdict"] = "needs_review"
        result["evidence"] = [citation.model_dump() for citation in valid]
        result["validation_issues"] = issues
        result["decision"] = None
        output.append(result)
    return output


def apply_critique(items, critique):
    by_id = {item["criterion_id"]: item for item in items}
    for issue in critique.issues:
        if issue.criterion_id not in by_id:
            raise AppError(
                "INVALID_CRITIC_TARGET", "검증 역할이 알 수 없는 기준을 참조했습니다.", 422
            )
        item = by_id[issue.criterion_id]
        item["verdict"] = "needs_review"
        item["validation_issues"].append("검증 역할: " + issue.reason)
    return items

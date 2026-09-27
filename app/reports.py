def inline(value):
    """Inline Markdown text.

    Raw HTML is neutralized with a Markdown backslash escape so a rendered report
    cannot execute document content, while quotes and ampersands stay as typed.
    HTML entity escaping would corrupt the plain .md file that reviewers read.
    """
    return str(value).replace("<", "\\<").replace("\n", " ")


def cell(value):
    """Table cell text: inline rules plus the pipe escape that keeps the row intact."""
    return inline(value).replace("|", "\\|")


def markdown_report(run):
    lines = [
        f"# {inline(run['request']['title'])}",
        "",
        f"- 업무: {inline(run['pack']['name'])} / {inline(run['pack']['version'])}",
        f"- 실행 ID: {run['id']}",
        f"- 실행 모드: {run['provenance']['execution']}",
        f"- 상태: {run['status']} / revision {run['revision']}",
        f"- 입력 SHA256: {run['input_hash']}",
        f"- 팩 SHA256: {run['provenance']['pack_hash']}",
        "",
    ]
    if run["request"]["mode"] == "demo":
        lines += ["> 고정 응답을 재생한 데모입니다. 모델 성능 평가 결과가 아닙니다.", ""]
    lines += [
        "사람의 채택은 검토 의견에 대한 결정입니다. 실제 소프트웨어의 동작이나 업무 사실을 보증하지 않습니다.",
        "",
        "## 검토 결과",
        "",
        "| 기준 | 판정 | 사유 | 수정 제안 | 사람 검토 |",
        "| --- | --- | --- | --- | --- |",
    ]
    for item in run["items"]:
        decision = item["decision"]
        suggestion = (
            decision["edited_suggestion"]
            if decision and decision["action"] == "edit"
            else item["suggestion"]
        )
        decision_label = (
            f"{decision['action']} · {decision['actor']} · {decision['note']}"
            if decision
            else "대기"
        )
        lines.append(
            "| "
            + " | ".join(
                cell(value or "—")
                for value in (
                    item["criterion_id"],
                    run["pack"]["labels"][item["verdict"]],
                    item["reason"],
                    suggestion,
                    decision_label,
                )
            )
            + " |"
        )
    lines += ["", "## 근거와 확인 사항", ""]
    for item in run["items"]:
        lines += [f"### {inline(item['criterion_id'])}", ""]
        for citation in item["evidence"]:
            lines.append(f"- {inline(citation['chunk_id'])}: {inline(citation['quote'])}")
        for issue in item["validation_issues"]:
            lines.append(f"- 확인 필요: {inline(issue)}")
    lines += ["", "## 문서 버전", ""]
    for document in run["request"]["documents"]:
        lines.append(
            f"- {inline(document['id'])}: {inline(document['title'])} / {inline(document['version'])}"
        )
    lines += ["", "## 실행 이력", ""]
    for event in run["trace"]:
        lines.append(
            f"- {event['stage']}: {event['duration_ms']}ms / {inline(event.get('model', event.get('kind', '')))}"
        )
    return "\n".join(lines) + "\n"


def diagnostic_metrics(run):
    items = run["items"]
    counts = {label: sum(i["verdict"] == label for i in items) for label in run["pack"]["labels"]}
    token_values = [
        event.get("prompt_tokens") for event in run["trace"] if event.get("billable_model_call")
    ]
    output_values = [
        event.get("completion_tokens") for event in run["trace"] if event.get("billable_model_call")
    ]

    def total_known(values):
        return sum(values) if values and all(v is not None for v in values) else None

    return {
        "run_id": run["id"],
        "mode": run["request"]["mode"],
        "item_count": len(items),
        "verdict_counts": counts,
        "decided_count": sum(bool(item["decision"]) for item in items),
        "validation_issue_count": sum(len(item["validation_issues"]) for item in items),
        "duration_ms": sum(event["duration_ms"] for event in run["trace"]),
        "prompt_tokens": total_known(token_values),
        "completion_tokens": total_known(output_values),
        "cost": None,
        "model_quality_measured": False,
        "note": "운영 집계입니다. 정확도·비용은 정답셋과 실제 요금 정보 없이 추정하지 않습니다.",
    }

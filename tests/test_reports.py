from app.reports import cell, inline
from tests.test_workflow import finish


def test_inline_keeps_quotes_and_neutralizes_raw_html():
    assert inline("'빠르게'의 기준") == "'빠르게'의 기준"
    assert inline('"인용" & 기호') == '"인용" & 기호'
    assert inline("a <script> b") == "a \\<script> b"
    assert inline("두 줄\n입력") == "두 줄 입력"


def test_only_table_cells_escape_the_pipe():
    assert inline("TC-01 | 절차") == "TC-01 | 절차"
    assert cell("TC-01 | 절차") == "TC-01 \\| 절차"


def test_report_stays_readable_markdown(client, example):
    run = finish(client, example)
    report = client.get("/api/runs/" + run["id"] + "/report.md").text
    # HTML entity escaping used to corrupt every apostrophe in the delivered report.
    assert "&#x27;" not in report
    assert "&quot;" not in report
    assert "&amp;" not in report
    assert "'빠르게'의 시간 기준" in report
    # Evidence bullets are not table rows, so the pipe must stay as written.
    assert "TC-01 | 절차" in report

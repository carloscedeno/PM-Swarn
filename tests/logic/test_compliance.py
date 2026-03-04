import pytest
from src.model.issue import Issue
from src.logic.compliance import compute_compliance

def create_issue(status="STRATA DONE", notion_url="http://notion.so/doc", doc_status="valid", stories_present=True):
    return Issue(
        id="123",
        key="SWARN-123",
        summary="Test Issue",
        status=status,
        updated="2026-03-04T12:00:00Z",
        issuetype="Story",
        notion_doc_url=notion_url,
        doc_status=doc_status,
        stories_json_present=stories_present
    )

def test_compute_compliance_compliant():
    issue = create_issue()
    updated_issue = compute_compliance(issue)
    assert updated_issue.compliance_status == "compliant"
    assert len(updated_issue.gaps) == 0

def test_compute_compliance_missing_doc():
    issue = create_issue(notion_url=None)
    updated_issue = compute_compliance(issue)
    assert updated_issue.compliance_status == "non-compliant"
    assert "missing_doc" in updated_issue.gaps

def test_compute_compliance_invalid_doc():
    issue = create_issue(doc_status="invalid")
    updated_issue = compute_compliance(issue)
    assert updated_issue.compliance_status == "non-compliant"
    assert "invalid_doc" in updated_issue.gaps

def test_compute_compliance_missing_stories_json():
    issue = create_issue(stories_present=False)
    updated_issue = compute_compliance(issue)
    assert updated_issue.compliance_status == "non-compliant"
    assert "missing_stories_json" in updated_issue.gaps

def test_compute_compliance_multiple_gaps():
    issue = create_issue(notion_url=None, stories_present=False)
    updated_issue = compute_compliance(issue)
    assert updated_issue.compliance_status == "non-compliant"
    assert "missing_doc" in updated_issue.gaps
    assert "missing_stories_json" in updated_issue.gaps
    assert "invalid_doc" not in updated_issue.gaps # Since notion_doc_url is None

def test_compute_compliance_non_done_status():
    issue = create_issue(status="STRATA IN PROGRESS")
    updated_issue = compute_compliance(issue)
    assert updated_issue.compliance_status is None
    assert len(updated_issue.gaps) == 0

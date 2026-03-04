import pytest
from src.model.issue import Issue
from src.jira.evidence import verify_evidence

@pytest.fixture
def base_issue():
    return Issue(
        id="10001",
        key="DEV-1",
        summary="Test Story",
        status="STRATA TO DO",
        updated="2023-01-01T00:00:00.000Z",
        issuetype="Story",
        work_type="STORIES"
    )

def test_verify_evidence_attachment_found(base_issue):
    raw_issue = {
        "fields": {
            "attachment": [
                {"filename": "somefile.txt"},
                {"filename": "stories.json"}
            ]
        }
    }
    verify_evidence(base_issue, raw_issue)
    assert base_issue.stories_json_present is True
    assert "missing_stories_json" not in base_issue.gaps

def test_verify_evidence_attachment_not_found(base_issue):
    raw_issue = {
        "fields": {
            "attachment": [
                {"filename": "presentation.pptx"}
            ]
        }
    }
    verify_evidence(base_issue, raw_issue)
    assert base_issue.stories_json_present is False

def test_verify_evidence_link_found(base_issue):
    raw_issue = {
        "fields": {
            "issuelinks": [
                {
                    "outwardIssue": {
                        "fields": {"summary": "Reference to stories.json in docs"}
                    }
                }
            ]
        }
    }
    verify_evidence(base_issue, raw_issue)
    assert base_issue.stories_json_present is True

def test_verify_evidence_gap_recorded_in_done(base_issue):
    base_issue.status = "STRATA DONE"
    raw_issue = {"fields": {"attachment": []}}
    verify_evidence(base_issue, raw_issue)
    assert base_issue.stories_json_present is False
    assert "missing_stories_json" in base_issue.gaps

def test_verify_evidence_not_stories_type(base_issue):
    base_issue.work_type = "PRD"
    raw_issue = {
        "fields": {
            "attachment": [{"filename": "stories.json"}]
        }
    }
    verify_evidence(base_issue, raw_issue)
    assert base_issue.stories_json_present is None

import pytest
from src.model.issue import Issue
from src.beadbox.evidence import verify_bead_evidence

def create_test_issue(key: str, status: str) -> Issue:
    return Issue(
        id=key,
        key=key,
        summary="Test Bead",
        status=status,
        updated="2026-03-04T12:00:00Z",
        issuetype="Story"
    )

def test_evidence_in_description():
    """Test that stories.json in the description works."""
    issue = create_test_issue(key="BD-1", status="STRATA DONE")
    issue.work_type = "STORIES"
    raw_bead = {"description": "Here is the link to stories.json: URL"}
    
    verify_bead_evidence(issue, raw_bead)
    
    assert issue.stories_json_present is True
    assert "missing_stories_json" not in issue.gaps
    assert issue.compliance_status is None

def test_evidence_in_attachments_dict():
    """Test when attachments are dicts with name containing stories.json."""
    issue = create_test_issue(key="BD-2", status="STRATA DONE")
    issue.work_type = "STORIES"
    raw_bead = {
        "description": "No link here",
        "attachments": [
            {"name": "some_image.png"},
            {"name": "my_stories.json"}
        ]
    }
    
    verify_bead_evidence(issue, raw_bead)
    
    assert issue.stories_json_present is True

def test_evidence_in_attachments_string():
    """Test when attachments are strings (links) containing stories.json."""
    issue = create_test_issue(key="BD-3", status="STRATA DONE")
    issue.work_type = "STORIES"
    raw_bead = {
        "attachments": [
            "https://example.com/other.txt",
            "https://example.com/path/to/stories.json"
        ]
    }
    
    verify_bead_evidence(issue, raw_bead)
    
    assert issue.stories_json_present is True

def test_missing_evidence_in_strata_done():
    """Test gap generation when STRATA DONE and missing stories.json."""
    issue = create_test_issue(key="BD-4", status="STRATA DONE")
    issue.work_type = "STORIES"
    raw_bead = {"description": "Nothing here"}
    
    verify_bead_evidence(issue, raw_bead)
    
    assert issue.stories_json_present is False
    assert "missing_stories_json" in issue.gaps
    assert issue.compliance_status == "non-compliant"

def test_missing_evidence_not_done():
    """Test no gap when not in STRATA DONE."""
    issue = create_test_issue(key="BD-5", status="STRATA IN PROGRESS")
    issue.work_type = "STORIES"
    raw_bead = {"description": "Working on it"}
    
    verify_bead_evidence(issue, raw_bead)
    
    assert issue.stories_json_present is False
    assert "missing_stories_json" not in issue.gaps

def test_not_stories_work_type():
    """Test when work_type is not STORIES."""
    issue = create_test_issue(key="BD-6", status="STRATA DONE")
    issue.work_type = "PRD"
    raw_bead = {"description": "Nothing here"}
    
    verify_bead_evidence(issue, raw_bead)
    
    assert issue.stories_json_present is None
    assert "missing_stories_json" not in issue.gaps

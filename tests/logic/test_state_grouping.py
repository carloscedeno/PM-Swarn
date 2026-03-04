from src.logic.state_grouping import classify_state_group, normalize_issue

def test_classify_state_group_queue():
    assert classify_state_group("STRATA TO DO") == "queue"
    assert classify_state_group("strata to do") == "queue"

def test_classify_state_group_blocked():
    assert classify_state_group("STRATA BLOCKED") == "blocked"
    assert classify_state_group(" strata blocked  ") == "blocked"

def test_classify_state_group_done():
    assert classify_state_group("STRATA DONE") == "done"

def test_classify_state_group_wip():
    assert classify_state_group("STRATA IN PROGRESS") == "wip"
    assert classify_state_group("STRATA IN TESTING") == "wip"
    assert classify_state_group("STRATA TO DEPLOYMENT") == "wip"
    assert classify_state_group("STRATA IN INTEGRATION") == "wip"

def test_classify_state_group_unknown(caplog):
    assert classify_state_group("SOME OTHER STATUS") == "unknown"
    assert "Unknown status encountered" in caplog.text

def test_normalize_issue():
    raw = {
        "id": "10001",
        "key": "SWARN-1",
        "fields": {
            "summary": "Implement things",
            "status": {"name": "STRATA IN TESTING"},
            "assignee": {"displayName": "Alice"},
            "updated": "2026-03-04T10:00:00Z",
            "issuetype": {"name": "Story"},
            "parent": {"key": "SWARN-EPIC-1"}
        }
    }
    
    issue = normalize_issue(raw)
    
    assert issue.id == "10001"
    assert issue.key == "SWARN-1"
    assert issue.summary == "Implement things"
    assert issue.status == "STRATA IN TESTING"
    assert issue.assignee == "Alice"
    assert issue.updated == "2026-03-04T10:00:00Z"
    assert issue.issuetype == "Story"
    assert issue.parent == "SWARN-EPIC-1"
    assert issue.state_group == "wip"
    assert issue.work_type == "STORIES"

def test_normalize_issue_minimal():
    raw = {
        "id": "10002",
        "key": "SWARN-2",
        "fields": {
            "summary": "Minimal issue",
            "status": {"name": "STRATA TO DO"},
            "updated": "2026-03-04T10:00:00Z",
            "issuetype": {"name": "Task"}
        }
    }
    
    issue = normalize_issue(raw)
    
    assert issue.id == "10002"
    assert issue.key == "SWARN-2"
    assert issue.summary == "Minimal issue"
    assert issue.status == "STRATA TO DO"
    assert issue.assignee is None
    assert issue.parent is None
    assert issue.state_group == "queue"
    assert issue.work_type == "STORIES"

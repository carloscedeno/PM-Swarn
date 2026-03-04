from unittest.mock import MagicMock
from src.jira.client import JiraClient
from src.jira.jql import fetch_issues_by_jql

def test_fetch_issues_by_jql_success():
    mock_client = MagicMock(spec=JiraClient)
    
    mock_client.execute_jql.side_effect = [
        {
            "total": 2,
            "issues": [
                {"id": "1001", "key": "STRATA-1", "fields": {"summary": "Test 1"}},
                {"id": "1002", "key": "STRATA-2", "fields": {"summary": "Test 2"}}
            ]
        }
    ]
    
    result = fetch_issues_by_jql("project = STRATA", client=mock_client)
    
    assert "error_code" not in result
    assert result["total"] == 2
    assert len(result["issues"]) == 2
    assert result["issues"][0]["key"] == "STRATA-1"
    
    # Verify the client was called with the correct fields
    mock_client.execute_jql.assert_called_once()
    _, kwargs = mock_client.execute_jql.call_args
    assert "summary" in kwargs["fields"]
    assert "status" in kwargs["fields"]
    assert kwargs["start_at"] == 0

def test_fetch_issues_by_jql_pagination():
    mock_client = MagicMock(spec=JiraClient)
    
    mock_client.execute_jql.side_effect = [
        {
            "total": 3,
            "issues": [
                {"id": "1", "key": "S-1"},
                {"id": "2", "key": "S-2"}
            ]
        },
        {
            "total": 3,
            "issues": [
                {"id": "3", "key": "S-3"}
            ]
        }
    ]
    
    result = fetch_issues_by_jql("project = S", client=mock_client)
    
    assert "error_code" not in result
    assert result["total"] == 3
    assert len(result["issues"]) == 3
    assert mock_client.execute_jql.call_count == 2

def test_fetch_issues_by_jql_error():
    mock_client = MagicMock(spec=JiraClient)
    mock_client.execute_jql.return_value = {
        "error_code": "HTTP_400",
        "error_message": "Bad Request"
    }
    
    result = fetch_issues_by_jql("invalid jql", client=mock_client)
    
    assert "error_code" in result
    assert result["error_code"] == "HTTP_400"
    assert "issues" not in result

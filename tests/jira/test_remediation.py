import pytest
import respx
import httpx
from src.jira.client import JiraClient
from src.model.issue import Issue
from src.jira.remediation import remediate_issue

@pytest.fixture
def client_env(monkeypatch):
    monkeypatch.setenv("JIRA_BASE_URL", "https://example.atlassian.net")
    monkeypatch.setenv("JIRA_API_TOKEN", "fake_token")
    monkeypatch.setenv("JIRA_EMAIL", "test@example.com")

@pytest.mark.asyncio
@respx.mock
async def test_remediate_issue_new_gaps(client_env):
    client = JiraClient()
    issue = Issue(
        id="1", key="STRATA-1", summary="Sum", status="STRATA DONE", 
        updated="now", issuetype="Task", gaps=["missing_doc", "missing_stories_json"]
    )
    
    # Mock get_comments - empty
    respx.get(f"{client.base_url}/rest/api/3/issue/STRATA-1/comment").mock(
        return_value=httpx.Response(200, json={"comments": []})
    )
    
    # Mock add_comment - twice
    mock_post = respx.post(f"{client.base_url}/rest/api/3/issue/STRATA-1/comment").mock(
        return_value=httpx.Response(201, json={"id": "new-comment-id"})
    )
    
    remediated = await remediate_issue(client, issue, "http://report")
    
    assert len(remediated) == 2
    assert "missing_doc" in remediated
    assert "missing_stories_json" in remediated
    assert mock_post.call_count == 2

@pytest.mark.asyncio
@respx.mock
async def test_remediate_issue_idempotency(client_env):
    client = JiraClient()
    issue = Issue(
        id="1", key="STRATA-1", summary="Sum", status="STRATA DONE", 
        updated="now", issuetype="Task", gaps=["missing_doc"]
    )
    
    # Mock get_comments - already has the remediation
    existing_body = "Compliance Gap: missing_doc"
    respx.get(f"{client.base_url}/rest/api/3/issue/STRATA-1/comment").mock(
        return_value=httpx.Response(200, json={
            "comments": [{"id": "100", "body": existing_body}]
        })
    )
    
    mock_post = respx.post(f"{client.base_url}/rest/api/3/issue/STRATA-1/comment").mock(
        return_value=httpx.Response(201, json={"id": "should-not-be-called"})
    )
    
    remediated = await remediate_issue(client, issue, "http://report")
    
    assert len(remediated) == 0
    assert mock_post.call_count == 0

@pytest.mark.asyncio
@respx.mock
async def test_remediate_issue_no_gaps(client_env):
    client = JiraClient()
    issue = Issue(
        id="1", key="STRATA-1", summary="Sum", status="STRATA DONE", 
        updated="now", issuetype="Task", gaps=[]
    )
    
    remediated = await remediate_issue(client, issue, "http://report")
    assert remediated == []

import httpx
import pytest
import respx
from src.jira.client import JiraClient

@pytest.fixture
def client_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("JIRA_BASE_URL", "https://example.atlassian.net")
    monkeypatch.setenv("JIRA_API_TOKEN", "fake_token")
    monkeypatch.setenv("JIRA_EMAIL", "test@example.com")

def test_jira_client_init(client_env):
    client = JiraClient()
    assert client.base_url == "https://example.atlassian.net"
    assert client.api_token == "fake_token"
    assert client.email == "test@example.com"
    assert client._get_auth() == ("test@example.com", "fake_token")

@respx.mock
def test_execute_jql_success(client_env):
    client = JiraClient()
    
    jql_query = "project = STRATA"
    mock_url = f"{client.base_url}/rest/api/3/search"
    mock_response = {
        "startAt": 0,
        "maxResults": 50,
        "total": 1,
        "issues": [{"id": "1", "key": "STRATA-1"}]
    }
    
    request = respx.post(mock_url).mock(return_value=httpx.Response(200, json=mock_response))
    
    result = client.execute_jql(jql=jql_query, fields=["summary"])
    
    assert request.called
    assert "error_code" not in result
    assert result["total"] == 1
    assert result["issues"][0]["key"] == "STRATA-1"

@respx.mock
def test_execute_jql_http_error(client_env):
    client = JiraClient()
    mock_url = f"{client.base_url}/rest/api/3/search"
    
    respx.post(mock_url).mock(return_value=httpx.Response(401, text="Unauthorized"))
    
    result = client.execute_jql("project = STRATA", fields=["summary"])
    
    assert "error_code" in result
    assert result["error_code"] == "HTTP_401"
    assert "Unauthorized" in result["error_message"]

@respx.mock
def test_execute_jql_timeout(client_env):
    client = JiraClient()
    mock_url = f"{client.base_url}/rest/api/3/search"
    
    respx.post(mock_url).mock(side_effect=httpx.ReadTimeout("Timeout"))
    
    result = client.execute_jql("project = STRATA", fields=["summary"])
    
    assert "error_code" in result
    assert result["error_code"] == "TIMEOUT"

def test_execute_jql_missing_config():
    client = JiraClient(base_url="", api_token="", email="")
    
    result = client.execute_jql("project = STRATA", fields=["summary"])
    
    assert "error_code" in result
    assert result["error_code"] == "CONFIG_ERROR"

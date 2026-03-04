import pytest
import respx
import httpx
from src.notion.client import NotionClient

@pytest.fixture
def client():
    return NotionClient(token="test_token")

@respx.mock
def test_query_database_success(client):
    db_id = "test_db"
    route = respx.post(f"https://api.notion.com/v1/databases/{db_id}/query").mock(
        return_value=httpx.Response(200, json={"results": []})
    )
    
    response = client.query_database(db_id)
    assert response == {"results": []}
    assert route.called

@respx.mock
def test_query_database_error(client):
    db_id = "test_db"
    respx.post(f"https://api.notion.com/v1/databases/{db_id}/query").mock(
        return_value=httpx.Response(401, text="Unauthorized")
    )
    
    response = client.query_database(db_id)
    assert response["error"] == "HTTP_401"
    assert "Unauthorized" in response["message"]

@respx.mock
def test_search_success(client):
    route = respx.post("https://api.notion.com/v1/search").mock(
        return_value=httpx.Response(200, json={"results": []})
    )
    
    response = client.search("test_query")
    assert response == {"results": []}
    assert route.called

def test_client_missing_token():
    client = NotionClient(token=None)
    # Ensure no environment variable is interfering
    import os
    orig_token = os.environ.get("NOTION_TOKEN")
    if "NOTION_TOKEN" in os.environ:
        del os.environ["NOTION_TOKEN"]
    
    try:
        response = client.query_database("db")
        assert response["error"] == "NOTION_TOKEN_MISSING"
        
        response = client.search("query")
        assert response["error"] == "NOTION_TOKEN_MISSING"
    finally:
        if orig_token:
            os.environ["NOTION_TOKEN"] = orig_token

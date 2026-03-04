import pytest
import respx
import httpx
from src.notion.client import NotionClient

@pytest.fixture
def client():
    return NotionClient(token="test_token")

@pytest.mark.asyncio
@respx.mock
async def test_query_database_success(client):
    db_id = "test_db"
    route = respx.post(f"https://api.notion.com/v1/databases/{db_id}/query").mock(
        return_value=httpx.Response(200, json={"results": []})
    )
    
    response = await client.query_database(db_id)
    assert response == {"results": []}
    assert route.called

@pytest.mark.asyncio
@respx.mock
async def test_query_database_error(client):
    db_id = "test_db"
    respx.post(f"https://api.notion.com/v1/databases/{db_id}/query").mock(
        return_value=httpx.Response(401, text="Unauthorized")
    )
    
    response = await client.query_database(db_id)
    assert response["error"] == "HTTP_401"
    assert "Unauthorized" in response["message"]

@pytest.mark.asyncio
@respx.mock
async def test_search_success(client):
    route = respx.post("https://api.notion.com/v1/search").mock(
        return_value=httpx.Response(200, json={"results": []})
    )
    
    response = await client.search("test_query")
    assert response == {"results": []}
    assert route.called

@pytest.mark.asyncio
async def test_client_missing_token():
    client = NotionClient(token=None)
    # Ensure no environment variable is interfering
    import os
    orig_token = os.environ.get("NOTION_TOKEN")
    if "NOTION_TOKEN" in os.environ:
        del os.environ["NOTION_TOKEN"]
    
    try:
        response = await client.query_database("db")
        assert response["error"] == "NOTION_TOKEN_MISSING"
        
        response = await client.search("query")
        assert response["error"] == "NOTION_TOKEN_MISSING"
    finally:
        if orig_token:
            os.environ["NOTION_TOKEN"] = orig_token
@pytest.mark.asyncio
@respx.mock
async def test_create_page_success(client):
    route = respx.post("https://api.notion.com/v1/pages").mock(
        return_value=httpx.Response(200, json={"id": "page_123"})
    )
    
    response = await client.create_page("parent_123", {"title": []})
    assert response["id"] == "page_123"
    assert route.called

@pytest.mark.asyncio
@respx.mock
async def test_append_block_children_success(client):
    block_id = "block_123"
    route = respx.patch(f"https://api.notion.com/v1/blocks/{block_id}/children").mock(
        return_value=httpx.Response(200, json={"results": []})
    )
    
    response = await client.append_block_children(block_id, [{"type": "paragraph"}])
    assert response == {"results": []}
    assert route.called

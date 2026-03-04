import pytest
import os
from unittest.mock import MagicMock
from src.notion.search_docs import resolve_notion_doc
from src.notion.client import NotionClient

@pytest.fixture
def mock_client():
    return MagicMock(spec=NotionClient)

def test_resolve_notion_doc_db_hit(mock_client):
    os.environ["NOTION_DOCS_DATABASE_ID"] = "test_db"
    mock_client.query_database.return_value = {
        "results": [{"url": "https://notion.so/page1"}]
    }
    
    url = resolve_notion_doc("STORY-005", mock_client)
    assert url == "https://notion.so/page1"
    mock_client.query_database.assert_called_once()

def test_resolve_notion_doc_search_hit(mock_client):
    os.environ["NOTION_DOCS_DATABASE_ID"] = "test_db"
    # DB search fails
    mock_client.query_database.return_value = {"results": []}
    # Global search hits
    mock_client.search.return_value = {
        "results": [
            {
                "url": "https://notion.so/page-STORY-005",
                "properties": {
                    "title": {
                        "type": "title",
                        "title": [{"plain_text": "Spec for STORY-005"}]
                    }
                }
            }
        ]
    }
    
    url = resolve_notion_doc("STORY-005", mock_client)
    assert url == "https://notion.so/page-STORY-005"
    mock_client.search.assert_called_once_with("STORY-005")

def test_resolve_notion_doc_no_hit(mock_client):
    os.environ["NOTION_DOCS_DATABASE_ID"] = "test_db"
    mock_client.query_database.return_value = {"results": []}
    mock_client.search.return_value = {"results": []}
    
    url = resolve_notion_doc("STORY-005", mock_client)
    assert url is None

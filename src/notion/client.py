import os
import httpx
from typing import Any, Dict, List, Optional

class NotionClient:
    """Client for interacting with the Notion API."""

    def __init__(self, token: Optional[str] = None):
        """
        Initialize the Notion client.
        
        Args:
            token: The Notion Internal Integration Token. Defaults to NOTION_TOKEN env var.
        """
        self.token = token or os.environ.get("NOTION_TOKEN")
        self.version = "2022-06-28"
        self.base_url = "https://api.notion.com/v1"

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for Notion API requests."""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Notion-Version": self.version
        }

    def query_database(self, database_id: str, filter_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Query a Notion database.
        
        Args:
            database_id: The ID of the database to query.
            filter_data: Optional filter criteria.
            
        Returns:
            The API response as a dictionary.
        """
        if not self.token:
            return {"error": "NOTION_TOKEN_MISSING"}

        url = f"{self.base_url}/databases/{database_id}/query"
        try:
            with httpx.Client(headers=self._get_headers(), timeout=10.0) as client:
                response = client.post(url, json=filter_data or {})
                if response.status_code == 200:
                    return response.json()
                return {
                    "error": f"HTTP_{response.status_code}",
                    "message": response.text
                }
        except Exception as e:
            return {"error": "INTERNAL_ERROR", "message": str(e)}

    def search(self, query: str) -> Dict[str, Any]:
        """
        Search for pages or databases.
        
        Args:
            query: The search query string.
            
        Returns:
            The API response as a dictionary.
        """
        if not self.token:
            return {"error": "NOTION_TOKEN_MISSING"}

        url = f"{self.base_url}/search"
        payload = {
            "query": query,
            "filter": {"property": "object", "value": "page"},
            "page_size": 5
        }
        try:
            with httpx.Client(headers=self._get_headers(), timeout=10.0) as client:
                response = client.post(url, json=payload)
                if response.status_code == 200:
                    return response.json()
                return {
                    "error": f"HTTP_{response.status_code}",
                    "message": response.text
                }
        except Exception as e:
            return {"error": "INTERNAL_ERROR", "message": str(e)}

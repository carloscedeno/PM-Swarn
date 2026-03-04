import os
import httpx
from typing import Any, Dict, List, Optional

class JiraClient:
    """Client for interacting with the Jira REST API."""

    def __init__(self, base_url: Optional[str] = None, api_token: Optional[str] = None, email: Optional[str] = None):
        """
        Initialize the Jira client.
        
        Args:
            base_url: The Jira instance URL. Defaults to JIRA_BASE_URL env var.
            api_token: The Jira API token. Defaults to JIRA_API_TOKEN env var.
            email: The Jira account email. Defaults to JIRA_EMAIL env var.
        """
        self.base_url = base_url or os.environ.get("JIRA_BASE_URL", "").rstrip("/")
        self.api_token = api_token or os.environ.get("JIRA_API_TOKEN")
        self.email = email or os.environ.get("JIRA_EMAIL")

        if not self.base_url or not self.api_token or not self.email:
            # In a real app we might raise an error here, but we will handle auth lazily
            pass

    def _get_auth(self) -> tuple[str, str]:
        """Get HTTP basic auth tuple."""
        return (self.email or "", self.api_token or "")

    async def execute_jql(self, jql: str, fields: List[str], start_at: int = 0, max_results: int = 50) -> Dict[str, Any]:
        """
        Execute a JQL query and return the results.
        
        Args:
            jql: The JQL query string.
            fields: List of fields to return.
            start_at: The starting index.
            max_results: The maximum number of results to return per page.
            
        Returns:
            A dictionary containing either the successful response data or an error.
        """
        if not self.base_url:
            return {
                "error_code": "CONFIG_ERROR",
                "error_message": "JIRA_BASE_URL is not configured"
            }

        url = f"{self.base_url}/rest/api/3/search"
        payload = {
            "jql": jql,
            "fields": fields,
            "startAt": start_at,
            "maxResults": max_results
        }
        
        try:
            async with httpx.AsyncClient(auth=self._get_auth(), timeout=10.0) as client:
                response = await client.post(url, json=payload)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {
                        "error_code": f"HTTP_{response.status_code}",
                        "error_message": f"Jira API returned status {response.status_code}: {response.text}"
                    }
                    
        except httpx.ReadTimeout:
            return {
                "error_code": "TIMEOUT",
                "error_message": "Request to Jira API timed out."
            }
        except httpx.RequestError as e:
            return {
                "error_code": "REQUEST_ERROR",
                "error_message": f"Network error occurred: {str(e)}"
            }
        except Exception as e:
            return {
                "error_code": "INTERNAL_ERROR",
                "error_message": f"An unexpected error occurred: {str(e)}"
            }

    async def get_comments(self, issue_key: str) -> Dict[str, Any]:
        """
        Get all comments for an issue.
        
        Args:
            issue_key: The issue key (e.g., 'STRATA-1').
            
        Returns:
            A dictionary containing either the comments data or an error.
        """
        if not self.base_url:
            return {
                "error_code": "CONFIG_ERROR",
                "error_message": "JIRA_BASE_URL is not configured"
            }

        url = f"{self.base_url}/rest/api/3/issue/{issue_key}/comment"
        
        try:
            async with httpx.AsyncClient(auth=self._get_auth(), timeout=10.0) as client:
                response = await client.get(url)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {
                        "error_code": f"HTTP_{response.status_code}",
                        "error_message": f"Jira API returned status {response.status_code}: {response.text}"
                    }
                    
        except Exception as e:
            return {
                "error_code": "INTERNAL_ERROR",
                "error_message": f"An unexpected error occurred: {str(e)}"
            }

    async def add_comment(self, issue_key: str, body: str) -> Dict[str, Any]:
        """
        Add a comment to an issue.
        
        Args:
            issue_key: The issue key.
            body: The comment text.
            
        Returns:
            A dictionary containing either the created comment data or an error.
        """
        if not self.base_url:
            return {
                "error_code": "CONFIG_ERROR",
                "error_message": "JIRA_BASE_URL is not configured"
            }

        url = f"{self.base_url}/rest/api/3/issue/{issue_key}/comment"
        # Atlassian Document Format (ADF) for Jira V3 API
        payload = {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "text": body,
                                "type": "text"
                            }
                        ]
                    }
                ]
            }
        }
        
        try:
            async with httpx.AsyncClient(auth=self._get_auth(), timeout=10.0) as client:
                response = await client.post(url, json=payload)
                
                if response.status_code == 201:
                    return response.json()
                else:
                    return {
                        "error_code": f"HTTP_{response.status_code}",
                        "error_message": f"Jira API returned status {response.status_code}: {response.text}"
                    }
                    
        except Exception as e:
            return {
                "error_code": "INTERNAL_ERROR",
                "error_message": f"An unexpected error occurred: {str(e)}"
            }

import os
from typing import Optional
from .client import NotionClient

def resolve_notion_doc(issue_key: str, client: NotionClient) -> Optional[str]:
    """
    Find the associated document in Notion for a given issue key.
    
    Args:
        issue_key: The Jira issue key (e.g., 'STORY-005').
        client: The NotionClient instance.
        
    Returns:
        The URL of the Notion page if found, otherwise None.
    """
    database_id = os.environ.get("NOTION_DOCS_DATABASE_ID")
    
    # Strategy 1: Search database for issue key in title
    if database_id:
        filter_data = {
            "filter": {
                "property": "title",
                "title": {
                    "contains": issue_key
                }
            }
        }
        results = client.query_database(database_id, filter_data)
        if results and "results" in results and len(results["results"]) > 0:
            return results["results"][0].get("url")

    # Strategy 2: Global search for issue key in title/content
    search_results = client.search(issue_key)
    if search_results and "results" in search_results:
        # Filter for exact or close matches in titles among search results
        for result in search_results["results"]:
            properties = result.get("properties", {})
            # Notion search results for pages usually have title in a property named 'title' or 'Name'
            title_property = properties.get("title") or properties.get("Name")
            if title_property and title_property.get("type") == "title":
                title_text = "".join([t.get("plain_text", "") for t in title_property.get("title", [])])
                if issue_key in title_text:
                    return result.get("url")
            
            # If no obvious title match, we can still fall back to the first search result
            # as Notion search already filters by the query string.
            if not result.get("url"):
                continue
            
            # Additional heuristic: if issue_key is in the URL, it's a strong sign
            if issue_key.lower() in result.get("url", "").lower():
                return result.get("url")

        # Fallback to first result if any
        if len(search_results["results"]) > 0:
            return search_results["results"][0].get("url")

    return None

from typing import Any, Dict, List
from src.jira.client import JiraClient

async def fetch_issues_by_jql(jql: str, client: JiraClient | None = None) -> Dict[str, Any]:
    """
    Fetch issues from Jira using the given JQL, requesting the minimum required fields.
    
    Minimum fields for auditing:
    - key, id
    - summary, issuetype, status, assignee, updated, parent
    - attachment, issuelinks (for evidence verification)
    
    Args:
        jql: The JQL string.
        client: An optional JiraClient instance.
        
    Returns:
        A dictionary with a list of 'issues', or 'error_code'/'error_message' if failed.
    """
    if client is None:
        client = JiraClient()
        
    required_fields = [
        "summary",
        "issuetype",
        "status",
        "assignee",
        "updated",
        "parent",
        "attachment",
        "issuelinks"
    ]
    
    all_issues: List[Dict[str, Any]] = []
    start_at = 0
    max_results = 50
    
    while True:
        response = await client.execute_jql(
            jql=jql,
            fields=required_fields,
            start_at=start_at,
            max_results=max_results
        )
        
        if "error_code" in response:
            return response
            
        issues = response.get("issues", [])
        all_issues.extend(issues)
        
        total = response.get("total", 0)
        start_at += len(issues)
        
        if start_at >= total or not issues:
            break
            
    return {
        "total": len(all_issues),
        "issues": all_issues
    }

from typing import List, Dict, Any
from src.jira.client import JiraClient
from src.model.issue import Issue

# Mapping of gap codes to human-readable rules and documentation references
GAP_RULES = {
    "missing_doc": {
        "rule": "Every STRATA DONE issue must have an associated Notion document in the Product Documentation DB.",
        "failed_rule": "Notion Document missing",
        "action": "Please ensure a Notion page exists and matches the issue key."
    },
    "invalid_doc": {
        "rule": "Notion documentation must contain all 4 required sections (Overview, Implementation, Verification, Maintenance) and reference the issue key.",
        "failed_rule": "Incomplete Notion Document",
        "action": "Please update the Notion document to include all required sections."
    },
    "missing_stories_json": {
        "rule": "Issues with work_type=STORIES must have a 'stories.json' file attached or linked in Jira.",
        "failed_rule": "stories.json evidence missing",
        "action": "Please attach or link the 'stories.json' file to this Jira issue."
    }
}

async def remediate_issue(client: JiraClient, issue: Issue, report_url: str) -> List[str]:
    """
    Apply idempotent remediation for compliance gaps detected in an issue.
    
    Args:
        client: The JiraClient instance.
        issue: The normalized Issue model.
        report_url: URL to the full Notion report.
        
    Returns:
        A list of gap types that were remediated (commented on).
    """
    if not issue.gaps:
        return []

    # Fetch existing comments to prevent duplicates
    comments_result = await client.get_comments(issue.key)
    existing_comments = []
    if "comments" in comments_result:
        for comment in comments_result["comments"]:
            # Jira V3 API comment body is a complex ADF structure
            # We simplify search by looking for the gap code in the flattened text
            # In a real app we'd be more rigorous
            body = str(comment.get("body", ""))
            existing_comments.append(body)

    remediated = []
    
    for gap in issue.gaps:
        if gap not in GAP_RULES:
            continue
            
        # Check if we already remediated this specific gap
        # We look for a specific signature in the comments
        signature = f"Compliance Gap: {gap}"
        if any(signature in c for c in existing_comments):
            continue
            
        rule_info = GAP_RULES[gap]
        comment_body = (
            f"⚠️ {signature}\n\n"
            f"*Failed Rule:* {rule_info['failed_rule']}\n"
            f"*Action:* {rule_info['action']}\n\n"
            f"Details: {rule_info['rule']}\n"
            f"Full Report: {report_url}"
        )
        
        result = await client.add_comment(issue.key, comment_body)
        if "id" in result:
            remediated.append(gap)
            
    return remediated

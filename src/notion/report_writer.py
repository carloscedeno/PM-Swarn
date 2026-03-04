import os
import datetime
from typing import List, Dict, Any
from src.model.issue import Issue
from .client import NotionClient

async def generate_run_report(run_id: str, jql: str, issues: List[Issue], client: NotionClient) -> Dict[str, Any]:
    """
    Generate an audit report in Notion.
    
    Args:
        run_id: Unique identifier for the run.
        jql: The JQL used to pull issues.
        issues: List of normalized Issue objects.
        client: NotionClient instance.
        
    Returns:
        The API response from Notion.
    """
    parent_id = os.environ.get("NOTION_REPORTS_PARENT_ID")
    if not parent_id:
        return {"error": "NOTION_REPORTS_PARENT_ID_MISSING"}

    # 1. Compute KPIs
    kpis = _compute_kpis(issues)
    
    # 2. Prepare Page Properties
    timestamp = datetime.datetime.now().isoformat()
    properties = {
        "title": {
            "title": [{"text": {"content": f"Audit Report: {run_id} - {timestamp}"}}]
        }
    }
    
    # 3. Prepare Block Children (Content)
    children = _prepare_report_blocks(run_id, jql, kpis, issues)
    
    # 4. Create Page
    return await client.create_page(parent_id, properties, children)

def _compute_kpis(issues: List[Issue]) -> Dict[str, int]:
    """Compute KPIs from a list of issues."""
    kpis = {
        "total": len(issues),
        "done": 0,
        "wip": 0,
        "blocked": 0,
        "queue": 0,
        "missing_doc": 0,
        "invalid_doc": 0,
        "missing_stories_json": 0,
        "compliant_done": 0,
        "non_compliant_done": 0
    }
    
    for issue in issues:
        # State groups
        if issue.state_group == "done": kpis["done"] += 1
        elif issue.state_group == "wip": kpis["wip"] += 1
        elif issue.state_group == "blocked": kpis["blocked"] += 1
        elif issue.state_group == "queue": kpis["queue"] += 1
        
        # Gaps
        if "missing_doc" in issue.gaps: kpis["missing_doc"] += 1
        if "invalid_doc" in issue.gaps: kpis["invalid_doc"] += 1
        if "missing_stories_json" in issue.gaps: kpis["missing_stories_json"] += 1
        
        # Compliance (only for done)
        if issue.state_group == "done":
            if issue.compliance_status == "compliant":
                kpis["compliant_done"] += 1
            else:
                kpis["non_compliant_done"] += 1
                
    return kpis

def _prepare_report_blocks(run_id: str, jql: str, kpis: Dict[str, int], issues: List[Issue]) -> List[Dict[str, Any]]:
    """Prepare Notion blocks for the report."""
    blocks = [
        _heading(1, "Run Metadata"),
        _paragraph(f"**Run ID:** {run_id}"),
        _paragraph(f"**Timestamp:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"),
        _paragraph(f"**JQL Used:** `{jql}`"),
        
        _heading(1, "KPIs Overview"),
        _bullet(f"**Total Issues:** {kpis['total']}"),
        _bullet(f"**Done:** {kpis['done']} ({kpis['compliant_done']} compliant / {kpis['non_compliant_done']} non-compliant)"),
        _bullet(f"**WIP:** {kpis['wip']}"),
        _bullet(f"**Blocked:** {kpis['blocked']}"),
        _bullet(f"**Queue:** {kpis['queue']}"),
        
        _heading(2, "Detected Gaps"),
        _bullet(f"**Missing Docs:** {kpis['missing_doc']}"),
        _bullet(f"**Invalid Docs:** {kpis['invalid_doc']}"),
        _bullet(f"**Missing stories.json:** {kpis['missing_stories_json']}"),
        
        _heading(1, "Issue Details"),
    ]
    
    # Add issue-level details (simplified for MVP/Notion limits, only non-compliant/blocked first)
    priority_issues = [i for i in issues if i.compliance_status == "non-compliant" or i.state_group == "blocked"]
    
    if priority_issues:
        blocks.append(_heading(2, "Priority Findings (Non-Compliant or Blocked)"))
        for issue in priority_issues:
            gaps_str = ", ".join(issue.gaps) if issue.gaps else "None"
            blocks.append(_bullet(f"[{issue.key}](https://your-domain.atlassian.net/browse/{issue.key}) - {issue.status} - Gaps: {gaps_str}"))
    else:
        blocks.append(_paragraph("No priority findings detected in this run."))
        
    return blocks

# Helper functions for Notion Block creation
def _heading(level: int, text: str) -> Dict[str, Any]:
    type_map = {1: "heading_1", 2: "heading_2", 3: "heading_3"}
    return {
        "object": "block",
        "type": type_map[level],
        type_map[level]: {
            "rich_text": [{"type": "text", "text": {"content": text}}]
        }
    }

def _paragraph(text: str) -> Dict[str, Any]:
    # Basic markdown parsing for bold and code
    rich_text = []
    # Simplified parser: splits by ** or `
    import re
    tokens = re.split(r'(\*\*.*?\*\*|`.*?`)', text)
    for token in tokens:
        if token.startswith("**") and token.endswith("**"):
            rich_text.append({"type": "text", "text": {"content": token[2:-2]}, "annotations": {"bold": True}})
        elif token.startswith("`") and token.endswith("`"):
            rich_text.append({"type": "text", "text": {"content": token[1:-1]}, "annotations": {"code": True}})
        elif token:
            rich_text.append({"type": "text", "text": {"content": token}})
            
    return {
        "object": "block",
        "type": "paragraph",
        "paragraph": {"rich_text": rich_text}
    }

def _bullet(text: str) -> Dict[str, Any]:
    # Re-using paragraph rich_text logic would be better but keeping it simple for now
    rich_text = []
    import re
    # Match links [text](url)
    parts = re.split(r'(\[.*?\]\(.*?\))', text)
    for part in parts:
        link_match = re.match(r'\[(.*?)\]\((.*?)\)', part)
        if link_match:
            rich_text.append({
                "type": "text", 
                "text": {"content": link_match.group(1), "link": {"url": link_match.group(2)}}
            })
        else:
            # Fallback to bold/code for the rest
            tokens = re.split(r'(\*\*.*?\*\*|`.*?`)', part)
            for token in tokens:
                if token.startswith("**") and token.endswith("**"):
                    rich_text.append({"type": "text", "text": {"content": token[2:-2]}, "annotations": {"bold": True}})
                elif token.startswith("`") and token.endswith("`"):
                    rich_text.append({"type": "text", "text": {"content": token[1:-1]}, "annotations": {"code": True}})
                elif token:
                    rich_text.append({"type": "text", "text": {"content": token}})

    return {
        "object": "block",
        "type": "bulleted_list_item",
        "bulleted_list_item": {"rich_text": rich_text}
    }

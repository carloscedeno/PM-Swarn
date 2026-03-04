from typing import Any, Dict
from src.model.issue import Issue

def verify_evidence(issue: Issue, raw_issue: Dict[str, Any]) -> None:
    """
    Verify evidence (stories.json) for an issue.
    
    If work_type is STORIES, it checks attachments and links for 'stories.json'.
    If status is STRATA DONE and evidence is missing, it records a gap.
    """
    if issue.work_type != "STORIES":
        return

    fields = raw_issue.get("fields", {})
    
    # Check attachments
    attachments = fields.get("attachment", [])
    found_in_attachments = any(
        "stories.json" in (att.get("filename", "").lower())
        for att in attachments
    )
    
    # Check issue links
    issuelinks = fields.get("issuelinks", [])
    found_in_links = False
    for link in issuelinks:
        # Check outward/inward issue summaries or descriptions if available
        # or if the link itself has a name containing stories.json (though usually it's a URL)
        outward = link.get("outwardIssue", {})
        inward = link.get("inwardIssue", {})
        
        link_text = (
            (outward.get("fields", {}).get("summary", "") or "") + 
            (inward.get("fields", {}).get("summary", "") or "")
        ).lower()
        
        if "stories.json" in link_text:
            found_in_links = True
            break
            
    issue.stories_json_present = found_in_attachments or found_in_links
    
    # Check for gaps if status is STRATA DONE
    if issue.status == "STRATA DONE" and not issue.stories_json_present:
        if "missing_stories_json" not in issue.gaps:
            issue.gaps.append("missing_stories_json")

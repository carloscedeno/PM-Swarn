import logging
from typing import Dict, Any
from src.model.issue import Issue

logger = logging.getLogger(__name__)

def verify_bead_evidence(issue: Issue, raw_bead: Dict[str, Any]):
    """
    Verify if stories.json exists as an attachment/link or in description.
    Updates issue.stories_json_present and issue.gaps.
    """
    if issue.work_type != "STORIES":
        return
        
    issue.stories_json_present = False
    
    # 1. Check description for conventional section
    description = raw_bead.get("description", "")
    if "stories.json" in description.lower():
        issue.stories_json_present = True
    
    # 2. Check attachments/links if present in Beadbox structure
    attachments = raw_bead.get("attachments", [])
    for attachment in attachments:
        if isinstance(attachment, dict):
            name = attachment.get("name", "")
            if "stories.json" in name.lower():
                issue.stories_json_present = True
                break
        elif isinstance(attachment, str) and "stories.json" in attachment.lower():
            issue.stories_json_present = True
            break
            
    # 3. Apply compliance rules for STRATA DONE
    if issue.status == "STRATA DONE":
        if not issue.stories_json_present:
            if "missing_stories_json" not in issue.gaps:
                issue.gaps.append("missing_stories_json")
                issue.compliance_status = "non-compliant"

import logging
from typing import Dict, Any
from src.model.issue import Issue
from src.logic.work_type_detection import detect_work_type
from src.jira.evidence import verify_evidence

logger = logging.getLogger(__name__)

def classify_state_group(status: str) -> str:
    """
    Classify a Beadbox/Jira status into an internal state_group.
    
    Rules:
    - `STRATA TO DO`, `STRATA TO DEPLOYMENT` -> `queue` / `wip`
    - `STRATA BLOCKED` -> `blocked`
    - `STRATA DONE` -> `done`
    - `STRATA IN PROGRESS`, `STRATA IN TESTING`, `STRATA IN INTEGRATION` -> `wip`
    - Any other (PRD states) -> `queue` or `wip` depending on context, 
      but for Stories check they are mostly not 'done'.
    """
    status_upper = status.upper().strip()
    
    if status_upper in ["STRATA TO DO"]:
        return "queue"
    elif status_upper == "STRATA BLOCKED":
        return "blocked"
    elif status_upper == "STRATA DONE":
        return "done"
    elif status_upper in [
        "STRATA IN PROGRESS", 
        "STRATA IN TESTING", 
        "STRATA TO DEPLOYMENT", 
        "STRATA IN INTEGRATION"
    ]:
        return "wip"
    else:
        # Many PRD states are effectively backlog/queue for the SDLC check
        from src.logic.work_type_detection import PRD_STATES
        if status_upper in PRD_STATES:
            return "queue"
            
        logger.warning(f"Unknown status encountered for state_group classification: {status}")
        return "unknown"

def normalize_issue(raw_data: Dict[str, Any]) -> Issue:
    """
    Normalize raw data (Beadbox bead or Jira issue) into an Issue model instance.
    """
    # Detect if it's Beadbox or Jira based on presence of 'fields'
    if "fields" in raw_data:
        # Jira structure
        fields = raw_data.get("fields", {})
        status_obj = fields.get("status", {})
        status_name = status_obj.get("name", "UNKNOWN_STATUS") if isinstance(status_obj, dict) else "UNKNOWN_STATUS"
        
        assignee_obj = fields.get("assignee")
        assignee_name = assignee_obj.get("displayName") if isinstance(assignee_obj, dict) else None
        
        issuetype_obj = fields.get("issuetype", {})
        issuetype_name = issuetype_obj.get("name", "UNKNOWN_TYPE") if isinstance(issuetype_obj, dict) else "UNKNOWN_TYPE"
        
        parent_obj = fields.get("parent")
        parent_key = parent_obj.get("key") if isinstance(parent_obj, dict) else None
        
        issue_id = str(raw_data.get("id", ""))
        issue_key = raw_data.get("key", "")
        summary = fields.get("summary", "")
        updated = fields.get("updated", "")
    else:
        # Beadbox structure (per client.py and PRD)
        issue_id = str(raw_data.get("id", ""))
        issue_key = raw_data.get("key", issue_id) # Beads might use id as key if key missing
        summary = raw_data.get("summary", raw_data.get("title", ""))
        status_name = raw_data.get("status", "UNKNOWN_STATUS")
        assignee_name = raw_data.get("assignee")
        updated = raw_data.get("updated_at", "")
        issuetype_name = raw_data.get("type", "Story")
        parent_key = raw_data.get("parent_id")

    # Compute state_group
    state_group = classify_state_group(status_name)
    
    # Compute work_type
    work_type = detect_work_type(status_name)
    
    issue = Issue(
        id=issue_id,
        key=issue_key,
        summary=summary,
        status=status_name,
        assignee=assignee_name,
        updated=updated,
        issuetype=issuetype_name,
        parent=parent_key,
        state_group=state_group,
        work_type=work_type
    )
    
    # Local check for stories.json evidence in description (Beadbox style)
    if "description" in raw_data:
        desc = raw_data["description"]
        if "stories.json" in desc.lower():
            issue.stories_json_present = True

    # Note: verify_evidence (Jira specific) might need a Beadbox version or remain for hybrid
    # For now, we manually handle description check above.
    
    return issue

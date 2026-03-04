import logging
from typing import Dict, Any
from src.model.issue import Issue
from src.logic.work_type_detection import detect_work_type

logger = logging.getLogger(__name__)

def classify_state_group(status: str) -> str:
    """
    Classify a Jira status into an internal state_group.
    
    Rules:
    - `STRATA TO DO` -> `queue`
    - `STRATA BLOCKED` -> `blocked`
    - `STRATA DONE` -> `done`
    - `STRATA IN PROGRESS`, `STRATA IN TESTING`, `STRATA TO DEPLOYMENT`, `STRATA IN INTEGRATION` -> `wip`
    - Any other -> `unknown` (and logs a warning)
    """
    status_upper = status.upper().strip()
    
    if status_upper == "STRATA TO DO":
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
        logger.warning(f"Unknown status encountered for state_group classification: {status}")
        return "unknown"

def normalize_issue(raw_issue_dict: Dict[str, Any]) -> Issue:
    """
    Normalize a raw Jira issue dictionary into an Issue model instance.
    Expected raw format roughly matches the fields requested from Jira.
    """
    # Extract fields from nested Jira structure (assuming standard Jira API v3 format)
    # The actual structure of raw_issue_dict from the API is usually:
    # {
    #   "id": "10000",
    #   "key": "DEV-1",
    #   "fields": {
    #       "summary": "...",
    #       "status": {"name": "STRATA TO DO", ...},
    #       "assignee": {"displayName": "...", ...} or None,
    #       "updated": "2023-01-01...",
    #       "issuetype": {"name": "Story", ...},
    #       "parent": {"key": "EPIC-1", ...} or not present
    #   }
    # }
    
    fields = raw_issue_dict.get("fields", {})
    
    # Status
    status_obj = fields.get("status", {})
    status_name = status_obj.get("name", "UNKNOWN_STATUS") if isinstance(status_obj, dict) else "UNKNOWN_STATUS"
    
    # Assignee
    assignee_obj = fields.get("assignee")
    assignee_name = None
    if isinstance(assignee_obj, dict):
        assignee_name = assignee_obj.get("displayName") or assignee_obj.get("accountId")
        
    # Issue Type
    issuetype_obj = fields.get("issuetype", {})
    issuetype_name = issuetype_obj.get("name", "UNKNOWN_TYPE") if isinstance(issuetype_obj, dict) else "UNKNOWN_TYPE"
    
    # Parent
    parent_obj = fields.get("parent")
    parent_key = parent_obj.get("key") if isinstance(parent_obj, dict) else None
    
    # Base issue properties
    issue_id = raw_issue_dict.get("id", "")
    issue_key = raw_issue_dict.get("key", "")
    summary = fields.get("summary", "")
    updated = fields.get("updated", "")
    
    # Compute state_group
    state_group = classify_state_group(status_name)
    
    # Compute work_type
    work_type = detect_work_type(status_name)
    
    return Issue(
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

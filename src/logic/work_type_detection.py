import logging
from typing import Set

logger = logging.getLogger(__name__)

PRD_STATES: Set[str] = {
    "PRD CREATED",
    "STRATA GROOMING",
    "STRATA TO PRODUCT REVIEW",
    "TO REVIEW",
    "STRATA TECHNICAL PRD",
    "STRATA STORIES.JSON CREATION",
    "TO DEVELOPMENT",
    "ON HOLD",
    "ON HOLD TO ASSIGN",
    "WAITING FOR DEVELOPMENT"
}

STORIES_STATES: Set[str] = {
    "STRATA TO DO",
    "STRATA IN PROGRESS",
    "STRATA IN TESTING",
    "STRATA TO DEPLOYMENT",
    "STRATA IN INTEGRATION",
    "STRATA BLOCKED",
    "STRATA DONE"
}

def detect_work_type(status: str) -> str:
    """
    Determine if an issue belongs to the PRD or STORIES workflow
    based on its status. 
    Returns:
        "PRD", "STORIES", or "unknown"
    """
    status_upper = status.upper().strip()
    
    if status_upper in PRD_STATES:
        return "PRD"
    elif status_upper in STORIES_STATES:
        return "STORIES"
    else:
        logger.warning(f"Unknown status encountered for work_type classification: {status}")
        return "unknown"

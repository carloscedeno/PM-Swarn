from typing import Optional
from pydantic import BaseModel

class Issue(BaseModel):
    """Normalized Jira issue model."""
    id: str
    key: str
    summary: str
    status: str
    assignee: Optional[str] = None
    updated: str
    issuetype: str
    parent: Optional[str] = None
    state_group: Optional[str] = None
    work_type: Optional[str] = None

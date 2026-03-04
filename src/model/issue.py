from typing import Optional, List
from pydantic import BaseModel, Field

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
    stories_json_present: Optional[bool] = None
    gaps: List[str] = Field(default_factory=list)

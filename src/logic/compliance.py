from src.model.issue import Issue

def compute_compliance(issue: Issue) -> Issue:
    """
    Compute compliance for STRATA DONE issues.
    
    If status is STRATA DONE, it requires:
    - notion_doc_url is not None (gap: missing_doc)
    - doc_status is 'valid' (gap: invalid_doc)
    - stories_json_present is True (gap: missing_stories_json)
    """
    if issue.status.upper() != "STRATA DONE":
        return issue

    new_gaps = []
    
    if issue.notion_doc_url is None:
        new_gaps.append("missing_doc")
    
    if issue.notion_doc_url is not None and issue.doc_status == "invalid":
        new_gaps.append("invalid_doc")
        
    if issue.stories_json_present is not True:
        new_gaps.append("missing_stories_json")
        
    # Append new gaps to existing gaps, avoiding duplicates
    for gap in new_gaps:
        if gap not in issue.gaps:
            issue.gaps.append(gap)
            
    if not new_gaps:
        issue.compliance_status = "compliant"
    else:
        issue.compliance_status = "non-compliant"
        
    return issue

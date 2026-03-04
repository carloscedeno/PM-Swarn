from typing import List, Dict, Any, Optional

def validate_doc(content: str, issue_key: str) -> Dict[str, Any]:
    """
    Validates that a Notion document contains the required minimum sections
    and an explicit reference to the Jira issue key.
    
    Required Sections:
    1. Context / Problem
    2. Solution / Decision
    3. Acceptance criteria or Definition of Done
    4. Explicit reference to the issue key
    
    Args:
        content: The text content of the Notion page.
        issue_key: The Jira issue key to look for.
        
    Returns:
        A dictionary containing:
        - doc_status: 'valid', 'invalid', or 'missing'
        - missing_sections: A list of missing section names
    """
    if not content:
        return {
            "doc_status": "missing",
            "missing_sections": ["Full Content"]
        }
    
    required_sections = [
        "Context / Problem",
        "Solution / Decision",
        "Acceptance criteria",
    ]
    
    missing_sections = []
    
    # Simple check for sections (case-insensitive)
    content_lower = content.lower()
    for section in required_sections:
        if section.lower() not in content_lower:
            # Special case for "Acceptance criteria or Definition of Done"
            if section == "Acceptance criteria":
                if "definition of done" not in content_lower:
                    missing_sections.append(section)
            else:
                missing_sections.append(section)
                
    # Check for explicit issue key reference
    if issue_key.lower() not in content_lower:
        missing_sections.append(f"Reference to {issue_key}")
        
    status = "valid" if not missing_sections else "invalid"
    
    return {
        "doc_status": status,
        "missing_sections": missing_sections
    }

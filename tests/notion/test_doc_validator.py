import pytest
from src.notion.doc_validator import validate_doc

def test_validate_doc_valid():
    content = """
    # Context / Problem
    This is a problem description.
    
    # Solution / Decision
    This is the solution.
    
    # Acceptance criteria
    - It works.
    
    Reference: STORY-006
    """
    result = validate_doc(content, "STORY-006")
    assert result["doc_status"] == "valid"
    assert len(result["missing_sections"]) == 0

def test_validate_doc_missing_sections():
    content = """
    # Context / Problem
    This is a problem description.
    
    Reference: STORY-006
    """
    result = validate_doc(content, "STORY-006")
    assert result["doc_status"] == "invalid"
    assert "Solution / Decision" in result["missing_sections"]
    assert "Acceptance criteria" in result["missing_sections"]

def test_validate_doc_missing_key():
    content = """
    # Context / Problem
    This is a problem description.
    
    # Solution / Decision
    This is the solution.
    
    # Acceptance criteria
    - It works.
    """
    result = validate_doc(content, "STORY-006")
    assert result["doc_status"] == "invalid"
    assert "Reference to STORY-006" in result["missing_sections"]

def test_validate_doc_alternative_dod():
    content = """
    # Context / Problem
    This is a problem description.
    
    # Solution / Decision
    This is the solution.
    
    # Definition of Done
    - It works.
    
    Reference: STORY-006
    """
    result = validate_doc(content, "STORY-006")
    assert result["doc_status"] == "valid"
    assert len(result["missing_sections"]) == 0

def test_validate_doc_empty():
    result = validate_doc("", "STORY-006")
    assert result["doc_status"] == "missing"
    assert "Full Content" in result["missing_sections"]

def test_validate_doc_none():
    result = validate_doc(None, "STORY-006")
    assert result["doc_status"] == "missing"
    assert "Full Content" in result["missing_sections"]

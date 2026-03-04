import pytest
from src.logic.work_type_detection import detect_work_type

def test_detect_work_type_prd():
    assert detect_work_type("PRD CREATED") == "PRD"
    assert detect_work_type("STRATA GROOMING") == "PRD"
    assert detect_work_type("STRATA TO PRODUCT REVIEW") == "PRD"
    assert detect_work_type("TO REVIEW") == "PRD"
    assert detect_work_type("STRATA TECHNICAL PRD") == "PRD"
    assert detect_work_type("STRATA STORIES.JSON CREATION") == "PRD"
    assert detect_work_type("TO DEVELOPMENT") == "PRD"
    assert detect_work_type("On Hold") == "PRD"
    assert detect_work_type("ON HOLD TO ASSIGN") == "PRD"
    assert detect_work_type("Waiting for development") == "PRD"

def test_detect_work_type_stories():
    assert detect_work_type("STRATA TO DO") == "STORIES"
    assert detect_work_type("strata in progress") == "STORIES"
    assert detect_work_type("STRATA IN TESTING") == "STORIES"
    assert detect_work_type("STRATA TO DEPLOYMENT") == "STORIES"
    assert detect_work_type("STRATA IN INTEGRATION") == "STORIES"
    assert detect_work_type("STRATA BLOCKED") == "STORIES"
    assert detect_work_type("STRATA DONE") == "STORIES"

def test_detect_work_type_unknown(caplog):
    assert detect_work_type("SOME RANDOM STATUS") == "unknown"
    assert "Unknown status encountered for work_type classification: SOME RANDOM STATUS" in caplog.text

    assert detect_work_type("") == "unknown"
    assert detect_work_type("   ") == "unknown"

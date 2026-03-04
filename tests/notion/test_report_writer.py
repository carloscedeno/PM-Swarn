import pytest
import respx
import httpx
from src.notion.client import NotionClient
from src.notion.report_writer import generate_run_report, _compute_kpis
from src.model.issue import Issue

@pytest.fixture
def client():
    return NotionClient(token="test_token")

def test_compute_kpis():
    issues = [
        Issue(id="1", key="STORY-001", summary="S1", status="Done", updated="now", issuetype="Story", state_group="done", compliance_status="compliant"),
        Issue(id="2", key="STORY-002", summary="S2", status="Done", updated="now", issuetype="Story", state_group="done", compliance_status="non-compliant", gaps=["missing_doc"]),
        Issue(id="3", key="STORY-003", summary="S3", status="WIP", updated="now", issuetype="Story", state_group="wip", gaps=["invalid_doc"]),
        Issue(id="4", key="STORY-004", summary="S4", status="Blocked", updated="now", issuetype="Story", state_group="blocked", gaps=["missing_stories_json"]),
    ]
    
    kpis = _compute_kpis(issues)
    assert kpis["total"] == 4
    assert kpis["done"] == 2
    assert kpis["wip"] == 1
    assert kpis["blocked"] == 1
    assert kpis["compliant_done"] == 1
    assert kpis["non_compliant_done"] == 1
    assert kpis["missing_doc"] == 1
    assert kpis["invalid_doc"] == 1
    assert kpis["missing_stories_json"] == 1

@pytest.mark.asyncio
@respx.mock
async def test_generate_run_report_success(client, monkeypatch):
    monkeypatch.setenv("NOTION_REPORTS_PARENT_ID", "parent_123")
    
    issues = [
        Issue(id="1", key="STORY-001", summary="S1", status="Done", updated="now", issuetype="Story", state_group="done", compliance_status="compliant")
    ]
    
    route = respx.post("https://api.notion.com/v1/pages").mock(
        return_value=httpx.Response(200, json={"id": "new_page_id"})
    )
    
    response = await generate_run_report("run_1", "project = SWARN", issues, client)
    
    assert response["id"] == "new_page_id"
    assert route.called
    
    # Check payload structure (simplified)
    request_data = route.calls.last.request.read().decode()
    assert "parent_123" in request_data
    assert "Audit Report: run_1" in request_data
    assert "KPIs Overview" in request_data

@pytest.mark.asyncio
async def test_generate_run_report_missing_parent(client, monkeypatch):
    monkeypatch.delenv("NOTION_REPORTS_PARENT_ID", raising=False)
    response = await generate_run_report("run_1", "jql", [], client)
    assert response["error"] == "NOTION_REPORTS_PARENT_ID_MISSING"

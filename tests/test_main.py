import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.main import process_bead, main
from src.model.issue import Issue

@pytest.fixture
def mock_notion_client():
    client = MagicMock()
    return client

@pytest.fixture
def sample_bead():
    return {
        "id": "bead-123",
        "description": "A sample bead with stories.json",
        "state": "DONE"
    }

@pytest.mark.asyncio
async def test_process_bead_valid(mock_notion_client, sample_bead):
    with patch("src.main.normalize_issue", return_value=Issue(
        id="bead-123",
        key="bead-123",
        summary="A sample bead",
        status="STRATA DONE",
        assignee="testuser",
        updated="2026-03-04T12:00:00Z",
        issuetype="Story",
        work_type="STORIES",
        state_group="done",
        stories_json_present=False
    )), \
    patch("src.main.verify_bead_evidence", side_effect=lambda i, b: setattr(i, "stories_json_present", True)), \
    patch("src.main.resolve_notion_doc", new_callable=AsyncMock, return_value="https://notion.so/doc"):

        issue = await process_bead(sample_bead, mock_notion_client)
        
        assert issue.key == "bead-123"
        assert issue.stories_json_present is True
        assert issue.doc_status == "valid"
        assert issue.notion_doc_url == "https://notion.so/doc"

@pytest.mark.asyncio
async def test_process_bead_missing_doc(mock_notion_client, sample_bead):
    with patch("src.main.normalize_issue", return_value=Issue(
        id="bead-123",
        key="bead-123",
        summary="A sample bead",
        status="STRATA DONE",
        assignee="testuser",
        updated="2026-03-04T12:00:00Z",
        issuetype="Story",
        work_type="STORIES",
        state_group="done",
        stories_json_present=True
    )), \
    patch("src.main.verify_bead_evidence"), \
    patch("src.main.resolve_notion_doc", new_callable=AsyncMock, return_value=None):

        issue = await process_bead(sample_bead, mock_notion_client)
        
        assert issue.doc_status == "missing"
        assert "missing_doc" in issue.gaps
        assert issue.compliance_status == "non-compliant"

@pytest.mark.asyncio
async def test_main_flow():
    # Mock clients and their methods
    with patch("src.main.BeadboxClient") as mock_bead_client_cls, \
         patch("src.main.NotionClient") as mock_notion_client_cls, \
         patch("src.main.process_bead", new_callable=AsyncMock) as mock_process_bead, \
         patch("src.main.generate_run_report", new_callable=AsyncMock) as mock_generate_report, \
         patch("src.beadbox.remediation.remediate_bead", new_callable=AsyncMock) as mock_remediate_bead:
        
        mock_bead_client = mock_bead_client_cls.return_value
        mock_bead_client.list_beads.return_value = [{"id": "bead-1"}]
        
        # Mock data processing functions
        mock_issue = Issue(
            id="bead-1", key="bead-1", summary="test", status="STRATA DONE", assignee="u", updated="time", issuetype="Story"
        )
        mock_process_bead.return_value = mock_issue
        mock_generate_report.return_value = {"url": "https://test.notion.so/report"}

        # Execute main
        await main()
        
        # Verifications
        mock_bead_client.list_beads.assert_called_once()
        mock_notion_client_cls.assert_called_once()
        
        # Check that process_bead was called with the bead and the notion client
        mock_process_bead.assert_called_once_with({"id": "bead-1"}, mock_notion_client_cls.return_value)
        
        # Check generate report
        mock_generate_report.assert_called_once()
        args, _ = mock_generate_report.call_args
        assert "Beadbox" in args[1] # Check mode desc
        assert args[2] == [mock_issue] # Check processed issues

        # Check that remediation was requested
        mock_remediate_bead.assert_called_once_with(mock_bead_client, mock_issue, "https://test.notion.so/report")

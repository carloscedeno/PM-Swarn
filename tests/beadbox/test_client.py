import unittest
import os
import tempfile
import json
from unittest.mock import patch
from src.beadbox.client import BeadboxClient, BeadboxSpecialist
from src.model.issue import Issue

class TestBeadboxClient(unittest.TestCase):
    def setUp(self):
        self.temp_workspace = tempfile.TemporaryDirectory()
        self.beads_dir = os.path.join(self.temp_workspace.name, ".beads")
        os.makedirs(self.beads_dir)

    def tearDown(self):
        self.temp_workspace.cleanup()

    @patch('src.beadbox.client.BeadboxCLI.is_available')
    @patch('src.beadbox.client.BeadboxCLI.list_beads')
    def test_list_beads_with_cli(self, mock_list_beads, mock_is_available):
        mock_is_available.return_value = True
        mock_list_beads.return_value = (True, [{"id": "BEAD-001"}])
        
        client = BeadboxClient(workspace_path=self.temp_workspace.name)
        beads = client.list_beads()
        
        self.assertEqual(len(beads), 1)
        self.assertEqual(beads[0]["id"], "BEAD-001")

    @patch('src.beadbox.client.BeadboxCLI.is_available')
    def test_list_beads_fallback_registry(self, mock_is_available):
        mock_is_available.return_value = False
        
        # Create registry.json
        registry_data = [{"id": "BEAD-002"}]
        with open(os.path.join(self.beads_dir, "registry.json"), "w") as f:
            json.dump(registry_data, f)
            
        client = BeadboxClient(workspace_path=self.temp_workspace.name)
        beads = client.list_beads()
        
        self.assertEqual(len(beads), 1)
        self.assertEqual(beads[0]["id"], "BEAD-002")

    @patch('src.beadbox.client.BeadboxCLI.is_available')
    def test_list_beads_fallback_registry_dict(self, mock_is_available):
        mock_is_available.return_value = False
        
        # Create registry.json
        registry_data = {"beads": [{"id": "BEAD-003"}]}
        with open(os.path.join(self.beads_dir, "registry.json"), "w") as f:
            json.dump(registry_data, f)
            
        client = BeadboxClient(workspace_path=self.temp_workspace.name)
        beads = client.list_beads()
        
        self.assertEqual(len(beads), 1)
        self.assertEqual(beads[0]["id"], "BEAD-003")

    @patch('src.beadbox.client.BeadboxCLI.is_available')
    def test_list_beads_fallback_individual_files(self, mock_is_available):
        mock_is_available.return_value = False
        
        # Create individual bead files
        bead_data = {"id": "BEAD-004"}
        with open(os.path.join(self.beads_dir, "BEAD-004.bead"), "w") as f:
            json.dump(bead_data, f)
            
        client = BeadboxClient(workspace_path=self.temp_workspace.name)
        beads = client.list_beads()
        
        self.assertEqual(len(beads), 1)
        self.assertEqual(beads[0]["id"], "BEAD-004")

    @patch('src.beadbox.client.BeadboxCLI.is_available')
    @patch('src.beadbox.client.BeadboxCLI.list_beads')
    def test_list_beads_cli_fails_fallback_registry(self, mock_list_beads, mock_is_available):
        mock_is_available.return_value = True
        mock_list_beads.return_value = (False, [])
        
        # Create registry.json
        registry_data = [{"id": "BEAD-005"}]
        with open(os.path.join(self.beads_dir, "registry.json"), "w") as f:
            json.dump(registry_data, f)
            
        client = BeadboxClient(workspace_path=self.temp_workspace.name)
        beads = client.list_beads()
        
        self.assertEqual(len(beads), 1)
        self.assertEqual(beads[0]["id"], "BEAD-005")

class TestBeadboxSpecialist(unittest.TestCase):
    def setUp(self):
        self.temp_workspace = tempfile.TemporaryDirectory()
        self.client = BeadboxClient(workspace_path=self.temp_workspace.name)
        self.specialist = BeadboxSpecialist(client=self.client)

    @patch.object(BeadboxClient, 'list_beads')
    def test_get_issues_mapping(self, mock_list_beads):
        mock_list_beads.return_value = [
            {
                "id": "BEAD-101",
                "summary": "Test finding",
                "status": "STRATA IN PROGRESS",
                "assignee": "alice",
                "updated": "2026-03-04T12:00:00Z"
            },
            {
                "id": "BEAD-102"
                # Missing most fields to test fallbacks
            }
        ]
        
        issues = self.specialist.get_issues()
        self.assertEqual(len(issues), 2)
        
        # Check fully populated issue
        self.assertEqual(issues[0].id, "BEAD-101")
        self.assertEqual(issues[0].key, "BEAD-101")
        self.assertEqual(issues[0].summary, "Test finding")
        self.assertEqual(issues[0].status, "STRATA IN PROGRESS")
        self.assertEqual(issues[0].assignee, "alice")
        self.assertEqual(issues[0].updated, "2026-03-04T12:00:00Z")
        self.assertEqual(issues[0].issuetype, "Bead")
        
        # Check defaults for missing fields
        self.assertEqual(issues[1].id, "BEAD-102")
        self.assertEqual(issues[1].key, "BEAD-102")
        self.assertEqual(issues[1].summary, "No summary provided")
        self.assertEqual(issues[1].status, "STRATA TO DO")
        self.assertIsNone(issues[1].assignee)
        self.assertIsNotNone(issues[1].updated) # Should default to current time
        self.assertEqual(issues[1].issuetype, "Bead")


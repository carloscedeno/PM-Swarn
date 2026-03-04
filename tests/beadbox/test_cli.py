import unittest
from unittest.mock import patch, MagicMock
from src.beadbox.cli import BeadboxCLI

class TestBeadboxCLI(unittest.TestCase):
    @patch('src.beadbox.cli.subprocess.run')
    def test_is_available_true(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        self.assertTrue(BeadboxCLI.is_available())

    @patch('src.beadbox.cli.subprocess.run')
    def test_is_available_false(self, mock_run):
        mock_run.return_value = MagicMock(returncode=1)
        self.assertFalse(BeadboxCLI.is_available())

    @patch('src.beadbox.cli.subprocess.run')
    def test_is_available_exception(self, mock_run):
        mock_run.side_effect = Exception("Not found")
        self.assertFalse(BeadboxCLI.is_available())

    @patch('src.beadbox.cli.subprocess.run')
    def test_list_beads_success(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout='[{"id": "BEAD-001"}]')
        success, beads = BeadboxCLI.list_beads()
        self.assertTrue(success)
        self.assertEqual(len(beads), 1)
        self.assertEqual(beads[0]["id"], "BEAD-001")

    @patch('src.beadbox.cli.subprocess.run')
    def test_list_beads_not_a_list(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout='{"id": "BEAD-001"}')
        success, beads = BeadboxCLI.list_beads()
        self.assertFalse(success)
        self.assertEqual(beads, [])

    @patch('src.beadbox.cli.subprocess.run')
    def test_list_beads_invalid_json(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout='invalid json')
        success, beads = BeadboxCLI.list_beads()
        self.assertFalse(success)
        self.assertEqual(beads, [])

    @patch('src.beadbox.cli.subprocess.run')
    def test_list_beads_command_failed(self, mock_run):
        mock_run.return_value = MagicMock(returncode=1, stderr='error')
        success, beads = BeadboxCLI.list_beads()
        self.assertFalse(success)
        self.assertEqual(beads, [])

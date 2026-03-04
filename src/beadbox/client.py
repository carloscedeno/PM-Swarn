import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from .cli import BeadboxCLI
from src.model.issue import Issue

logger = logging.getLogger(__name__)

class BeadboxClient:
    """Client for interacting with Beadbox workspaces via 'bd' CLI or direct filesystem access."""

    def __init__(self, workspace_path: Optional[str] = None):
        """
        Initialize the Beadbox client.
        
        Args:
            workspace_path: Path to the workspace directory containing .beads/. 
                           Defaults to BEADBOX_WORKSPACE_PATH env var or current directory.
        """
        self.workspace_path = workspace_path or os.environ.get("BEADBOX_WORKSPACE_PATH", os.getcwd())
        self.beads_dir = os.path.join(self.workspace_path, ".beads")
        self._has_cli = BeadboxCLI.is_available()

    def list_beads(self) -> List[Dict[str, Any]]:
        """
        List all beads in the workspace.
        Falls back to direct filesystem reading if CLI is unavailable.
        """
        if self._has_cli:
            success, beads = BeadboxCLI.list_beads()
            if success:
                return beads
            else:
                logger.warning("CLI list failed, falling back to FS reading.")
                return self._list_beads_fs()
        else:
            return self._list_beads_fs()

    def _list_beads_fs(self) -> List[Dict[str, Any]]:
        """
        Fallback: List beads by reading from .beads/registry.json if available,
        or scanning individual .bead files in .beads/.
        """
        beads = []
        if not os.path.exists(self.beads_dir):
            logger.warning(f"Beads directory not found: {self.beads_dir}")
            return []

        registry_path = os.path.join(self.beads_dir, "registry.json")
        if os.path.exists(registry_path):
            try:
                with open(registry_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Assuming registry.json contains a list of beads or a dict with beads
                    if isinstance(data, list):
                        return data
                    elif isinstance(data, dict) and 'beads' in data:
                        return data['beads']
            except Exception as e:
                logger.error(f"Failed to read registry.json: {e}. Falling back to individual files.")

        # Fallback to reading individual files if registry.json is missing or corrupt
        for filename in os.listdir(self.beads_dir):
            if filename.endswith(".bead"):
                path = os.path.join(self.beads_dir, filename)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if "id" in data:
                            beads.append(data)
                except Exception:
                    continue
        return beads

    def get_bead_details(self, bead_id: str) -> Optional[Dict[str, Any]]:
        """Get details for a specific bead."""
        # Implementation depends on file naming convention
        path = os.path.join(self.beads_dir, f"{bead_id}.bead")
        if not os.path.exists(path):
            path = os.path.join(self.beads_dir, f"{bead_id}.json")
            
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return None
        return None

class BeadboxSpecialist:
    """Specialist for interacting with Beadbox to retrieve normalized issues."""
    
    def __init__(self, client: BeadboxClient):
        self.client = client
        
    def get_issues(self) -> List[Issue]:
        """
        List all beads and normalize them into the Orchestrator's Issue model.
        """
        raw_beads = self.client.list_beads()
        issues = []
        for bead in raw_beads:
            bead_id = bead.get("id", "UNKNOWN")
            
            # Default to current time if updated is not found
            updated_str = bead.get("updated") or bead.get("updated_at") or datetime.now(timezone.utc).isoformat()
            
            issue = Issue(
                id=bead_id,
                key=bead_id,
                summary=bead.get("summary", "No summary provided"),
                status=bead.get("status", "STRATA TO DO"),
                assignee=bead.get("assignee"),
                updated=updated_str,
                issuetype="Bead"
            )
            issues.append(issue)
        return issues


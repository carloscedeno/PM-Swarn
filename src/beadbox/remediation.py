import os
import json
import logging
import hashlib
from typing import List, Dict, Any, Optional
from src.model.issue import Issue
from src.beadbox.client import BeadboxClient

logger = logging.getLogger(__name__)

# Standard header for automation comments to ensure idempotency
AUTOMATION_HEADER = "<!-- PM-SWARN-AUDIT-FINGERPRINT: {fingerprint} -->"

def calculate_fingerprint(bead_id: str, gaps: List[str]) -> str:
    """Calculate a stable fingerprint for a set of gaps on a bead."""
    # Sort gaps for stability
    gaps_str = ",".join(sorted(gaps))
    seed = f"{bead_id}:{gaps_str}:v1"
    return hashlib.md5(seed.encode()).hexdigest()[:12]

async def remediate_bead(client: BeadboxClient, issue: Issue, report_url: str):
    """
    Apply remediation to a Beadbox bead by adding an idempotent comment.
    """
    if not issue.gaps:
        return

    # 1. Compute fingerprint
    fingerprint = calculate_fingerprint(issue.id, issue.gaps)
    fingerprint_header = AUTOMATION_HEADER.format(fingerprint=fingerprint)

    # 2. Check if already remediated
    details = client.get_bead_details(issue.id)
    if not details:
        logger.error(f"Could not retrieve details for bead {issue.id} for remediation.")
        return

    comments = details.get("comments", [])
    for comment in comments:
        if fingerprint_header in comment.get("text", ""):
            logger.info(f"Bead {issue.id} already has a comment for these gaps (fingerprint: {fingerprint}).")
            return

    # 3. Construct comment body
    gaps_list = "\n".join([f"- **{gap}**" for gap in issue.gaps])
    body = f"""{fingerprint_header}
### 🤖 Automation: Documentation/Evidence Gap Detected

The following gaps were identified during the PM Swarn Weekly Audit:

{gaps_list}

**Remediation Steps:**
1. Ensure a valid PRD exists in Notion matching this ticket.
2. For Stories, attach/link `stories.json` evidence.
3. [View Full Audit Report]({report_url})

*This comment was generated automatically.*
"""

    # 4. Apply comment
    # In Beadbox FS mode, we append to the 'comments' array in the .bead file
    await add_bead_comment_fs(client, issue.id, body)

async def add_bead_comment_fs(client: BeadboxClient, bead_id: str, text: str):
    """Add a comment to a bead using direct filesystem access."""
    path = os.path.join(client.beads_dir, f"{bead_id}.bead")
    if not os.path.exists(path):
        return

    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if "comments" not in data:
            data["comments"] = []
            
        import datetime
        new_comment = {
            "id": f"comment-{int(datetime.datetime.now().timestamp())}",
            "text": text,
            "created_at": datetime.datetime.now().isoformat()
        }
        data["comments"].append(new_comment)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
            
        logger.info(f"Added remediation comment to bead {bead_id}")
    except Exception as e:
        logger.error(f"Failed to add comment to bead {bead_id}: {str(e)}")

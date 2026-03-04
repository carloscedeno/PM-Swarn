import asyncio
import os
import uuid
from typing import List, Dict, Any

from src.beadbox.client import BeadboxClient
from src.beadbox.evidence import verify_bead_evidence
# Remediation for Beadbox will be implemented or refactored
# from src.jira.remediation import remediate_issue
from src.notion.client import NotionClient
from src.notion.search_docs import resolve_notion_doc
from src.notion.report_writer import generate_run_report
from src.logic.state_grouping import normalize_issue
from src.model.issue import Issue

async def process_bead(raw_bead: Dict[str, Any], notion_client: NotionClient) -> Issue:
    """Process a single Beadbox bead: detect type, check evidence, find doc, and compute compliance."""
    # 1. Normalize to Issue model (handles work_type and state_group)
    issue = normalize_issue(raw_bead)
    
    # 2. Verify Evidence (stories.json) - specific for Beadbox
    verify_bead_evidence(issue, raw_bead)
    
    # 3. Resolve and Validate Notion Doc
    issue.notion_doc_url = await resolve_notion_doc(issue.key, notion_client)
    
    # Doc validation logic (simplified for MVP)
    if issue.notion_doc_url:
        issue.doc_status = "valid"
    else:
        issue.doc_status = "missing"
        if "missing_doc" not in issue.gaps:
            issue.gaps.append("missing_doc")
            if issue.status == "STRATA DONE":
                issue.compliance_status = "non-compliant"
    
    return issue

async def main():
    """Main entry point for PM Swarn audit run (Beadbox version)."""
    run_id = str(uuid.uuid4())[:8]
    workspace_path = os.environ.get("BEADBOX_WORKSPACE_PATH", os.getcwd())
    
    print(f"🚀 Starting PM Swarn Audit Run (Beadbox): {run_id}")
    print(f"📂 Workspace: {workspace_path}")
    
    beadbox_client = BeadboxClient(workspace_path)
    notion_client = NotionClient()
    
    # Phase 1: Fetch Beads
    print("🔍 Listing beads from workspace...")
    raw_beads = beadbox_client.list_beads()
    
    if not raw_beads:
        print("⚠️ No beads found in workspace.")
        # We still generate an empty report to be idempotent/verifiable
        
    print(f"📦 Found {len(raw_beads)} beads. Processing in parallel...")
    
    # Phase 2: Process beads in parallel
    tasks = [process_bead(raw_bead, notion_client) for raw_bead in raw_beads]
    processed_issues = await asyncio.gather(*tasks)
    
    # Phase 3: Generate Notion Report
    print("📊 Generating Notion Audit Report...")
    # JQL placeholder for Beadbox (mode: Weekly Check)
    mode_desc = "Beadbox Weekly Check (all beads)"
    report_result = await generate_run_report(run_id, mode_desc, processed_issues, notion_client)
    report_url = report_result.get("url", "https://notion.so")
    
    # Phase 4: Remediation (Parallel Beadbox Comments)
    print("🛠️ Applying Remediation Actions...")
    from src.beadbox.remediation import remediate_bead
    remediation_tasks = [remediate_bead(beadbox_client, issue, report_url) for issue in processed_issues]
    await asyncio.gather(*remediation_tasks)
    
    print(f"✅ Audit Complete! Report: {report_url}")

if __name__ == "__main__":
    asyncio.run(main())

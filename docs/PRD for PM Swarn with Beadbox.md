# PRD for PM Swarn

## Asynchronous Multi-Agent System for Software Delivery Lifecycle (SDLC)

**Version:** 4.1 (Fully specified — English)

**Target framework:** Antigravity (AI Orchestration)

**Sources of truth:** Beadbox (execution + `stories.json` artifact) as a substitute for Jira ([https://beadbox.app/en/docs/getting-started](https://beadbox.app/en/docs/getting-started)), Notion (documentation in the “Product Documentation” database), (Optional) GitHub (future phase)

**Guiding principle:** run **asynchronous** (parallel) validations and actions to maximize speed, keep prompts small, and produce **verifiable** outputs.

---

### 1) Executive Summary

This product builds an AI “Swarm” (Orchestrator + Specialist agents) that automates SDLC quality control and traceability across Beadbox (as Jira substitute) and Notion.

The system runs, on-demand (and optionally scheduled), a **Weekly Check** execution that:

- pulls items from Beadbox via saved filters / CLI-driven status queries (JQL substitute),
- validates evidence (Notion documentation + `stories.json` evidence attached/linked in Beadbox when applicable),
- detects discrepancies and risks (missing doc, invalid doc, blocked, etc.),
- creates idempotent remediation actions in Beadbox (comment or sub-task),
- and publishes an audit report in Notion.

---

### 2) Context & Problem

**Current pain**

- Beadbox (as Jira substitute) reflects execution status, but does not guarantee specification quality or closure evidence.
- Notion contains knowledge (PRDs, specs, guides), but is not always consistently linked to Beadbox items.
- Outcome: manual reporting, “done” tickets without verifiable evidence, context loss, and rework.

**Root cause**

- Lack of an automated mechanism that:
    - enforces traceability (ticket ↔ doc ↔ artifacts),
    - verifies minimum quality before work is considered “delivered”,
    - and turns gaps into concrete actions.

---

### 3) Goals, Non-Goals, and Success Metrics

### 3.0 Governance + standards (from Executive Acta 2026-02-25)

The Swarm must align with the org framework improvements agreed on 2026-02-25:

- WBS hierarchy (traceability): Initiative → EPIC → Stories (with PRD) → Tasks (executable).
- Blueprint gate (Phase 1): before technical decomposition, every Initiative must include at minimum:
    - Flowchart
    - Sequence Diagram
    - (Added) Post Functional Specification
- Grooming is a mandatory gate before development:
    - Validate story atomicity, dependencies, technical clarity, scope adjustment, readiness for Phase 2.
    - No story goes to development without: PRD complete + technical validation + clear acceptance criteria.
- PRD is the internal contract (Product + Architecture) and must include (minimum):
    - General User Story Scope, User Journey, UI Reference
    - Technical & Development Foundation
    - Data Modeling & Usage
    - Integrability (API requirements)
    - Observability (success metrics, project metrics, development metrics)
    - Implementation Plan, Test Plan, Business Rules, Guardrails
- Audit/quality gate before delivery:
    - 100% acceptance criteria met
    - ≥ 90% code coverage
    - Tests executed and documented
    - If gaps: audit produces structured report + new Stories; if functional void: new PRD.
- Change management is controlled:
    - Gates are immutable without formal consensus
    - Changes must be proposed, approved, documented, and socialized
    - Keepers for versioning/change control: Jonathan + Daniel

#### 3.1 Goals

1. Automate **Weekly Check** (status + evidence + actions).
2. Increase documentation/evidence compliance before work is closed.
3. Reduce ambiguity-driven interruptions for Dev/BA.
4. Keep costs low (free-first) and execution fast.

#### 3.2 Non-Goals (for now)

- Do not replace Beadbox as the execution system (it is the Jira substitute for this Swarm).
- Do not redesign Beadbox workflows/states.
- Do not mass-transition Beadbox items in the MVP (only create/suggest remediation actions).
- Do not depend on GitHub for the MVP (reserved for a later phase).

#### 3.3 MVP Success Metrics

- Report generation time: from 3–4h/week down to < 5 minutes of supervision.
- Latency: < 60 seconds for up to 50 issues per run.
- Compliance: 100% of issues in the final state (STRATA DONE) meet minimum evidence requirements.
- Autonomy: ≥ 70% of discrepancies turned into remediation actions with no manual intervention.
- Idempotency: 0 duplicate remediation actions per run.

---

### 4) Personas / Users

- **BA/PM (Primary):** needs reliable reports, quality auditing, and a backlog of corrections.
- **Engineering Lead:** needs visibility into true WIP, blockers, and evidence debt.
- **Dev/QA:** needs executable stories and evidence-based closure.

---

### 5) Product Principles (Quality Bar)

- **Everything must be verifiable:** binary acceptance criteria (Pass/Fail), explicit rules.
- **Atomicity:** stories are small (one working session).
- **Idempotency:** each gap yields at most 1 remediation action (with a stable fingerprint).
- **Minimize payload/tokens:** request/read only required fields.
- **Graceful degradation:** if Notion or Jira fail, produce partial output with explicit errors.
- **Auditability:** every run has a `run_id`, timestamps, and linked evidence.

---

### 6) Workflows (State Scope) — Beadbox as Jira substitute

### 6.0 How to install, connect, and use Beadbox in this Swarm

Goal: treat Beadbox as the execution system (Jira substitute) while Notion remains documentation + reporting.

Installation (from Beadbox docs: [https://beadbox.app/en/docs/getting-started](https://beadbox.app/en/docs/getting-started))

- Install beads CLI (engine): install `bd` (macOS: `brew install beads`) and verify with `bd --version`.
- Install Beadbox desktop app: macOS: `brew tap beadbox/cask && brew install --cask beadbox` (or download from GitHub Releases).

Workspace setup (what the Swarm relies on)

- Choose a project folder (ideally the repo root) and initialize the Beadbox workspace from the Beadbox Quick Start (“Set Up Workspace”).
- Beadbox stores workspace metadata locally (it detects workspaces via `~/.beads/registry.json` and by finding a `.beads/` folder inside project directories).

Operational usage (how the Swarm interacts)

- Source of truth is the local Git-backed beads store. The Swarm reads tickets (“beads”) and their metadata from the workspace and produces results.
- Changes can be made either:
    - in the Beadbox UI (recommended for PM/BA), or
    - via CLI (recommended for automations). Beadbox updates in real time when CLI changes happen.

What the Swarm must be able to do (Beadbox Specialist responsibilities)

- Locate the target workspace directory (repo path) and ensure `.beads/` exists.
- List beads by status / filters (JQL substitute).
- Read bead fields: id/key (or stable identifier), title/summary, status, assignee, updated, parent/epic, attachments/links, comments.
- Detect `stories.json` evidence as an attachment/link or as a referenced file path in bead description (define one standard and enforce it).
- Write remediation actions idempotently as either:
    - a comment with a stable fingerprint header, and/or
    - a sub-task/child bead under the original.

Standard to replace JQL

- Instead of “JQL”, define a saved filter contract for the Weekly Check (e.g., statuses in scope + labels/priority + epic scope).
- For manual mode, accept an explicit list of bead IDs/keys.

Evidence standard in Beadbox (recommended)

- For STORIES work items, store evidence using one of:
    - attachment/link whose name contains `stories.json`, or
    - a conventional markdown section in the bead description: “Evidence: stories.json: <path or link>”
- Keep it deterministic: the Swarm must parse it without guessing.

Notes / constraints

- Because Beadbox is local-first, the Swarm execution environment must have filesystem access to the workspace (same machine or a mounted volume). If the Swarm runs in the cloud, you’ll need a sync/export step (out of MVP scope).

This PRD covers two work types. Implementation should use Beadbox as a Jira substitute (see: [https://beadbox.app/en/docs/getting-started](https://beadbox.app/en/docs/getting-started)).

#### 6.1 Work Type: Strata PRD (specification flow)

Observed states/stages:

- `PRD CREATED`
- `STRATA GROOMING`
- `STRATA TO PRODUCT REVIEW` and/or `to review`
- `STRATA TECHNICAL PRD`
- `STRATA STORIES.JSON CREATION`
- `TO DEVELOPMENT`
- Cross-cutting: `On Hold`, `On hold to assign`, `Waiting for development`

Operational interpretation:

- A PRD is considered **ready-for-execution** when:
    - it reaches `STRATA STORIES.JSON CREATION` and a `stories.json` exists, or
    - it transitions to `TO DEVELOPMENT` and is linked to the Stories execution flow.
- There is a technical refinement loop: `TO DEVELOPMENT` → `STRATA TECHNICAL PRD` (“Add Tech Details”).

#### 6.2 Work Type: Strata Stories.json (execution flow)

Confirmed states:

- Queue: `STRATA TO DO`
- WIP: `STRATA IN PROGRESS`, `STRATA IN TESTING`, `STRATA TO DEPLOYMENT`, `STRATA IN INTEGRATION`
- Blocked: `STRATA BLOCKED`
- Closed/Delivered (only): `STRATA DONE`

Confirmed transitions:

- Move to testing: `Strata to Testing` → `STRATA IN TESTING`

Artifact:

- `stories.json` lives in **Beadbox** (as an attachment/link, or referenced deterministically in the bead description).

---

### 7) MVP Scope (what it does exactly)

#### 7.1 Supported inputs

- **Configurable Beadbox filter/query** (JQL substitute: e.g., statuses / labels / priority / epic scope).
- **Explicit issue key list** (manual mode).

#### 7.2 Outputs

- **Audit report** in Notion (one page per run or per period).
- **Remediation actions** in Beadbox (comment or sub-task depending on standard).
- **Executive summary** (KPIs and top risks).

#### 7.3 Core computed fields (MVP)

For each evaluated issue, the system computes:

- `workflow_type`: PRD or Stories
- `state_group`: queue / wip / blocked / done
- `evidence_status`:
    - `stories_json_present` (only for Stories work type)
    - `notion_doc_found`
    - `notion_doc_quality` (valid/invalid)
- `compliance_status`: compliant / non-compliant

---

### 8) Functional Requirements (FR) — detailed and testable

#### FR1 — Pull issues from Beadbox (Jira substitute)

**Description:** execute the Beadbox equivalent of a query/filter (JQL substitute) and extract minimum required fields.

Minimum required fields:

- Identity: `key`, `id` (if available)
- Metadata: `summary`, `issuetype`, `status`, `assignee`, `updated`, `parent`
- Attachments/links: evidence of `stories.json` (filename or link)

Acceptance criteria:

- Given a valid Beadbox query/filter, the system returns a list of items (may be empty) without errors.
- If the query/filter returns 0 results, the system produces a report with KPIs=0 and no error.
- If Beadbox returns an error/timeout, the system returns `partial_failure` with details.

#### FR2 — Detect work type (PRD vs Stories)

**Description:** determine which workflow an issue belongs to in order to apply the correct evidence rules.

Acceptance criteria:

- For an issue in the Stories workflow states, `work_type=STORIES`.
- For an issue in the PRD workflow states, `work_type=PRD`.
- If it cannot be inferred, `work_type=unknown` and the report lists it as a finding.

#### FR3 — Verify `stories.json` evidence (in Beadbox)

**Description:** for Stories work type issues, verify that an attachment/link representing `stories.json` exists.

Rules:

- In `STRATA DONE`: `stories.json` is **mandatory**.
- In WIP: missing evidence is a configurable warning (MVP reports it).

Acceptance criteria:

- If `jira_status=STRATA DONE` and evidence is missing, `missing_stories_json=true`.
- If evidence exists, `stories_json_present=true`.

#### FR4 — Resolve documentation in Notion (Product Documentation DB)

**Description:** find the associated document in the Notion “Product Documentation” database.

Matching strategy (in order):

1. Match `issue key` in `Doc name` title.
2. Match `issue key` in page content.
3. (Recommended future) dedicated “Jira Key” property.

Acceptance criteria:

- If a doc is found, `notion_doc_url` is a non-empty URL.
- If not found, `missing_doc=true`.

#### FR5 — Validate minimum doc quality (Notion)

**Description:** validate that a found doc contains the required minimum sections.

Minimum checklist:

- Context / Problem
- Solution / Decision
- Acceptance criteria or Definition of Done
- Explicit reference to the `issue key`

Acceptance criteria:

- If `notion_doc_url=null`, then `doc_status=missing`.
- If doc contains all required sections, `doc_status=valid`.
- If any section is missing, `doc_status=invalid` and the system lists which sections are missing.

#### FR6 — Compliance rules for STRATA DONE

**Description:** an issue counts as compliant delivery only if it meets all required evidence.

Compliance definition:

- Beadbox state is `STRATA DONE` (or the equivalent closed/done state in Beadbox).
- `stories.json` evidence exists in Beadbox.
- Notion doc is found and `doc_status=valid`.

Acceptance criteria:

- If any requirement fails, `compliance_status=non-compliant`.
- If all pass, `compliance_status=compliant`.

#### FR7 — Create idempotent remediation actions in Beadbox

**Description:** create a remediation action when gaps exist.

Gap types (MVP):

- `missing_doc`
- `invalid_doc`
- `missing_stories_json`

Remediation action standard:

- Consistent header/title (e.g., “Automation: Documentation/Evidence Gap”).
- Body includes:
    - issue key
    - detected gap(s)
    - failed rule(s)
    - link to the Notion report
    - remediation steps

Idempotency rule:

- Do not duplicate remediation if an equivalent action already exists for the same issue and gap type.

Acceptance criteria:

- For an issue with a gap, create at most 1 remediation action per gap type.
- Re-running the same check does not create duplicates.

#### FR8 — Write the Notion report

**Description:** publish a run report with traceability.

Minimum sections:

- Run metadata: date, `run_id`, JQL used.
- KPIs:
    - total_issues
    - done_count, wip_count, blocked_count, queue_count
    - missing_doc_count, invalid_doc_count, missing_stories_json_count
    - compliant_done_count vs non_compliant_done_count
- Top findings:
    - top blockers
    - top non-compliant done
- Issue-level details:
    - key/id, status, links (Beadbox, Notion doc if exists), gaps, remediation action reference

Acceptance criteria:

- The report is created even if gaps exist.
- For partial failures, the report includes a non-empty “Errors” section.

---

### 9) Non-Functional Requirements (NFR) — expanded

- **Performance:** < 60s for 50 issues (MVP) using Jira+Notion parallelism.
- **Cost:** small prompts, limited fields, cache TTL 5 minutes.
- **Resilience:** retries with backoff; graceful degradation.
- **Security/Privacy:** mask PII; do not store tokens in plaintext.
- **Observability:** per-step logs (latency, counts, errors, run_id).
- **Traceability:** every run links evidence and actions.

---

### 10) Data Model (Orchestrator standard output)

For each issue, the orchestrator outputs (conceptually):

- `issue_key`
- `work_type` (PRD|STORIES)
- `jira_status`
- `state_group` (queue|wip|blocked|done)
- `stories_json_present` (true|false|null)
- `notion_doc_url` (url|null)
- `doc_status` (valid|invalid|missing)
- `gaps` (list)
- `action_created` (true|false)
- `action_reference` (link/ID if applicable)

---

### 11) Swarm Architecture (Antigravity) — Beadbox + Notion

### 11.0 Inter-agent communication contract (how agents talk to each other)

This section defines the message protocol so the Orchestrator and Specialists can work asynchronously while staying deterministic and idempotent.

Principles

- Single source of truth for identifiers: each Beadbox item must have a stable `bead_id` (or equivalent) used across all agents.
- Small payloads: Specialists return only the fields the Orchestrator needs.
- Deterministic responses: never return “best effort” free text when a field can be structured.

Shared envelope (all agent-to-agent messages)

- `run_id`: string (unique per execution)
- `request_id`: string (unique per call; used for tracing)
- `agent`: string (e.g., "orchestrator", "beadbox_specialist", "notion_specialist")
- `type`: string (one of the message types below)
- `created_at`: ISO timestamp
- `payload`: object (message-specific)

Message types

1) `WORKLIST_REQUEST` (Orchestrator → Beadbox Specialist)

Payload:

- `workspace_path`: string
- `query`: { `saved_filter_name?`: string, `statuses?`: string[], `text_search?`: string, `limit?`: number }
- `mode`: "weekly_check" | "manual"

2) `WORKLIST_RESULT` (Beadbox Specialist → Orchestrator)

Payload:

- `items`: array of { `bead_id`: string, `title`: string, `status`: string, `assignee?`: string, `updated_at?`: ISO string, `parent_id?`: string }
- `errors`: array of { `code`: string, `message`: string } (may be empty)

3) `ITEM_DETAILS_REQUEST` (Orchestrator → Beadbox Specialist)

Payload:

- `workspace_path`: string
- `bead_id`: string
- `fields`: string[] (allowlist to minimize payload; e.g., ["description","attachments","comments","dependencies"])

4) `ITEM_DETAILS_RESULT` (Beadbox Specialist → Orchestrator)

Payload:

- `bead_id`: string
- `details`: {
    
    `description?`: string,
    
    `attachments?`: array of { `name`: string, `url_or_path`: string },
    
    `links?`: array of string,
    
    `comments?`: array of { `id`: string, `text`: string, `created_at`: ISO string }
    
    }
    
- `errors`: array of { `code`: string, `message`: string }

5) `DOC_RESOLVE_REQUEST` (Orchestrator → Notion Specialist)

Payload:

- `issue_key_or_bead_id`: string
- `match_strategy`: ["title", "content"]

6) `DOC_RESOLVE_RESULT` (Notion Specialist → Orchestrator)

Payload:

- `issue_key_or_bead_id`: string
- `notion_doc_url`: url | null
- `confidence`: "high" | "medium" | "low"
- `errors`: array of { `code`: string, `message`: string }

7) `DOC_VALIDATE_REQUEST` (Orchestrator → Notion Specialist)

Payload:

- `notion_doc_url`: url
- `required_sections`: string[] (e.g., ["Context / Problem","Solution / Decision","Acceptance criteria or Definition of Done","Issue key reference"])
- `issue_key_or_bead_id`: string

8) `DOC_VALIDATE_RESULT` (Notion Specialist → Orchestrator)

Payload:

- `notion_doc_url`: url
- `doc_status`: "valid" | "invalid" | "missing"
- `missing_sections`: string[]
- `errors`: array of { `code`: string, `message`: string }

9) `REMEDIATION_UPSERT_REQUEST` (Orchestrator → Beadbox Specialist)

Payload:

- `workspace_path`: string
- `bead_id`: string
- `gap_type`: "missing_doc" | "invalid_doc" | "missing_stories_json"
- `fingerprint`: string (stable; used for idempotency)
- `action_type`: "comment" | "subtask" | "both"
- `body_markdown`: string

10) `REMEDIATION_UPSERT_RESULT` (Beadbox Specialist → Orchestrator)

Payload:

- `bead_id`: string
- `gap_type`: string
- `created`: boolean
- `reference`: string (comment id / subtask id)
- `errors`: array of { `code": string,` message`: string }

Idempotency handshake (required)

- Orchestrator computes `fingerprint = hash(bead_id + gap_type + rule_version)`.
- Beadbox Specialist must search existing comments/subtasks for the fingerprint header before creating anything.

Error contract

- Specialists should never throw unstructured errors; always populate `errors[]`.
- Orchestrator must continue execution per-item even when some items error (partial failure).

This contract is intentionally tool-agnostic: it works whether the Specialist uses Beadbox UI automation or the `bd` CLI under the hood.

#### 11.1 Orchestrator (Manager)

Responsible for:

- planning an execution DAG,
- running specialists in parallel,
- consolidating results,
- deciding remediation actions,
- producing the final report.

#### 11.2 Beadbox Specialist (Taskmaster) — Jira substitute

Capabilities:

- run Beadbox searches/filters (JQL substitute),
- load item details (issues/tickets),
- verify attachments/links (e.g., `stories.json` evidence),
- create a comment/sub-task (MVP: at least a comment) in Beadbox.

#### 11.3 Notion Specialist (Archivist)

Capabilities:

- query the Product Documentation database,
- open candidate pages,
- validate the minimum doc checklist.

---

### 12) End-to-End Use Cases

#### UC1 — Weekly Check (primary)

Input: Beadbox saved filter/query (JQL substitute).

Flow:

1. Beadbox: list items + minimum details (parallel).
2. Notion: resolve docs by issue key (parallel).
3. Validate evidence and compliance.
4. Create idempotent remediation actions.
5. Publish Notion report.

Output:

- Report + created actions.

#### UC2 — On-demand audit (issue list)

Input: list of issue keys.

Output: gap report + actions.

---

### 13) Definition of Done (MVP)

The MVP is done when:

- UC1 works end-to-end.
- Notion report is generated with KPIs and issue-level details.
- Beadbox remediation actions are created without duplicates.
- `STRATA DONE` is correctly audited (doc + `stories.json`).
- Partial failures are handled without stopping the whole run.

---

### 14) Initial backlog (to convert into `stories.json`)

**Epic:** Weekly SDLC Check (Jira + Notion)

- STORY-001: Execute JQL and extract minimum required fields.
- STORY-002: Detect work type and group state (queue/wip/blocked/done).
- STORY-003: Verify `stories.json` evidence in Jira.
- STORY-004: Resolve Notion docs (Product Documentation DB) by issue key.
- STORY-005: Validate minimum doc checklist (valid/invalid/missing).
- STORY-006: Compute compliance (especially for STRATA DONE).
- STORY-007: Create idempotent Jira remediation actions.
- STORY-008: Generate Notion report (metadata + KPIs + details + errors).
- STORY-009: Error handling, retries, and partial reporting.

---

## stories.json (Ralph Protocol)

```json
{
  "epic": "Weekly SDLC Check (Beadbox + Notion)",
  "status": "active",
  "stories": [
    {
      "id": "STORY-001",
      "description": "Execute configurable JQL and return a list of issues with the minimum fields required for auditing.",
      "files_to_touch": [
        "src/jira/client.ts",
        "src/jira/jql.ts"
      ],
      "acceptance_criteria": [
        "Given a valid JQL, the system returns a list of issues (may be empty) without errors.",
        "Each issue includes key, summary, status, assignee, updated, issuetype, and parent (if present).",
        "If Jira returns an error/timeout, the output includes non-empty error_code and error_message."
      ],
      "passes": false
    },
    {
      "id": "STORY-002",
      "description": "Normalize Jira issues into an internal model and classify state_group (queue/wip/blocked/done) based on Jira status.",
      "files_to_touch": [
        "src/model/issue.ts",
        "src/logic/stateGrouping.ts"
      ],
      "acceptance_criteria": [
        "If status is STRATA TO DO then state_group=queue.",
        "If status is STRATA BLOCKED then state_group=blocked.",
        "If status is STRATA DONE then state_group=done.",
        "If status is one of STRATA IN PROGRESS, STRATA IN TESTING, STRATA TO DEPLOYMENT, STRATA IN INTEGRATION then state_group=wip.",
        "For an unknown status, state_group=unknown and a warning is recorded in the output."
      ],
      "passes": false
    },
    {
      "id": "STORY-003",
      "description": "Detect the issue work_type (PRD vs STORIES) so the correct evidence rules are applied.",
      "files_to_touch": [
        "src/logic/workTypeDetection.ts"
      ],
      "acceptance_criteria": [
        "For an issue in the Stories workflow states, work_type=STORIES.",
        "For an issue in the PRD workflow states, work_type=PRD.",
        "If it cannot be inferred, work_type=unknown and the report lists it as a finding."
      ],
      "passes": false
    },
    {
      "id": "STORY-004",
      "description": "Verify `stories.json` evidence in Jira for issues with work_type=STORIES.",
      "files_to_touch": [
        "src/jira/evidence.ts"
      ],
      "acceptance_criteria": [
        "If work_type=STORIES and the issue has an attachment or link whose name contains 'stories.json', then stories_json_present=true.",
        "If work_type=STORIES and no evidence is detected, then stories_json_present=false.",
        "If jira_status=STRATA DONE and stories_json_present=false, the issue includes gap=missing_stories_json."
      ],
      "passes": false
    },
    {
      "id": "STORY-005",
      "description": "Search Notion documentation (Product Documentation DB) for each issue key using title and content matching.",
      "files_to_touch": [
        "src/notion/searchDocs.ts"
      ],
      "acceptance_criteria": [
        "Given an issue key, the system attempts to find 0 or 1 associated document.",
        "If a document is found, notion_doc_url is a non-empty URL.",
        "If no document is found, notion_doc_url=null and doc_status=missing."
      ],
      "passes": false
    },
    {
      "id": "STORY-006",
      "description": "Validate minimum quality of the matched Notion document (required sections + explicit issue key reference).",
      "files_to_touch": [
        "src/notion/docValidator.ts"
      ],
      "acceptance_criteria": [
        "If notion_doc_url=null then doc_status=missing.",
        "If notion_doc_url!=null and content includes all 4 required sections, doc_status=valid.",
        "If notion_doc_url!=null and at least 1 required section is missing, doc_status=invalid and the system lists missing sections."
      ],
      "passes": false
    },
    {
      "id": "STORY-007",
      "description": "Compute compliance for STRATA DONE (valid Notion doc + `stories.json` present) and generate a gaps list per issue.",
      "files_to_touch": [
        "src/logic/compliance.ts"
      ],
      "acceptance_criteria": [
        "If jira_status=STRATA DONE and doc_status=valid and stories_json_present=true then compliance_status=compliant.",
        "If jira_status=STRATA DONE and (doc_status!=valid or stories_json_present!=true) then compliance_status=non-compliant.",
        "Each non-compliant issue has a non-empty gaps list (missing_doc, invalid_doc, and/or missing_stories_json)."
      ],
      "passes": false
    },
    {
      "id": "STORY-008",
      "description": "Create an idempotent Jira remediation action (comment or sub-task) for each detected gap.",
      "files_to_touch": [
        "src/jira/remediation.ts"
      ],
      "acceptance_criteria": [
        "For an issue with a gap, the system creates exactly 1 remediation action per gap type if it does not already exist.",
        "The remediation contains: issue key, gap, failed rule, and a link to the Notion report.",
        "Re-running the check with the same gap does not create duplicates."
      ],
      "passes": false
    },
    {
      "id": "STORY-009",
      "description": "Generate a Notion report page with run_id, KPIs, findings, and per-issue links.",
      "files_to_touch": [
        "src/notion/reportWriter.ts"
      ],
      "acceptance_criteria": [
        "A report is created/updated with a non-empty run_id and a timestamp.",
        "The report includes KPIs: total, done, wip, blocked, queue, missing_doc, invalid_doc, missing_stories_json.",
        "Each listed issue includes a Jira link and (if present) a Notion doc link.",
        "If there are partial errors, the report contains a non-empty 'Errors' section."
      ],
      "passes": false
    }
  ]
}
```

Note: adjust `files_to_touch` to match the actual repo structure once it is defined.
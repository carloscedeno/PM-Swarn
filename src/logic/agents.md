# Logic Layer & Rules

Purpose: Core business rules for compliance, state grouping, and work type classification.

## Capabilities

- **Work Type Detection**: Classify as PRD or Container/Stories via `work_type_detection.py`.
- **State Grouping**: Normalize Jira status into Queue/WIP/Blocked/Done via `state_grouping.py`.
- **Compliance Engine**: Compute final pass/fail status based on evidence via `compliance.py`.

## Conventions

- STRATA DONE is the primary target for strict compliance auditing.
- Use binary criteria for acceptance (compliant vs non-compliant).

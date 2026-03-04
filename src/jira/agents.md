# Jira Specialist Agent

Purpose: Interface with Jira Cloud to manage issue data and remediation.

## Capabilities

- **Issue Discovery**: Execute JQL via `jql.py`.
- **Data Access**: Fetch issue details, comments, and attachments via `client.py`.
- **Evidence Verification**: Check for `stories.json` presence via `evidence.py`.
- **Remediation**: Post idempotent comments to Jira via `remediation.py`.

## Conventions

- Use Jira API v3 (ADF for body, but simplified text matching for MVP).
- Always ensure idempotency by checking existing comments before posting.

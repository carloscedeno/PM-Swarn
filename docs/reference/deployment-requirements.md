# Deployment Requirements

**Status:** Active | **Last Updated:** 2026-02-20

These are mandatory requirements that every repository must satisfy before it can be deployed. They apply to all service types (Microservice, Lambda, Agent, MCP).

---

## DR-1: Environment Variables (.env.example)

The repository **must** contain an up-to-date `.env.example` file listing every environment variable the service needs at runtime.

- Include a short comment describing each variable's purpose.
- Use placeholder values (never real secrets).
- Keep `.env.example` in sync whenever a new env var is added or removed.

**Verification:** `.env.example` exists at the repo root and lists all variables referenced in the codebase.

---

## DR-2: Limited Responsibilities (Single-Purpose)

Each repository **must** have a single, well-defined responsibility. The following combinations are **not allowed** in a single repo:

- MCP server **+** Agent in the same codebase.
- Multiple MCP servers in one repo.
- Multiple listening ports (only one port exposed).

A service should do **one thing well**. If it needs to be both an MCP and an Agent, split them into separate repositories.

**Verification:** Dockerfile exposes at most one port; `package.json`/`pyproject.toml` does not bundle multiple server entry points; no mixed MCP + Agent startup scripts.

---

## DR-3: Dockerfile (docker build only, no docker-compose)

The repository **must** include a `Dockerfile` that builds successfully with a plain `docker build` command.

- The image must be self-contained; it must **not** require `docker-compose` to run.
- Use multistage builds to minimize image size.
- Include a `HEALTHCHECK` instruction.
- Keep `.dockerignore` updated.

**Verification:** `docker build -t <service-name> .` completes with exit code 0. No `docker-compose.yml` or `docker-compose.yaml` is required to run the service.

---

## DR-4: Service Type in README

The `README.md` **must** clearly state the service type in one of these categories:

| Type | Description |
|------|-------------|
| **Microservice** | Long-running HTTP/gRPC service deployed as a container. |
| **Lambda** | Serverless function triggered by events (AWS Lambda, GCP Cloud Function, etc.). |
| **Agent** | AI agent (e.g. LangGraph, CrewAI) that processes tasks autonomously. |
| **MCP** | Model Context Protocol server providing tools/resources to AI assistants. |

Place the service type prominently at the top of the README, e.g.:

```markdown
# My Service Name

> **Service type:** Microservice
```

**Verification:** README.md contains a service type declaration matching one of the four categories above.

---

## DR-5: Connectivity & Access Documentation

The `README.md` **must** document:

1. **Upstream dependencies** — Which other services this repo connects to (e.g. "Connects to: Records Grid MS, Line Items MS, PostgreSQL").
2. **Access pattern** — Who or what accesses this service. Use one of these categories:

| Access Pattern | Description |
|----------------|-------------|
| **Internet (humans only)** | Exposed to end-users via the internet (e.g. frontend API). |
| **Humans + other services** | Accessed by both end-users and internal services. |
| **Internal only (Strata/OrderBahn services)** | Only accessed by other internal microservices; not internet-facing. |

Example in README:

```markdown
## Connectivity

**Connects to:** Records Grid MS, Line Items MS, Tenants MS, PostgreSQL
**Accessed by:** Internal only (Strata/OrderBahn services)
```

**Verification:** README.md contains a connectivity/access section listing upstream dependencies and access pattern.

---

## Enforcement

These requirements are enforced at two levels:

### In stories.json (story creation)

Every new `stories.json` **must** include a deployment-readiness story that verifies all five requirements. Example:

```json
{
  "id": "DEPLOY-01",
  "description": "Verify deployment requirements (DR-1 through DR-5)",
  "files_to_touch": [".env.example", "Dockerfile", "README.md"],
  "acceptance_criteria": [
    ".env.example exists and lists all env vars used in the codebase",
    "Service has a single responsibility (one port, no MCP+Agent mix)",
    "docker build completes successfully without docker-compose",
    "README.md states service type (Microservice | Lambda | Agent | MCP)",
    "README.md documents upstream dependencies and access pattern"
  ],
  "passes": false
}
```

### In audits

The `audit-repo-compliance` command includes a **Deployment requirements** phase that checks all five rules and contributes to the alignment score.

---

## Quick Checklist

- [ ] `.env.example` exists and is up to date (DR-1)
- [ ] Single responsibility: one port, no mixed service types (DR-2)
- [ ] `Dockerfile` builds with `docker build` alone (DR-3)
- [ ] README states service type: Microservice / Lambda / Agent / MCP (DR-4)
- [ ] README documents connectivity and access pattern (DR-5)

# PM Swarn: Weekly SDLC Check

**Service Type:** Agent

PM Swarn is an asynchronous multi-agent system designed to automate SDLC quality control and traceability across Jira and Notion. It identifies gaps in documentation and evidence (like `stories.json`) and generates idempotent remediation actions and audit reports.

## 📋 Table of Contents

- [Description](#description)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Documentation](#documentation)
- [Project Structure](#project-structure)

## Description

The system runs on-demand or scheduled **Weekly Checks** to:

- Pull issues from Jira via configurable JQL.
- Validate evidence (`stories.json` in Jira, Notion documentation quality).
- Detect discrepancies and risks (missing docs, invalid docs, blocked states).
- Create idempotent remediation actions in Jira (comments).
- Publish comprehensive audit reports in Notion.

## Tech Stack

- **Language:** Python 3.10+
- **Manager/Orchestrator:** Antigravity (AI Orchestration)
- **API Clients:** `httpx` for Jira and Notion API interactions
- **Validation:** `pydantic` for data modeling and normalization
- **Testing:** `pytest` with `respx` for API mocking
- **Dependency Management:** `uv` (recommended) or `pip`

## Architecture

The project follows a modular, specialist-agent architecture:

- **Jira Specialist (`src/jira`)**: Handles JQL execution, issue loading, and remediation actions.
- **Notion Specialist (`src/notion`)**: Handles document resolution, quality validation, and report writing.
- **Logic Layer (`src/logic`)**: Contains core compliance rules, state grouping, and work type detection.
- **Data Model (`src/model`)**: Defines the internal, normalized representation of Jira issues and compliance results.

## Getting Started

### Prerequisites

- Python 3.10+
- `uv` (recommended) or `pip`
- Jira API Token and Notion Integration Token

### Installation

1. **Clone the repository:**

   ```bash
   git clone <repository-url>
   cd pm-swarn
   ```

2. **Install dependencies:**
   Using `uv`:

   ```bash
   uv sync
   ```

   Using `pip`:

   ```bash
   pip install .
   ```

3. **Set up environment variables:**
   Copy `.env.example` to `.env` and fill in your credentials:

   ```bash
   cp .env.example .env
   ```

### Running the Application

To run the full audit cycle (placeholder for main execution script):

```bash
python -m src.main
```

## Development Workflow

The project follows the **Strata Dev Framework** with these key stages:

1. **PRIME**: Analyze the Jira story and identify technical requirements.
2. **PLAN**: Draft an implementation plan covering specialists and models.
3. **EXECUTE**: Implement the logic and associated tests.
4. **VERIFY**: Run the test suite and compliance audit.
5. **UPDATE**: Update `stories.json` and prepare the Pull Request.

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=src
```

## Documentation

- **PRD**: [PRD for PM Swarn](docs/PRD%20for%20PM%20Swarn.md)
- **Stories**: [stories.json](docs/specs/stories.json)
- **Audit Reports**: Generated in the configured Notion database.

## Project Structure

```bash
pm-swarn/
├── docs/               # PRD, specs, and audit reports
├── src/
│   ├── jira/           # Jira API integration and specialist logic
│   ├── notion/         # Notion API integration and report writing
│   ├── logic/          # Compliance validation and rules
│   └── model/          # Normalized data models
├── tests/              # Comprehensive test suite
├── .env.example        # Template for environment variables
├── Dockerfile          # Containerization for deployment
└── pyproject.toml      # Project dependencies and configuration
```

---
Built with ❤️ using Python and Antigravity

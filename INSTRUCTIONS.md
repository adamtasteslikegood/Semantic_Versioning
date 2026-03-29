# Project Evolution and Publishing Guide

This document describes how to take this repository from a local Python project
to a packaged and published Semantic Versioning validator with a FastAPI backend
and a backend-powered Gemini analyzer.

The project is currently centered around:

- a strict SemVer 2.0.0 validator
- a CLI entrypoint
- a FastAPI API
- a Gemini-backed analyzer endpoint
- packaging metadata in `pyproject.toml`

## Project Goals

This repository should remain:

- strict about Semantic Versioning 2.0.0 compliance
- lightweight in dependencies
- consistent across CLI and API behavior
- safe with secret handling
- intentional about versioning and release changes

## Current Repository Structure

Expected key files:

- `semver_validator/main.py`
  - SemVer regex
  - `validate_semver()`
  - CLI entrypoint
- `semver_validator/api.py`
  - FastAPI app
  - `/validate` endpoint
  - `/analyze` endpoint
- `pyproject.toml`
  - package metadata
  - dependencies
  - script entrypoint
- `README.md`
  - user-facing setup and usage documentation
- `AGENTS.md`
  - repository-specific agent instructions
- `CODEX.md`
  - Codex/OpenAI-style workflow defaults
- `GEMINI.md`
  - Gemini-specific engineering guidance
- `.env_example`
  - example environment variable template
- `.gitignore`
  - excludes secrets, virtual environments, and build/cache artifacts

## Environment Setup

### Option A: Standard `venv`

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

Install the project in editable mode:

```bash
pip install -e .
```

### Option B: Direct dependency install

If you are not installing the package itself yet, you can install the runtime
dependencies directly:

```bash
pip install fastapi uvicorn
```

## Environment Variables

The analyzer endpoint expects a Gemini API key to be available to the backend.

Create a local `.env` file for development:

```bash
GEMINI_API_KEY=<your_api_key>
```

Important rules:

- never commit `.env`
- keep the Gemini API key server-side
- do not expose secrets in frontend JavaScript or static HTML
- keep `.env_example` in sync with the expected environment variables

## Versioning Policy

This project is currently at `0.5.0` and is still pre-`1.0.0`.

Use Semantic Versioning carefully:

- `MAJOR` for incompatible public API or CLI changes after `1.0.0`
- `MINOR` for backward-compatible functionality additions
- `PATCH` for backward-compatible bug fixes

Before `1.0.0`, breaking changes are still allowed, but they should be made
intentionally, documented clearly, and used to move the project toward a stable
public contract.

For this repository, treat the following as public contracts:

- the JSON structure returned by `validate_semver()`
- CLI invocation and argument behavior
- API request/response behavior for `/validate`
- API request/response behavior for `/analyze`

If one of those changes in a breaking way, that should be considered a
major-version concern.

## Phase 1: Core Validator and CLI

Goal: maintain a strict, reusable SemVer validation core.

### Requirements

- `validate_semver()` must remain the source of truth for validation
- validation must stay aligned with SemVer 2.0.0
- CLI output should remain JSON-friendly
- CLI exit behavior should remain useful for scripting

### Recommended validation examples

Should pass:

- `1.0.0`
- `0.1.0`
- `2.1.3-alpha`
- `1.0.0-beta.1`
- `1.0.0+build.1`
- `1.0.0-beta.1+exp.sha.5114f85`

Should fail:

- `01.0.0`
- `1.02.3`
- `1.0`
- `1.0.0-`
- `1.0.0+`
- `1.0.0-alpha..1`

### CLI usage examples

Run the CLI through the package entrypoint:

```bash
semver-cli 1.2.3
```

Or run the module directly:

```bash
python -m semver_validator.main 1.2.3
```

Interactive mode:

```bash
semver-cli --interactive
```

## Phase 2: FastAPI Backend

Goal: expose the validator over HTTP while preserving the same core behavior.

### Requirements

- `/validate` should call `validate_semver()`
- API responses should stay aligned with the shared validator
- avoid duplicating validation logic in multiple places
- keep endpoint behavior simple and explicit

### Local development

Run the API locally:

```bash
uvicorn semver_validator.api:app --reload
```

Validate a version:

```bash
curl "http://127.0.0.1:8000/validate?version=1.2.3"
```

## Phase 3: Gemini Analyzer Endpoint

Goal: move AI release analysis to the backend so secrets remain secure and the
frontend only talks to your own API.

### Backend design

The `/analyze` endpoint should:

- accept a current version and a description of changes
- validate the current version before attempting analysis
- read `GEMINI_API_KEY` from the backend environment
- call Gemini from the Python server
- return structured JSON to the frontend

### Security rules

- never place `GEMINI_API_KEY` in frontend code
- never hardcode the key into the repository
- do not return secrets in error messages
- keep backend failures explicit but safe

### Example request

```bash
curl -X POST "http://127.0.0.1:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "current_version": "1.2.3",
    "changes": "- add analyzer endpoint\n- fix CLI output\n- update README"
  }'
```

### Expected response shape

```json
{
  "current_version": "1.2.3",
  "validation": {
    "status": "pass",
    "major": 1,
    "minor": 2,
    "patch": 3,
    "prerelease": null,
    "buildmetadata": null
  },
  "analysis": {
    "bump_type": "MINOR",
    "next_version": "1.3.0",
    "explanation": "Adds backward-compatible functionality, so a MINOR version bump is appropriate."
  }
}
```

### Failure behavior

If the version is invalid:

- reject the request before calling Gemini
- return a clear client-facing validation error

If Gemini fails:

- return a backend error indicating the upstream request failed
- avoid pretending the analysis succeeded
- keep the response free of sensitive values

## Phase 4: Packaging and Release Hygiene

Goal: keep the package metadata aligned with the real codebase.

### `pyproject.toml` expectations

Ensure package metadata reflects:

- current version
- current dependencies
- correct entrypoint

Current runtime dependencies should include:

- `fastapi`
- `uvicorn`

### Build the package

```bash
python -m build
```

If needed, install build tooling first:

```bash
pip install build
```

### Publish the package

```bash
twine upload dist/*
```

If needed, install publishing tooling first:

```bash
pip install twine
```

## Suggested Release Workflow

For the current pre-`1.0.0` milestone and upcoming stable release work:

1. create or update a `release/x.y.z` branch from `master`
2. merge feature, fix, docs, and chore branches into the release branch
3. verify the validator still behaves correctly
4. verify CLI behavior still works
5. verify FastAPI endpoints still work
6. verify `.env_example` matches the backend requirements
7. update documentation if behavior changed
8. update `pyproject.toml` version intentionally
9. commit with a clear message
10. tag the release from `master` after the release branch is finalized
11. build and publish

## Example Version Decisions

Use `PATCH` when:

- fixing a bug in the validator without changing its public output contract
- improving error handling without breaking clients
- correcting documentation or packaging metadata

Use `MINOR` when:

- adding a new backward-compatible endpoint
- adding optional functionality
- enhancing documentation and tooling in ways that do not break users

Use `MAJOR` when:

- changing the validator response schema incompatibly
- changing CLI arguments incompatibly
- changing request or response structures in a breaking API way

## Branch Strategy

Use `master` as the primary branch.

Recommended branch naming:

- `release/x.y.z` for the upcoming release integration branch
- `feat/...` for new features
- `fix/...` for bug fixes
- `docs/...` for documentation-only changes
- `chore/...` for maintenance tasks

Examples:

- `release/0.5.0`
- `release/1.0.0`
- `feat/analyzer-endpoint`
- `fix/api-error-handling`
- `docs/readme-api-usage`

Recommended flow:

- branch feature work from the active release branch or from `master`, depending
  on team preference
- merge completed `feat/...`, `fix/...`, `docs/...`, and `chore/...` branches
  into the active `release/x.y.z` branch
- finalize and verify the release branch
- merge the completed release branch back into `master`
- tag the release from `master`

## Documentation Maintenance

Whenever behavior changes, review and update:

- `README.md`
- `AGENTS.md`
- `CODEX.md`
- `GEMINI.md`
- `.env_example`

Keep documentation aligned with the actual repository state rather than a future
roadmap that no longer matches the code.

## Non-goals

Unless explicitly requested, do not:

- replace the strict regex with a looser parser
- duplicate validation logic across interfaces
- move secret handling into the frontend
- add heavy dependencies without a clear reason
- introduce breaking public behavior casually

## Final Guidance

This repository should evolve with a bias toward:

- strict SemVer correctness
- shared core logic
- secure backend integrations
- stable public contracts
- small, maintainable changes

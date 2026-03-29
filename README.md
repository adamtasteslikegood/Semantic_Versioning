# SemVer Validator

A small Python project for validating Semantic Versioning 2.0.0 strings.

The repository currently includes:

- a reusable core validator
- a command-line interface
- a FastAPI API endpoint
- agent instruction files for Codex/OpenAI-style workflows

The validator is intentionally strict and is designed to preserve SemVer 2.0.0
correctness rather than accept loosely formatted version strings.

## Features

- Strict SemVer 2.0.0 validation
- Structured JSON-serializable output
- CLI support for direct validation
- Interactive CLI mode
- FastAPI `/validate` endpoint
- FastAPI `/analyze` endpoint for backend Gemini-powered release analysis
- Lightweight packaging via `pyproject.toml`
- Automated tests for validator, CLI, and API behavior

## Project Layout

- `semver_validator/main.py`
  - SemVer regex
  - `validate_semver()`
  - CLI entrypoint
- `semver_validator/api.py`
  - FastAPI app
  - `/validate` endpoint
- `pyproject.toml`
  - package metadata
  - dependencies
  - script entrypoint
- `AGENTS.md`
  - repo-specific agent instructions
- `CODEX.md`
  - Codex/OpenAI-style default workflow guidance
- `tests/`
  - automated tests for validator, CLI, and API behavior
- `docs/1.0.0-checklist.md`
  - stabilization checklist for the `1.0.0` release

## Requirements

- Python 3.8+
- Dependencies listed in `pyproject.toml`

Current runtime dependencies:

- `fastapi>=0.100.0`
- `uvicorn>=0.20.0`

For the analyzer feature, the API also expects:

- `GEMINI_API_KEY` to be available in the environment

## Installation

### Option 1: Create a virtual environment and install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

On Windows:

```bash
.venv\Scripts\activate
pip install -e .
```

### Option 2: Install dependencies directly

```bash
pip install fastapi uvicorn
```

## Environment Setup

Create a local `.env` file for development and set your Gemini API key there:

```bash
GEMINI_API_KEY=<your_api_key>
```

An example template is included in:

- `.env_example`

Important:

- keep `.env` out of version control
- do not expose the Gemini API key in frontend code
- the FastAPI backend should read the key server-side and call Gemini on behalf
  of the frontend

## CLI Usage

You can validate a SemVer string from the command line.

### Using the package entrypoint

```bash
semver-cli 1.0.0-beta.2+exp.sha.5114f85
```

### Using the module directly

```bash
python -m semver_validator.main 1.0.0-beta.2+exp.sha.5114f85
```

### Example output

```json
{
  "status": "pass",
  "major": 1,
  "minor": 0,
  "patch": 0,
  "prerelease": "beta.2",
  "buildmetadata": "exp.sha.5114f85"
}
```

### Invalid example

```bash
semver-cli 01.0.0
```

Example failure output:

```json
{
  "status": "fail",
  "reason": "String does not match SemVer 2.0.0 specifications. Ensure it is in X.Y.Z format, contains no leading zeroes on numbers, and uses valid characters [0-9A-Za-z-] for pre-release/build tags."
}
```

### Interactive mode

```bash
semver-cli --interactive
```

Or:

```bash
python -m semver_validator.main --interactive
```

## API Usage

Run the FastAPI app locally with Uvicorn:

```bash
uvicorn semver_validator.api:app --reload
```

Then call the validation endpoint:

```bash
http://127.0.0.1:8000/validate?version=1.0.0-beta.1%2Bexp.sha.5114f85
```

You can also test it in a browser or with `curl`:

```bash
curl "http://127.0.0.1:8000/validate?version=1.2.3"
```

Expected response:

```json
{
  "status": "pass",
  "major": 1,
  "minor": 2,
  "patch": 3,
  "prerelease": null,
  "buildmetadata": null
}
```

### Analyzer endpoint

The API also supports an analyzer endpoint that sends release-change context to
Gemini from the backend instead of exposing the API key in the frontend.

Endpoint:

```text
POST /analyze
```

Example request body:

```json
{
  "current_version": "1.2.3",
  "changes": "- add new /analyze endpoint\n- fix CLI output formatting\n- update README examples"
}
```

Example `curl` request:

```bash
curl -X POST "http://127.0.0.1:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "current_version": "1.2.3",
    "changes": "- add new /analyze endpoint\n- fix CLI output formatting\n- update README examples"
  }'
```

Expected response shape:

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

If `current_version` is invalid, the API should reject the request before
attempting the Gemini call.

## Validation Notes

This project follows Semantic Versioning 2.0.0 rules, including:

- no leading zeroes in numeric identifiers except `0`
- support for prerelease identifiers
- support for build metadata
- rejection of malformed or partial version strings

Examples that should pass:

- `1.0.0`
- `0.1.0`
- `2.1.3-alpha`
- `1.0.0-beta.1`
- `1.0.0+build.1`
- `1.0.0-beta.1+exp.sha.5114f85`

Examples that should fail:

- `01.0.0`
- `1.02.3`
- `1.0`
- `1.0.0-`
- `1.0.0+`
- `1.0.0-alpha..1`

## Agent Guidance

This repository includes agent-oriented instruction files:

- `AGENTS.md` for repo-specific engineering rules and workflows
- `CODEX.md` for default Codex/OpenAI-style project guidance

Recommended workflows for agent-based changes include:

- validator change workflow
- CLI/API parity workflow
- packaging and release workflow
- docs sync workflow
- breaking change gate

There is also a dedicated stabilization checklist for the stable release in:

- `docs/1.0.0-checklist.md`

If you are making automated or agent-assisted changes, keep the following
principles in mind:

- preserve strict SemVer 2.0.0 behavior
- keep `validate_semver()` as the single source of truth
- avoid duplicated validation logic
- keep output contracts stable
- treat CLI/API/output-schema breaking changes as major-version concerns

## Packaging Notes

Project metadata is defined in `pyproject.toml`.

Current package version:

- `0.5.0`

Script entrypoint:

- `semver-cli = "semver_validator.main:main"`

## Release Workflow

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

1. create or update the active `release/x.y.z` branch from `master`
2. merge completed `feat/...`, `fix/...`, `docs/...`, and `chore/...` branches
   into the active release branch
3. verify CLI, API, and analyzer behavior
4. update documentation and package metadata
5. finalize the release branch
6. merge it back into `master`
7. tag the release from `master`

## Future Improvements

Potential future additions could include:

- CI checks for validator, CLI, and API behavior
- analyzer integration testing with a real local `GEMINI_API_KEY`
- publishing workflow improvements
- optional executable packaging
- public API hardening and stability work for `1.0.0`

For `1.0.0` planning and release readiness, see:

- `docs/1.0.0-checklist.md`

Current automated coverage includes:

- core validator tests
- CLI behavior tests
- `/validate` endpoint tests
- `/analyze` endpoint tests with mocked upstream responses

## License

Add a license file if you plan to distribute the project publicly.

## Contributing

Keep changes small, explicit, and consistent with the current behavior of the
validator. Favor correctness and interface stability over broader refactors.

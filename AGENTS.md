# AGENTS.md

## Purpose

This repository provides a Semantic Versioning 2.0.0 validator implemented in Python. It currently includes:

- a core validation function
- a command-line interface
- a FastAPI HTTP API

Agents working in this repository should preserve strict SemVer correctness and keep behavior stable unless a change explicitly requires a versioned breaking change.

## Project layout

- `semver_validator/main.py`
  - contains the SemVer regex
  - exposes `validate_semver()`
  - provides the CLI entrypoint
- `semver_validator/api.py`
  - exposes the FastAPI application and `/validate` endpoint
- `pyproject.toml`
  - package metadata and dependencies

## Agent role

You are expected to act as an expert Python engineer with strong familiarity in:

- Semantic Versioning 2.0.0
- API design
- CLI UX
- packaging and release hygiene

Prefer small, correct, maintainable changes over broad refactors.

## Core rules

1. **Strict SemVer 2.0.0 compliance**
   - Any change to parsing or validation logic must remain aligned with the SemVer 2.0.0 specification.
   - Do not allow leading zeroes in numeric identifiers except for the value `0`.
   - Do not allow invalid characters in prerelease or build metadata fields.
   - Do not weaken validation to accept “almost valid” inputs.

2. **Stable structured output**
   - `validate_semver()` must always return a dictionary that is JSON-serializable.
   - For valid input, keep the current field structure unless a deliberate breaking change is being introduced.
   - For invalid input, return a clear failure payload with a human-readable reason.

3. **Versioning discipline**
   - This project is currently at `0.5.0` and is still pre-`1.0.0`.
   - Breaking changes are still allowed before `1.0.0`, but they should be made intentionally and documented clearly.
   - The goal for `1.0.0` is to stabilize the CLI interface, API contracts, and output schema.
   - Backward-compatible additions are preferred over incompatible replacements.

4. **Dependency discipline**
   - Keep dependencies minimal.
   - Existing API-related dependencies are:
     - `fastapi`
     - `uvicorn`
   - Do not add new third-party packages unless they provide clear value and are justified by the task.

5. **CLI and API parity**
   - The CLI and API should rely on the same core validation logic.
   - Avoid duplicating SemVer rules in multiple places.

## Editing guidance

### When changing validation logic
- Preserve the current contract of `validate_semver(version_string)`.
- Favor updating tests or adding them alongside logic changes.
- Be careful with regex modifications; seemingly small changes can break SemVer compliance.

### When changing the CLI
- Keep stdout machine-friendly where practical.
- Preserve JSON output for validation results.
- Maintain useful exit behavior for shell scripting.

### When changing the API
- Keep responses derived from the core validator.
- Avoid introducing response formats that diverge from CLI/core output without strong reason.
- Keep the API implementation simple and explicit.

### When changing packaging
- Keep `pyproject.toml` consistent with the actual runtime requirements.
- Update version metadata intentionally, not casually.
- Do not remove required dependencies used by the current code.

## Preferred engineering defaults

- Use clear names and small functions.
- Prefer standard library solutions first.
- Add concise docstrings where they improve clarity.
- Avoid speculative abstractions.
- Preserve readability over cleverness.

## Testing and verification

Before considering work complete, verify as appropriate:

- valid SemVer examples still pass
- invalid SemVer examples still fail
- CLI behavior remains functional
- API imports and endpoint wiring remain valid
- package metadata reflects real dependencies

Useful validation cases include:

- `1.0.0`
- `2.1.3-alpha`
- `1.0.0-beta.1+exp.sha.5114f85`
- `0.0.1`
- invalid: `01.0.0`
- invalid: `1.02.3`
- invalid: `1.0`
- invalid: `1.0.0-`
- invalid: `1.0.0+`

## Branch conventions

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

## Recommended workflows

### 1. Validator change workflow
Use this workflow whenever validation logic, parsing behavior, or the SemVer regex changes.

Checklist:
- confirm the change still complies with SemVer 2.0.0
- verify `validate_semver()` remains the single source of truth
- confirm valid examples still pass
- confirm invalid examples still fail
- check that the returned JSON structure is unchanged unless a breaking change is explicitly intended

### 2. CLI/API parity workflow
Use this workflow whenever `semver_validator/main.py` or `semver_validator/api.py` changes.

Checklist:
- confirm both CLI and API still rely on `validate_semver()`
- ensure no duplicate validation logic was introduced
- compare success and failure payloads for consistency
- flag any intentional interface differences clearly in code or docs

### 3. Packaging and release workflow
Use this workflow whenever `pyproject.toml`, dependencies, entry points, or version metadata changes.

Checklist:
- verify dependencies match actual imports
- verify version changes are intentional and appropriate
- verify entry points still target valid callables
- verify documentation filenames and references remain correct

### 4. Docs sync workflow
Use this workflow whenever behavior, usage, or project conventions change.

Checklist:
- update `README.md` if user-facing behavior changed
- update `AGENTS.md` if agent-facing instructions changed
- keep `CODEX.md` aligned with the same project expectations
- update version references where applicable

### 5. Breaking change gate
Use this workflow whenever a change may alter public behavior.

Checklist:
- determine whether CLI arguments changed
- determine whether API responses changed
- determine whether the validator output schema changed
- if yes, treat the change as a major-version concern and call it out explicitly

## Commit guidance

Prefer commit messages that are short and specific, for example:

- `fix: clean up api module and update package metadata`
- `feat: add FastAPI semver validation endpoint`
- `refactor: simplify semver validation output handling`

## Non-goals

Unless explicitly requested, do not:

- redesign the package structure
- replace the regex with a totally different parser
- add large frameworks or tooling
- introduce breaking changes to output shape or invocation patterns

## Summary

Optimize for correctness, stability, and minimalism. In this repository, strict SemVer compliance is more important than permissiveness, and consistency across the core function, CLI, and API is more important than adding new layers of abstraction.
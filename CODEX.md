# CODEX.md

## Purpose

This file provides default Codex-style instructions for working in this repository.

The repository contains a Python implementation of a strict Semantic Versioning 2.0.0 validator, along with:
- a reusable validation function
- a CLI entrypoint
- a FastAPI API

When making changes, optimize for correctness, consistency, and minimalism.

## Project overview

Primary files and responsibilities:

- `semver_validator/main.py`
  - contains the SemVer validation regex
  - exposes `validate_semver(version_string)`
  - provides the CLI entrypoint
- `semver_validator/api.py`
  - exposes the FastAPI application
  - provides the `/validate` endpoint
- `pyproject.toml`
  - package metadata
  - runtime dependencies
  - script entrypoints

## Core engineering rules

### 1. Preserve strict SemVer 2.0.0 behavior
Any change to parsing or validation must remain compliant with the Semantic Versioning 2.0.0 specification.

Important constraints:
- no leading zeroes in numeric identifiers except `0`
- no invalid characters in prerelease or build metadata
- do not accept partially valid or loosely formatted versions
- do not weaken validation just to be permissive

### 2. Keep core logic centralized
The CLI and API should both use the same core validator.

Preferred rule:
- `validate_semver()` is the source of truth
- avoid duplicating validation logic in multiple files
- prefer reuse over branching behavior by interface

### 3. Maintain stable output contracts
`validate_semver()` should always return a JSON-serializable dictionary.

Current expectations:
- valid input returns structured fields for version components
- invalid input returns a failure payload with a readable reason

Do not change output keys casually. The project is currently at `0.5.0`, so pre-`1.0.0` changes are still possible, but they should be intentional and documented clearly. The goal for `1.0.0` is to stabilize response shape, CLI behavior, and API behavior.

### 4. Keep dependencies minimal
Use the standard library when possible.

Current third-party dependencies are:
- `fastapi`
- `uvicorn`

Do not add new dependencies unless they are clearly necessary for the task.

### 5. Prefer small, targeted changes
Avoid broad refactors unless explicitly requested.

Good defaults:
- fix the root cause
- preserve existing public behavior
- improve readability when touching code
- avoid speculative abstractions

## Coding defaults

### Python style
- write clear, direct Python
- prefer descriptive names
- keep functions focused
- use docstrings when they add real clarity
- avoid unnecessary indirection

### API style
- keep endpoints simple
- derive API responses from the core validator
- avoid introducing response formats that diverge from the validator without a strong reason

### CLI style
- keep output machine-friendly where practical
- preserve JSON output behavior for validation results
- maintain sensible exit codes for scripting use

### Packaging style
- keep `pyproject.toml` aligned with actual runtime requirements
- update version metadata intentionally
- do not remove dependencies that are actively used by the codebase

## Validation guidance

When modifying validator behavior, use examples like these to reason-check changes.

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

## Suggested workflow

When implementing a change:
1. understand whether it affects core validation, CLI behavior, API behavior, or packaging
2. make the smallest change that fully solves the problem
3. preserve shared behavior across interfaces
4. check for unintended contract changes
5. keep the code easy for the next engineer to understand

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

## Commit message defaults

Prefer short, specific commit messages, for example:
- `fix: clean up api module and update package metadata`
- `feat: add semver validation API endpoint`
- `refactor: simplify semver validator flow`

## Non-goals

Unless explicitly requested, do not:
- redesign the repository structure
- replace the regex with a totally different parser
- add heavy frameworks or build tooling
- change output schemas in breaking ways
- introduce clever abstractions that make the code harder to maintain

## Final instruction

In this repository, correctness is more important than cleverness, and consistency is more important than novelty.
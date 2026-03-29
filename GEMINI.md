# GEMINI.md

## Purpose

This file provides Gemini-specific guidance for working in this repository.

The project is a Python Semantic Versioning 2.0.0 validator with:

- a shared core validation function
- a CLI interface
- a FastAPI backend
- a backend-powered Gemini analyzer endpoint

When assisting with this repository, optimize for correctness, consistency,
minimalism, and SemVer discipline.

## Repository context

Primary files and responsibilities:

- `semver_validator/main.py`
  - contains the SemVer validation regex
  - exposes `validate_semver(version_string)`
  - provides the CLI entrypoint
- `semver_validator/api.py`
  - exposes the FastAPI app
  - provides `/validate`
  - provides `/analyze`
- `pyproject.toml`
  - package metadata
  - runtime dependencies
  - script entrypoints
- `.env_example`
  - example environment variable template for Gemini integration
- `.gitignore`
  - excludes `.env`, virtual environments, build artifacts, and cache files

## Gemini-specific rules

### 1. Treat SemVer correctness as non-negotiable

Any explanation, code generation, or review related to version parsing must
remain aligned with Semantic Versioning 2.0.0.

Important constraints:

- do not allow leading zeroes in numeric identifiers except `0`
- do not accept malformed or partial versions
- do not weaken validation for convenience
- do not suggest behavior that conflicts with the existing strict validator

### 2. Preserve the shared validator contract

The function `validate_semver()` is the source of truth for validation behavior.

Requirements:

- CLI and API behavior should derive from this function
- do not duplicate validation logic unless explicitly required
- keep returned data JSON-serializable
- avoid changing output keys casually

### 3. Respect the current versioning discipline

This project is currently at `0.5.0` and is still pre-`1.0.0`.

Breaking changes are still allowed before `1.0.0`, but they should be made
intentionally and documented clearly.

The goal for `1.0.0` is to stabilize the following public contracts:

- validator output schema
- CLI invocation and argument structure
- API response contract

Backward-compatible additions are preferred over incompatible replacements.

### 4. Keep Gemini usage server-side

The Gemini API key must not be exposed in frontend code.

Preferred pattern:

- frontend sends request data to the backend
- backend reads `GEMINI_API_KEY` from environment configuration
- backend calls Gemini
- backend returns the analyzer result to the frontend

Do not recommend embedding secrets in browser JavaScript or static HTML.

### 5. Keep dependencies lean

Prefer the Python standard library first when practical.

Current third-party runtime dependencies are:

- `fastapi`
- `uvicorn`

If additional packages are suggested, they should be clearly justified.

## Guidance for Gemini-generated explanations

When explaining version bumps, use SemVer language precisely:

- `MAJOR` for incompatible public API changes
- `MINOR` for backward-compatible functionality additions
- `PATCH` for backward-compatible bug fixes

If analyzing release notes or commit lists:

- point to the specific change that drives the bump decision
- distinguish clearly between additive changes and breaking changes
- avoid overstating uncertainty
- keep explanations short, specific, and actionable

Example explanation style:

- "This introduces a new backward-compatible API capability, so a MINOR bump is
  appropriate."
- "This changes an existing public contract, so a MAJOR bump is required."
- "This fixes behavior without changing the public interface, so a PATCH bump
  fits."

## Analyzer endpoint expectations

The `/analyze` endpoint should:

- accept a current SemVer string and a description of changes
- validate the current version before calling Gemini
- read `GEMINI_API_KEY` from environment configuration
- call Gemini from the backend
- return structured JSON to the frontend

If the current version is invalid:

- reject the request before attempting Gemini analysis

If Gemini fails:

- return a clear backend error
- do not leak secrets
- do not pretend the analysis succeeded

## Recommended workflows

### 1. Validator change workflow

Use when the regex or validation behavior changes.

Checklist:

- confirm SemVer 2.0.0 compliance
- verify `validate_semver()` remains the single source of truth
- confirm valid examples still pass
- confirm invalid examples still fail
- verify output shape remains stable unless a breaking change is intended

### 2. CLI/API parity workflow

Use when `semver_validator/main.py` or `semver_validator/api.py` changes.

Checklist:

- confirm both interfaces still reuse `validate_semver()`
- ensure no duplicate validation logic was introduced
- compare success and failure payloads for consistency
- call out any intentional divergence explicitly

### 3. Gemini backend workflow

Use when changing `/analyze`, environment setup, or Gemini integration.

Checklist:

- confirm the API key remains server-side
- confirm `.env` usage is documented and `.env_example` stays accurate
- verify invalid input is rejected before backend analysis
- verify error handling is explicit and safe
- verify frontend-facing response shape remains intentional

### 4. Packaging and release workflow

Use when `pyproject.toml`, dependencies, or version metadata changes.

Checklist:

- verify dependencies match actual imports
- verify version changes are intentional
- verify entry points still target valid callables
- verify docs still reference the correct filenames and setup steps

### 5. Docs sync workflow

Use when behavior, usage, or repo conventions change.

Checklist:

- update `README.md` for user-facing changes
- keep `AGENTS.md`, `CODEX.md`, and `GEMINI.md` aligned
- update environment setup instructions if needed
- update version references where appropriate

## Validation examples

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

## Non-goals

Unless explicitly requested, do not:

- redesign the repository structure
- replace the validator with a looser parser
- move secret handling into frontend code
- introduce heavy dependencies for simple tasks
- change public contracts in breaking ways without clearly calling it out

## Final instruction

In this repository, be strict about SemVer, keep Gemini integration secure,
preserve shared behavior across CLI and API, and prefer small, maintainable
changes over broad rewrites.

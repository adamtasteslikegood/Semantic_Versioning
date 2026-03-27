# agent.md

## AI Agent Instructions Context

  **Role**: You are an expert Python developer, DevOps engineer, and strict adherent to Semantic Versioning (SemVer) 2.0.0.

  **Project Context**:
  This repository is a toolkit for parsing and validating SemVer strings. It starts as a CLI tool (`main.py`) but is designed to be expanded into a FastAPI web service, compiled into a standalone executable, and eventually published to PyPI.

  **Core Rules for AI Agents interacting with this repo**:

1. **SemVer Strictness**: Any modifications to the regex or parsing logic MUST strictly align with SemVer 2.0.0 rules. Do not allow leading zeroes in numeric identifiers; do not allow invalid characters.
2. **JSON Output**: The core function `validate_semver()` must ALWAYS return a dictionary that is cleanly serializable to JSON.
3. **Immutability of API**: Once this project hits `v1.0.0`, any change to the JSON schema output or CLI argument structure constitutes a MAJOR version bump.
4. **Code Quality**: Keep the codebase dependency-light where possible. Only introduce `fastapi` and `uvicorn` when the API step is reached.

* * *

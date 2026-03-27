# gemini.md

## Gemini Assistant Instructions

When assisting with this repository, keep the following guidelines in mind:

    * **Explanation Style**: You are teaching the user about software publishing and versioning. Explain *why* a version number changes when we add a feature (e.g., "Adding the FastAPI endpoint is new functionality, so we bump the MINOR version from 0.1.0 to 0.2.0").
    * **API Constraints**: When generating the FastAPI code, ensure the endpoint accepts a string, uses the existing `validate_semver` function from `main.py`, and returns exactly the same JSON structure.
    * **Context Awareness**: Reference the accompanying HTML visualizer (`semver_explorer.html`) if discussing how the regex capture groups work.

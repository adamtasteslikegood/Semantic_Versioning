# INSTRUCTIONS.md

## Project Evolution & Publishing Guide

This document outlines the steps to take this repository from an initial script
(v0.1.0) to a fully published, stable release (v1.0.0) following
Semantic Versioning rules.

## Phase 1: Initial Setup (v0.1.0)

**Currently in this phase.**
The API is considered unstable (0.y.z).

1. Initialize a git repository: `git init`
2. Add the generated files (`main.py`, `README.md`, `INSTRUCTIONS.md`, etc.).
3. Commit the code: `git commit -m "Initial commit of SemVer CLI"`
4. Tag the release: `git tag v0.1.0`

## Phase 2: Adding the API (v0.2.0)

_Action: Adding functionality in a backwards-compatible manner (increment MINOR)._

1. Install FastAPI and Uvicorn: `pip install fastapi uvicorn`
2. Create a new file named `api.py`.
3. Import the `validate_semver` function from `main.py`.
4. Create a GET or POST endpoint (e.g., `/validate?version=...`) that returns the JSON from the validator.
5. Test locally: `uvicorn api:app --reload`
6. Commit and tag: `git commit -m "Add FastAPI endpoint"`, then `git tag v0.2.0`

## Phase 3: Compiling to an Executable (v0.3.0)

**Action: Adding new deployment functionality.**
We want users to run this without needing Python installed.

1. Install PyInstaller: `pip install pyinstaller`
2. Run PyInstaller to create a single standalone binary for the CLI tool:

   ```bash
   pyinstaller --onefile main.py --name semver-tool
   ```

3. Test the executable found in the `dist/` folder.

4. Add `build/`, `dist/`, and `*.spec` to your `.gitignore` file.

5. Commit and tag: `git commit -m "Add PyInstaller build configuration"`, then `git tag v0.3.0`

### Phase 4: Preparing for PyPI (v0.4.0)

---

_Action: Project restructuring for distribution._

1. Create a `pyproject.toml` file at the root of your repository to define the package metadata (name, version, dependencies).

2. Move `main.py` and `api.py` into a package directory (e.g., `semver_utils/`).

3. Update imports to reflect the new structure.

4. In `pyproject.toml`, define a `[project.scripts]` entry point so that when users install via pip, they get the CLI command automatically (e.g., `semver-cli = "semver_utils.main:main"`).

5. Commit and tag: `git tag v0.4.0`

## Phase 5: The Public API & Stable Release (v1.0.0)

---

**Action: Declaring the API stable.**

- By tagging `1.0.0`, you are declaring that the JSON output format and
- CLI arguments are the stable "Public API". Any future changes to
- how the JSON is structured will require bumping to `2.0.0`.

1. Ensure all documentation is up to date.

2. Install the build tools: `pip install build twine`

3. Build the distribution archives: `python -m build`

4. Publish to the Python Package Index (PyPI):

```bash
twine upload dist/*
```

1. Commit and tag: `git tag v1.0.0`

Congratulations! You have successfully published a package and adhered strictly to Semantic Versioning throughout the process.

---

> > Would you like me to go ahead and write the `api.py` file for
> > Phase 2 now, or are you still getting the initial folder
> > structure set up?

# README.md

## SemVer Validator
  
  A command-line utility and foundational project for validating Semantic Versioning (SemVer) 2.0.0 strings. It parses valid version numbers into their constituent parts (Major, Minor, Patch, Pre-release, Build Metadata) and outputs the results as JSON.
  
## Features

* Strict adherence to SemVer 2.0.0 rules using official Regular Expressions.
* Returns structured JSON data for easy integration with other tools.
* Interactive mode for manual testing.
* Designed to be expanded into a FastAPI service and published to PyPI.
  
## Usage

### Command Line

  Pass a version string directly to the script to get a JSON response:
  
```bash
    python main.py 1.0.0-beta.2+exp.sha.5114f85
```

**Output:**

```JSON

    {
      "status": "pass",
      "major": 1,
      "minor": 0,
      "patch": 0,
      "prerelease": "beta.2",
      "buildmetadata": "exp.sha.5114f85"
    }
```

### Interactive Mode

Run the tool in an interactive loop:

```Bash

    python main.py --interactive

```

### Project Roadmap

See `INSTRUCTIONS.md` for the step-by-step guide on how this project will evolve from a simple script (v0.1.0) to a published API and executable (v1.0.0).

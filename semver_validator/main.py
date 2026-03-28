import argparse
import json
import re
import sys

# Official SemVer 2.0.0 Regex with named capture groups for Python
SEMVER_REGEX = re.compile(
    r"^(?P<major>0|[1-9]\d*)\."
    r"(?P<minor>0|[1-9]\d*)\."
    r"(?P<patch>0|[1-9]\d*)"
    r"(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    r"(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)


def validate_semver(version_string):
    """
    Validates a version string against SemVer 2.0.0 rules.
    Returns a dictionary suitable for JSON serialization.
    """
    match = SEMVER_REGEX.match(version_string.strip())

    if match:
        data = match.groupdict()
        return {
            "status": "pass",
            "major": int(data["major"]),
            "minor": int(data["minor"]),
            "patch": int(data["patch"]),
            "prerelease": data["prerelease"],
            "buildmetadata": data["buildmetadata"],
        }
    else:
        # A more complex parser would be needed for exact syntax errors,
        # but this covers the general failure based on the regex.
        return {
            "status": "fail",
            "reason": "String does not match SemVer 2.0.0 specifications. "
            "Ensure it is in X.Y.Z format, contains no leading zeroes on numbers, "
            "and uses valid characters [0-9A-Za-z-] for pre-release/build tags.",
        }


def interactive_mode():
    """Runs a loop allowing the user to type versions and see the JSON output."""
    print("--- SemVer Validator Interactive Mode ---")
    print("Type a version number to validate, or 'quit'/'exit' to stop.")
    while True:
        try:
            user_input = input("\nEnter version: ").strip()
            if user_input.lower() in ["quit", "exit", "q"]:
                break
            if not user_input:
                continue

            result = validate_semver(user_input)
            print(json.dumps(result, indent=2))
        except (KeyboardInterrupt, EOFError):
            print("\nExiting interactive mode.")
            break


def main():
    parser = argparse.ArgumentParser(
        description="Validate Semantic Versioning (SemVer) 2.0.0 strings.",
        epilog="Example: python main.py 1.0.0-beta.1+exp.sha.5114f85",
    )

    # Mutually exclusive group so we don't try to parse a positional arg if interactive is passed
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "version", nargs="?", help="The version string to validate (e.g., 2.1.0)"
    )
    group.add_argument(
        "-i", "--interactive", action="store_true", help="Run in interactive mode"
    )

    args = parser.parse_args()

    if args.interactive:
        interactive_mode()
    elif args.version:
        result = validate_semver(args.version)
        # Print valid JSON to stdout
        print(json.dumps(result, indent=2))
        # Exit with error code if validation failed (useful for bash scripts)
        if result["status"] == "fail":
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

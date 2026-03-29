import json
import sys

from fastapi.testclient import TestClient

from semver_validator.api import app
from semver_validator.main import validate_semver

client = TestClient(app)


def test_validate_semver_accepts_basic_version():
    result = validate_semver("1.2.3")

    assert result["status"] == "pass"
    assert result["major"] == 1
    assert result["minor"] == 2
    assert result["patch"] == 3
    assert result["prerelease"] is None
    assert result["buildmetadata"] is None


def test_validate_semver_accepts_prerelease_and_buildmetadata():
    result = validate_semver("1.0.0-beta.1+exp.sha.5114f85")

    assert result == {
        "status": "pass",
        "major": 1,
        "minor": 0,
        "patch": 0,
        "prerelease": "beta.1",
        "buildmetadata": "exp.sha.5114f85",
    }


def test_validate_semver_rejects_leading_zeroes():
    result = validate_semver("01.2.3")

    assert result["status"] == "fail"
    assert "SemVer 2.0.0" in result["reason"]


def test_validate_semver_rejects_incomplete_version():
    result = validate_semver("1.0")

    assert result["status"] == "fail"
    assert "X.Y.Z" in result["reason"]


def test_validate_endpoint_returns_success_payload():
    response = client.get("/validate", params={"version": "2.3.4"})

    assert response.status_code == 200
    assert response.json() == {
        "status": "pass",
        "major": 2,
        "minor": 3,
        "patch": 4,
        "prerelease": None,
        "buildmetadata": None,
    }


def test_validate_endpoint_returns_failure_payload():
    response = client.get("/validate", params={"version": "1.02.3"})

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "fail"
    assert "SemVer 2.0.0" in body["reason"]


def test_analyze_endpoint_rejects_invalid_current_version():
    response = client.post(
        "/analyze",
        json={
            "current_version": "01.2.3",
            "changes": "- add analyzer endpoint",
        },
    )

    assert response.status_code == 400
    body = response.json()
    assert body["detail"]["message"] == (
        "The current_version must be a valid SemVer 2.0.0 string."
    )
    assert body["detail"]["validation"]["status"] == "fail"


def test_cli_valid_version_outputs_json_and_zero_exit_code(monkeypatch, capsys):
    from semver_validator import main as main_module

    monkeypatch.setattr(sys, "argv", ["semver-cli", "1.2.3"])

    main_module.main()

    captured = capsys.readouterr()
    body = json.loads(captured.out)

    assert body == {
        "status": "pass",
        "major": 1,
        "minor": 2,
        "patch": 3,
        "prerelease": None,
        "buildmetadata": None,
    }


def test_cli_invalid_version_exits_with_code_one(monkeypatch, capsys):
    from semver_validator import main as main_module

    monkeypatch.setattr(sys, "argv", ["semver-cli", "01.2.3"])

    try:
        main_module.main()
        raised = None
    except SystemExit as exc:
        raised = exc

    assert raised is not None
    assert raised.code == 1

    captured = capsys.readouterr()
    body = json.loads(captured.out)
    assert body["status"] == "fail"

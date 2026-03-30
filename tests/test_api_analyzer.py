import json
from urllib.error import HTTPError, URLError

from fastapi.testclient import TestClient

from semver_validator import api as api_module
from semver_validator.api import AnalyzeResponse, app

client = TestClient(app)


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def read(self):
        return json.dumps(self._payload).encode("utf-8")

    def close(self):
        return None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def test_analyze_endpoint_returns_structured_analysis(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")

    gemini_payload = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": json.dumps(
                                {
                                    "bump_type": "MINOR",
                                    "next_version": "0.6.0",
                                    "explanation": (
                                        "Adds backward-compatible functionality, "
                                        "so a MINOR bump is appropriate."
                                    ),
                                }
                            )
                        }
                    ]
                }
            }
        ]
    }

    def fake_urlopen(req, timeout=30):
        assert req.full_url.endswith(":generateContent")
        assert req.get_method() == "POST"
        assert req.headers["Content-type"] == "application/json"
        assert req.headers["X-goog-api-key"] == "test-key"
        assert timeout == 30

        body = json.loads(req.data.decode("utf-8"))
        assert body["contents"][0]["parts"][0]["text"].startswith(
            "Current Version: 0.5.0"
        )
        assert "Changes/Commits" in body["contents"][0]["parts"][0]["text"]

        return FakeResponse(gemini_payload)

    monkeypatch.setattr(api_module.request, "urlopen", fake_urlopen)

    response = client.post(
        "/analyze",
        json={
            "current_version": "0.5.0",
            "changes": "- add analyzer endpoint\n- add automated tests",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "current_version": "0.5.0",
        "validation": {
            "status": "pass",
            "major": 0,
            "minor": 5,
            "patch": 0,
            "prerelease": None,
            "buildmetadata": None,
        },
        "analysis": {
            "bump_type": "MINOR",
            "next_version": "0.6.0",
            "explanation": (
                "Adds backward-compatible functionality, "
                "so a MINOR bump is appropriate."
            ),
        },
    }


def test_analyze_endpoint_returns_500_when_api_key_missing(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    response = client.post(
        "/analyze",
        json={
            "current_version": "0.5.0",
            "changes": "- add analyzer endpoint",
        },
    )

    assert response.status_code == 500
    assert "GEMINI_API_KEY is not configured" in response.json()["detail"]


def test_analyze_endpoint_returns_502_for_http_error(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")

    def fake_urlopen(req, timeout=30):
        raise HTTPError(
            req.full_url,
            503,
            "Service Unavailable",
            hdrs=None,
            fp=FakeResponse({"error": {"message": "upstream failed"}}),
        )

    monkeypatch.setattr(api_module.request, "urlopen", fake_urlopen)

    response = client.post(
        "/analyze",
        json={
            "current_version": "0.5.0",
            "changes": "- add analyzer endpoint",
        },
    )

    assert response.status_code == 502
    body = response.json()["detail"]
    assert body["message"] == "Gemini API request failed."
    assert body["status_code"] == 503
    assert "upstream failed" in body["response"]


def test_analyze_endpoint_returns_502_for_network_error(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")

    def fake_urlopen(req, timeout=30):
        raise URLError("network down")

    monkeypatch.setattr(api_module.request, "urlopen", fake_urlopen)

    response = client.post(
        "/analyze",
        json={
            "current_version": "0.5.0",
            "changes": "- add analyzer endpoint",
        },
    )

    assert response.status_code == 502
    assert response.json()["detail"] == "Unable to reach Gemini API: network down"


def test_analyze_endpoint_returns_502_for_unexpected_gemini_response(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")

    def fake_urlopen(req, timeout=30):
        return FakeResponse({"candidates": []})

    monkeypatch.setattr(api_module.request, "urlopen", fake_urlopen)

    response = client.post(
        "/analyze",
        json={
            "current_version": "0.5.0",
            "changes": "- add analyzer endpoint",
        },
    )

    assert response.status_code == 502
    body = response.json()["detail"]
    assert body["message"] == "Gemini API returned an unexpected response format."
    assert body["response"] == {"candidates": []}


def test_analyze_response_model_accepts_valid_payload():
    result = AnalyzeResponse.model_validate(
        {
            "bump_type": "PATCH",
            "next_version": "0.5.1",
            "explanation": "This is a backward-compatible bug fix.",
        }
    )

    assert result.bump_type == "PATCH"
    assert result.next_version == "0.5.1"
    assert result.explanation == "This is a backward-compatible bug fix."


def test_analyze_endpoint_returns_502_for_invalid_analysis_shape(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")

    gemini_payload = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": json.dumps(
                                {
                                    "bump_type": "MINOR",
                                    "next_version": "0.6.0",
                                }
                            )
                        }
                    ]
                }
            }
        ]
    }

    def fake_urlopen(req, timeout=30):
        return FakeResponse(gemini_payload)

    monkeypatch.setattr(api_module.request, "urlopen", fake_urlopen)

    response = client.post(
        "/analyze",
        json={
            "current_version": "0.5.0",
            "changes": "- add analyzer endpoint",
        },
    )

    assert response.status_code == 502
    body = response.json()["detail"]
    assert body["message"] == "Gemini API returned an invalid analysis payload."
    assert body["response"] == {
        "bump_type": "MINOR",
        "next_version": "0.6.0",
    }


def test_analyze_endpoint_returns_502_for_unsupported_bump_type(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")

    gemini_payload = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": json.dumps(
                                {
                                    "bump_type": "BREAKING",
                                    "next_version": "1.0.0",
                                    "explanation": "This should not be accepted.",
                                }
                            )
                        }
                    ]
                }
            }
        ]
    }

    def fake_urlopen(req, timeout=30):
        return FakeResponse(gemini_payload)

    monkeypatch.setattr(api_module.request, "urlopen", fake_urlopen)

    response = client.post(
        "/analyze",
        json={
            "current_version": "0.5.0",
            "changes": "- breaking API change",
        },
    )

    assert response.status_code == 502
    body = response.json()["detail"]
    assert body["message"] == "Gemini API returned an unsupported bump_type."
    assert body["response"] == {
        "bump_type": "BREAKING",
        "next_version": "1.0.0",
        "explanation": "This should not be accepted.",
    }


def test_analyze_endpoint_returns_502_for_empty_next_version(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")

    gemini_payload = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": json.dumps(
                                {
                                    "bump_type": "PATCH",
                                    "next_version": "   ",
                                    "explanation": "Bug fix only.",
                                }
                            )
                        }
                    ]
                }
            }
        ]
    }

    def fake_urlopen(req, timeout=30):
        return FakeResponse(gemini_payload)

    monkeypatch.setattr(api_module.request, "urlopen", fake_urlopen)

    response = client.post(
        "/analyze",
        json={
            "current_version": "0.5.0",
            "changes": "- bug fix",
        },
    )

    assert response.status_code == 502
    body = response.json()["detail"]
    assert body["message"] == "Gemini API returned an empty next_version."
    assert body["response"] == {
        "bump_type": "PATCH",
        "next_version": "   ",
        "explanation": "Bug fix only.",
    }


def test_analyze_endpoint_returns_502_for_empty_explanation(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")

    gemini_payload = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": json.dumps(
                                {
                                    "bump_type": "PATCH",
                                    "next_version": "0.5.1",
                                    "explanation": "   ",
                                }
                            )
                        }
                    ]
                }
            }
        ]
    }

    def fake_urlopen(req, timeout=30):
        return FakeResponse(gemini_payload)

    monkeypatch.setattr(api_module.request, "urlopen", fake_urlopen)

    response = client.post(
        "/analyze",
        json={
            "current_version": "0.5.0",
            "changes": "- bug fix",
        },
    )

    assert response.status_code == 502
    body = response.json()["detail"]
    assert body["message"] == "Gemini API returned an empty explanation."
    assert body["response"] == {
        "bump_type": "PATCH",
        "next_version": "0.5.1",
        "explanation": "   ",
    }

import json
import os
from urllib import error, request

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from semver_validator.main import validate_semver

load_dotenv()


class AnalyzeRequest(BaseModel):
    current_version: str
    changes: str


app = FastAPI(
    title="SemVer Validator API",
    description=(
        "A simple API to validate Semantic Versioning 2.0.0 strings and analyze "
        "release changes with Gemini."
    ),
    version="1.0.0",
)


@app.get("/validate")
def validate_version(
    version: str = Query(..., description="The SemVer string to validate"),
):
    """
    Pass a version string to this endpoint to receive a JSON response
    detailing whether it passes or fails SemVer 2.0.0 rules.
    """
    return validate_semver(version)


@app.post("/analyze")
def analyze_release(request_body: AnalyzeRequest):
    """
    Analyze a current version and a list of changes using the Gemini API.

    The server reads `GEMINI_API_KEY` from the environment so the frontend
    does not need direct access to the API key.
    """
    validation_result = validate_semver(request_body.current_version)
    if validation_result["status"] == "fail":
        raise HTTPException(
            status_code=400,
            detail={
                "message": "The current_version must be a valid SemVer 2.0.0 string.",
                "validation": validation_result,
            },
        )

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail=(
                "GEMINI_API_KEY is not configured. Set it in your environment or "
                "load it from a .env file before starting the server."
            ),
        )

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": (
                            f"Current Version: {request_body.current_version}\n\n"
                            f"Changes/Commits:\n{request_body.changes}"
                        )
                    }
                ]
            }
        ],
        "system_instruction": {
            "parts": [
                {
                    "text": (
                        "You are a strict Semantic Versioning 2.0.0 expert release "
                        "manager. Analyze the provided Current Version and the list "
                        "of Changes/Commits. Determine whether the next release "
                        "requires a MAJOR, MINOR, or PATCH bump based on standard "
                        "SemVer rules. If the current version is invalid, mark it as "
                        "INVALID_FORMAT. Briefly explain your logic and return only a "
                        "JSON object."
                    )
                }
            ]
        },
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": {
                "type": "OBJECT",
                "properties": {
                    "bump_type": {
                        "type": "STRING",
                        "enum": ["MAJOR", "MINOR", "PATCH", "INVALID_FORMAT"],
                    },
                    "next_version": {"type": "STRING"},
                    "explanation": {"type": "STRING"},
                },
                "required": ["bump_type", "next_version", "explanation"],
            },
        },
    }

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent"
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        },
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=30) as response:
            response_data = json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        response_text = exc.read().decode("utf-8", errors="replace")
        raise HTTPException(
            status_code=502,
            detail={
                "message": "Gemini API request failed.",
                "status_code": exc.code,
                "response": response_text,
            },
        ) from exc
    except error.URLError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Unable to reach Gemini API: {exc.reason}",
        ) from exc

    try:
        raw_text = response_data["candidates"][0]["content"]["parts"][0]["text"]
        analysis = json.loads(raw_text)
    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
        raise HTTPException(
            status_code=502,
            detail={
                "message": "Gemini API returned an unexpected response format.",
                "response": response_data,
            },
        ) from exc

    return {
        "current_version": request_body.current_version,
        "validation": validation_result,
        "analysis": analysis,
    }

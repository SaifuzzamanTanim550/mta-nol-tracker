"""Gemini PDF extraction service.

Sends an uploaded NOL PDF to Gemini and returns the extracted fields as a
plain dict matching our NOL schema. The API key is read from config (which
reads it from the environment) — it is never hardcoded here.

Uses the current `google-genai` SDK.
"""
import json
import re

from google import genai
from google.genai import types

from .. import config
from ..models import NOL_FIELDS

# One client, created lazily so the app still imports if the key is absent.
_client = None


def _get_client():
    global _client
    if _client is None:
        if not config.GEMINI_API_KEY:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. Add it to your .env file or the host's "
                "environment variables, then restart the server."
            )
        _client = genai.Client(api_key=config.GEMINI_API_KEY)
    return _client


_PROMPT = """You are a data-entry assistant for the MTA bus depot. You are given a
New York City Notice of Liability (NOL) PDF — a camera-violation notice issued to
the Metropolitan Transportation Authority.

Extract the following fields and return them as a single JSON object. Use the exact
keys listed below. If a value is not present in the document, return an empty string
for that key. Do not invent values.

Keys to return:
- NOL_Number: the "Notice #" number
- Issue_Date: the issue date, formatted YYYY-MM-DD
- Type_of_Violation: choose the closest match from this list ONLY:
  ["ACE", "Bus Lane", "Courtesy", "Parking", "Red Light", "School Bus Safety",
   "Speeding", "Weigh in Motion", "Work Zone Safety"].
  School-zone speed camera notices are "Speeding". Bus-lane / automated camera
  enforcement notices are "ACE".
- Enforcement_Agency: choose the closest match from this list ONLY:
  ["NYCDOT", "YPVB", "NCTPVA", "NYSDOT", "COY", "TOH"]. NYC DOF / DOT camera
  programs are "NYCDOT".
- Violation_Date: formatted YYYY-MM-DD
- Violation_Time: formatted HH:MM (24-hour)
- Violation_Location: the location text
- Speed_Over_Limit: speed over the limit if shown, else empty string
- Fine_Amount: the amount due as a number only, no dollar sign (e.g. "50.00")
- Due_Date: formatted YYYY-MM-DD
- License_Plate_Number: the plate number shown on the notice

Leave every other field empty; staff fill those in. Return ONLY the JSON object,
with no markdown fences and no commentary.
"""


def _empty_record() -> dict:
    return {k: "" for k in NOL_FIELDS}


def _coerce_json(text: str) -> dict:
    """Pull a JSON object out of the model's reply, tolerating stray fences."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        text = match.group(0)
    return json.loads(text)


def extract_fields_from_pdf(pdf_bytes: bytes) -> dict:
    """Run extraction. Returns a dict with all NOL fields (blanks where the
    model found nothing). Raises RuntimeError with a clear message on failure."""
    client = _get_client()

    try:
        response = client.models.generate_content(
            model=config.GEMINI_MODEL,
            contents=[
                types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf"),
                _PROMPT,
            ],
        )
    except Exception as e:  # noqa: BLE001 — surface a readable error to the UI
        raise RuntimeError(f"Gemini request failed: {e}") from e

    try:
        parsed = _coerce_json(response.text)
    except Exception:
        raise RuntimeError(
            "Could not read the extraction result. Please enter the fields manually."
        )

    record = _empty_record()
    for key in NOL_FIELDS:
        if key in parsed and parsed[key] is not None:
            record[key] = str(parsed[key])
    record["Status"] = record.get("Status") or "OPEN"
    return record

"""OpenAI PDF extraction service.

Sends an uploaded NOL PDF to OpenAI and returns the extracted fields as a
plain dict matching our NOL schema. The API key is read from config (which
reads it from the environment) — it is never hardcoded here.

Uses the OpenAI Responses API, which accepts a PDF directly.
"""
import base64
import json
import re

from openai import OpenAI

from .. import config
from ..models import NOL_FIELDS

# One client, created lazily so the app still imports if the key is absent.
_client = None


def _get_client():
    global _client
    if _client is None:
        if not config.OPENAI_API_KEY:
            raise RuntimeError(
                "OPENAI_API_KEY is not set. Add it to your .env file or the host's "
                "environment variables, then restart the server."
            )
        _client = OpenAI(api_key=config.OPENAI_API_KEY)
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
- Type_of_Violation: First look at the small program code printed in the colored
  box in the TOP-RIGHT corner of the notice (for example "BLC" or "ACE"). Map that
  code to the violation type using this table:
    BLC -> "Bus Lane"
    ACE -> "ACE"
    RLC -> "Red Light"
    SZC -> "Speeding"   (school zone speed camera)
    SBS -> "School Bus Safety"
    WZC -> "Work Zone Safety"
    WIM -> "Weigh in Motion"
  If the code is not present or not in the table, fall back to the body text and
  choose the closest match. The value returned must be EXACTLY one of:
  ["ACE", "Bus Lane", "Courtesy", "Parking", "Red Light", "School Bus Safety",
   "Speeding", "Weigh in Motion", "Work Zone Safety"].
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
    text = (text or "").strip()
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
    data_url = "data:application/pdf;base64," + base64.b64encode(pdf_bytes).decode()

    try:
        response = client.responses.create(
            model=config.OPENAI_MODEL,
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": _PROMPT},
                        {
                            "type": "input_file",
                            "filename": "nol.pdf",
                            "file_data": data_url,
                        },
                    ],
                }
            ],
        )
    except Exception as e:  # noqa: BLE001 — surface a readable error to the UI
        raise RuntimeError(f"OpenAI request failed: {e}") from e

    try:
        parsed = _coerce_json(response.output_text)
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
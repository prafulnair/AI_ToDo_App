# ai_client.py
import os, json
from datetime import datetime
from typing import Optional, Dict, Any

import google.generativeai as genai
from utils import safe_category
import dateparser
from datetime import datetime
import os

from dotenv import load_dotenv
load_dotenv()

TZ = os.getenv("LOCAL_TZ", "America/Toronto")
now_iso = datetime.now().isoformat()
_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")


def _get_resp_text(resp: Any) -> str:
    """Robustly extract text from a Gemini response object."""
    txt = (getattr(resp, "text", None) or "").strip()
    if txt:
        return txt
    # Fallback extraction path used by some SDK versions
    try:
        cand = resp.candidates[0]
        parts = getattr(cand, "content", cand).parts
        txt = "".join(getattr(p, "text", "") for p in parts).strip()
    except Exception:
        pass
    return txt


def _parse_due_iso(s: Optional[str]) -> Optional[datetime]:
    if not s:
        return None
    s = s.strip()
    # Handle trailing Z
    if s.endswith("Z"):
        s = s.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(s)
    except Exception:
        # As a secondary parse path, accept natural-ish ISO-like strings
        dt = dateparser.parse(s, settings={"PREFER_DATES_FROM": "future"})
        return dt


def categorize_and_enrich(text: str) -> Dict[str, Any]:
    """
    Calls Gemini to classify the task and infer priority/due date.
    Returns:
        {
          "category": "work|personal|health|career|errand",
          "priority": int (1..5),
          "due_dt": datetime | None
        }
    Raises:
        RuntimeError on API/config/JSON/validation errors.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set")

    genai.configure(api_key=api_key)

    model = genai.GenerativeModel(
        model_name=_MODEL,
        generation_config={
            "response_mime_type": "application/json",
            # Optionally bound response size:
            # "max_output_tokens": 512,
        },
    )

    allowed_categories = ["work", "personal", "health", "career", "errand"]

    user = f"""
You are an API. Return JSON only—no prose, no markdown.

Given a single to-do text, infer:
- category: one of ["work", "personal", "health", "career", "errand"]
- priority: integer 1..5 (1=lowest, 5=highest) based on urgency/importance implied by the text
- due_dt_iso: an ISO 8601 datetime string with timezone offset if a due time/date is clearly implied, else null
- rationale: very short reason (one sentence)

Context:
- current_time_iso: "{now_iso}"
- timezone: "{TZ}"

Rules for due_dt_iso:
- If only a time is given (e.g., "by 17:30"), assume it refers to today in the given timezone.
- If that time has already passed today, use the next calendar day at that time.
- If only a day is given (e.g., "tomorrow", "next Monday"), pick 09:00 local time unless a time is stated.
- Always return ISO 8601 with timezone offset (e.g., 2025-09-03T17:30:00-04:00).
- Never return a datetime in the past relative to current_time_iso; roll forward to the next valid occurrence instead.

Input text:
"{text.strip()}"

Return JSON with exactly this shape:
{{
  "category": "work|personal|health|career|errand",
  "priority": 1,
  "due_dt_iso": "2025-09-02T18:00:00-04:00" | null,
  "rationale": "string"
}}
"""

    resp = model.generate_content(user)

    # If safety blocks, surface it clearly
    pf = getattr(resp, "prompt_feedback", None)
    if pf and getattr(pf, "block_reason", None):
        raise RuntimeError(f"blocked_by_safety: {pf.block_reason}")

    text_out = _get_resp_text(resp)
    if not text_out:
        raise RuntimeError("empty_response_from_gemini")

    try:
        data = json.loads(text_out)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"invalid_json_from_gemini: {e}")

    # Basic schema validation
    for k in ("category", "priority", "due_dt_iso"):
        if k not in data:
            raise RuntimeError(f"missing_key_in_gemini_json: {k}")

    category = safe_category(str(data["category"]).lower())
    priority = int(data["priority"])
    if priority < 1 or priority > 5:
        raise RuntimeError("priority_out_of_range")

    due_dt = _parse_due_iso(data.get("due_dt_iso"))

    return {
        "category": category,
        "priority": priority,
        "due_dt": due_dt,
    }
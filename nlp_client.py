# nlp_client.py
import os, json
from typing import Any, Dict
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
TZ = os.getenv("LOCAL_TZ", "America/Toronto")
now_iso = datetime.now().isoformat()

def _get_resp_text(resp: Any) -> str:
    txt = (getattr(resp, "text", None) or "").strip()
    if txt:
        return txt
    try:
        cand = resp.candidates[0]
        parts = getattr(cand, "content", cand).parts
        txt = "".join(getattr(p, "text", "") for p in parts).strip()
    except Exception:
        txt = ""
    return txt


def parse_command_nlp(user_text: str, categories: list[str]) -> Dict[str, Any]:
    """
    Interpret natural-language input (like 'delete all work tasks today')
    into structured intent JSON.
    """

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set")
    genai.configure(api_key=api_key)

    model = genai.GenerativeModel(
        model_name=_MODEL,
        generation_config={"response_mime_type": "application/json"},
    )

    prompt = f"""
You are an API. Return JSON only — no prose.

Interpret the user request into one of these intents:
- "add_task" (if it's clearly adding a todo)
- "complete_all" (bulk complete tasks in a category)
- "delete_all" (bulk delete tasks in a category)
- "filter" (show tasks matching category and/or time)
- "unknown" (if unclear)

Context:
- current_time_iso: "{now_iso}"
- timezone: "{TZ}"
- available_categories: {categories}

Rules:
- "category" should be one of the available_categories if possible, else null.
- "time" can be "today", "tomorrow", "this_week", or null.
- Always return a rationale (1 sentence).

User input:
"{user_text}"

Return JSON exactly like this:
{{
  "intent": "add_task|complete_all|delete_all|filter|unknown",
  "category": "string|null",
  "time": "today|tomorrow|this_week|null",
  "rationale": "string"
}}
    """

    resp = model.generate_content(prompt)
    txt = _get_resp_text(resp)
    if not txt:
        raise RuntimeError("empty_response_from_gemini")

    try:
        data = json.loads(txt)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"invalid_json_from_gemini: {e}")

    # safety checks
    if "intent" not in data:
        data["intent"] = "unknown"
    if "category" not in data:
        data["category"] = None
    if "time" not in data:
        data["time"] = None
    if "rationale" not in data:
        data["rationale"] = ""

    return data


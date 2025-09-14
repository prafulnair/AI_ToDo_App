# ai_client.py
import os, json, re
from datetime import datetime
from typing import Optional, Dict, Any, Sequence, Tuple
import difflib

import google.generativeai as genai
import dateparser
from dotenv import load_dotenv

load_dotenv()

TZ = os.getenv("LOCAL_TZ", "America/Toronto")
now_iso = datetime.now().isoformat()
_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")


# -------------------------
# Helpers
# -------------------------

def _get_resp_text(resp: Any) -> str:
    """Robustly extract text from a Gemini response object."""
    txt = (getattr(resp, "text", None) or "").strip()
    if txt:
        return txt
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
    if s.endswith("Z"):
        s = s.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(s)
    except Exception:
        dt = dateparser.parse(s, settings={"PREFER_DATES_FROM": "future"})
        return dt


def _norm(s: str) -> str:
    """Lightweight normalization for category strings."""
    s = (s or "").strip().lower()
    s = re.sub(r"[_\-\s]+", " ", s)
    s = re.sub(r"[^\w\s]", "", s)
    return s


# A tiny alias/synonym map to nudge close matches
_SYNONYMS = {
    "exercise": "health",
    "fitness": "health",
    "gym": "health",
    "workout": "health",
    "wellness": "health",
    "meeting": "work",
    "office": "work",
    "job": "work",
    "career": "work",     # depending on how you want to split, map to "work"
    "errands": "errand",
    "shopping": "errand",
    "groceries": "errand",
    "school": "personal",
    "study": "personal",
}


def _closest_existing(
    proposed: str, existing: Sequence[str], threshold: float = 0.72
) -> Optional[str]:
    """
    Returns an existing category name if it's sufficiently similar to 'proposed'.
    Uses difflib ratio + synonym nudges.
    """
    if not proposed or not existing:
        return None

    p_norm = _norm(proposed)
    # Synonym direct map
    if p_norm in _SYNONYMS and _SYNONYMS[p_norm] in { _norm(e) for e in existing }:
        # Return the *actual* casing from existing
        target_norm = _SYNONYMS[p_norm]
        for e in existing:
            if _norm(e) == target_norm:
                return e

    # Fuzzy match
    best: Tuple[float, Optional[str]] = (0.0, None)
    for e in existing:
        ratio = difflib.SequenceMatcher(None, p_norm, _norm(e)).ratio()
        if ratio > best[0]:
            best = (ratio, e)
    if best[0] >= threshold:
        return best[1]
    return None


# -------------------------
# Gemini call
# -------------------------

def categorize_and_enrich(
    text: str,
    existing_categories: Optional[Sequence[str]] = None,
) -> Dict[str, Any]:
    """
    Calls Gemini to classify the task and infer priority/due date.
    Supports dynamic categories by passing in current existing categories.
    The model either selects one of the existing categories (if appropriate)
    or proposes a new category (<= 3 words). We then post-process to map
    similar proposals back to an existing category using fuzzy matching.

    Returns:
        {
          "category": str,           # final category (existing or new)
          "priority": int (1..5),
          "due_dt": datetime | None,
          "raw_category": str,       # model's proposed category (for debugging/telemetry)
          "used_existing": bool      # whether it mapped to an existing one
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
        },
    )

    existing_str = ", ".join(sorted(existing_categories or [])) or "(none)"

    user = f"""
You are an API. Return JSON only—no prose, no markdown.

Given a single to-do text, infer:
- category_proposed: a short category string (<= 3 words). You MUST first try to reuse an existing category if it's semantically close.
- used_existing: boolean — true if you reused an existing category name from the list, false if you introduced a new one.
- priority: integer 1..5 (1=lowest, 5=highest) based on urgency/importance implied by the text
- due_dt_iso: an ISO 8601 datetime string with timezone offset if a due time/date is clearly implied, else null
- rationale: very short reason (one sentence)

Context:
- current_time_iso: "{now_iso}"
- timezone: "{TZ}"
- existing_categories: [{existing_str}]

Rules:
- Prefer reusing an existing category if it's a reasonable semantic match (e.g., "exercise" ≈ "health").
- If only a time is given (e.g., "by 17:30"), assume it refers to today in the given timezone; if that time already passed today, roll to next day.
- If only a day is given (e.g., "tomorrow", "next Monday"), pick 09:00 local time unless a time is stated.
- Always return ISO 8601 with timezone offset (e.g., 2025-09-03T17:30:00-04:00).
- Never return a datetime in the past relative to current_time_iso.

Input text:
"{text.strip()}"

Return JSON with exactly this shape:
{{
  "category_proposed": "string",
  "used_existing": true,
  "priority": 1,
  "due_dt_iso": "2025-09-02T18:00:00-04:00" | null,
  "rationale": "string"
}}
"""

    resp = model.generate_content(user)

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

    for k in ("category_proposed", "used_existing", "priority", "due_dt_iso"):
        if k not in data:
            raise RuntimeError(f"missing_key_in_gemini_json: {k}")

    proposed_raw = str(data["category_proposed"]).strip()
    priority = int(data["priority"])
    if priority < 1 or priority > 5:
        raise RuntimeError("priority_out_of_range")

    due_dt = _parse_due_iso(data.get("due_dt_iso"))

    # Post-process: if the model proposed something new, try to map it to an existing category
    existing_categories = existing_categories or []
    final_category = proposed_raw
    used_existing = bool(data.get("used_existing"))

    if not used_existing:
        mapped = _closest_existing(proposed_raw, existing_categories)
        if mapped:
            final_category = mapped
            used_existing = True

    # Always normalize presentation minimally (strip whitespace)
    final_category = final_category.strip()

    return {
        "category": final_category,      # <-- final canonical category to persist
        "priority": priority,
        "due_dt": due_dt,
        "raw_category": proposed_raw,    # debugging/telemetry if you want it
        "used_existing": used_existing,
    }


# ai_client.py (add near bottom)

def parse_command_nlp(text: str, existing_categories: list[str]) -> dict:
    """
    Use Gemini to parse a natural language command.
    Returns structured JSON:
      {
        "action": "show|complete_all|delete_category",
        "category": "work|health|..." | null,
        "timeframe": "today|tomorrow|this_week|all" | null,
        "rationale": "string"
      }
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
You are an API. Return JSON only.

Task:
Parse this user command: "{text}"

Context:
- Existing categories: {existing_categories}
- Valid actions: ["show", "complete_all", "delete_category"]
- Valid timeframes: ["today", "tomorrow", "this_week", "all"]

Rules:
- If user says things like "finish all", "mark everything done" → action=complete_all.
- If user says "delete {{"some category"}}" → action=delete_category with category.
- If user says "show all ..." → action=show with filters.
- If category mentioned doesn’t match existing ones, still return it but mark rationale.
- If timeframe not specified, set to "all".
- Always include a rationale.

Return JSON:
{{
  "action": "show",
  "category": "work",
  "timeframe": "today",
  "rationale": "User asked to show today's work tasks"
}}
"""

    resp = model.generate_content(prompt)

    text_out = _get_resp_text(resp)
    if not text_out:
        raise RuntimeError("empty_response_from_gemini")

    try:
        data = json.loads(text_out)
    except Exception as e:
        raise RuntimeError(f"invalid_json_from_gemini: {e}")

    # enforce keys
    for k in ("action", "category", "timeframe", "rationale"):
        if k not in data:
            raise RuntimeError(f"missing_key_in_ai_response: {k}")

    return data


# -------------------------
# Summarization
# -------------------------

def summarize_tasks(tasks: list[dict], intent: dict) -> dict:
    """
    Summarize tasks into structured KPIs + highlights.
    Input: list of task dicts (id, text, category, status, priority, due_dt)
    Output: summary JSON + markdown narrative.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set")
    genai.configure(api_key=api_key)

    model = genai.GenerativeModel(
        model_name=_MODEL,
        generation_config={"response_mime_type": "application/json"},
    )

    # trim tasks to top 100 to avoid token bloat
    task_slice = tasks[:100]

    prompt = f"""
You are an API. Return JSON only — no prose.

Task:
Summarize the following todo tasks for the user.

Context:
- Intent: {json.dumps(intent, ensure_ascii=False)}
- Current time: {now_iso}
- Tasks (JSON list): {json.dumps(task_slice, default=str, ensure_ascii=False)}

Return JSON with exactly this shape:
{{
  "headline": "string",
  "kpis": {{ "open": 0, "completed": 0, "overdue": 0, "due_today": 0 }},
  "highlights": ["string", "string"],
  "by_category": [
    {{ "name": "Work", "open": 3, "done": 2 }}
  ],
  "urgent_ids": [1,2],
  "overdue_ids": [3],
  "markdown": "### Summary\\n- bullet points in markdown"
}}
"""

    resp = model.generate_content(prompt)
    text_out = _get_resp_text(resp)
    if not text_out:
        raise RuntimeError("empty_response_from_gemini")

    try:
        data = json.loads(text_out)
    except Exception as e:
        raise RuntimeError(f"invalid_json_from_gemini: {e}")

    return data


# Extend parser to include summarize
def parse_command_nlp(text: str, existing_categories: list[str]) -> dict:
    """
    Extended parser: now also supports 'summarize'.
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
You are an API. Return JSON only.

Parse this user command: "{text}"

Context:
- Existing categories: {existing_categories}
- Valid actions: ["show", "complete_all", "delete_category", "summarize"]
- Valid timeframes: ["today", "tomorrow", "this_week", "all"]

Rules:
- If user says "summarize" (e.g. "summarize today", "summarize social work this week") → action=summarize with category/timeframe.
- Otherwise rules are same as before.

Return JSON:
{{
  "action": "summarize",
  "category": "social",
  "timeframe": "today",
  "rationale": "User asked to summarize today's social tasks"
}}
"""

    resp = model.generate_content(prompt)
    text_out = _get_resp_text(resp)
    if not text_out:
        raise RuntimeError("empty_response_from_gemini")

    try:
        data = json.loads(text_out)
    except Exception as e:
        raise RuntimeError(f"invalid_json_from_gemini: {e}")

    for k in ("action", "category", "timeframe", "rationale"):
        if k not in data:
            raise RuntimeError(f"missing_key_in_ai_response: {k}")

    return data
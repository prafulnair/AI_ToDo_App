import os
import json
import re
from datetime import datetime
from typing import Optional, Dict, Any, Sequence
from collections import Counter

import google.generativeai as genai
import dateparser
from dotenv import load_dotenv

# Adjust import path if your layout differs. You used backend.similarity previously.
from backend.similarity import reconcile_category

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
    s = (s or "").strip().lower()
    s = re.sub(r"[_\-\s]+", " ", s)
    s = re.sub(r"[^\w\s]", "", s)
    return s


def _coarse_hint(text: str) -> Optional[str]:
    """
    Ultra-light hinting for obviously misclassified phrases.
    Keeps it minimal to avoid hardcoding everything.
    """
    t = _norm(text)
    shopping_markers = [
        "buy", "purchase", "order", "shop", "shopping", "grocery", "groceries",
        "supermarket", "market", "milk", "bread", "egg", "eggs", "vegetable",
        "vegetables", "veggies", "onion", "garlic", "ginger", "paste",
        "tomato", "chicken", "meat", "beef", "pork", "fish", "detergent",
        "toilet paper", "paper towels", "shampoo", "soap"
    ]
    if any(w in t for w in shopping_markers):
        return "Errand"
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
    Then reconciles with user's existing categories (or creates a canonical one
    from synonyms if allowed).
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set")

    genai.configure(api_key=api_key)

    model = genai.GenerativeModel(
        model_name=_MODEL,
        generation_config={"response_mime_type": "application/json"},
    )

    existing_categories = list(existing_categories or [])
    existing_str = ", ".join(sorted(existing_categories)) or "(none)"

    hint = _coarse_hint(text)  # e.g., "Errand" for grocery-like input

    user = f"""
You are an API. Return JSON only—no prose, no markdown.

Given a single to-do text, infer:
- category_proposed: a short category string (<= 3 words). Prefer obvious high-level families like Errand, Work, Health, Family, Personal, etc.
- used_existing: boolean — true if you reused a name from the existing list; false if you introduced a new one.
- priority: integer 1..5 (1=lowest, 5=highest) based on urgency/importance implied by the text.
- due_dt_iso: an ISO 8601 datetime string with timezone offset if a due time/date is clearly implied, else null.
- rationale: very short reason (one sentence).

Context:
- current_time_iso: "{now_iso}"
- timezone: "{TZ}"
- existing_categories: [{existing_str}]
- hint_category: "{hint or ''}"  # If non-empty, treat as a strong hint (e.g., groceries → Errand).

Rules:
- If the text clearly implies shopping or groceries, do NOT classify as Health; use Errand (or an existing close equivalent).
- If only a time is given (e.g., "by 17:30"), assume today local time; if that time passed, roll to next day.
- If only a day is given (e.g., "tomorrow", "next Monday"), default to 09:00 local time unless a time is stated.
- Always return ISO 8601 with timezone offset (e.g., 2025-09-03T17:30:00-04:00).
- Never return a datetime in the past relative to current_time_iso.
- Return JSON only, exactly as specified.

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

    # --- DEBUG LOGGING ---
    print("DEBUG — Raw category from Gemini:", proposed_raw)
    print("DEBUG — Existing categories:", existing_categories)

    # One clean reconciliation pass
    final_category, rec_dbg = reconcile_category(
        proposed=proposed_raw,
        existing=existing_categories,
        allow_create_from_synonym=None,  # use env default (on by default)
    )
    print("DEBUG — Reconcile info:", rec_dbg)

    # Coarse hint override (very targeted; only triggers on obvious grocery/shopping)
    if hint and _norm(hint) != _norm(final_category):
        # If the hint differs strongly from the final and Gemini proposed something like "health"
        # for a clear grocery-like text, prefer the hint.
        final_category = hint

    print("DEBUG — Final category chosen:", final_category)

    # used_existing is true if we ended up with an existing category name
    used_existing = _norm(final_category) in {_norm(c) for c in existing_categories}

    return {
        "category": final_category.strip(),
        "priority": priority,
        "due_dt": due_dt,
        "raw_category": proposed_raw,
        "used_existing": used_existing,
    }


# -------------------------
# NLP command parsing
# -------------------------

def parse_command_nlp(text: str, existing_categories: list[str]) -> dict:
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
- Valid actions: ["show", "complete_all", "delete_category", "summarize"]
- Valid timeframes: ["today", "tomorrow", "this_week", "all"]

Rules:
- If user says things like "finish all", "mark everything done" → action=complete_all.
- If user says "delete {{"some category"}}" → action=delete_category with category.
- If user says "show all ..." → action=show with filters.
- If timeframe not specified, set to "all".
- If user says "summarize" (e.g. "summarize today") → action=summarize.
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

    for k in ("action", "category", "timeframe", "rationale"):
        if k not in data:
            raise RuntimeError(f"missing_key_in_ai_response: {k}")

    return data


# -------------------------
# Summarization
# -------------------------

def _fallback_narrative(task_slice: list[dict], intent: dict) -> str:
    now = datetime.now()
    open_tasks = [t for t in task_slice if str(t.get("status", "open")) != "done"]
    completed = len([t for t in task_slice if str(t.get("status", "open")) == "done"])

    def _dt(t):
        v = t.get("due_dt")
        try:
            return datetime.fromisoformat(v) if isinstance(v, str) else v
        except Exception:
            return None

    due_today = [t for t in open_tasks if _dt(t) and _dt(t).date() == now.date()]
    overdue = [t for t in open_tasks if _dt(t) and _dt(t) < now]

    top_cat = ""
    if open_tasks:
        c = Counter([str(t.get("category", "")).strip() or "Uncategorized" for t in open_tasks])
        top_cat = c.most_common(1)[0][0]

    focus = ""
    pick = None
    if overdue:
        pick = overdue[0]
    elif due_today:
        pick = due_today[0]
    else:
        hp = [t for t in open_tasks if int(t.get("priority", 0)) >= 4]
        if hp:
            pick = hp[0]
    if pick:
        focus = f' Focus first on “{pick.get("text", "")}”.'

    tf = intent.get("timeframe") or "your list"
    bits = []
    if open_tasks:
        bits.append(f"{len(open_tasks)} open")
    if completed:
        bits.append(f"{completed} completed")
    if overdue:
        bits.append(f"{len(overdue)} overdue")
    if due_today:
        bits.append(f"{len(due_today)} due today")
    counters = ", ".join(bits) if bits else "nothing new"

    cat_line = f" {top_cat} has the most items." if top_cat else ""
    return f"For {tf}, you have {counters}.{cat_line}{focus}".strip()


def summarize_tasks(tasks: list[dict], intent: dict) -> dict:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set")
    genai.configure(api_key=api_key)

    model = genai.GenerativeModel(
        model_name=_MODEL,
        generation_config={"response_mime_type": "application/json"},
    )

    task_slice = tasks[:100]

    prompt = f"""
You are an API. Return JSON only.

Create a summary of these tasks. The "narrative" must be 1–3 sentences, plain text, friendly, concise, and specific.

Context:
- Intent: {json.dumps(intent, ensure_ascii=False)}
- Current time: {now_iso}
- Tasks: {json.dumps(task_slice, default=str, ensure_ascii=False)}

Return JSON:
{{
  "headline": "string",
  "kpis": {{ "open": 0, "completed": 0, "overdue": 0, "due_today": 0 }},
  "highlights": ["string"],
  "by_category": [{{ "name": "Work", "open": 3, "done": 2 }}],
  "urgent_ids": [1],
  "overdue_ids": [2],
  "markdown": "- bullet one\\n- bullet two",
  "narrative": "Plain conversational recap"
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

    nar = (data.get("narrative") or "").strip()
    md = (data.get("markdown") or "").strip()
    if not nar or "Structured summary" in nar or "Structured summary" in md or len(nar) < 20:
        data["narrative"] = _fallback_narrative(task_slice, intent)

    return data


# -------------------------
# Intent detection
# -------------------------

def filter_tasks_with_ai(tasks: list[dict], category_query: str) -> list[dict]:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set")
    genai.configure(api_key=api_key)

    model = genai.GenerativeModel(
        model_name=_MODEL,
        generation_config={"response_mime_type": "application/json"},
    )

    task_slice = tasks[:100]
    prompt = f"""
You are an API. Return JSON only.

From this list of tasks, select only those relevant to the user query.

Query: "{category_query}"

Tasks:
{json.dumps(task_slice, ensure_ascii=False)}

Return JSON:
{{ "keep_ids": [1, 3, 7] }}
"""
    resp = model.generate_content(prompt)
    text_out = _get_resp_text(resp)

    try:
        data = json.loads(text_out)
        keep_ids = set(data.get("keep_ids", []))
        return [t for t in tasks if t["id"] in keep_ids]
    except Exception:
        return tasks


def detect_intent(user_text: str) -> dict:
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

Decide if the user is trying to ADD A TASK or issue a COMMAND.

Definitions:
- "add_task": adding a new todo item (like "buy milk tomorrow").
- "command": control requests (like "show all tasks", "summarize today", "delete category work", "complete all").

Input: "{user_text}"

Return JSON:
{{
  "intent": "add_task" | "command",
  "rationale": "short one-sentence reason"
}}
"""

    resp = model.generate_content(prompt)
    text_out = _get_resp_text(resp)
    return json.loads(text_out)
import dateparser

VALID_CATS = {"work","personal","health","career","errand"}

def parse_due_dt(text: str):
    # Parses “by 18:00”, “tomorrow 7am”, “next monday”, etc.
    return dateparser.parse(text, settings={"PREFER_DATES_FROM": "future"})

def safe_category(cat: str) -> str:
    return cat if cat in VALID_CATS else "personal"

import re

def parse_command(s: str):
    s = (s or "").strip()
    if not s: return ("noop", None)

    if s.lower() in {"exit", "quit", "q"}:
        return ("exit", None)
    if s.lower() in {"help", "h", "?"}:
        return ("help", None)
    if s.lower() in {"show all", "list", "ls"}:
        return ("show_all", None)
    if s.lower().startswith("show immediate"):
        return ("show_immediate", None)

    m = re.match(r"show\s+(\w+)", s, re.I)
    if m:
        return ("show_category", m.group(1).lower())

    m = re.match(r"(done|complete)\s+(\d+)", s, re.I)
    if m:
        return ("done", int(m.group(2)))

    m = re.match(r"(del|delete|remove)\s+(\d+)", s, re.I)
    if m:
        return ("delete", int(m.group(2)))

    if s.lower().startswith("add "):
        return ("add", s[4:].strip())

    # fallback: treat as add (lets users type natural sentences)
    return ("add", s)
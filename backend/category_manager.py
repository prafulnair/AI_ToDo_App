# backend/category_manager.py
from __future__ import annotations

import os, json
from backend.db import CategoryAlias
import google.generativeai as genai

import re
from datetime import datetime
from typing import List, Sequence, Optional, Tuple
from collections import Counter

from sqlalchemy.orm import Session

from backend.db import TaskDB, CategoryMeta
from backend.embeddings import _load_encoder

Vector = Sequence[float]

# -----------------
# Small utilities
# -----------------

def _mean(vectors: List[Vector]) -> Optional[List[float]]:
    if not vectors:
        return None
    n = len(vectors)
    acc = [0.0] * len(vectors[0])
    for v in vectors:
        for i, x in enumerate(v):
            acc[i] += x
    return [x / n for x in acc]

def _cosine(a: Vector, b: Vector) -> float:
    return float(sum(x * y for x, y in zip(a, b)))

_WORD_RE = re.compile(r"[a-zA-Z][a-zA-Z\-\']{2,}")

STOPWORDS = {
    # tiny, purpose-built; we can expand later
    "the","and","for","with","this","that","your","you","our","are","was","were","will",
    "today","tomorrow","yesterday","tonight","asap","before","after","next","by","at","on",
    "to","from","of","in","a","an","is","be","am","pm","due","do","get","make","need","have",
    "pick","pickup","bring","put","set","send",
}

def _tokenize(text: str) -> List[str]:
    return [w.lower() for w in _WORD_RE.findall(text or "") if w]

def _top_keywords(texts: List[str], k: int = 6) -> List[str]:
    cnt = Counter()
    for t in texts:
        for w in _tokenize(t):
            if w not in STOPWORDS and not w.isdigit():
                cnt[w] += 1
    return [w for w, _ in cnt.most_common(k)]

# -----------------
# Public API
# -----------------

def update_meta(db: Session, session_id: str, category: str) -> Optional[CategoryMeta]:
    """
    Recompute and persist metadata for (session_id, category):
      - size
      - centroid (mean of task embeddings)
      - label_fit (mean cosine of label embedding vs task embeddings)
      - sample_texts (last 5 tasks)
      - top_keywords (simple token frequency)
    Gracefully degrades if encoder is unavailable.
    """
    if not category:
        return None

    # Fetch tasks in this category (most recent first)
    tasks: List[TaskDB] = (
        db.query(TaskDB)
        .filter(TaskDB.session_id == session_id, TaskDB.category == category)
        .order_by(TaskDB.created_at.desc())
        .all()
    )
    size = len(tasks)
    texts = [t.text.strip() for t in tasks if (t.text or "").strip()]

    # Ensure row exists
    meta: Optional[CategoryMeta] = (
        db.query(CategoryMeta)
        .filter(CategoryMeta.session_id == session_id, CategoryMeta.category == category)
        .first()
    )
    if meta is None:
        meta = CategoryMeta(session_id=session_id, category=category, size=0)
        db.add(meta)

    # Always update lightweight parts
    meta.size = size
    meta.set_sample_texts([t.text for t in tasks[:5]])
    meta.set_top_keywords(_top_keywords(texts))
    meta.updated_at = datetime.utcnow()

    # Try to compute centroid + label_fit if encoder exists
    encode, _ = _load_encoder()
    if encode is not None and texts:
        try:
            task_vecs = encode(texts)
            centroid = _mean(task_vecs)
            meta.set_centroid(centroid)

            # Label embedding & fit score
            label_vec = encode([category])[0]
            if task_vecs:
                meta.label_fit = float(sum(_cosine(label_vec, v) for v in task_vecs) / len(task_vecs))
            else:
                meta.label_fit = 0.0
        except Exception:
            # Leave vector fields as-is if encoding fails
            pass

    db.commit()
    db.refresh(meta)
    return meta

def _env_f(name: str, default: str) -> float:
    try:
        return float(os.getenv(name, default))
    except Exception:
        return float(default)

def _env_i(name: str, default: str) -> int:
    try:
        return int(os.getenv(name, default))
    except Exception:
        return int(default)

def _normalize_label(s: str) -> str:
    s = (s or "").strip()
    s = re.sub(r"\s+", " ", s)
    # cap at LABEL_RENAME_MAX_WORDS
    max_words = _env_i("LABEL_RENAME_MAX_WORDS", "3")
    parts = s.split(" ")
    s = " ".join(parts[:max_words])
    # nice casing
    return " ".join(w.capitalize() for w in s.split())

def _gemini_propose_label(meta: CategoryMeta, neighbors: list[str]) -> Optional[str]:
    """
    Ask the LLM for a compact umbrella label for this category card.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    genai.configure(api_key=api_key)
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    model = genai.GenerativeModel(model_name=model_name, generation_config={"response_mime_type": "application/json"})

    card = {
        "current_label": meta.category,
        "samples": meta.get_sample_texts(),
        "keywords": meta.get_top_keywords(),
        "entities": meta.get_top_entities(),
        "avoid_labels": neighbors[:10],  # keep short
    }

    prompt = f"""
You are an API. Return JSON only.

Goal: Propose ONE short umbrella label (<=3 words) that best covers these tasks as a single category.
Prefer a broader, everyday descriptor over a single-item noun.

Category card (JSON):
{json.dumps(card, ensure_ascii=False)}

Rules:
- Avoid labels that collide with "avoid_labels".
- Prefer umbrella phrasing; For example:("Household chores") over narrow ("Household waste"). This is just an example, don't take it literally. Just generalize and use umbreall phrasing.
- Keep <=3 words; Title Case.
- If the current label is already best, return it as-is.

Return JSON exactly:
{{ "label": "String" }}
"""
    try:
        resp = model.generate_content(prompt)
        txt = (getattr(resp, "text", None) or "").strip()
        if not txt:
            return None
        data = json.loads(txt)
        cand = _normalize_label(data.get("label", "")) or None
        return cand
    except Exception:
        return None

def _label_fit_for_candidate(encode, candidate: str, texts: list[str]) -> float:
    try:
        if not candidate or not texts:
            return 0.0
        label_vec = encode([candidate])[0]
        task_vecs = encode(texts)
        sims = [float(sum(a*b for a, b in zip(label_vec, v))) for v in task_vecs]
        return float(sum(sims) / len(sims)) if sims else 0.0
    except Exception:
        return 0.0

def consider_rename(db: Session, session_id: str, category: str) -> Optional[str]:
    """
    If the current label doesn't fit the cluster well, propose and apply an umbrella rename.
    Returns the new label if a rename happened; else None.
    """
    meta: Optional[CategoryMeta] = (
        db.query(CategoryMeta)
        .filter(CategoryMeta.session_id == session_id, CategoryMeta.category == category)
        .first()
    )
    if not meta:
        return None

    # Preconditions / thresholds
    min_size = _env_i("LABEL_RENAME_MIN_SIZE", "3")
    fit_tau = _env_f("LABEL_RENAME_FIT_TAU", "0.62")
    improve_delta = _env_f("LABEL_RENAME_IMPROVE_DELTA", "0.06")
    cooldown_hours = _env_i("LABEL_RENAME_COOLDOWN_HOURS", "24")

    if meta.size < min_size:
        return None

    # Cooldown
    if meta.last_renamed_at:
        dt = datetime.utcnow() - meta.last_renamed_at
        if dt.total_seconds() < cooldown_hours * 3600:
            return None

    # Build a richer text sample (up to ~30) for fit scoring
    tasks: List[TaskDB] = (
        db.query(TaskDB)
        .filter(TaskDB.session_id == session_id, TaskDB.category == category)
        .order_by(TaskDB.created_at.desc())
        .limit(30)
        .all()
    )
    texts = [t.text.strip() for t in tasks if (t.text or "").strip()]
    if not texts:
        return None

    # If current fit is already good, skip
    current_fit = float(meta.label_fit or 0.0)
    if current_fit >= fit_tau:
        return None

    # Neighbor labels to avoid (existing categories excluding self)
    neighbors = [
        r[0] for r in db.query(TaskDB.category)
        .filter(TaskDB.session_id == session_id)
        .distinct().all()
    ]
    neighbors = [n for n in neighbors if (n or "").strip() and n != category]

    # Ask LLM for an umbrella label
    candidate = _gemini_propose_label(meta, neighbors) or ""
    candidate = _normalize_label(candidate)
    if not candidate or candidate == category:
        return None

    # If candidate already exists in this session, prefer merging into it
    exists = (
        db.query(TaskDB)
        .filter(TaskDB.session_id == session_id, TaskDB.category == candidate)
        .limit(1)
        .first()
    )
    encode, _ = _load_encoder()

    # Score candidate fit improvement (if encoder is available)
    cand_fit = _label_fit_for_candidate(encode, candidate, texts) if encode else 1.0  # optimistic if no encoder

    # Accept only if improves enough and passes tau
    if cand_fit < fit_tau or cand_fit < current_fit + improve_delta:
        return None

    old = category
    new = candidate

    # Apply rename: update tasks
    db.query(TaskDB).filter(
        TaskDB.session_id == session_id,
        TaskDB.category == old
    ).update({"category": new})

    # Update / move meta row to new label
    # (We try to re-use the same row to keep history; ensure uniqueness)
    meta.label_history = meta.get_label_history() + [old]
    meta.category = new
    meta.last_renamed_at = datetime.utcnow()
    meta.updated_at = datetime.utcnow()
    db.add(meta)

    # Alias old -> new (so future inputs snap)
    alias = (
        db.query(CategoryAlias)
        .filter(CategoryAlias.session_id == session_id, CategoryAlias.alias == old)
        .first()
    )
    if alias:
        alias.canonical = new
        alias.updated_at = datetime.utcnow()
        db.add(alias)
    else:
        db.add(CategoryAlias(session_id=session_id, alias=old, canonical=new))

    db.commit()
    print(f"📝 RENAMED category '{old}' → '{new}' (fit {current_fit:.3f} → {cand_fit:.3f})")

    # Refresh meta after rename (centroid/fit will be recomputed by update_meta call next time)
    return new
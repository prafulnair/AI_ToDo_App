# backend/category_manager.py
from __future__ import annotations

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
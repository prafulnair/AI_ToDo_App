# backend/embeddings.py
import os
from functools import lru_cache
from typing import Dict, List, Optional, Sequence, Tuple

from sqlalchemy.orm import Session
from backend.db import TaskDB

Vector = Sequence[float]

@lru_cache(maxsize=1)
def _load_encoder():
    model_id = os.getenv("SENTENCE_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
    try:
        from sentence_transformers import SentenceTransformer  # type: ignore
        model = SentenceTransformer(model_id)

        def _encode(texts: Sequence[str]) -> List[List[float]]:
            return model.encode(list(texts), normalize_embeddings=True).tolist()
        return _encode, model_id
    except Exception:
        return None, None

def _cosine(a: Vector, b: Vector) -> float:
    return float(sum(x*y for x, y in zip(a, b)))

def _mean(vectors: List[Vector]) -> Optional[List[float]]:
    if not vectors:
        return None
    n = len(vectors)
    m = [0.0]*len(vectors[0])
    for v in vectors:
        for i, x in enumerate(v):
            m[i] += x
    return [x / n for x in m]

def build_category_centroids(db: Session, session_id: str) -> Dict[str, Vector]:
    """
    Returns {category: centroid_vector} for this session.
    Uses all tasks (open/done).
    """
    encode, _ = _load_encoder()
    if encode is None:
        return {}

    rows: List[TaskDB] = (
        db.query(TaskDB)
        .filter(TaskDB.session_id == session_id)
        .with_entities(TaskDB.category, TaskDB.text)
        .all()
    )

    by_cat: Dict[str, List[str]] = {}
    for cat, text in rows:
        text = (text or "").strip()
        if not text:
            continue
        by_cat.setdefault(cat or "Uncategorized", []).append(text)

    centroids: Dict[str, Vector] = {}
    for cat, texts in by_cat.items():
        vecs = encode(texts)
        c = _mean(vecs)
        if c is not None:
            centroids[cat] = c
    return centroids

def nearest_category_for_text(
    text: str,
    db: Session,
    session_id: str,
    tau: float = float(os.getenv("CLUSTER_ASSIGN_TAU", "0.72")),
) -> Optional[Tuple[str, float]]:
    """
    Given a new task text, returns (category, similarity) if above tau; else None.
    """
    encode, _ = _load_encoder()
    if encode is None:
        return None
    text = (text or "").strip()
    if not text:
        return None

    centroids = build_category_centroids(db, session_id)
    if not centroids:
        return None

    [v] = encode([text])
    best_cat, best_sim = None, -1.0
    for cat, cvec in centroids.items():
        sim = _cosine(v, cvec)
        if sim > best_sim:
            best_sim = sim
            best_cat = cat

    if best_cat is not None and best_sim >= tau:
        return best_cat, best_sim
    return None

def _task_text_for_search(t: Dict) -> str:
    # include category hint if present; short & robust
    cat = (t.get("category") or "").strip()
    txt = (t.get("text") or "").strip()
    return f"{txt} [label:{cat}]" if cat else txt

def filter_tasks_by_query(
    tasks: List[Dict],
    query: str,
    *,
    tau: float = float(os.getenv("SEARCH_TAU", "0.55")),
    topk: int = int(os.getenv("SEARCH_TOPK", "50")),
) -> List[Dict]:
    """
    Vector-search over tasks for a free-form query.
    Returns a filtered list (top-k above tau), preserving original task dicts.
    Falls back to returning `tasks` unchanged if encoder is unavailable.
    """
    encode, _ = _load_encoder()
    if encode is None:
        return tasks

    if not query or not tasks:
        return tasks

    qv = encode([query])[0]
    corpus = [_task_text_for_search(t) for t in tasks]
    tv = encode(corpus)

    scored: List[Tuple[float, Dict]] = []
    for vec, t in zip(tv, tasks):
        sim = _cosine(qv, vec)
        if sim >= tau:
            scored.append((sim, t))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [t for _, t in scored[:topk]] or tasks  # graceful fallback if nothing passes tau
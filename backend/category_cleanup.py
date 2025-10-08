# backend/category_cleanup.py
import os
from sqlalchemy import func
from sqlalchemy.orm import Session
from backend.db import TaskDB
from backend.embeddings import _load_encoder, _cosine, build_category_centroids


def _env_float(name: str, default: str) -> float:
    try:
        return float(os.getenv(name, default))
    except Exception:
        return float(default)


def cleanup_categories(db: Session, session_id: str):
    """
    MERGE ONLY (no hiding).
    Merge semantically duplicate categories by centroid similarity.
    """
    encode, _ = _load_encoder()
    if encode is None:
        print("⚠️  Cleanup skipped: encoder unavailable.")
        return

    tau_merge = _env_float("MERGE_TAU", "0.74")  # slightly more permissive

    # Build centroids and counts
    rows = (
        db.query(
            TaskDB.category,
            func.count().label("n"),
        )
        .filter(TaskDB.session_id == session_id)
        .group_by(TaskDB.category)
        .all()
    )
    if not rows:
        return

    counts = {r[0]: int(r[1]) for r in rows}
    centroids = build_category_centroids(db, session_id)
    cats = list(centroids.keys())
    if len(cats) < 2:
        return

    # Union-find over pairwise sims
    parents = {c: c for c in cats}

    def find(x: str) -> str:
        while parents[x] != x:
            parents[x] = parents[parents[x]]
            x = parents[x]
        return x

    def union(a: str, b: str):
        ra, rb = find(a), find(b)
        if ra != rb:
            parents[rb] = ra

    for i, c1 in enumerate(cats):
        for c2 in cats[i + 1 :]:
            sim = _cosine(centroids[c1], centroids[c2])
            if sim >= tau_merge:
                union(c1, c2)

    comps = {}
    for c in cats:
        root = find(c)
        comps.setdefault(root, set()).add(c)

    def _score_label(name: str) -> tuple:
        # Prefer more populated labels, then non-underscore, then longer / nicer looking
        return (
            counts.get(name, 0),
            0 if not name.startswith("_") else -1,
            len(name),
            name.title(),
        )

    changed = False
    for root, group in comps.items():
        if len(group) <= 1:
            continue
        canonical = max(group, key=_score_label)
        for old in group:
            if old == canonical:
                continue
            db.query(TaskDB).filter(
                TaskDB.session_id == session_id,
                TaskDB.category == old,
            ).update({"category": canonical})
            print(f"🔄  Merged '{old}' → '{canonical}' (sim≥{tau_merge})")
            changed = True

    if changed:
        db.commit()

    print(f"✅ Cleanup (merge-only) done | merged_components={sum(1 for g in comps.values() if len(g)>1)}")
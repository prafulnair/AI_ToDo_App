# backend/similarity.py
"""
Category reconciliation utilities.

Purpose
-------
Given a model-proposed category (free-form) and a list of existing categories,
pick the best existing category when it makes sense — otherwise keep the
proposed one (allowing "organic" categories).

Strategy (in order)
-------------------
1) Exact match (case/spacing/punct normalized)
2) Synonym map (configurable)
3) Semantic similarity via SentenceTransformers (optional, lazy, configurable)
4) Fuzzy string similarity (difflib)

If none exceed thresholds, we keep the proposed category to preserve organic growth.

Environment variables
---------------------
SENTENCE_MODEL_NAME   : HuggingFace model id (default: "sentence-transformers/all-MiniLM-L6-v2")
SIMILARITY_MODEL_MIN  : Float [0..1], minimum cosine similarity to accept (default: 0.58)
SIMILARITY_FUZZY_MIN  : Float [0..1], minimum difflib ratio to accept (default: 0.88)

Dependencies (optional)
-----------------------
pip install sentence-transformers
"""

from __future__ import annotations

import os
import re
import difflib
from functools import lru_cache
from typing import Dict, Mapping, Optional, Sequence, Tuple, Any

Vector = Sequence[float]


# ---------------------------
# Normalization helpers
# ---------------------------

def _norm(s: str) -> str:
    """Normalize category strings for comparison."""
    s = (s or "").strip().lower()
    s = re.sub(r"[_\-\s]+", " ", s)        # collapse whitespace/underscores/dashes
    s = re.sub(r"[^\w\s]", "", s)          # strip punctuation
    return s


def _original_case_lookup(existing: Sequence[str]) -> Dict[str, str]:
    """
    Map normalized -> original casing for existing categories.
    If duplicates normalize identically, first wins (order stable).
    """
    out: Dict[str, str] = {}
    for e in existing:
        k = _norm(e)
        if k not in out:
            out[k] = e
    return out


# ---------------------------
# Optional embedding backend
# ---------------------------

@lru_cache(maxsize=1)
def _load_encoder():
    """
    Lazy-load SentenceTransformer. Returns (encode_fn, model_name) or (None, None)
    if not available.
    """
    model_id = os.getenv("SENTENCE_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer(model_id)

        def _encode(texts: Sequence[str]) -> Any:
            # Normalize inputs early for better matching consistency
            return model.encode(list(texts), normalize_embeddings=True)  # unit-length vectors

        return _encode, model_id
    except Exception:
        return None, None


def _cosine(a: Vector, b: Vector) -> float:
    # Vectors are already normalized by encode(), so cosine == dot
    return float(sum(x * y for x, y in zip(a, b)))


# ---------------------------
# Default synonyms (extendable)
# ---------------------------

_DEFAULT_SYNONYMS: Mapping[str, str] = {
    # left (proposed) -> right (canonical family)
    "exercise": "health",
    "fitness": "health",
    "gym": "health",
    "workout": "health",
    "wellness": "health",
    "meeting": "work",
    "office": "work",
    "job": "work",
    "career": "work",
    "errands": "errand",
    "shopping": "errand",
    "groceries": "errand",
    "grocery": "errand",
    "school": "personal",
    "study": "personal",
}


# ---------------------------
# Public API
# ---------------------------

def reconcile_category(
    proposed: str,
    existing: Sequence[str],
    *,
    synonyms: Optional[Mapping[str, str]] = None,
    threshold_model: Optional[float] = None,
    threshold_fuzzy: Optional[float] = None,
) -> Tuple[str, Dict[str, Any]]:
    """
    Reconcile a model-proposed category with existing categories.

    Parameters
    ----------
    proposed : str
        Free-form category proposed by an upstream model.
    existing : Sequence[str]
        Existing category names (user's current set). Order is preserved.
    synonyms : Mapping[str, str], optional
        Extra synonym map (normalized keys/values). Merged on top of defaults.
    threshold_model : float, optional
        Min cosine similarity to accept a semantic match. Defaults from env
        SIMILARITY_MODEL_MIN or 0.58.
    threshold_fuzzy : float, optional
        Min difflib ratio to accept fuzzy match. Defaults from env
        SIMILARITY_FUZZY_MIN or 0.88.

    Returns
    -------
    (final_category, debug)
        final_category : str
            Either one of `existing` (original casing) or the original `proposed`.
        debug : dict
            Diagnostics: chosen method, scores, thresholds, model name, etc.

    Notes
    -----
    - We only map to an existing category if confidence is high enough.
      Otherwise we keep `proposed` to allow organic category creation.
    - If `proposed` already matches an existing (after normalization), we return
      that exact existing (preserving original casing).
    """
    dbg: Dict[str, Any] = {
        "proposed": proposed,
        "existing": list(existing),
        "method": None,
        "scores": {},
        "thresholds": {},
        "model": {},
    }

    if not proposed:
        dbg["method"] = "noop-empty-proposed"
        return proposed, dbg

    if not existing:
        dbg["method"] = "noop-no-existing"
        return proposed.strip(), dbg

    # Thresholds (env or defaults)
    threshold_model = (
        threshold_model
        if threshold_model is not None
        else float(os.getenv("SIMILARITY_MODEL_MIN", "0.58"))
    )
    threshold_fuzzy = (
        threshold_fuzzy
        if threshold_fuzzy is not None
        else float(os.getenv("SIMILARITY_FUZZY_MIN", "0.88"))
    )
    dbg["thresholds"] = {
        "model": threshold_model,
        "fuzzy": threshold_fuzzy,
    }

    norm_prop = _norm(proposed)
    canon_map = _original_case_lookup(existing)
    existing_norm = list(canon_map.keys())

    # 1) Exact normalized match → return original casing
    if norm_prop in canon_map:
        final_cat = canon_map[norm_prop]
        dbg["method"] = "exact"
        return final_cat, dbg

    # 2) Synonym map
    syn = dict(_DEFAULT_SYNONYMS)
    if synonyms:
        # user-supplied synonyms take precedence
        for k, v in synonyms.items():
            syn[_norm(k)] = _norm(v)
    if norm_prop in syn:
        mapped_norm = syn[norm_prop]
        # Only map if the canonical synonym already exists in user's set
        if mapped_norm in existing_norm:
            final_cat = canon_map[mapped_norm]
            dbg["method"] = "synonym"
            dbg["scores"]["synonym"] = f"{norm_prop}→{mapped_norm}"
            return final_cat, dbg

    # 3) Semantic similarity (SentenceTransformers) — optional
    encode, model_name = _load_encoder()
    if encode is not None:
        try:
            prop_vec = encode([norm_prop])[0]
            ex_vecs = encode(existing_norm)
            best_score = -1.0
            best_idx = -1
            for idx, vec in enumerate(ex_vecs):
                score = _cosine(prop_vec, vec)
                if score > best_score:
                    best_score = score
                    best_idx = idx
            dbg["scores"]["model_best"] = float(best_score)
            dbg["model"]["name"] = model_name

            if best_score >= threshold_model and 0 <= best_idx < len(existing_norm):
                chosen_norm = existing_norm[best_idx]
                final_cat = canon_map[chosen_norm]
                dbg["method"] = "model"
                return final_cat, dbg
        except Exception as exc:
            # Silent degrade to fuzzy; record for debugging.
            dbg["model"]["error"] = str(exc)

    # 4) Fuzzy fallback
    best_ratio = 0.0
    best_key = None
    for k in existing_norm:
        ratio = difflib.SequenceMatcher(None, norm_prop, k).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_key = k
    dbg["scores"]["fuzzy_best"] = float(best_ratio)

    if best_key and best_ratio >= threshold_fuzzy:
        final_cat = canon_map[best_key]
        dbg["method"] = "fuzzy"
        return final_cat, dbg

    # 5) No confident mapping → keep proposed (organic)
    dbg["method"] = "keep_proposed"
    return proposed.strip(), dbg
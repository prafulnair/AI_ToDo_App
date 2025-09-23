"""
Category reconciliation (organic; no synonyms, no static mappings).

Goal
----
Let the LLM propose free-form categories. Only merge into an *existing*
category when there's strong evidence they are the same label:
1) Exact match after normalization (case/spacing/punct, simple plural handling)
2) Semantic similarity via SentenceTransformers (optional, lazy, cached)
3) Fuzzy string similarity (difflib) as a last resort

If nothing is convincing, KEEP the proposed category (allow "organic" growth).

Environment (optional)
----------------------
SENTENCE_MODEL_NAME     : HF model id (default: "sentence-transformers/all-MiniLM-L6-v2")
SIMILARITY_MODEL_MIN    : Float [0..1], cosine threshold (default: 0.58)
SIMILARITY_FUZZY_MIN    : Float [0..1], difflib ratio threshold (default: 0.88)

Install (optional)
------------------
pip install sentence-transformers
"""

from __future__ import annotations

import os
import re
import difflib
from functools import lru_cache
from typing import Any, Dict, Sequence, Tuple

Vector = Sequence[float]


# ---------------------------
# Normalization helpers
# ---------------------------

def _norm(s: str) -> str:
    """Normalize category strings for comparison (case/spacing/punct)."""
    s = (s or "").strip().lower()
    s = re.sub(r"[^\w\s]+", " ", s)   # convert punctuation/separators to spaces
    s = re.sub(r"[_\s]+", " ", s)     # collapse underscores/whitespace
    return s.strip()


def _singularize(word: str) -> str:
    """Ultra-light singularization for common plurals."""
    if word.endswith("ies") and len(word) > 3:
        return word[:-3] + "y"
    if word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return word


def _norm_with_plural(s: str) -> str:
    """Normalize and singularize simple plurals."""
    base = _norm(s)
    return _singularize(base)


def _original_case_lookup(existing: Sequence[str]) -> Dict[str, str]:
    """Map normalized -> original casing for existing categories (stable first-wins)."""
    out: Dict[str, str] = {}
    for e in existing:
        k = _norm_with_plural(e)
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
        from sentence_transformers import SentenceTransformer  # type: ignore
        model = SentenceTransformer(model_id)

        def _encode(texts: Sequence[str]) -> Any:
            # Normalize embeddings so cosine == dot
            return model.encode(list(texts), normalize_embeddings=True)

        return _encode, model_id
    except Exception:
        return None, None


@lru_cache(maxsize=64)
def _encode_existing_tuple(model_name: str, existing_norm: Tuple[str, ...]):
    """Cache embeddings for a fixed set of existing categories."""
    encode, _ = _load_encoder()
    if encode is None:
        return None
    return encode(existing_norm)


def _cosine(a: Vector, b: Vector) -> float:
    return float(sum(x * y for x, y in zip(a, b)))


# ---------------------------
# Public API
# ---------------------------

def reconcile_category(
    proposed: str,
    existing: Sequence[str],
    *,
    threshold_model: float | None = None,
    threshold_fuzzy: float | None = None,
) -> Tuple[str, Dict[str, Any]]:
    """
    Reconcile a model-proposed category with the user's existing set.

    Returns
    -------
    (final_category, debug)
        final_category : str
            Either an existing category (original casing) or the original proposed value.
        debug : dict
            Diagnostics with method, scores, thresholds, model info.
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
    dbg["thresholds"] = {"model": threshold_model, "fuzzy": threshold_fuzzy}

    norm_prop = _norm_with_plural(proposed)
    canon_map = _original_case_lookup(existing)
    existing_norm = list(canon_map.keys())

    # 1) Exact normalized match
    if norm_prop in canon_map:
        final_cat = canon_map[norm_prop]
        dbg["method"] = "exact"
        return final_cat, dbg

    # 2) Semantic similarity (if available)
    encode, model_name = _load_encoder()
    if encode is not None:
        try:
            ex_vecs = _encode_existing_tuple(model_name, tuple(existing_norm))
            if ex_vecs is not None:
                prop_vec = encode([norm_prop])[0]
                best_score, best_idx = -1.0, -1
                for idx, vec in enumerate(ex_vecs):
                    score = _cosine(prop_vec, vec)
                    if score > best_score:
                        best_score, best_idx = score, idx
                dbg["scores"]["model_best"] = float(best_score)
                dbg["model"]["name"] = model_name
                if best_score >= threshold_model and 0 <= best_idx < len(existing_norm):
                    chosen_norm = existing_norm[best_idx]
                    final_cat = canon_map[chosen_norm]
                    dbg["method"] = "model"
                    return final_cat, dbg
        except Exception as exc:
            dbg["model"]["error"] = str(exc)

    # 3) Fuzzy fallback
    best_ratio, best_key = 0.0, None
    for k in existing_norm:
        ratio = difflib.SequenceMatcher(None, norm_prop, k).ratio()
        if ratio > best_ratio:
            best_ratio, best_key = ratio, k
    dbg["scores"]["fuzzy_best"] = float(best_ratio)
    if best_key and best_ratio >= threshold_fuzzy:
        final_cat = canon_map[best_key]
        dbg["method"] = "fuzzy"
        return final_cat, dbg

    # 4) Keep proposed (organic)
    dbg["method"] = "keep_proposed"
    return proposed.strip(), dbg
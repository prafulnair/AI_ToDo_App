import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from backend import similarity


def test_norm_converts_separators_to_spaces():
    assert similarity._norm("Groceries/Errands") == "groceries errands"


def test_reconcile_category_with_stubbed_encoder(monkeypatch):
    """Reconciliation should fall back to the stubbed model and reuse existing."""

    def fake_load_encoder():
        def fake_encode(texts):
            vocab = {"errands": 0, "groceries": 1, "meat": 2}
            vectors = []
            for text in texts:
                tokens = text.split()
                normalized_tokens = [
                    "errands" if token == "shopping" else token for token in tokens
                ]
                vec = [0.0, 0.0, 0.0]
                for token in normalized_tokens:
                    idx = vocab.get(token)
                    if idx is not None:
                        vec[idx] += 1.0
                vectors.append(vec)
            return vectors

        return fake_encode, "stub-model"

    # Clear the real cache and swap in the stub encoder
    similarity._load_encoder.cache_clear()
    monkeypatch.setattr(similarity, "_load_encoder", fake_load_encoder)

    final, dbg = similarity.reconcile_category(
        "meat shopping", ["Groceries/Errands"]
    )

    assert final == "Groceries/Errands"
    assert dbg["method"] == "model"
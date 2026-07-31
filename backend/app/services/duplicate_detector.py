"""Duplicate / copyright detection using ChromaDB vector search.

Queries the ChromaDB collection for the nearest CLIP embeddings and
returns the best match above the configured similarity threshold.
"""

from __future__ import annotations

from collections.abc import Sequence

from app.services.chroma_store import query_similar


def find_duplicate(
    new_embedding: Sequence[float],
    threshold: float | None = None,
) -> dict:
    """Return the best matching record above the similarity threshold, if any.

    Delegates the actual vector search to ChromaDB (ANN with cosine distance).
    """
    matches = query_similar(
        list(new_embedding),
        n_results=5,
        threshold=threshold,
    )

    if matches:
        best = matches[0]  # Already sorted by distance (closest first)
        return {
            "is_duplicate": True,
            "matched_user": best["uploaded_by"],
            "matched_filename": best["filename"],
            "similarity": best["similarity"],
            "uploaded_at": best["uploaded_at"],
        }

    return {"is_duplicate": False, "similarity": 0.0}

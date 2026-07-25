"""Cosine-similarity duplicate / copyright matching over stored CLIP embeddings."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np

from app.config import settings
from app.models import MediaHistory


def calculate_cosine_similarity(vec1: Sequence[float], vec2: Sequence[float]) -> float:
    a = np.asarray(vec1, dtype=np.float32).flatten()
    b = np.asarray(vec2, dtype=np.float32).flatten()
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0.0:
        return 0.0
    return float(np.dot(a, b) / denom)


def find_duplicate(
    new_embedding: Sequence[float],
    stored_records: Sequence[MediaHistory],
    threshold: float | None = None,
) -> dict:
    """Return the best matching record above the similarity threshold, if any."""
    threshold = settings.duplicate_threshold if threshold is None else threshold

    best_record: MediaHistory | None = None
    best_similarity = 0.0
    for record in stored_records:
        if not record.embedding:
            continue
        similarity = calculate_cosine_similarity(new_embedding, record.embedding)
        if similarity > best_similarity:
            best_similarity = similarity
            best_record = record

    if best_record is not None and best_similarity >= threshold:
        return {
            "is_duplicate": True,
            "matched_user": best_record.uploaded_by,
            "matched_filename": best_record.filename,
            "similarity": round(best_similarity, 4),
            "uploaded_at": best_record.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }
    return {"is_duplicate": False, "similarity": round(best_similarity, 4)}

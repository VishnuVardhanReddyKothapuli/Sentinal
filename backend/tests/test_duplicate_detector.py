import datetime

from app.models import MediaHistory
from app.services.duplicate_detector import calculate_cosine_similarity, find_duplicate


def _record(embedding, user="alice", filename="a.png"):
    return MediaHistory(
        filename=filename,
        file_hash="x",
        nsfw_status="SFW",
        nsfw_score=0.1,
        is_nsfw=False,
        embedding=embedding,
        uploaded_by=user,
        created_at=datetime.datetime(2024, 1, 1, 12, 0, 0),
    )


def test_cosine_identical():
    assert calculate_cosine_similarity([1, 0, 0], [1, 0, 0]) == 1.0


def test_cosine_orthogonal():
    assert calculate_cosine_similarity([1, 0], [0, 1]) == 0.0


def test_cosine_zero_vector():
    assert calculate_cosine_similarity([0, 0], [1, 1]) == 0.0


def test_find_duplicate_hit():
    stored = [_record([1.0, 0.0, 0.0], user="bob")]
    result = find_duplicate([0.99, 0.01, 0.0], stored, threshold=0.92)
    assert result["is_duplicate"] is True
    assert result["matched_user"] == "bob"


def test_find_duplicate_miss():
    stored = [_record([1.0, 0.0, 0.0])]
    result = find_duplicate([0.0, 1.0, 0.0], stored, threshold=0.92)
    assert result["is_duplicate"] is False

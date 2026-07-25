import io

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.config import settings
from app.database import SessionLocal, init_db
from app.main import app
from app.models import MediaHistory
from app.services import classifier


@pytest.fixture(autouse=True)
def _setup(monkeypatch, tmp_path):
    # Use a temporary SQLite DB and stub the ML models so tests are deterministic
    # and do not download multi-GB weights.
    init_db()
    db = SessionLocal()
    db.query(MediaHistory).delete()
    db.commit()
    db.close()

    monkeypatch.setattr(classifier, "classify_media", lambda image: (0.9, 1))
    monkeypatch.setattr(
        classifier, "generate_embedding", lambda image: [1.0, 0.0, 0.0]
    )
    yield


def _png_bytes(color=(255, 0, 0)):
    buf = io.BytesIO()
    Image.new("RGB", (8, 8), color).save(buf, format="PNG")
    return buf.getvalue()


def test_health():
    client = TestClient(app)
    assert client.get("/health").json() == {"status": "ok"}


def test_moderate_flags_nsfw():
    client = TestClient(app)
    resp = client.post(
        "/api/moderate",
        files={"file": ("a.png", _png_bytes(), "image/png")},
        data={"uploaded_by": "alice", "deep_match": "false"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["is_nsfw"] is True
    assert body["nsfw_status"] == "NSFW"
    assert body["nsfw_score"] >= settings.nsfw_threshold


def test_deep_match_detects_duplicate():
    client = TestClient(app)
    files = {"file": ("a.png", _png_bytes(), "image/png")}
    first = client.post(
        "/api/moderate", files=files, data={"uploaded_by": "alice", "deep_match": "true"}
    )
    assert first.json()["duplicate"]["is_duplicate"] is False

    files2 = {"file": ("b.png", _png_bytes((0, 255, 0)), "image/png")}
    second = client.post(
        "/api/moderate", files=files2, data={"uploaded_by": "bob", "deep_match": "true"}
    )
    dup = second.json()["duplicate"]
    assert dup["is_duplicate"] is True
    assert dup["matched_user"] == "alice"


def test_history():
    client = TestClient(app)
    client.post(
        "/api/moderate",
        files={"file": ("a.png", _png_bytes(), "image/png")},
        data={"uploaded_by": "alice"},
    )
    resp = client.get("/api/history")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1

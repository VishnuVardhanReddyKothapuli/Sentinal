# Backend — Content Moderation & Copyright Engine

FastAPI service that handles image/GIF NSFW classification and CLIP-based
duplicate/copyright detection. Also serves the static frontend UI.

## Prerequisites

- Python 3.10+
- (Optional) MySQL — SQLite is used by default for zero-setup dev.

## Setup

```bash
# 1. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env            # edit if needed

# 4. Start the server
uvicorn app.main:app --reload --port 8000
```

Open **http://localhost:8000** — frontend + API, all in one.

Interactive API docs: http://localhost:8000/docs

## API

| Method | Path            | Description                                              |
|--------|-----------------|----------------------------------------------------------|
| `GET`  | `/`             | Serves the frontend (static HTML).                       |
| `GET`  | `/health`       | Liveness probe.                                          |
| `POST` | `/api/moderate` | Multipart upload: `file`, `uploaded_by`, `deep_match`.   |
| `GET`  | `/api/history`  | Recent analyzed uploads.                                 |

`POST /api/moderate` returns the NSFW status/score, frames analyzed (for GIFs),
and a `duplicate` block. When `deep_match=true`, a 512-dim CLIP embedding is
generated and compared (cosine similarity) against stored records; matches above
`DUPLICATE_THRESHOLD` (default 0.92) report the original uploader.

## Models

- **NSFW:** `Falconsai/nsfw_image_detection` (Hugging Face image-classification)
- **Embeddings:** `openai/clip-vit-base-patch32`

Models download lazily on first request. The first call may take a while.

## Tests

```bash
pip install -r requirements-dev.txt
pytest          # ML models are stubbed; no weights downloaded
ruff check .
```
# Sentinal
# Sentinal

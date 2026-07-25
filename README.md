# SentiNal — NSFW & Copyright Moderator

AI-powered content moderation tool. Upload an image or GIF — the system flags
explicit (NSFW) content and detects if the same file was already posted by
someone else.

```
                                          Hugging Face
┌──────────────┐   multipart POST   ┌──────────────┐    models     ┌───────────────────────┐
│  Static HTML │ ─────────────────▶ │   FastAPI    │ ────────────▶ │  Falconsai NSFW       │
│  (vanilla)   │ ◀───────────────── │   backend    │ ◀──────────── │  CLIP ViT-B/32        │
└──────────────┘    JSON result     └──────┬───────┘               └───────────────────────┘
                                           │ SQLAlchemy
                                           ▼
                                   ┌───────────────┐
                                   │ SQLite / MySQL│  embeddings + history
                                   └───────────────┘
```

## Stack

| Layer       | Tech                                   | Notes                                              |
|-------------|----------------------------------------|-----------------------------------------------------|
| Frontend    | Single HTML file (vanilla CSS + JS)    | No build step, no npm. Served by FastAPI.            |
| Backend     | Python, FastAPI, SQLAlchemy 2           | `/api/moderate`, `/api/history`                      |
| NSFW model  | `Falconsai/nsfw_image_detection`       | GIFs sampled into keyframes; max score aggregated.   |
| Embeddings  | `openai/clip-vit-base-patch32`         | 512-dim CLIP vector per image.                       |
| Database    | SQLite (default) / MySQL (production)  | Stores upload history + JSON embeddings.             |

Duplicate detection compares the incoming CLIP embedding against stored records
using cosine similarity; matches above `0.92` report the original uploader.

## Prerequisites

- **Python 3.10+** — that's it. No Node.js, no npm, no Docker required.

## Quick Start

```bash
# 1. Clone and enter the project
git clone <repo-url>
cd nsfw-copyright-moderator/backend

# 2. Create a virtual environment
python -m venv venv

# 3. Activate it
# Linux / macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Set up environment config
cp .env.example .env        # edit .env if needed

# 6. Start the server
uvicorn app.main:app --reload --port 8000
```

Open **http://localhost:8000** — the frontend loads automatically.

> **Note:** The first analysis downloads ML model weights (~500 MB). This may
> take a minute. Subsequent requests are fast.

## Environment Variables

All config lives in `backend/.env`. Defaults work out of the box for local dev:

| Variable             | Default                              | Description                        |
|----------------------|--------------------------------------|------------------------------------|
| `DATABASE_URL`       | `sqlite:///./moderation.db`          | Database connection string         |
| `NSFW_MODEL_ID`      | `Falconsai/nsfw_image_detection`     | Hugging Face NSFW classifier       |
| `CLIP_MODEL_ID`      | `openai/clip-vit-base-patch32`       | CLIP model for embeddings          |
| `NSFW_THRESHOLD`     | `0.5`                                | Score above = flagged NSFW         |
| `DUPLICATE_THRESHOLD`| `0.92`                               | Cosine similarity match threshold  |
| `MAX_GIF_FRAMES`     | `16`                                 | Max keyframes sampled from GIFs    |
| `CORS_ORIGINS`       | `*`                                  | Allowed origins                    |
| `LAZY_LOAD_MODELS`   | `true`                               | Load ML models on first request    |

## API Endpoints

| Method | Path            | Description                                            |
|--------|-----------------|--------------------------------------------------------|
| `GET`  | `/`             | Serves the frontend UI                                 |
| `GET`  | `/health`       | Health check                                           |
| `POST` | `/api/moderate` | Upload file for analysis (multipart form)              |
| `GET`  | `/api/history`  | Recent uploads list                                    |
| `GET`  | `/docs`         | Interactive Swagger API docs                           |

### `POST /api/moderate`

Form fields:
- `file` — image or GIF (required)
- `uploaded_by` — username string (default: `anonymous`)
- `deep_match` — `true` to enable copyright/duplicate detection (default: `false`)

## Features

- **Quick Scan** — NSFW classification only (fast)
- **Deep Match** — NSFW + CLIP embedding comparison for duplicate/copyright detection
- Drag-and-drop or click-to-upload
- NSFW confidence score bar
- Duplicate match alert with original uploader info
- Upload history table

## Project Layout

```
nsfw-copyright-moderator/
├── README.md                  ← you are here
├── backend/
│   ├── app/
│   │   ├── main.py            ← FastAPI app + serves frontend
│   │   ├── config.py          ← settings from .env
│   │   ├── database.py        ← SQLAlchemy setup
│   │   ├── models.py          ← DB models
│   │   ├── schemas.py         ← Pydantic schemas
│   │   ├── routers/
│   │   │   └── moderate.py    ← /api/moderate, /api/history
│   │   └── services/
│   │       ├── classifier.py  ← NSFW model + CLIP embeddings
│   │       └── duplicate_detector.py
│   ├── tests/
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
└── frontend/
    └── index.html             ← entire UI (HTML + CSS + JS)
```

## Tests

```bash
cd backend
pip install -r requirements-dev.txt
pytest          # ML models are stubbed; no weights downloaded
ruff check .
```
# Sentinal
# Sentinal

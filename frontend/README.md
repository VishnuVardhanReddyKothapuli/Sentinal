# Frontend — SentiNal UI

A single static HTML file with inline CSS and JavaScript. No build tools, no
dependencies, no npm — served directly by the FastAPI backend.

## How It Works

The backend serves `index.html` at `/`. All API calls go to the same origin
(`/api/moderate`, `/api/history`), so no proxy or CORS config is needed.

## Features

- **Quick Scan** tab — NSFW check only
- **Deep Match** tab — NSFW + copyright/duplicate lookup
- Drag-and-drop or click-to-upload (images, GIFs)
- NSFW confidence score bar
- Duplicate match alert with original uploader info
- Recent uploads history table

## Running

No separate frontend server needed. Just start the backend:

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

Open **http://localhost:8000**.

## Editing

Edit `index.html` directly. Changes are picked up on the next page refresh
(the backend reads the file on each request when using `--reload`).
# Sentinal

# ──────────────────────────────────────────────────────────
#  Sentinal — Multi-stage Dockerfile
#  Builds the React frontend and runs the FastAPI backend
#  in a single container.
#
#  Build:  docker build -t sentinal .
#  Run:    docker run -p 8000:8000 sentinal
#  Open:   http://localhost:8000
# ──────────────────────────────────────────────────────────

# ==================== Stage 1: Build Frontend ====================
FROM node:20-alpine AS frontend-build

WORKDIR /frontend

# Install dependencies first (layer caching)
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

# Copy source and build the Vite production bundle
COPY frontend/ ./
RUN npm run build


# ==================== Stage 2: Python Runtime ====================
FROM python:3.13-slim AS runtime

# Prevent .pyc files and enable real-time log output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies required by some Python packages
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies (cached unless requirements.txt changes)
COPY backend/requirements.txt ./
# Install CPU-only PyTorch first (no CUDA in container — saves ~3.5 GB)
RUN pip install --no-cache-dir torch==2.12.0 --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend application code
COPY backend/app ./app
COPY backend/create_db.py ./

# Copy the built frontend to where main.py expects it.
# main.py resolves:  Path(__file__).parent.parent.parent / "frontend" / "dist"
# In Docker __file__ = /app/app/main.py  →  .parent³ = /  →  /frontend/dist
COPY --from=frontend-build /frontend/dist /frontend/dist

# Set default environment variables (override at runtime with -e or .env)
ENV DATABASE_URL="sqlite:///./moderation.db" \
    NSFW_MODEL_ID="Falconsai/nsfw_image_detection" \
    CLIP_MODEL_ID="openai/clip-vit-base-patch32" \
    NSFW_THRESHOLD="0.5" \
    DUPLICATE_THRESHOLD="0.92" \
    MAX_GIF_FRAMES="16" \
    CORS_ORIGINS="*" \
    LAZY_LOAD_MODELS="true" \
    CHROMA_PERSIST_DIR="/app/chroma_data" \
    CHROMA_COLLECTION_NAME="media_embeddings"

# Persist ChromaDB vector data and SQLite DB across container restarts
VOLUME ["/app/chroma_data"]

# Expose the FastAPI port
EXPOSE 8000

# Health check — lightweight ping every 30s
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run the server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

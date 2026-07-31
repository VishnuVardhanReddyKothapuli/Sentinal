from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import init_db
from app.routers import moderate
from app.services import classifier
from app.services.chroma_store import init_chroma

# Path to the Vite build output (frontend/dist/).
FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    init_chroma()
    if not settings.lazy_load_models:
        classifier.load_models()
    yield


app = FastAPI(
    title="Content Moderation & Copyright Engine",
    description="NSFW classification and CLIP-based duplicate/copyright detection.",
    version="1.0.0",
    lifespan=lifespan,
)

origins = (
    ["*"]
    if settings.cors_origins.strip() == "*"
    else [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(moderate.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


# Serve Vite build assets if they exist (production mode).
assets_dir = FRONTEND_DIST / "assets"
if assets_dir.is_dir():
    app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="static-assets")


@app.get("/", response_class=HTMLResponse)
def serve_frontend() -> HTMLResponse:
    """Serve the React SPA index.html from the Vite build."""
    index = FRONTEND_DIST / "index.html"
    if not index.exists():
        return HTMLResponse(
            content="<h3>Frontend not built yet.</h3>"
            "<p>Run <code>npm run build</code> in the <code>frontend/</code> directory, "
            "or use the Vite dev server at <a href='http://localhost:5173'>localhost:5173</a>.</p>",
            status_code=200,
        )
    return HTMLResponse(content=index.read_text(encoding="utf-8"))


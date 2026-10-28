# Sentinal

**A Safety Gateway Platform.**

An image and video moderation workspace built from the supplied Sentinal project directive. React 18, Vite, Tailwind, Lucide, Chart.js, and Axios power the frontend; FastAPI, SQLAlchemy, JWT authentication, and Alembic power the API.

## Included

- Public landing page with live platform counters, login and registration.
- Safety, similarity, and combined analysis with file previews and upload progress.
- Safety score meters, extracted text, explanations, and private comparison media.
- Account history with search, status filtering, pagination, detail views, and deletion.
- Role-protected admin telemetry, audit events, and bulk deletion.
- Local Falconsai and OpenCLIP inference, Tesseract OCR, and embedded Qdrant.
- SQLite for accounts/history, with one backend process and one data directory.
- Apple-inspired white glass interface with a persistent black theme switch.
- React deployment on Vercel and a FastAPI Docker image for Hugging Face Spaces or Cloud Run.

Missing models or failed analysis stages are reported explicitly. Local development does **not** generate fake safety scores or matches. Content is marked `REVIEW` when the requested safety coverage is incomplete.

## Run locally

Use Python **3.11 or 3.12** for the broadest AI dependency compatibility and Node.js **22+**. The lightweight API can run without downloading model weights. Commands below are for PowerShell, from the project root.

```powershell
Copy-Item .env.example .env
python -c "import sys; assert sys.version_info[:2] in ((3, 11), (3, 12)), 'Select Python 3.11 or 3.12 before creating the environment'; print(sys.version)"
python -m venv backend/.venv
backend/.venv/Scripts/python.exe -m pip install -r backend/requirements.txt
cd frontend
npm.cmd install
cd ..
```

Start the API in one terminal:

```powershell
cd backend
.venv/Scripts/python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Start the interface in another terminal:

```powershell
cd frontend
npm.cmd run dev -- --host 127.0.0.1
```

Open [Sentinal](http://localhost:5173). Register an account to begin. The API reference is at [localhost:8000/docs](http://localhost:8000/docs).

If startup reports `No module named 'pydantic_core._pydantic_core'`, check `backend/.venv/Scripts/python.exe --version` against the version used to install dependencies. Recreating an existing environment with another Python version can leave incompatible compiled packages behind. Stop the backend before repairing the environment, and use the same Python version for environment creation and package installation. The verified local environment uses Python 3.12. Do not rerun the environment-creation command with a different system Python over this environment.

On macOS/Linux, use `python3 -m venv backend/.venv`, `backend/.venv/bin/python`, and `npm` in the equivalent commands. Keep the backend working directory at `backend` so SQLite and uploaded files live under `backend/data`.

Create an administrator through the local CLI:

```powershell
cd backend
.venv/Scripts/python.exe -m app.bootstrap_admin --username admin --email admin@example.com
```

The CLI prompts for a password. There is no default administrator or shared password.

## Enable inference

Install the additional model packages into the same virtual environment:

```powershell
backend/.venv/Scripts/python.exe -m pip install -r backend/requirements-ai.txt
```

Install the Tesseract OCR executable separately and ensure it is on PATH. Configure its path with `TESSERACT_CMD` if needed. Set `ENABLE_AI_MODELS=true` in `.env` to allow model loading; the first time a model runs it downloads weights and caches them under the local `DATA_DIR`.

Leave `QDRANT_URL` empty for embedded local Qdrant; no API key or separate vector server is needed. `DATA_DIR` determines the default SQLite, uploaded media, vector storage and model-cache paths.

Before starting the backend, download/cache the models and verify actual inference with synthetic media:

```powershell
cd backend
.venv/Scripts/python.exe -m ai_engine.verify
```

This checks real safety scores, OCR, duplicate matching, account isolation, deletion, and video inference. It uses temporary local vector storage and disables Gemini for the verification process.

An existing remote Qdrant deployment remains supported through `QDRANT_URL` and `QDRANT_API_KEY`, but is not part of the default architecture.

See [the inference guide](backend/ai_engine/README.md) for capabilities, thresholds, model behavior, video limits, and configuration. Model scores require validation against your use case. Short uploads can be processed locally without full model downloads, but validation remains the operator's responsibility.

## Run the container stack

Requires Docker Engine and Docker Compose. Set a private random `JWT_SECRET` of at least 32 characters in `.env.docker` before starting.

```powershell
Copy-Item .env.docker.example .env.docker
# Edit .env.docker and replace every example secret.
docker compose --env-file .env.docker up --build -d
docker compose --env-file .env.docker exec backend python -m app.bootstrap_admin --username admin --email admin@example.com
```

Open [the containerized interface](http://localhost:8080). The stack contains only the frontend and backend. SQLite, embedded Qdrant, media and model caches live in the backend data volume. AI packages are installed only when `BUILD_AI` is enabled or the default build path is used.

Stop the stack without deleting stored data:

```powershell
docker compose --env-file .env.docker down
```

## Verify

```powershell
./scripts/check.ps1
```

Or run `python -m pytest -q` in `backend`, then `npm test` and `npm run build` in `frontend`. The frontend checks verify result rendering for missing models, OCR outcomes, similarity explanations, and review states.

## Project map

For Vercel, Hugging Face Docker Spaces and Cloud Run settings, see [deployment](docs/DEPLOYMENT.md). Hosted local files are ephemeral; the provided cloud examples are disposable demos. Current [Hugging Face and cloud examples](docs/DEPLOYMENT.md) remain separate from the local development workflow.

```text
backend/app/          Authentication, persistence, API routes and admin CLI
backend/ai_engine/    Media decoding, safety, OCR, embeddings and explanation
backend/alembic/      Schema migrations
backend/tests/        API integration tests
frontend/src/         React pages, shared controls and API state
docs/                 Original directive, architecture and API notes
docker-compose.yml    API and frontend; one persistent backend data volume
IMPLEMENTATION.md     Phase tracking and agent execution log
```

See [architecture and operational boundaries](docs/ARCHITECTURE.md) and [API routes](docs/API.md). Before deploying publicly, configure HTTPS, private secrets, rate limiting, model validation, backups, and review flows for production use.

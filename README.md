# Sentinel

**Intelligent Defense Against Unbounded Content.**

An image and video moderation workspace built from the supplied Sentinel project directive. React 18, Vite, Tailwind, Lucide, Chart.js, and Axios power the frontend; FastAPI, SQLAlchemy, JWT authentication, and Alembic power the API.

## Included

- Public landing page with live platform counters, login and registration.
- Safety, similarity, and combined analysis with file previews and upload progress.
- Safety score meters, extracted text, explanations, and private comparison media.
- Account history with search, status filtering, pagination, detail views, and deletion.
- Role-protected admin telemetry, audit events, and bulk deletion.
- Optional Falconsai, OpenCLIP, Tesseract, Qdrant, and Gemini integrations.
- SQLite local development and a MySQL 8/Qdrant Docker Compose stack.

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

Open [Sentinel](http://localhost:5173). Register an account to begin. The API reference is at [localhost:8000/docs](http://localhost:8000/docs).

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

Install the Tesseract OCR executable separately and ensure it is on PATH. Configure its path with `TESSERACT_CMD` if needed. Set `ENABLE_AI_MODELS=true` in `.env` to allow model loading; the first analysis downloads model weights and can take several minutes. For GPU acceleration, install a PyTorch build appropriate to your hardware before the AI requirements.

For local development, leave `QDRANT_URL` empty and set `QDRANT_LOCAL_PATH=data/qdrant`. This uses persistent local Qdrant storage and needs no API key or separate server. Run only one backend worker with local storage; use a Qdrant server for multiple workers or production. To use a server instead, set `QDRANT_URL` to its endpoint; the URL takes precedence over local storage. For Google-generated explanations, set `GEMINI_API_KEY`; otherwise the pipeline returns a factual local explanation of its measured signals and missing capabilities. Enabling Gemini sends a selected media frame and analysis context to Google.

Before starting the backend, download/cache the models and verify actual inference with synthetic media:

```powershell
cd backend
.venv/Scripts/python.exe -m ai_engine.verify
```

This checks real safety scores, OCR, duplicate matching, account isolation, deletion, and video inference. It uses temporary local vector storage and disables Gemini for the verification process. It does not add records to your account. First-time model downloads can take several minutes; cached weights are reused by the backend. Restart the backend after changing `.env` or installing dependencies.

For Qdrant Cloud: create a cluster at [Qdrant Cloud](https://cloud.qdrant.io), open its **API Keys** tab, and create a **Database API key** with write/manage access. Copy the cluster endpoint into `QDRANT_URL` and the key into `QDRANT_API_KEY` in your private `.env`. This is a database key, not a cloud-management key. See [Qdrant authentication](https://qdrant.tech/documentation/cloud/authentication/). Never put real credentials in `.env.example`.

See [the inference guide](backend/ai_engine/README.md) for capabilities, thresholds, model behavior, video limits, and configuration. Model scores require validation against your use case. Short unsafe moments between sampled video frames can be missed.

## Run the container stack

Requires Docker Engine and Docker Compose. Set private values in `.env.docker` before starting. Use URL-safe characters for `MYSQL_PASSWORD` because it is interpolated into the database URL.

```powershell
Copy-Item .env.docker.example .env.docker
# Edit .env.docker and replace every example secret.
docker compose --env-file .env.docker up --build -d
docker compose --env-file .env.docker exec backend python -m app.bootstrap_admin --username admin --email admin@example.com
```

Open [the containerized interface](http://localhost:8080). MySQL and Qdrant remain on the internal container network. To install heavy models in the backend image, set both `BUILD_AI=true` and `ENABLE_AI_MODELS=true`, then rebuild. Tesseract is included in the backend image. Database migrations run before the API starts; media, model caches, and databases use persistent volumes.

Stop the stack without deleting stored data:

```powershell
docker compose --env-file .env.docker down
```

## Verify

```powershell
./scripts/check.ps1
```

Or run `python -m pytest -q` in `backend`, then `npm test` and `npm run build` in `frontend`. The frontend checks verify result rendering for missing models, OCR outcomes, similarity explanations, match scores, and escaped OCR text. Automated provider tests use controlled fakes so authentication, ownership, failure behavior, frame sampling, and vector scope can be tested without network model downloads. Consult [IMPLEMENTATION.md](IMPLEMENTATION.md) for the checks performed in this workspace and remaining external verification.

## Project map

```text
backend/app/          Authentication, persistence, API routes and admin CLI
backend/ai_engine/    Media decoding, safety, OCR, embeddings and explanation
backend/alembic/      Schema migrations
backend/tests/        API integration tests
frontend/src/         React pages, shared controls and API state
docs/                 Original directive, architecture and API notes
docker-compose.yml    MySQL, Qdrant, API and frontend services
IMPLEMENTATION.md     Phase tracking and agent execution log
```

See [architecture and operational boundaries](docs/ARCHITECTURE.md) and [API routes](docs/API.md). Before deploying publicly, configure HTTPS, private secrets, rate limiting, model validation, backups, a retention policy, and a human review process.
# Sentinal

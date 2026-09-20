# Deployment

The frontend deploys independently to Vercel. The backend Docker image runs FastAPI, SQLite, embedded Qdrant, Falconsai and OpenCLIP in one process. Start with local Docker using the [README](../README.md) to verify the full application.

## Hosting cost and persistence

- Vercel hosts the static React build; check your plan's usage and eligibility limits.
- Hugging Face CPU Basic has no hourly compute charge, but **creating a Docker Space currently requires a paid plan**. See [Spaces overview](https://huggingface.co/docs/hub/spaces-overview).
- Ordinary [Space storage](https://huggingface.co/docs/hub/spaces-storage) disappears on restart. Cloud Run's [writable filesystem](https://docs.cloud.google.com/run/docs/container-contract#file_system_access) is memory-backed and disappears when an instance stops. Neither example below retains accounts, history, uploads or vectors across instance replacement.
- Cloud Run has a [usage-based free tier](https://cloud.google.com/run/pricing), not a guarantee of zero cost. Builds, image storage, traffic and AI runtime can incur charges.

For durable operation with this exact architecture, use a single host with a persistent local disk and backups, such as the supplied Docker Compose deployment. Do not point a live SQLite database or embedded Qdrant directory at an object-storage bucket without verified filesystem semantics. Raising minimum instances or setting a maximum of one does not solve data loss.

## Backend configuration

Use these runtime settings on either host:

```dotenv
ENVIRONMENT=production
DATA_DIR=/app/data
ENABLE_AI_MODELS=true
AUTO_CREATE_TABLES=false
INFERENCE_CONCURRENCY=1
CORS_ORIGINS=https://your-project.vercel.app
```

Set `JWT_SECRET` in the host's secret manager to a private random string of at least 32 characters. Generate one locally with `python -c "import secrets; print(secrets.token_urlsafe(48))"`. Keep it stable across releases. Leave `DATABASE_URL`, `QDRANT_URL`, `QDRANT_LOCAL_PATH`, `QDRANT_API_KEY`, `HF_HOME` and `GEMINI_API_KEY` unset for the default local architecture. The data directory derives storage paths; no database or vector-service credentials are needed.

`CORS_ORIGINS` must contain the exact frontend origin, without a trailing slash or path. Multiple permitted origins are comma-separated. Add custom domains or specific preview URLs explicitly. Do not put backend secrets into frontend environment variables.

The image includes AI dependencies and OCR by default, listens on `PORT` (7860 by default), and applies database migrations before starting one API worker. Models download on first inference, so that request can take several minutes. A health response confirms API/database availability, not successful inference; perform an actual upload before relying on the deployment.

## Hugging Face Docker Space

1. Create a **Docker / blank** Space under an eligible account. Use a public API URL reachable by the browser; do not embed a Hugging Face access token in React.
2. Copy the **contents of `backend/`** to the Space repository root. Include `Dockerfile`, `.dockerignore`, `requirements*.txt`, `alembic.ini`, `alembic/`, `app/` and `ai_engine/`. Never upload `.env`, `.venv`, `data/`, credentials or uploaded media. The repository-root Dockerfile must be the backend Dockerfile, not a nested file.
3. Create the Space repository's root `README.md` with this metadata:

   ```yaml
   ---
   title: Sentinel API
   sdk: docker
   app_port: 7860
   ---
   ```

4. In Space **Settings**, add the backend variables above and the `JWT_SECRET` secret. Keep `PORT=7860`. Push the selected backend source files to build the image.
5. Wait for the Space to run. Open `https://YOUR-SPACE-SUBDOMAIN.hf.space/api/v1/health` and `/docs`. Copy the actual app URL shown by Hugging Face rather than guessing its hostname.

These port, metadata and secret settings follow the [Docker Spaces documentation](https://huggingface.co/docs/hub/spaces-sdks-docker). A Space restart resets this demo's data and downloaded models. Bucket attachment alone has not been validated as a live database solution here.

## Vercel frontend

1. Import the project repository in Vercel. Set **Root Directory** to `frontend` and select **Vite**.
2. Use `npm run build` as the build command and `dist` as the output directory. The included `frontend/vercel.json` supplies the SPA fallback for direct page links.
3. Set `VITE_API_URL` to the backend's full API prefix, for example `https://YOUR-SPACE-SUBDOMAIN.hf.space/api/v1` or `https://YOUR-SERVICE.run.app/api/v1`.
4. Deploy, then set the backend's `CORS_ORIGINS` to the exact Vercel production origin and restart the backend if needed.
5. Register, sign in, upload a test image, refresh a history detail URL, switch themes, and delete the test record. Check that a second account cannot see the first account's media.

Vite substitutes this API URL at build time: changing it requires a frontend redeploy. The browser calls the API directly over HTTPS; Vercel does not run the models. See [Vite on Vercel](https://vercel.com/docs/frameworks/frontend/vite).

## Cloud Run: disposable demo alternative

Use a Google Cloud project with billing, Artifact Registry, Cloud Build and Cloud Run enabled. Build `backend/` as the Docker build context and push the image to your Artifact Registry repository. In the Cloud Run console, create a service from that image:

- Allow public invocation so the browser can reach the API; Sentinel's authenticated routes still require its JWT.
- Set container port to **8080**; Cloud Run supplies `PORT` and the image uses it.
- Start with **2 CPU, 4 GiB memory**, request timeout **900 seconds**, request concurrency **1**, maximum instances **1**, minimum instances **0**. Measure real model usage and raise memory if required.
- Set the backend variables above and bind `JWT_SECRET` from Secret Manager, granting the service identity access to that secret.
- Keep the image's single-worker startup command. Deploy and use the service URL as the Vercel API base with `/api/v1` appended.

Memory includes writable files, downloaded models and uploaded media as well as inference. Even at maximum instances 1, replacement/redeployment loses the local data, and revision transitions can temporarily serve distinct data stores. This option demonstrates integration; it is not durable hosting for this storage design.

## Administration and existing data

For local Docker, create an administrator with `docker compose --env-file .env.docker exec backend python -m app.bootstrap_admin --username admin --email admin@example.com`; it prompts for the password. On a remote host, run the same module through an authorized container terminal with the same data directory and secrets. There is no default admin or public role-promotion endpoint.

Existing SQLite deployments can retain their data directory. Existing MySQL data is **not automatically migrated** by changing the connection URL: export and validate accounts, records and audit data before retiring the old service, and keep media paths and vector IDs consistent. Preserve old database backups and Docker volumes until migration is verified. Stop the backend before taking a coordinated backup of SQLite, local Qdrant and uploads.

The Compose data volume keeps its existing `media_data` name so existing uploads remain available. Old MySQL and standalone Qdrant volumes are not deleted or imported automatically. Do not use `docker compose down -v` when preserving data.

An existing SQLite database created with `AUTO_CREATE_TABLES=true` may have tables but no Alembic revision. Migration startup can then fail with "table already exists". Back up the database first, compare its schema against `backend/alembic/versions/`, and only if it matches the complete current schema run `python -m alembic stamp head` from `backend` using the same database settings, followed by `python -m alembic upgrade head`. Stamping records a version; it does not migrate or repair a different schema. For new installations, let migrations create a fresh database.

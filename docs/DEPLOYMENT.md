2. Copy the **contents of `backend/`** to the Space repository root. Include `Dockerfile`, `.dockerignore`, `requirements*.txt`, `alembic.ini`, `alembic/`, `app/` and `ai_engine/`. Never upload `.env`, `.venv`, `data/`, credentials or uploaded media. The repository-root Dockerfile must be the backend Dockerfile, not a nested file.
3. Create the Space repository's root `README.md` with this metadata:

   ```yaml
   ---
   title: Sentinal API
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

- Allow public invocation so the browser can reach the API; Sentinal's authenticated routes still require its JWT.
- Set container port to **8080**; Cloud Run supplies `PORT` and the image uses it.
- Start with **2 CPU, 4 GiB memory**, request timeout **900 seconds**, request concurrency **1**, maximum instances **1**, minimum instances **0**. Measure real model usage and raise memory if required.
- Set the backend variables above and bind `JWT_SECRET` from Secret Manager, granting the service identity access to that secret.
- Keep the image's single-worker startup command. Deploy and use the service URL as the Vercel API base with `/api/v1` appended.

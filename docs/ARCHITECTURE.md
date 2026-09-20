# Sentinel architecture

```text
Vercel: React / Vite frontend
             |
             | HTTPS /api/v1 + bearer token
             v
FastAPI: one process in a Docker container
Hugging Face Spaces / Cloud Run / local Docker
             |
       +-----+------------------+
       |                        |
       v                        v
SQLite                     Embedded local Qdrant
accounts, history, audit   account-scoped vectors
             |
             +--- Local CPU inference
                  Falconsai NSFW (~343 MB weights)
                  OpenCLIP ViT-B-32 (~605 MB weights)
                  Tesseract OCR
```

Model sizes are approximate checkpoint sizes, not RAM or total installation requirements. PyTorch, decoded frames, activations and caches need additional space. Inference runs in the API process; there is no paid inference API dependency. Gemini explanations are optional and disabled unless explicitly configured.

## Storage and processes

`DATA_DIR` holds SQLite (`sentinel.db`), uploads (`uploads/`), Qdrant (`qdrant/`) and downloaded models (`models/`) by default. Explicit storage environment variables can override these paths. Docker Compose mounts one named volume at the backend data directory. Back up this data with the backend stopped so database, vectors and media represent the same state.

Use **one API worker and one backend replica** with local Qdrant. Separate replicas would have separate account databases and indexes; sharing the local index between processes is unsupported. SQLite and Qdrant are independent stores, so failed vector cleanup is reported instead of assuming a distributed transaction. Remote Qdrant remains an optional compatibility setting, not a required service.

Cloud Run's writable filesystem is memory-backed and disappears with the instance. Hugging Face Space disk also resets on restart. The hosted examples are therefore disposable demos. A maximum of one instance does not provide persistence. Durable operation with this architecture requires a host with a suitable persistent local disk; an object-storage bucket is not automatically a compatible live SQLite/Qdrant filesystem. See [deployment and hosting limitations](DEPLOYMENT.md).

## Request lifecycle

1. React sends its JWT to FastAPI; the API checks role and account ownership.
2. Uploads are bounded, checked as supported media and assigned a record ID.
3. The local pipeline decodes an image or samples video frames, then runs the requested safety/OCR and similarity checks.
4. Missing models or failed stages produce explicit warnings and `REVIEW`, never fabricated safety scores.
5. Embedded Qdrant searches only the current account's vectors. Default cosine thresholds are 0.88 for duplicates and 0.70 for near matches.
6. SQLite stores the result and audit event; authenticated media routes serve previews. React renders results and account history.

## Inference boundaries

Falconsai classifies NSFW content. OpenCLIP embeddings support similarity and auxiliary zero-shot category signals. These scores are not calibrated probabilities or guarantees of safety. OCR text screening uses a configurable lexicon with limited contextual coverage.

Video defaults to one sampled frame per second, at most 60 frames; unsafe moments between samples can be missed. Explicitly enabling Gemini sends a sampled frame and analysis signals to Google. Media and OCR remain untrusted input.

The browser remembers the selected white or black theme locally. Authentication retains the existing JWT localStorage flow. Production use still requires representative model evaluation, human review, HTTPS, retention controls and backups.

# Sentinel architecture

Sentinel is a React client backed by a FastAPI API and SQLAlchemy persistence. Local development uses SQLite; the container stack uses MySQL 8 and Qdrant. Uploaded media and analysis history are scoped to the authenticated account. Administrators have explicit platform-wide access.

## Request lifecycle

1. The client attaches its JWT to API requests. The API resolves the user from the database and applies role and ownership checks.
2. An upload is streamed to bounded storage, validated as supported media, and assigned an analysis record identifier.
3. The inference package decodes the image or samples video frames. It evaluates the requested safety/OCR and similarity branches.
4. Available model signals produce scores; missing capabilities produce explicit warnings and a review decision. No random or demonstration scores are used.
5. Qdrant searches are restricted to the current account. Cosine similarity at 0.88 identifies duplicates, and 0.70 identifies near matches.
6. The completed result is persisted with its owner and audit information. The client renders the result and can retrieve it from account history.

## Inference boundaries

Falconsai is a binary NSFW model. CLIP zero-shot prompts provide auxiliary signals for the requested safe/explicit/suggestive/gore categories. These model scores are not calibrated probabilities or a guarantee of safety. Text screening uses a configurable rule lexicon and has limited linguistic and contextual coverage.

Video is sampled at one frame per second, up to 60 frames; content between samples can be missed. Model, OCR, and vector failures must be visible in each result. Gemini, when explicitly configured with a key, receives a sampled frame and its analysis signals to produce a short explanation. Treat media and OCR text as untrusted content in that prompt.

## Operational boundaries

This is a runnable project foundation, not a certified moderation system. Production operation requires evaluation on representative data, a human review process, load testing, TLS, secret management, storage backups and retention controls. JWT storage follows the directive's browser localStorage requirement; a production deployment can migrate to secure HttpOnly cookies with CSRF controls.

The API performs bounded inference in-process. Multiple workers each load their own models; large deployments should move inference into a dedicated job queue and GPU worker service. MySQL and Qdrant are independent stores, so vector cleanup failures require reconciliation rather than an assumption of distributed transactions.

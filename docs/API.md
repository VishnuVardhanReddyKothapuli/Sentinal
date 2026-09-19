# Sentinel API

Base path: `/api/v1`. The running API provides its generated OpenAPI specification at `/openapi.json` and interactive reference at `/docs`.

Authenticated routes expect `Authorization: Bearer <access_token>`. Registration always creates a `USER`; administrator access must be granted through the backend administration command.

| Method | Path | Purpose |
| --- | --- | --- |
| POST | `/auth/register` | Register with `username`, `email`, `password` |
| POST | `/auth/login` | Sign in with `username`, `password` |
| GET | `/auth/me` | Resolve the current account |
| GET | `/health` | API health and inference capabilities |
| GET | `/metrics/public` | Platform scan, flagged, and account counts |
| POST | `/analyze/nsfw` | Safety and OCR analysis |
| POST | `/analyze/similarity` | Vector similarity analysis |
| POST | `/analyze/combined` | Safety, OCR, and similarity analysis |
| GET | `/user/history` | Paginated account history; supports `page`, `page_size`, `status`, `search` |
| GET | `/user/history/{id}` | Account-owned analysis detail |
| DELETE | `/user/history/{id}` | Delete an account-owned scan |
| GET | `/media/{id}` | Authenticated access to scan media |
| GET | `/admin/overview` | Platform telemetry, recent records, and audit events |
| DELETE | `/admin/records/{id}` | Administrator deletion of a scan |
| POST | `/admin/purge` | Administrator bulk deletion with `{ "ids": [...] }` |

Uploads use `multipart/form-data` with field `file`. Do not set the request Content-Type manually when using a browser FormData instance: the browser must supply the multipart boundary.

Scores and returned similarity values use percentages (0–100). Unavailable category scores are `null`; the client must render them as unavailable. `SAFE`, `FLAGGED`, and `REVIEW` describe the pipeline decision, not a legal determination. `warnings` and `capabilities` accompany results to make missing analysis visible. Similarity thresholds in the inference configuration use normalized cosine values (0–1).

The first item scanned by an account normally has no similarity matches. Searching and indexing are private to the current account. URLs for uploaded files require JWT authorization; clients fetch blobs through the authenticated API instead of using unauthenticated image URLs.

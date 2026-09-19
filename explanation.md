# Sentinel — Complete Project Explanation

## *Intelligent Defense Against Unbounded Content*

> **For:** Presentation · Interview · Viva · Technical Defense

---

## Table of Contents

1. [What Is Sentinel?](#1-what-is-sentinel)
2. [Problem Statement & Motivation](#2-problem-statement--motivation)
3. [Complete Tech Stack Breakdown](#3-complete-tech-stack-breakdown)
4. [System Architecture](#4-system-architecture)
5. [Why This Tech Stack? (Justification for Every Choice)](#5-why-this-tech-stack-justification-for-every-choice)
6. [AI / ML Pipeline Deep Dive](#6-ai--ml-pipeline-deep-dive)
7. [Database Design & Schema](#7-database-design--schema)
8. [Security Architecture](#8-security-architecture)
9. [API Design & REST Endpoints](#9-api-design--rest-endpoints)
10. [Frontend Architecture](#10-frontend-architecture)
11. [DevOps & Containerization](#11-devops--containerization)
12. [Real-World Uses & Applications](#12-real-world-uses--applications)
13. [Advantages Over Existing Solutions](#13-advantages-over-existing-solutions)
14. [Limitations & Honest Boundaries](#14-limitations--honest-boundaries)
15. [Key Technical Decisions & Trade-offs](#15-key-technical-decisions--trade-offs)
16. [Testing Strategy](#16-testing-strategy)
17. [Future Scope & Enhancements](#17-future-scope--enhancements)
18. [Presentation Talking Points](#18-presentation-talking-points)
19. [Likely Viva / Interview Questions & Answers](#19-likely-viva--interview-questions--answers)
20. [One-Liner Summaries for Quick Recall](#20-one-liner-summaries-for-quick-recall)

---

## 1. What Is Sentinel?

Sentinel is an **enterprise-grade, AI-powered content moderation and visual similarity platform**. It accepts images and videos, then:

| Capability | What It Does |
|---|---|
| **Safety Classification** | Scores content across 4 risk categories — Safe, Explicit, Suggestive, Gore |
| **OCR + Text Safety** | Extracts embedded text from images/video frames using Tesseract OCR and screens it against a configurable hate-speech / profanity lexicon |
| **Visual Similarity / Duplicate Detection** | Generates 512-dimensional CLIP embeddings, stores them in a vector database, and finds visually similar or duplicate content per user account |
| **AI Explainability** | Produces natural-language explanations of *why* content was flagged, either via computed signal summaries or Google Gemini multimodal AI |
| **Account History & Admin Controls** | Full audit trail, paginated history, role-based admin dashboard with bulk operations |

**In one sentence:** Sentinel is a full-stack content safety platform that combines deep learning vision models, OCR, vector search, and generative AI into a single deployable application with a modern React dashboard.

---

## 2. Problem Statement & Motivation

### The Problem

User-generated content platforms (social media, e-commerce marketplaces, educational portals, messaging apps) face an overwhelming volume of uploaded images and videos. Manual review does not scale. Harmful content — explicit imagery, gore, hate-speech embedded in images, and re-uploaded duplicate violations — can spread before human moderators even see it.

### Why It Matters

- **Legal compliance:** GDPR, COPPA, the EU Digital Services Act, and India's IT Rules 2021 mandate proactive removal of harmful content.
- **User safety:** Exposure to NSFW/violent content causes real harm, especially to minors.
- **Brand protection:** Platforms lose advertiser trust and user confidence when harmful content surfaces.
- **Operational cost:** Manual moderation at scale costs millions; AI-assisted triage reduces human effort by 60-80%.

### What Sentinel Solves

Sentinel provides an **automated first-pass triage system** that:
- Assigns risk scores to every upload before a human ever sees it
- Flags duplicates and near-matches of previously flagged content
- Extracts and screens text embedded inside images (memes, banners, screenshots)
- Explains its decisions in plain English (Gemini integration)
- Never fabricates scores — if a model is unavailable, the system honestly reports `REVIEW` with explicit warnings

---

## 3. Complete Tech Stack Breakdown

### Frontend

| Technology | Version | Purpose |
|---|---|---|
| **React** | 18.3 | Component-based UI framework with concurrent rendering |
| **Vite** | 6.2 | Lightning-fast build tool and dev server (ESBuild + Rollup) |
| **Tailwind CSS** | 3.4 | Utility-first CSS framework for rapid, consistent styling |
| **Lucide React** | 0.468 | Modern, lightweight icon library (tree-shakable SVG icons) |
| **Chart.js** | 4.4 | Canvas-based charting for score visualizations and admin telemetry |
| **Axios** | 1.8 | HTTP client with interceptors for JWT injection |
| **React Router DOM** | 6.30 | Client-side routing with protected route guards |
| **Headless UI** | 2.2 | Accessible, unstyled UI primitives (modals, menus, transitions) |
| **PostCSS + Autoprefixer** | 8.5 / 10.4 | CSS post-processing and vendor prefix automation |

### Backend

| Technology | Version | Purpose |
|---|---|---|
| **Python** | 3.11 / 3.12 | Primary runtime; selected for AI library compatibility |
| **FastAPI** | >=0.115 | High-performance async web framework with automatic OpenAPI docs |
| **Uvicorn** | latest | ASGI server with HTTP/1.1 support |
| **SQLAlchemy** | >=2.0.38 | Python ORM with modern mapped column syntax |
| **Alembic** | >=1.14 | Database migration management |
| **PyJWT** | >=2.10 | JSON Web Token creation and verification |
| **Argon2-cffi** | >=23.1 | Password hashing (winner of the Password Hashing Competition) |
| **Pydantic** | v2 (via pydantic-settings) | Request/response validation and configuration management |
| **Pillow** | >=11.1 | Image decoding and manipulation |
| **OpenCV (headless)** | >=4.10 | Video frame extraction and media validation |
| **python-multipart** | >=0.0.20 | Multipart form data parsing for file uploads |
| **httpx** | >=0.28 | Async HTTP client (used in testing) |

### AI / ML Stack

| Technology | Purpose |
|---|---|
| **PyTorch** (>=2.5) + **TorchVision** (>=0.20) | Deep learning framework and pretrained vision transforms |
| **Hugging Face Transformers** (>=4.48) | Model hub for loading Falconsai/nsfw_image_detection |
| **OpenCLIP** (>=2.30) | Open-source CLIP implementation for zero-shot classification + embeddings |
| **Tesseract OCR** (via pytesseract) | Optical character recognition on images and video frames |
| **Google Gemini API** (google-genai >=1.0) | Multimodal generative AI for natural-language explanations |
| **Qdrant** (qdrant-client >=1.13) | High-performance vector database for similarity search |

### Databases

| Database | Purpose |
|---|---|
| **SQLite** | Zero-configuration local development database |
| **MySQL 8.0** | Production relational database (users, records, audit logs) |
| **Qdrant** (v1.15) | Purpose-built vector database for CLIP embedding storage and cosine similarity search |

### DevOps

| Tool | Purpose |
|---|---|
| **Docker** + **Docker Compose** | Multi-container orchestration (MySQL, Qdrant, Backend, Frontend/Nginx) |
| **Nginx** | Production-grade reverse proxy serving the frontend static build |
| **Alembic Migrations** | Schema versioning and automated upgrades on container startup |

---

## 4. System Architecture

```
+-----------------------------------------------------+
|              React 18 + Tailwind CSS                 |
|        (Vite, Lucide, Chart.js, Axios)               |
|    Pages: Home, Login, Analyzer, History, Admin       |
+-------------------------+---------------------------+
                          |  REST / JWT (Bearer Token)
                          v
+-----------------------------------------------------+
|                 FastAPI Gateway                       |
|          (Auth, Validation, CORS, Routing)            |
|  Endpoints: /auth /analyze /user /admin /health       |
+--------+-----------------------------------+--------+
         |                                   |
         v                                   v
+--------------------+       +----------------------------+
|   Relational DB    |       |    AI Inference Core        |
|  SQLite / MySQL    |       |  +----------------------+  |
|                    |       |  | Falconsai NSFW       |  |
|  * Users           |       |  | OpenCLIP ViT-B32     |  |
|  * AnalysisRecords |       |  | Tesseract OCR        |  |
|  * AuditLogs       |       |  | Gemini Flash         |  |
|  * PlatformMetrics |       |  +----------------------+  |
+--------------------+       +-------------+--------------+
                                           |
                                           v
                             +----------------------------+
                             |   Vector Engine             |
                             |   Qdrant (512d CLIP)        |
                             |   Cosine Similarity         |
                             |   Per-User Tenancy          |
                             +----------------------------+
```

### Request Lifecycle (End to End)

1. **User uploads** an image/video through the React frontend
2. **Axios** attaches the JWT bearer token and sends a multipart POST to `/api/v1/analyze/{mode}`
3. **FastAPI** validates the token, resolves the user, checks file extension/size
4. **Media module** saves the file to bounded storage, validates it is decodable media
5. **AI pipeline** runs concurrently:
   - Falconsai classifies NSFW (binary) -> OpenCLIP adds 4-category zero-shot scores
   - Tesseract extracts embedded text -> Lexicon evaluates for flagged terms
   - OpenCLIP generates a 512-d embedding -> Qdrant searches for similar vectors (scoped to user)
6. **Pipeline** computes `SAFE`, `FLAGGED`, or `REVIEW` based on threshold logic
7. **(Optional)** Gemini receives a representative frame + scores -> returns a 2-3 sentence explanation
8. **Result** is persisted in the relational database with full audit logging
9. **Frontend** renders the result: radial score dials, OCR badge, similarity matches, explanation card

---

## 5. Why This Tech Stack? (Justification for Every Choice)

### React 18 — *Why not Angular or Vue?*

| Factor | React Advantage |
|---|---|
| **Ecosystem** | Largest community, most third-party components, massive hiring pool |
| **Concurrent Rendering** | React 18's concurrent features prevent UI blocking during heavy re-renders (analysis results) |
| **Component Reusability** | Confidence meters, media previews, and result cards are self-contained components |
| **Industry Standard** | Used by Meta, Netflix, Airbnb — interviewers expect it; it validates the candidate's industry relevance |

### FastAPI — *Why not Django or Flask or Express?*

| Factor | FastAPI Advantage |
|---|---|
| **Performance** | Built on Starlette/ASGI — benchmarks at 2-5x Flask/Django for I/O-bound workloads |
| **Async Native** | `async/await` for concurrent inference (safety + OCR + similarity run in parallel via `asyncio.gather`) |
| **Auto Documentation** | OpenAPI/Swagger UI generated from type hints — zero extra documentation effort |
| **Pydantic Validation** | Request/response schemas are validated at the framework level — no manual parsing |
| **Python AI Ecosystem** | Same language as PyTorch, Transformers, OpenCLIP — no cross-language serialization overhead |

### SQLAlchemy 2.0 — *Why not raw SQL or Django ORM?*

- **Mapped columns** with Python type hints provide IDE autocompletion and type checking
- **Database agnostic** — same code runs on SQLite (dev) and MySQL (prod) without changes
- **Alembic integration** — versioned schema migrations that auto-run on container startup

### Qdrant — *Why not Pinecone, Weaviate, or ChromaDB?*

| Factor | Qdrant Advantage |
|---|---|
| **Local + Cloud** | Runs embedded (no server needed for dev) OR as a Docker container OR as a managed cloud service |
| **Payload Filtering** | Native per-user tenant filtering on `user_id` — critical for account isolation in a multi-tenant system |
| **Performance** | Written in Rust — sub-millisecond search on millions of vectors |
| **Open Source** | No vendor lock-in; self-hostable with no license fees |

### Falconsai + OpenCLIP — *Why these specific models?*

| Model | Justification |
|---|---|
| **Falconsai/nsfw_image_detection** | Lightweight binary NSFW classifier (~500MB); runs on CPU; no GPU required for basic inference |
| **OpenCLIP ViT-B-32** | Multi-purpose: provides both (a) 4-category zero-shot classification AND (b) 512-d embeddings for similarity search — one model, two uses |
| **Combined approach** | Falconsai gives high-confidence binary NSFW detection; CLIP adds nuanced suggestive/gore categories — together they cover more ground than either alone |

### Argon2 — *Why not bcrypt?*

- **PHC winner**: Argon2 won the Password Hashing Competition (2015) and is recommended by OWASP
- **Memory-hard**: Resistant to GPU/ASIC brute-force attacks (bcrypt is not memory-hard)
- **Configurable**: Tunable time, memory, and parallelism parameters

### JWT — *Why not session-based auth?*

- **Stateless**: No server-side session store needed — scales horizontally
- **Decoupled**: Frontend and backend can be deployed independently (different origins, CDN, etc.)
- **Standard**: Industry-standard `Authorization: Bearer` header; every HTTP client supports it

### Vite — *Why not Webpack or Create React App?*

- **Speed**: ESBuild-based dev server starts in <300ms vs. 10-30s for Webpack
- **HMR**: Hot Module Replacement with sub-50ms updates
- **Modern**: Native ES modules, tree-shaking, code splitting — 316 KB gzipped production build

### Tailwind CSS — *Why not Bootstrap or custom CSS?*

- **No context switching**: Style directly in JSX without jumping between files
- **Purging**: Unused styles are automatically removed in production builds
- **Consistency**: Design tokens (colors, spacing, typography) enforced through configuration
- **Dark theme**: The cyber-defense aesthetic (`slate-950`, `cyan-500`, `rose-500`) is expressed naturally

---

## 6. AI / ML Pipeline Deep Dive

### 6.1 Safety Classification Pipeline

```
Image/Video -> Frame Sampling -> Falconsai Binary NSFW -> OpenCLIP Zero-Shot (4 categories) -> Score Fusion -> Decision
```

**Falconsai** produces:
- `normal` (0-1) -> mapped to `safe` (0-100%)
- `nsfw` (0-1) -> mapped to `explicit` (0-100%)

**OpenCLIP** adds:
- 4 text prompts scored via zero-shot classification:
  - "a safe ordinary non-explicit photograph without nudity or violence"
  - "a sexually explicit pornographic photograph with visible nudity"
  - "a sexually suggestive provocative photograph without explicit nudity"
  - "a graphic photograph of gore, bloody severe injuries or dismemberment"

**Score Fusion Logic:**
- `explicit` = max(Falconsai NSFW, CLIP explicit)
- `safe` = min(Falconsai normal, CLIP safe)
- `suggestive` and `gore` come directly from CLIP zero-shot
- Scores are **independent signals, NOT a probability distribution** — they do not sum to 100

### 6.2 Video Processing

- OpenCV samples **1 frame per second**, capped at **60 frames** (videos > 1 hour are rejected)
- **Worst-case aggregation**: risk categories take their maximum across all frames; safe takes the minimum
- 30-second decode budget with frame-by-frame time checks
- Images > 40 megapixels are rejected; decoded frames are downscaled to 1024px longest edge

### 6.3 OCR & Text Safety

- Tesseract extracts text from each frame (5-second timeout per frame)
- Deduplicated across frames; capped at 30,000 characters
- Extracted text is screened against a configurable rule-based lexicon
- Matching is **whole-word/phrase**, **Unicode-normalized**, **case-insensitive**
- Any flagged term triggers `FLAGGED` status with an explicit reason

### 6.4 Vector Similarity

- OpenCLIP generates a **512-dimensional L2-normalized** embedding per frame
- For video: frame embeddings are averaged, then re-normalized
- Stored in Qdrant with `user_id` as a tenant filter
- **Duplicate threshold**: cosine >= 0.88
- **Near-match threshold**: cosine >= 0.70
- Searches exclude the current record and only return matches >= 0.70

### 6.5 Gemini Explainability

- When configured, sends the representative frame + computed scores + OCR text to Google Gemini
- Prompt instructs: "Write 2-3 concise factual sentences... do not identify people... do not invent scores"
- The explanation **never changes computed decisions** — it is purely additive narrative
- Without Gemini, a deterministic computed-signal summary is used instead

### 6.6 Decision Logic

```
FLAGGED  ->  any risk signal >= 70%  OR  OCR text flagged  OR  duplicate (cosine >= 0.88)
REVIEW   ->  any risk signal 40-69%  OR  near-match (cosine 0.70-0.87)  OR  incomplete checks
SAFE     ->  all requested checks complete  AND  all risks < 40%  AND  no flagged text  AND  no near-matches
```

---

## 7. Database Design & Schema

### Users Table

| Column | Type | Purpose |
|---|---|---|
| id | UUID (VARCHAR 36) | Primary key |
| username | VARCHAR(50) | Unique login identifier |
| email | VARCHAR(100) | Unique email, validated |
| hashed_password | VARCHAR(255) | Argon2 hash |
| role | ENUM('USER', 'ADMIN') | Role-based access control |
| created_at | TIMESTAMP | Registration time |

### Analysis Records Table

| Column | Type | Purpose |
|---|---|---|
| id | UUID | Primary key |
| user_id | FK -> users.id | Owner (CASCADE delete) |
| file_name, file_type, file_url | VARCHAR | Media metadata |
| storage_path | VARCHAR(1000) | Server filesystem path |
| analysis_type | ENUM('NSFW','SIMILARITY','COMBINED') | What was requested |
| score_safe/explicit/suggestive/gore | DECIMAL(5,2) | Model scores (nullable) |
| extracted_text | TEXT | OCR output |
| text_flagged, text_flag_reason | BOOLEAN, VARCHAR | Lexicon screening result |
| vector_id | VARCHAR(64) | Qdrant point ID |
| is_duplicate, matched_record_id, similarity_score | BOOLEAN, FK, DECIMAL | Similarity results |
| ai_explanation | TEXT | Gemini or computed explanation |
| overall_status | ENUM('SAFE','FLAGGED','REVIEW') | Final verdict |
| result | JSON | Complete pipeline output (denormalized for fast retrieval) |
| created_at | TIMESTAMP | Analysis time |

### Audit Logs Table

| Column | Type | Purpose |
|---|---|---|
| id | UUID | Primary key |
| user_id | VARCHAR(36) | Who did it |
| action | VARCHAR(80) | ACCOUNT_CREATED, LOGIN, ANALYSIS_COMPLETED, RECORD_DELETED |
| details | TEXT | Context |
| created_at | TIMESTAMP | When |

### Design Rationale

- **JSON `result` column**: Stores the full pipeline output for fast single-query retrieval without joins. The individual score columns exist for efficient filtering/aggregation queries.
- **CASCADE on user deletion**: All user data (records, media, audit trail) is removed together.
- **Separate audit table**: Immutable event log for compliance; cannot be tampered with by regular users.

---

## 8. Security Architecture

### Authentication Flow

1. User registers -> password hashed with **Argon2** -> JWT issued
2. User logs in -> password verified against Argon2 hash -> JWT issued
3. Every subsequent request includes `Authorization: Bearer <token>`
4. FastAPI dependency resolves the user from the JWT's `sub` claim

### JWT Structure

```json
{
  "sub": "user-uuid",
  "iat": 1726200000,
  "exp": 1726203600,
  "iss": "sentinel",
  "aud": "sentinel-api"
}
```

- **Issuer/Audience validation** prevents token confusion attacks
- **Required claims** (`sub`, `exp`, `iat`) enforced at decode time
- **HS256** signing with a configurable secret key

### Authorization Model (RBAC)

| Role | Capabilities |
|---|---|
| **USER** | Upload, analyze, view own history, delete own records, access own media |
| **ADMIN** | Everything USER can do + platform-wide telemetry, view all records, bulk delete, audit logs |

- Admin role is created **only via CLI** (`bootstrap_admin.py`) — no web registration for admins
- Ownership checks: users can only access their own records; admins can access all

### Data Isolation

- **Media files** are served through an authenticated endpoint (`/api/v1/media/{id}`) — no direct filesystem URLs
- **Vector searches** are filtered by `user_id` — User A cannot see User B's similarity matches
- **History queries** are scoped to `user_id == current_user.id`
- **Security headers**: `X-Content-Type-Options: nosniff`, `Referrer-Policy: same-origin`, `Cache-Control: no-store`

---

## 9. API Design & REST Endpoints

| Method | Endpoint | Auth | Purpose |
|---|---|---|---|
| POST | `/api/v1/auth/register` | None | Create account |
| POST | `/api/v1/auth/login` | None | Authenticate |
| GET | `/api/v1/auth/me` | JWT | Get current user |
| GET | `/api/v1/health` | None | Service health + capabilities |
| GET | `/api/v1/metrics/public` | None | Platform counters (landing page) |
| POST | `/api/v1/analyze/nsfw` | JWT | Safety + OCR analysis |
| POST | `/api/v1/analyze/similarity` | JWT | Vector similarity analysis |
| POST | `/api/v1/analyze/combined` | JWT | Full pipeline (safety + OCR + similarity) |
| GET | `/api/v1/user/history` | JWT | Paginated user history (search, filter) |
| GET | `/api/v1/user/history/{id}` | JWT | Single record detail |
| DELETE | `/api/v1/user/history/{id}` | JWT | Delete own record |
| GET | `/api/v1/media/{id}` | JWT | Authenticated media access |
| GET | `/api/v1/admin/overview` | ADMIN | Platform telemetry + audit logs |
| DELETE | `/api/v1/admin/records/{id}` | ADMIN | Admin delete any record |
| POST | `/api/v1/admin/purge` | ADMIN | Bulk delete records |

### Design Principles

- **RESTful**: Resources map to nouns (`/analyze`, `/user/history`, `/admin/overview`)
- **Versioned**: `/api/v1/` prefix enables future breaking changes without disrupting existing clients
- **Consistent error handling**: Standard HTTP status codes (401, 403, 404, 409, 415, 422, 503)
- **Auto-documented**: FastAPI generates OpenAPI/Swagger UI at `/docs` automatically from type hints

---

## 10. Frontend Architecture

### Page Structure

| Page | Route | Purpose |
|---|---|---|
| **Home** | `/` | Landing page with live platform counters, feature cards, hero section |
| **Login** | `/login` | Auth card with login/register toggle |
| **Analyzer** | `/analyzer` | File upload -> analysis mode selection -> result display |
| **History** | `/history` | Paginated table with search, status filter, detail modal, delete |
| **Admin Dashboard** | `/admin` | Platform telemetry, all records, audit log, bulk actions |

### Component Architecture

```
src/
+-- App.jsx              <- Router, layout, protected routes
+-- api.js               <- Axios instance with JWT interceptor
+-- auth.jsx             <- Auth context provider
+-- main.jsx             <- React DOM entry point
+-- styles.css           <- Tailwind + custom styles (dark theme)
+-- components/
|   +-- common/          <- Navbar, Sidebar, MetricCard, ConfidenceMeter
|   +-- AnalysisResult.jsx  <- Score dials, OCR display, similarity matches
|   +-- MediaPreview.jsx    <- Image/video preview component
+-- pages/
    +-- Home.jsx, Login.jsx, Analyzer.jsx
    +-- History.jsx, AdminDashboard.jsx
    +-- NsfwAnalyzer.jsx, SimilarityChecker.jsx, CombinedChecker.jsx
```

### Key Frontend Patterns

- **JWT stored in localStorage** (per project directive; production would use HttpOnly cookies)
- **Axios interceptor** automatically attaches `Authorization: Bearer` header
- **Protected routes** redirect unauthenticated users to `/login`
- **Admin route guard** checks `role === 'ADMIN'` before rendering
- **Responsive design**: Verified at 320px, 768px, 1024px, and 1440px viewports
- **Accessible**: Upload input has ARIA label; closed mobile nav is hidden from keyboard/screen readers

---

## 11. DevOps & Containerization

### Docker Compose Stack

```yaml
Services:
  mysql      -> MySQL 8.0 with health checks and persistent volume
  qdrant     -> Qdrant v1.15.1 with persistent volume
  backend    -> FastAPI + Uvicorn (runs Alembic migrations on startup)
  frontend   -> Nginx serving the Vite production build
```

### Key Docker Decisions

- **Multi-stage builds**: Backend Dockerfile separates dependency installation from application code
- **Persistent volumes**: `mysql_data`, `qdrant_data`, `media_data`, `model_cache` survive container restarts
- **Internal networking**: MySQL and Qdrant are not exposed to the host — only the backend connects
- **Environment-driven configuration**: All secrets are in `.env.docker`, not hardcoded
- **Auto-migration**: `alembic upgrade head` runs before the API starts — schema is always current

---

## 12. Real-World Uses & Applications

### 1. Social Media Platforms

Automatically scan user-uploaded photos and videos before they become publicly visible. Flag explicit content for human review. Detect re-uploads of previously removed material using similarity search.

### 2. E-Commerce Marketplaces

Scan product listing images for inappropriate content. Detect duplicate product images that may indicate fraudulent listings. Extract and screen text in promotional banners.

### 3. Educational Platforms (EdTech)

Moderate student-submitted images and videos in collaborative projects. Ensure uploaded materials comply with institutional content policies. Critical for platforms used by minors (COPPA compliance).

### 4. Healthcare & Telemedicine

Screen patient-uploaded medical images for any non-medical content before clinician review. The `REVIEW` status ensures no automated decision replaces clinical judgment.

### 5. Legal & Compliance Departments

Audit large media collections for policy violations. The audit log provides a tamper-evident trail for regulatory compliance. Bulk purge capabilities support data retention policies.

### 6. Content Delivery Networks (CDNs)

Inline content scanning before caching and distribution. The sub-second inference time (for cached models) enables near-real-time moderation at the edge.

### 7. Internal Enterprise Tools

HR departments scanning internal communications and shared drives for policy violations. The per-user tenant isolation ensures departmental data boundaries.

### 8. News & Media Organizations

Verify authenticity of user-submitted images by detecting duplicates of known manipulated media. OCR extracts text from screenshots and infographics for editorial review.

---

## 13. Advantages Over Existing Solutions

| Advantage | Sentinel | Typical Cloud APIs (AWS Rekognition, Google Vision) |
|---|---|---|
| **Self-hosted** | Full data sovereignty; media never leaves your infrastructure | Media sent to third-party servers |
| **Cost** | No per-image API charges; only compute costs | $1-4 per 1000 images |
| **Customizable** | Swap models, adjust thresholds, customize lexicons | Fixed model, fixed thresholds |
| **Multi-modal** | Vision + OCR + Similarity + Explainability in one pipeline | Separate APIs for each capability |
| **Transparent** | Open-source models; you can inspect what scores mean | Black-box confidence scores |
| **Honest** | Reports `REVIEW` when capabilities are missing; never fabricates scores | May return partial results silently |
| **Per-user isolation** | Multi-tenant vector search with account-level privacy | Not applicable |
| **Offline capable** | Works without internet once models are cached | Requires internet |

---

## 14. Limitations & Honest Boundaries

> This section is critical for viva — examiners respect candidates who acknowledge limitations honestly.

1. **Not a certified moderation system**: Sentinel is a triage tool, not a legal determination. Human review is required for final decisions.
2. **Uncalibrated scores**: Suggestive and gore categories are zero-shot CLIP heuristics, not validated specialist classifiers. Scores do not sum to 100 and are not true probabilities.
3. **Video gaps**: 1 FPS sampling can miss brief unsafe moments. Content between sampled frames is invisible.
4. **OCR limitations**: Small text, stylized fonts, and non-Latin scripts may not be detected. The lexicon is a simple pattern matcher, not a sentiment/context analyzer.
5. **No real-time streaming**: Processes uploaded files, not live video streams.
6. **Single-process models**: Each worker loads its own model weights (~2-3 GB RAM). Large-scale deployments need a dedicated GPU inference queue.
7. **localStorage JWT**: Vulnerable to XSS. Production should use HttpOnly cookies with CSRF tokens.

---

## 15. Key Technical Decisions & Trade-offs

| Decision | Rationale | Trade-off |
|---|---|---|
| **SQLite for dev, MySQL for prod** | Zero-config local development; no Docker needed to start coding | Schema must be tested on both engines |
| **Inference in-process** | Simpler deployment; no message queue infrastructure | Each worker loads model weights independently |
| **Lazy model loading** | Fast startup; models load only on first analysis | First analysis request is slow (model download) |
| **Concurrency semaphore** | Prevents OOM from parallel model inference | Queues requests under high load |
| **JSON result column** | Fast single-query retrieval of full pipeline output | Slight denormalization; result is also in individual columns for queries |
| **OpenCLIP for both classification and embeddings** | One model serves two purposes; reduces memory footprint | 512-d embeddings are smaller than newer models (CLIP-L is 768-d) |
| **Per-user vector tenant filtering** | Privacy-preserving similarity search | Cannot detect cross-user duplicates (a business decision, not a bug) |
| **Deterministic fallback explanations** | Always returns an explanation even without Gemini | Less natural-sounding than Gemini narratives |

---

## 16. Testing Strategy

### Backend Tests (29 tests + 6 subtests)

- **Unit tests with fake providers**: No model downloads required; verifies pipeline logic, ownership, RBAC
- **Authentication tests**: Registration, login, JWT validation, token expiration
- **Ownership isolation**: User A cannot access User B's records or media
- **Admin RBAC**: Admin-only endpoints reject regular users
- **File upload validation**: Extension whitelist, media decoding validation, cleanup on failure
- **Vector cleanup**: Failed analyses clean up stored vectors to prevent orphans
- **Schema migrations**: Alembic upgrade -> check -> downgrade -> re-upgrade cycle

### Frontend Tests (5 scenarios)

- React server-side rendering of analysis results
- Correct display of missing models, OCR outcomes, similarity matches
- Safe escaping of embedded OCR text (XSS prevention)
- Production build verification (316 KB JS, 104 KB gzipped)

### Manual Verification

- Responsive breakpoints: 320px, 768px, 1024px, 1440px
- Mobile navigation accessibility
- Live platform counters
- Auth flow (login/register toggle, JWT injection, protected route redirect)

---

## 17. Future Scope & Enhancements

| Enhancement | Technical Approach |
|---|---|
| **Real-time moderation** | WebSocket endpoint + Redis pub/sub for live scan status |
| **GPU inference queue** | Celery/RQ workers with GPU access; API submits jobs, polls for results |
| **Cross-user deduplication** | Global vector index with access-control layer (for platform-wide duplicate detection) |
| **Advanced NLP** | Replace rule lexicon with a transformer-based toxicity classifier (Detoxify, Perspective API) |
| **Multi-language OCR** | Tesseract language packs + script detection for Arabic, Hindi, Chinese, etc. |
| **CSAM hash matching** | PhotoDNA or PDQ hash integration for known illegal content detection |
| **API rate limiting** | Token bucket algorithm via FastAPI middleware or Redis |
| **Kubernetes deployment** | Helm charts with horizontal pod autoscaling based on inference queue depth |
| **Webhook notifications** | POST callbacks when analysis completes (for async integrations) |
| **Model fine-tuning** | Train domain-specific classifiers on labeled moderation data |

---

## 18. Presentation Talking Points

### Opening (30 seconds)

> "Sentinel is an AI-powered content moderation platform that combines deep learning vision models, OCR, vector similarity search, and generative AI explainability into a single deployable system. It analyzes images and videos for safety risks, detects duplicates, extracts embedded text, and explains its decisions — all while being fully self-hostable with no per-image API costs."

### Key Differentiators (2 minutes)

1. **Honest AI**: When a model is unavailable, the system reports REVIEW with explicit warnings — it never fabricates safety scores.
2. **Multi-modal pipeline**: Safety + OCR + Similarity + Explainability in a single API call — not four separate services.
3. **Per-user privacy**: Vector searches are tenant-isolated. User A's uploads are invisible to User B's similarity searches.
4. **Self-hosted sovereignty**: Your media never leaves your infrastructure. No third-party API costs.
5. **Production-ready architecture**: Docker Compose stack, Alembic migrations, audit logging, RBAC, configurable thresholds.

### Demo Flow (3 minutes)

1. Show the landing page with live counters
2. Register a new account
3. Upload a safe image -> show SAFE verdict with score dials
4. Upload the same image again -> show DUPLICATE detection with similarity score
5. Show the history page with search and filtering
6. (If admin) Show the admin dashboard with telemetry and audit logs

### Closing (30 seconds)

> "Sentinel is not a replacement for human moderators — it's a force multiplier. It handles the first-pass triage at machine speed so humans can focus on the edge cases that require judgment. Every design decision reflects this philosophy: when in doubt, mark REVIEW and let a human decide."

---

## 19. Likely Viva / Interview Questions & Answers

### Q1: Why did you choose FastAPI over Django?

**A:** FastAPI is async-native, which is critical for our use case. The analysis pipeline runs safety classification, OCR, and similarity search concurrently using `asyncio.gather`. Django's synchronous architecture would either block the event loop or require a separate Celery task queue. FastAPI also auto-generates OpenAPI documentation from Pydantic type hints, eliminating manual API docs. For a CPU-bound ML inference API, FastAPI with Uvicorn provides 2-5x throughput over Django/Gunicorn.

### Q2: How does your similarity search work?

**A:** We use OpenCLIP ViT-B-32 to generate a 512-dimensional L2-normalized embedding for each image (or averaged frame embeddings for video). These embeddings are stored in Qdrant, a purpose-built vector database, with `user_id` as a payload filter for tenant isolation. When a new image is uploaded, we compute its embedding, query Qdrant for the top-k nearest neighbors using cosine similarity, and return matches above 0.70 (near-match) or 0.88 (duplicate). The search excludes the current record's own vector.

### Q3: What happens if a model fails or is unavailable?

**A:** This is a core design principle. Every pipeline stage is wrapped in an `_attempt()` function that catches exceptions and returns explicit error metadata. If Falconsai fails, scores remain `null` (never fabricated). If Qdrant fails, similarity is marked unknown. The overall status defaults to `REVIEW` with human-readable warnings explaining exactly which capabilities were missing. The system never produces a false `SAFE` verdict from incomplete analysis.

### Q4: How do you handle video processing?

**A:** Videos are processed by OpenCV. We sample 1 frame per second, capped at 60 frames. Videos over 1 hour are rejected outright. Each frame is downscaled to 1024px on its longest edge. Safety scores are aggregated using worst-case logic — risk categories take their maximum across all frames; the safe score takes its minimum. This ensures a single unsafe frame in an otherwise safe video will still trigger FLAGGED status. We enforce a 30-second decode budget with per-frame time checks.

### Q5: Why Argon2 and not bcrypt?

**A:** Argon2 is the winner of the Password Hashing Competition (2015) and is recommended by OWASP's 2024 guidelines. Unlike bcrypt, Argon2 is **memory-hard**, meaning it requires a configurable amount of RAM per hash computation. This makes GPU and ASIC brute-force attacks orders of magnitude more expensive. Bcrypt is compute-hard but memory-cheap, making it increasingly vulnerable to massively parallel GPU attacks.

### Q6: How is data privacy maintained in a multi-tenant system?

**A:** Four layers of isolation: (1) All database queries filter by `user_id == current_user.id`. (2) Vector searches in Qdrant include a `user_id` payload filter — User A's embeddings are invisible to User B's queries. (3) Media files are served through an authenticated API endpoint that checks ownership — no direct filesystem URLs. (4) Admin access is granted only via CLI, never through self-registration.

### Q7: What are the limitations of your NSFW classification?

**A:** Falconsai provides binary classification (normal vs. NSFW) — it's a single-label detector. To add nuance, we use OpenCLIP zero-shot classification with four text prompts (safe, explicit, suggestive, gore). However, these are **uncalibrated zero-shot scores**, not validated specialist classifiers. The scores are independent signals that don't sum to 100. We explicitly document this: "suggestive and gore are auxiliary heuristics, not calibrated probabilities." The system must be evaluated on domain-specific labeled data before production use.

### Q8: Why store the full result as JSON alongside individual score columns?

**A:** The JSON `result` column enables fast single-query retrieval of the complete pipeline output (scores, matches, warnings, capabilities, explanation) for the detail view and history. The individual `score_*` columns exist for efficient SQL-level filtering and aggregation — for example, "show all records where score_explicit > 70" or "average safety score across the platform." This is a deliberate denormalization that trades a few extra bytes per row for significantly faster reads.

### Q9: How would you scale this for 10,000 uploads per hour?

**A:** Three changes: (1) Move inference to a **dedicated GPU worker pool** using Celery/RQ with Redis as a broker — the API submits jobs and returns immediately with a "processing" status. (2) Horizontal pod autoscaling in **Kubernetes** based on inference queue depth. (3) Shared model loading — instead of each worker loading its own weights, use a **model serving framework** like NVIDIA Triton or TorchServe that loads models once and serves multiple workers via gRPC. The Qdrant and MySQL layers already support horizontal scaling natively.

### Q10: What is the role of Gemini in your pipeline?

**A:** Gemini is **optional and purely additive**. It receives a representative video frame, the computed safety scores, and extracted OCR text, then generates a 2-3 sentence natural-language explanation. Crucially, Gemini **never changes the computed decision** (SAFE/FLAGGED/REVIEW). It's an explainability layer, not a decision-maker. When Gemini is unavailable, the system falls back to a deterministic computed-signal summary. The prompt explicitly instructs Gemini not to identify people, not to invent scores, and to treat all OCR text as untrusted content.

### Q11: How do your database migrations work?

**A:** We use **Alembic**, which is SQLAlchemy's migration framework. Migration scripts are version-controlled in `backend/alembic/`. In Docker, the container runs `alembic upgrade head` before starting the API, ensuring the schema is always current. In development, SQLAlchemy's `create_all()` creates tables directly from model definitions. We verified the full migration lifecycle: upgrade -> schema check -> downgrade -> re-upgrade on an isolated test database.

### Q12: Explain the CORS configuration.

**A:** CORS (Cross-Origin Resource Sharing) is configured in FastAPI middleware. The `CORS_ORIGINS` setting specifies which frontend origins can call the API (e.g., `http://localhost:5173` for dev, `http://localhost:8080` for Docker). We allow `GET`, `POST`, `DELETE` methods and `Authorization` + `Content-Type` headers. Credentials are disabled because we use Bearer token auth, not cookies. This prevents unauthorized websites from making API calls with a user's browser session.

### Q13: What would you change for a production deployment?

**A:** (1) HTTPS with TLS certificates. (2) Move JWT from localStorage to HttpOnly cookies with CSRF protection. (3) Rate limiting on authentication and analysis endpoints. (4) Secret management via Vault or cloud KMS instead of `.env` files. (5) Object storage (S3/GCS) instead of local filesystem for uploads. (6) Inference queue with GPU workers instead of in-process models. (7) Monitoring with Prometheus/Grafana. (8) Regular backups with point-in-time recovery. (9) Data retention policies with automated purging. (10) Model validation on domain-specific labeled data.

---

## 20. One-Liner Summaries for Quick Recall

| Component | One-Liner |
|---|---|
| **Sentinel** | AI-powered content moderation platform combining vision models, OCR, vector similarity, and generative explainability |
| **Falconsai** | Lightweight binary NSFW classifier from Hugging Face (~500MB, CPU-capable) |
| **OpenCLIP ViT-B-32** | Dual-purpose model: zero-shot 4-category classification + 512-d embedding generation |
| **Tesseract** | Open-source OCR engine that extracts embedded text from images/video frames |
| **Qdrant** | Rust-based vector database for cosine similarity search with tenant filtering |
| **Gemini** | Google's multimodal AI that generates natural-language explanations of moderation decisions |
| **FastAPI** | Async Python web framework with auto-generated OpenAPI docs and Pydantic validation |
| **SQLAlchemy** | Python ORM enabling database-agnostic code (SQLite dev -> MySQL prod) |
| **Argon2** | Memory-hard password hashing algorithm; PHC competition winner; OWASP recommended |
| **JWT** | Stateless authentication tokens enabling horizontal scaling without session stores |
| **Vite** | ESBuild-based dev server with sub-300ms startup and HMR for React development |
| **Tailwind CSS** | Utility-first CSS framework enabling rapid consistent UI development with automatic purging |
| **Docker Compose** | Multi-container orchestration: MySQL + Qdrant + Backend + Frontend in one command |
| **Alembic** | Database migration tool that auto-runs on container startup for schema versioning |

---

> **Final Note for the Examiner / Interviewer:** Every architectural decision in Sentinel prioritizes **honesty over convenience**. The system will never tell you content is safe when it doesn't have the models to verify that claim. This "truthful degradation" philosophy — reporting REVIEW with explicit warnings when capabilities are missing — is what separates a responsible AI system from a dangerous one.

---

*Generated from the Sentinel project source code at `C:\Users\vishn\Desktop\Sentinal`*

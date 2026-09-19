# Sentinel inference package

`await analyze_media(path, mode, user_id, record_id)` accepts `nsfw`, `similarity`, or `combined`. Heavy libraries and model downloads are lazy. The verified API environment uses Python 3.12 and Pillow/OpenCV; use Python 3.11 or 3.12 and `pip install -r requirements-ai.txt` for the optional full inference stack. A Tesseract executable must be installed separately for OCR.

## Configuration

| Variable | Default / purpose |
|---|---|
| `ENABLE_AI_MODELS` | `false`; set `true` to allow loading/downloading Falconsai and OpenCLIP weights on first use |
| `QDRANT_URL` | Unset; e.g. `http://localhost:6333` |
| `QDRANT_API_KEY` | Database API key for a remote Qdrant server; not used by local storage |
| `QDRANT_LOCAL_PATH` | Optional persistent local storage directory, e.g. `data/qdrant`; used only when `QDRANT_URL` is empty. Single backend process only. |
| `HF_HOME` | Model download/cache directory, e.g. `data/models` from the backend working directory |
| `GEMINI_API_KEY` | Optional; when set, the representative frame and up to 3,000 OCR characters are sent to Google's Gemini service for explanation |
| `GEMINI_MODEL` | `gemini-3.6-flash`, replace with a model available to your account |
| `TESSERACT_CMD` | `tesseract` from PATH; may be an absolute executable path |
| `SENTINEL_TEXT_LEXICON` | Comma-separated replacement for the small built-in text safety phrase list; an empty string disables terms |

`get_capabilities()` reports configured dependencies, not service health or successfully loaded weights. Per-result `checks_complete` records actual completed stages. No service/model is contacted during import.

## Score and status contract

All scores and match values are percentages (0–100). Unknown category/similarity scores are `null`, never generated sample values. Safe and explicit come only from Falconsai's binary normal/NSFW classification. OpenCLIP ViT-B-32 (`laion2b_s34b_b79k`) supplies auxiliary prompt-relative suggestive/gore scores; its safe/explicit prompt rankings never override the trained binary classifier. Each video's risk categories take their maxima independently across samples; safe takes its minimum. Consequently the four signals **do not sum to 100** and **are not calibrated probabilities**. Suggestive/gore prompts are auxiliary heuristics, not validated specialist classifiers. If auxiliary loading fails, binary results survive and missing categories remain null.

Any visual risk signal at least 70, a configured OCR term, or a duplicate yields `FLAGGED`. Risk signals from 40 to below 70, near matches, incomplete requested checks, animated first-frame-only decoding, or truncated video analysis yield `REVIEW`. `SAFE` means all requested checks finished and their signals stayed below these thresholds; similarity-only SAFE is not a content safety verdict. OCR is a transparent whole-word/phrase rule list, normalizes Unicode and case, and does not establish intent or comprehensively detect hateful text.

OpenCLIP embeddings are 512-dimensional and L2-normalized. Video embeddings average normalized sampled-frame embeddings, then normalize again. Qdrant searches and deletes always filter by `user_id`; searches exclude the current record, only return cosine matches at least 0.70, and mark duplicates at least 0.88. `matches[].score` is percent cosine similarity, not an exact-duplicate probability. Store/query failures return unknown similarity and REVIEW. Collection: `sentinel_embeddings` (512 dimensions, cosine). Do not mix embeddings from other model versions into this collection.

Images over 40 megapixels are rejected, decoded frames are reduced to 1024 pixels on their longest edge, and videos over one hour are rejected. Videos sample one frame per second, at most 60 frames. Longer videos are explicitly partial and require review. Sampling can miss events between frames; small text may be lost during resizing. Decode elapsed time is checked between frames (30-second budget); this is not a hard OS-level decoder timeout. Deployments handling hostile media should isolate workers and enforce OS memory/time limits.

Gemini is optional and never changes computed decisions. It describes visible content and relevant text, and can explain a possible disagreement between that evidence and model scores. When unavailable, the narrative is a deterministic summary labeled `explanation_source=computed_signals`, with an actionable failure reason in warnings. A configured Gemini key opts into transmitting uploaded content to that service. Treat narratives as untrusted generated text and render them as text. Restart the backend after changing `GEMINI_MODEL`; old stored results are not rewritten, so re-analyze media to get corrected scores and a fresh explanation.

Invalid media raises `ValueError`. Optional inference/service failures return explicit warnings and incomplete results. `await delete_record(record_id, user_id)` (alias `delete_vector`) deletes using both tenant and record filters and raises on configured-service failure, enabling the caller to avoid silent orphaning.

## Verification

From `backend`: `python -m unittest discover -s ai_engine/tests -v`. Tests use fake providers; they do not download model weights or call cloud services. Full model quality and latency need validation on a representative labeled dataset before production use.

Official API references: [OpenCLIP](https://github.com/mlfoundations/open_clip), [Qdrant client](https://github.com/qdrant/qdrant-client), [Qdrant filters](https://qdrant.tech/documentation/search/filtering/), [Google Gen AI SDK](https://github.com/googleapis/python-genai).

Run `python -m ai_engine.verify` from `backend` to download/cache the real models and verify image/video inference, OCR, duplicate matching, tenant isolation, and deletion using synthetic media and temporary local vectors. This explicit verification requires the AI packages; it is separate from the offline unit suite. It does not call Gemini or change account records.

Remote Qdrant collections get keyword indexes for `user_id` and `record_id` before filtering, including when an older collection already exists. The configured database key needs permission to create the collection and its indexes and to read/write/delete points. Local storage uses the same tenant filters without payload indexes.

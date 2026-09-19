"""Asynchronous orchestration with truthful degradation when AI is unavailable."""

import asyncio
import logging
from pathlib import Path

from . import providers, vectors
from .lexicon import evaluate_text
from .media import sample_media

logger = logging.getLogger(__name__)
get_capabilities = providers.get_capabilities
EMPTY_SCORES = {"safe": None, "explicit": None, "suggestive": None, "gore": None}


async def _attempt(function, *args):
    try:
        return await asyncio.to_thread(function, *args), None
    except Exception as exc:
        logger.warning("AI adapter %s failed: %s", getattr(function, "__name__", type(function).__name__), type(exc).__name__)
        return None, str(exc) if isinstance(exc, providers.GeminiExplanationError) else type(exc).__name__


async def analyze_media(path: Path, mode: str, user_id: str, record_id: str) -> dict:
    mode = mode.lower()
    if mode not in ("nsfw", "similarity", "combined"):
        raise ValueError("Analysis mode must be nsfw, similarity, or combined.")
    if not user_id or not record_id:
        raise ValueError("Analysis requires user and record identifiers.")
    frames, warnings = await asyncio.to_thread(sample_media, Path(path))
    media_complete = not any(not warning.startswith("Video sampling analyzes") for warning in warnings)
    capabilities = get_capabilities()
    safety_requested = mode in ("nsfw", "combined")
    similarity_requested = mode in ("similarity", "combined")
    result = {
        "scores": dict(EMPTY_SCORES), "extracted_text": "", "text_flagged": False,
        "text_flag_reason": None, "ai_explanation": None, "matches": [],
        "similarity_score": None, "is_duplicate": False, "overall_status": "REVIEW",
        "capabilities": capabilities, "warnings": warnings, "frames_analyzed": len(frames),
        "vector_id": None, "representative_frame_index": 0,
        "checks_complete": {"media": media_complete, "safety": False, "ocr": False, "similarity": False},
        "score_semantics": "Independent model signals, not a probability distribution. Safe and explicit come only from the binary Falconsai normal/NSFW classifier; suggestive and gore use uncalibrated OpenCLIP zero-shot prompts and do not override the binary scores.",
    }
    operations = {}
    if safety_requested:
        if capabilities["nsfw"]:
            operations["nsfw"] = _attempt(providers.classify, frames)
        else:
            warnings.append("Visual NSFW classification is unavailable. Enable AI models and install the optional dependencies.")
        if capabilities["ocr"]:
            operations["ocr"] = _attempt(providers.extract_text, frames)
        else:
            warnings.append("OCR is unavailable. Install Tesseract and pytesseract to analyze embedded text.")
        warnings.append("Text safety uses a limited configurable phrase list and requires human interpretation.")
    if similarity_requested:
        if capabilities["embeddings"] and capabilities["vector_search"]:
            operations["similarity"] = _attempt(providers.embed, frames)
        else:
            warnings.append("Visual similarity is unavailable. Enable OpenCLIP and configure QDRANT_LOCAL_PATH for local storage or QDRANT_URL for a Qdrant server.")
    outcomes = dict(zip(operations, await asyncio.gather(*operations.values())))
    for name, (value, error) in outcomes.items():
        if error:
            warnings.append(f"{name.upper()} processing failed ({error}); that result is unavailable.")
            capabilities[name] = False
            continue
        if name == "nsfw":
            result["scores"], result["representative_frame_index"] = value
            result["checks_complete"]["safety"] = all(score is not None for score in result["scores"].values())
            if result["checks_complete"]["safety"]:
                warnings.append("Suggestive and gore are uncalibrated OpenCLIP zero-shot scores; they are not validated specialist classifiers.")
        elif name == "ocr":
            result["checks_complete"]["ocr"] = True
            result["extracted_text"] = value
            result["text_flagged"], result["text_flag_reason"] = evaluate_text(value)
        elif name == "similarity":
            stored, error = await _attempt(vectors.search_and_store, value, user_id, record_id)
            if error:
                warnings.append(f"Vector search or persistence failed ({error}); similarity is unavailable.")
                capabilities["vector_search"] = False
            else:
                result["matches"], result["vector_id"] = stored
                result["checks_complete"]["similarity"] = True
                result["similarity_score"] = result["matches"][0]["score"] if result["matches"] else 0.0
                top_match = result["matches"][0] if result["matches"] else {}
                raw_similarity = top_match.get("cosine_score", result["similarity_score"] / 100)
                result["is_duplicate"] = raw_similarity >= 0.88
    explicit = result["scores"]["explicit"]
    risks = [result["scores"][key] for key in ("explicit", "suggestive", "gore") if result["scores"][key] is not None]
    if safety_requested and not result["checks_complete"]["safety"]:
        warnings.append("Visual safety coverage is incomplete; unavailable category scores remain null.")
    safety_complete = not safety_requested or (result["checks_complete"]["safety"] and result["checks_complete"]["ocr"])
    similarity_complete = not similarity_requested or result["checks_complete"]["similarity"]
    if result["text_flagged"] or (risks and max(risks) >= 70):
        result["overall_status"] = "FLAGGED"
    elif result["is_duplicate"]:
        result["overall_status"] = "FLAGGED"
    elif media_complete and safety_complete and similarity_complete and (not risks or max(risks) < 40) and (result["similarity_score"] is None or result["similarity_score"] < 70):
        result["overall_status"] = "SAFE"
    summary = []
    if safety_requested:
        if not safety_complete:
            summary.append("Safety checks are incomplete; a human review is required.")
        else:
            summary.append(f"The computed safety assessment is {result['overall_status'].lower()}; model scores require contextual interpretation.")
        if explicit is not None:
            summary.append(f"The highest sampled explicit/NSFW model signal is {explicit:.1f}%.")
        if result["text_flagged"]:
            summary.append(result["text_flag_reason"] + ".")
    if similarity_requested:
        if result["similarity_score"] is None:
            summary.append("Similarity could not be assessed.")
        elif result["matches"]:
            summary.append(f"The closest stored item in your account has {result['similarity_score']:.1f}% cosine similarity.")
        else:
            summary.append("No stored item in your account met the 70% similarity threshold.")
    result["ai_explanation"] = " ".join(summary)
    result["explanation_source"] = "computed_signals"
    if capabilities["gemini"]:
        narrative, error = await _attempt(providers.explain, frames[result["representative_frame_index"]], result["scores"], result["extracted_text"], result["overall_status"])
        if error:
            warnings.append(f"Gemini explanation is unavailable ({error}); the explanation summarizes computed signals.")
            capabilities["gemini"] = False
        else:
            result["ai_explanation"] = narrative
            result["explanation_source"] = "gemini"
    for frame in frames:
        frame.close()
    return result


async def delete_vector(record_id: str, user_id: str) -> None:
    """Raise on configured-service failures so callers can avoid silent orphaning."""
    await asyncio.to_thread(vectors.delete, record_id, user_id)


delete_record = delete_vector

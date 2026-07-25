"""NSFW classification and CLIP embedding generation.

Models are loaded lazily on first use so the API can start instantly and so
test/CI environments without the model weights can still import the module.
"""

from __future__ import annotations

import io
import threading

import numpy as np
from PIL import Image, ImageSequence

from app.config import settings

_lock = threading.Lock()
_nsfw_pipeline = None
_clip_model = None
_clip_processor = None


def _load_nsfw():
    global _nsfw_pipeline
    if _nsfw_pipeline is None:
        with _lock:
            if _nsfw_pipeline is None:
                from transformers import pipeline

                _nsfw_pipeline = pipeline(
                    "image-classification", model=settings.nsfw_model_id
                )
    return _nsfw_pipeline


def _load_clip():
    global _clip_model, _clip_processor
    if _clip_model is None:
        with _lock:
            if _clip_model is None:
                import torch  # noqa: F401
                from transformers import CLIPModel, CLIPProcessor

                _clip_model = CLIPModel.from_pretrained(settings.clip_model_id)
                _clip_model.eval()
                _clip_processor = CLIPProcessor.from_pretrained(settings.clip_model_id)
    return _clip_model, _clip_processor


def load_models() -> None:
    """Eagerly load both models (used when lazy_load_models is disabled)."""
    _load_nsfw()
    _load_clip()


def extract_frames(image: Image.Image) -> list[Image.Image]:
    """Return RGB keyframes. Animated images are sampled at regular intervals."""
    n_frames = getattr(image, "n_frames", 1)
    if n_frames <= 1:
        return [image.convert("RGB")]

    step = max(1, n_frames // settings.max_gif_frames)
    frames: list[Image.Image] = []
    for idx, frame in enumerate(ImageSequence.Iterator(image)):
        if idx % step == 0:
            frames.append(frame.convert("RGB"))
        if len(frames) >= settings.max_gif_frames:
            break
    return frames or [image.convert("RGB")]


def classify_image(image: Image.Image) -> float:
    """Return the NSFW probability for a single image in [0, 1]."""
    pipe = _load_nsfw()
    predictions = pipe(image)
    for pred in predictions:
        if str(pred["label"]).lower() in {"nsfw", "porn", "explicit"}:
            return float(pred["score"])
    # If no positive label present, infer from the complement of the "normal" class.
    for pred in predictions:
        if str(pred["label"]).lower() in {"normal", "safe", "sfw", "neutral"}:
            return float(1.0 - pred["score"])
    return 0.0


def classify_media(image: Image.Image) -> tuple[float, int]:
    """Classify an image or animated GIF.

    For animated media every keyframe is scored and the maximum score is
    returned, so a single explicit frame flags the whole file.
    """
    frames = extract_frames(image)
    scores = [classify_image(frame) for frame in frames]
    return max(scores), len(frames)


def generate_embedding(image: Image.Image) -> list[float]:
    """Return an L2-normalized 512-dim CLIP embedding as a plain list."""
    import torch

    model, processor = _load_clip()
    inputs = processor(images=image.convert("RGB"), return_tensors="pt")
    with torch.no_grad():
        features = model.get_image_features(**inputs)
    vector = features[0].cpu().numpy().astype(np.float32)
    norm = np.linalg.norm(vector)
    if norm > 0:
        vector = vector / norm
    return vector.tolist()


def open_image(raw: bytes) -> Image.Image:
    return Image.open(io.BytesIO(raw))

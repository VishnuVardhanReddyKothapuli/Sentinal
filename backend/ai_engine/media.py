"""Bounded media decoding with deterministic one-frame-per-second sampling."""

import math
import time
import warnings
from pathlib import Path

from PIL import Image, ImageOps, UnidentifiedImageError

MAX_PIXELS = 40_000_000
MAX_FRAMES = 60
MAX_EDGE = 1024
MAX_VIDEO_SECONDS = 3600
Image.MAX_IMAGE_PIXELS = MAX_PIXELS


def _bounded(image: Image.Image) -> Image.Image:
    if image.width * image.height > MAX_PIXELS:
        raise ValueError("Media frame exceeds the 40 megapixel limit.")
    image = ImageOps.exif_transpose(image).convert("RGB")
    image.thumbnail((MAX_EDGE, MAX_EDGE))
    return image


def sample_media(path: Path) -> tuple[list[Image.Image], list[str]]:
    """Return decoded RGB frames. Longer videos are explicitly marked partial."""
    if not path.is_file():
        raise ValueError("Media file does not exist.")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(path) as image:
                if getattr(image, "n_frames", 1) > 1:
                    return [_bounded(image)], ["Animated image: only the first frame was analyzed."]
                return [_bounded(image)], []
    except (Image.DecompressionBombError, Image.DecompressionBombWarning) as exc:
        raise ValueError("Image exceeds the safe pixel limit.") from exc
    except (UnidentifiedImageError, OSError):
        pass

    try:
        import cv2
    except ImportError as exc:
        raise ValueError("Unsupported image or video decoding is unavailable; install opencv-python-headless.") from exc
    capture = cv2.VideoCapture(str(path))
    try:
        if not capture.isOpened():
            raise ValueError("File is not a supported, decodable image or video.")
        fps = capture.get(cv2.CAP_PROP_FPS)
        count = capture.get(cv2.CAP_PROP_FRAME_COUNT)
        width = capture.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
        if not all(math.isfinite(v) and v > 0 for v in (fps, count, width, height)):
            raise ValueError("Video metadata is invalid or missing.")
        duration = count / fps
        if width * height > MAX_PIXELS or duration > MAX_VIDEO_SECONDS:
            raise ValueError("Video exceeds the 40 megapixel or one hour limit.")
        requested = min(MAX_FRAMES, max(1, math.ceil(duration)))
        frames, notes = [], []
        started = time.monotonic()
        for second in range(requested):
            if time.monotonic() - started > 30:
                notes.append("Video decoding exceeded the time budget; analysis covers sampled frames only.")
                break
            capture.set(cv2.CAP_PROP_POS_MSEC, second * 1000)
            ok, raw = capture.read()
            if not ok:
                notes.append("Some video frames could not be decoded; analysis is partial.")
                break
            frames.append(_bounded(Image.fromarray(cv2.cvtColor(raw, cv2.COLOR_BGR2RGB))))
        if not frames:
            raise ValueError("Video contains no decodable frames.")
        if duration > MAX_FRAMES:
            notes.append("Video is longer than 60 seconds; only the first 60 one-second samples were analyzed.")
        notes.append("Video sampling analyzes one frame per second; events between samples may be missed.")
        return frames, notes
    finally:
        capture.release()

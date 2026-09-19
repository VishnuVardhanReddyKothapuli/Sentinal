from pathlib import Path
import warnings

from fastapi import HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}
VIDEO_EXTENSIONS = {'.mp4', '.mov', '.webm', '.avi', '.mkv'}


async def save_upload(file: UploadFile, target: Path, max_bytes: int) -> None:
    total = 0
    try:
        with target.open('xb') as output:
            while chunk := await file.read(1024 * 1024):
                total += len(chunk)
                if total > max_bytes:
                    raise HTTPException(413, f'Maximum upload size is {max_bytes // (1024 * 1024)} MB')
                output.write(chunk)
        if not total:
            raise HTTPException(422, 'Uploaded file is empty')
    except BaseException:
        target.unlink(missing_ok=True)
        raise
    finally:
        await file.close()


def validate_media(path: Path) -> str:
    extension = path.suffix.lower()
    if extension in IMAGE_EXTENSIONS:
        try:
            with warnings.catch_warnings():
                warnings.simplefilter('error', Image.DecompressionBombWarning)
                with Image.open(path) as image:
                    expected = {'.jpg': 'JPEG', '.jpeg': 'JPEG', '.png': 'PNG', '.webp': 'WEBP', '.gif': 'GIF'}
                    if image.format != expected[extension]:
                        raise ValueError('File content does not match its extension')
                    if image.width * image.height > 40_000_000:
                        raise ValueError('Image exceeds the 40 megapixel limit')
                    image.verify()
                with Image.open(path) as image:
                    image.load()
        except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError, Image.DecompressionBombWarning) as exc:
            raise HTTPException(422, 'Invalid or unsupported image content') from exc
        return 'IMAGE'
    if extension in VIDEO_EXTENSIONS:
        header = path.read_bytes()[:32] if path.stat().st_size < 32 else _header(path)
        valid_signature = (
            extension in {'.mp4', '.mov'} and header[4:8] == b'ftyp'
            or extension in {'.webm', '.mkv'} and header[:4] == b'\x1aE\xdf\xa3'
            or extension == '.avi' and header[:4] == b'RIFF' and header[8:12] == b'AVI '
        )
        if not valid_signature:
            raise HTTPException(422, 'Video content does not match its extension')
        try:
            import cv2
        except ImportError as exc:
            raise HTTPException(503, 'Video analysis requires the optional AI dependencies (OpenCV)') from exc
        capture = cv2.VideoCapture(str(path))
        try:
            if not capture.isOpened() or not capture.read()[0]:
                raise HTTPException(422, 'Video cannot be decoded')
        finally:
            capture.release()
        return 'VIDEO'
    raise HTTPException(415, 'Supported media: JPEG, PNG, WebP, GIF, MP4, MOV, WebM, AVI, MKV')


def _header(path: Path) -> bytes:
    with path.open('rb') as handle:
        return handle.read(32)

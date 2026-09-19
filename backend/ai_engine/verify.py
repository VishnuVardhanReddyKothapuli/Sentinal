"""Download/cache the real models and verify inference on synthetic media.

Run from backend: .venv/Scripts/python.exe -m ai_engine.verify
Uses temporary local vectors, never existing accounts or cloud explanations.
"""
import asyncio
import json
import os
from pathlib import Path
import tempfile
import time


async def verify():
    from app.config import get_settings
    get_settings()  # Load the same private environment as the API.
    os.environ['GEMINI_API_KEY'] = ''
    os.environ['QDRANT_URL'] = ''

    from PIL import Image, ImageDraw, ImageFont
    from .pipeline import analyze_media, delete_record, get_capabilities

    with tempfile.TemporaryDirectory(prefix='sentinel-inference-') as directory:
        folder = Path(directory)
        os.environ['QDRANT_LOCAL_PATH'] = str(folder / 'vectors')
        image = Image.new('RGB', (640, 400), 'white')
        ImageDraw.Draw(image).text((45, 150), 'SENTINEL TEST IMAGE', fill='black', font=ImageFont.load_default(size=40))
        path = folder / 'test.png'
        image.save(path)
        image.close()

        ready = get_capabilities()
        required = ['nsfw', 'suggestive', 'gore', 'ocr', 'embeddings', 'vector_search']
        missing = [name for name in required if not ready.get(name)]
        if missing:
            raise RuntimeError('Missing capabilities: ' + ', '.join(missing))
        print('Loading actual Falconsai/OpenCLIP models and running OCR. First run downloads weights.', flush=True)
        started = time.monotonic()
        first = await analyze_media(path, 'combined', 'verification-a', 'first')
        print(json.dumps({'checks': first['checks_complete'], 'scores': first['scores'], 'ocr': first['extracted_text'], 'warnings': first['warnings'], 'elapsed_seconds': round(time.monotonic() - started, 1)}), flush=True)
        assert all(first['checks_complete'].values()), 'One or more inference stages failed'
        assert 'SENTINEL' in first['extracted_text'].upper(), 'OCR did not read the synthetic text'
        assert not first['is_duplicate']

        second = await analyze_media(path, 'similarity', 'verification-a', 'second')
        assert second['is_duplicate'] and second['matches'][0]['record_id'] == 'first', 'Identical image was not matched'
        other = await analyze_media(path, 'similarity', 'verification-b', 'other')
        assert other['checks_complete']['similarity'] and not other['matches'], 'Cross-account vector leakage'
        await delete_record('first', 'verification-a')
        await delete_record('second', 'verification-a')
        after_delete = await analyze_media(path, 'similarity', 'verification-a', 'after-delete')
        assert not after_delete['matches'], 'Deleted vectors remained searchable'
        print('Real image safety, OCR, 512d embeddings, duplicate match, account isolation, and deletion passed.', flush=True)

        import cv2
        import numpy as np
        video = folder / 'test.avi'
        writer = cv2.VideoWriter(str(video), cv2.VideoWriter_fourcc(*'MJPG'), 5, (640, 400))
        assert writer.isOpened(), 'Cannot encode synthetic video'
        try:
            with Image.open(path) as source:
                frame = cv2.cvtColor(np.asarray(source), cv2.COLOR_RGB2BGR)
            for _ in range(10):
                writer.write(frame)
        finally:
            writer.release()
        result = await analyze_media(video, 'combined', 'verification-video', 'video')
        assert result['frames_analyzed'] == 2 and all(result['checks_complete'].values()), 'Video inference was incomplete'
        print('Real video safety, OCR, and similarity passed (2 sampled frames).', flush=True)


if __name__ == '__main__':
    asyncio.run(verify())

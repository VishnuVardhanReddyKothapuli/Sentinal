import asyncio
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from PIL import Image

from ai_engine import pipeline, providers, vectors
from ai_engine.lexicon import evaluate_text
from ai_engine.media import sample_media


def capabilities(**overrides):
    values = {"nsfw": False, "ocr": False, "embeddings": False, "vector_search": False, "gemini": False, "suggestive": False, "gore": False}
    values.update(overrides)
    return values


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.path = Path(self.directory.name) / "input.png"
        Image.new("RGB", (24, 24), "white").save(self.path)

    def tearDown(self):
        self.directory.cleanup()

    def analyze(self, mode="combined"):
        return asyncio.run(pipeline.analyze_media(self.path, mode, "tenant-a", "record-a"))

    def test_missing_models_never_claim_safe_or_fabricate_scores(self):
        with patch.object(pipeline, "get_capabilities", return_value=capabilities()):
            result = self.analyze()
        self.assertEqual(result["overall_status"], "REVIEW")
        self.assertTrue(all(value is None for value in result["scores"].values()))
        self.assertIsNone(result["similarity_score"])
        self.assertGreater(len(result["warnings"]), 0)

    def test_flagged_ocr_without_models(self):
        with patch.object(pipeline, "get_capabilities", return_value=capabilities(ocr=True)), patch.object(providers, "extract_text", return_value="KILL\nyourself"):
            result = self.analyze("nsfw")
        self.assertTrue(result["text_flagged"])
        self.assertEqual(result["overall_status"], "FLAGGED")

    def test_whole_words_and_unicode(self):
        self.assertFalse(evaluate_text("Scunthorpe shitake harmless")[0])
        self.assertTrue(evaluate_text("ＦＵＣＫ!")[0])
        with patch.dict(os.environ, {"SENTINEL_TEXT_LEXICON": "danger phrase"}):
            self.assertTrue(evaluate_text("a DANGER\n phrase here")[0])
            self.assertFalse(evaluate_text("danger phrases")[0])

    def test_partial_binary_scores_require_review(self):
        scores = {"safe": 99, "explicit": 1, "suggestive": None, "gore": None}
        with patch.object(pipeline, "get_capabilities", return_value=capabilities(nsfw=True, ocr=True)), patch.object(providers, "classify", return_value=(scores, 0)), patch.object(providers, "extract_text", return_value=""):
            self.assertEqual(self.analyze("nsfw")["overall_status"], "REVIEW")

    def test_complete_low_scores_can_be_safe_and_gore_flags(self):
        for gore, expected in [(1, "SAFE"), (50, "REVIEW"), (90, "FLAGGED")]:
            scores = {"safe": 99, "explicit": 1, "suggestive": 1, "gore": gore}
            with self.subTest(gore=gore), patch.object(pipeline, "get_capabilities", return_value=capabilities(nsfw=True, ocr=True)), patch.object(providers, "classify", return_value=(scores, 0)), patch.object(providers, "extract_text", return_value=""):
                self.assertEqual(self.analyze("nsfw")["overall_status"], expected)

    def test_ocr_failure_blocks_safe(self):
        scores = {"safe": 99, "explicit": 1, "suggestive": 1, "gore": 1}
        with patch.object(pipeline, "get_capabilities", return_value=capabilities(nsfw=True, ocr=True)), patch.object(providers, "classify", return_value=(scores, 0)), patch.object(providers, "extract_text", side_effect=RuntimeError("offline")):
            result = self.analyze("nsfw")
        self.assertEqual(result["overall_status"], "REVIEW")
        self.assertFalse(result["checks_complete"]["ocr"])

    def test_similarity_thresholds_and_tenant_arguments(self):
        for score, expected, duplicate in [(69.9, "SAFE", False), (70, "REVIEW", False), (88, "FLAGGED", True)]:
            with self.subTest(score=score), patch.object(pipeline, "get_capabilities", return_value=capabilities(embeddings=True, vector_search=True)), patch.object(providers, "embed", return_value=[1.0] + [0.0] * 511), patch.object(vectors, "search_and_store", return_value=([{"record_id": "previous", "score": score}], "vector")) as store:
                result = self.analyze("similarity")
                self.assertEqual(result["overall_status"], expected)
                self.assertEqual(result["is_duplicate"], duplicate)
                self.assertEqual(store.call_args.args[1:], ("tenant-a", "record-a"))

    def test_invalid_bytes_rejected(self):
        self.path.write_bytes(b"this is not an image")
        with self.assertRaises(ValueError):
            self.analyze()

    def test_rounding_does_not_create_duplicate(self):
        with patch.object(pipeline, "get_capabilities", return_value=capabilities(embeddings=True, vector_search=True)), patch.object(providers, "embed", return_value=[1.0] + [0.0] * 511), patch.object(vectors, "search_and_store", return_value=([{"record_id": "previous", "score": 88.0, "cosine_score": 0.87999}], "vector")):
            result = self.analyze("similarity")
        self.assertFalse(result["is_duplicate"])
        self.assertEqual(result["overall_status"], "REVIEW")

    def test_zero_shot_scores_preserve_worst_case_independently(self):
        fake = MagicMock(return_value=[[{"label": "normal", "score": 0.99}, {"label": "nsfw", "score": 0.01}], [{"label": "normal", "score": 0.1}, {"label": "nsfw", "score": 0.9}]])
        with patch.object(providers, "_classifier", return_value=fake), patch.object(providers, "get_capabilities", return_value={"suggestive": True}), patch.object(providers, "classify_auxiliary", return_value=[[0.1, 0.01, 0.01, 0.88], [0.8, 0.1, 0.05, 0.05]]):
            scores, representative = providers.classify([object(), object()])
        self.assertEqual(scores["explicit"], 90)
        self.assertEqual(scores["gore"], 88)
        self.assertEqual(scores["safe"], 10)
        self.assertEqual(representative, 1)


class VectorIsolationTests(unittest.TestCase):
    def test_mandatory_tenant_filter_in_search_and_delete(self):
        # A minimal typed-model substitute makes this contract test independent of Qdrant installation.
        def model(**kwargs):
            return SimpleNamespace(**kwargs)
        models = SimpleNamespace(FieldCondition=model, MatchValue=model, Filter=model, VectorParams=model, Distance=SimpleNamespace(COSINE="cosine"), PointStruct=model, FilterSelector=model)
        fake_client = MagicMock()
        fake_client.collection_exists.return_value = True
        fake_client.query_points.return_value = SimpleNamespace(points=[
            SimpleNamespace(payload={"user_id": "tenant-b", "record_id": "secret"}, score=0.99),
            SimpleNamespace(payload={"user_id": "tenant-a", "record_id": "old"}, score=0.89),
        ])
        with patch.dict(os.environ, {"QDRANT_URL": ""}), patch.dict("sys.modules", {"qdrant_client": SimpleNamespace(models=models)}), patch.object(vectors, "_client", return_value=fake_client):
            matches, _ = vectors.search_and_store([1.0] + [0.0] * 511, "tenant-a", "new")
            self.assertEqual([row["record_id"] for row in matches], ["old"])
            filters = fake_client.query_points.call_args.kwargs["query_filter"]
            self.assertEqual(filters.must[0].match.value, "tenant-a")
            self.assertEqual(filters.must_not[0].match.value, "new")
            self.assertEqual(fake_client.query_points.call_args.kwargs["score_threshold"], 0.7)
            vectors.delete("new", "tenant-a")
            deleted = fake_client.delete.call_args.kwargs["points_selector"].filter.must
            self.assertEqual([(item.key, item.match.value) for item in deleted], [("user_id", "tenant-a"), ("record_id", "new")])


class MediaTests(unittest.TestCase):
    def test_real_video_decoding_and_degraded_pipeline(self):
        import cv2
        import numpy as np
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "video.avi"
            writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"MJPG"), 5, (32, 32))
            self.assertTrue(writer.isOpened(), "OpenCV MJPG encoder must be available for this media verification")
            for index in range(12):
                writer.write(np.full((32, 32, 3), index * 15, dtype=np.uint8))
            writer.release()
            with patch.object(pipeline, "get_capabilities", return_value=capabilities()):
                result = asyncio.run(pipeline.analyze_media(path, "combined", "tenant-a", "video-record"))
        self.assertEqual(result["frames_analyzed"], 3)
        self.assertEqual(result["overall_status"], "REVIEW")
        self.assertIsNone(result["scores"]["explicit"])

    def test_video_cap_and_sampling(self):
        import numpy as np
        cv2 = SimpleNamespace(CAP_PROP_FPS=1, CAP_PROP_FRAME_COUNT=2, CAP_PROP_FRAME_WIDTH=3, CAP_PROP_FRAME_HEIGHT=4, CAP_PROP_POS_MSEC=5, COLOR_BGR2RGB=6)
        capture = MagicMock()
        capture.isOpened.return_value = True
        capture.get.side_effect = lambda prop: {1: 30, 2: 3600, 3: 24, 4: 24}[prop]
        capture.read.return_value = (True, np.zeros((24, 24, 3), dtype=np.uint8))
        cv2.VideoCapture = MagicMock(return_value=capture)
        cv2.cvtColor = lambda frame, mode: frame
        with tempfile.TemporaryDirectory() as directory, patch.dict("sys.modules", {"cv2": cv2}):
            path = Path(directory) / "video.mp4"
            path.write_bytes(b"fake video container")
            frames, warnings = sample_media(path)
        self.assertEqual(len(frames), 60)
        self.assertEqual([call.args[1] for call in capture.set.call_args_list], list(range(0, 60000, 1000)))
        self.assertTrue(any("first 60" in note for note in warnings))
        capture.release.assert_called_once()
        for frame in frames:
            frame.close()


if __name__ == "__main__":
    unittest.main()

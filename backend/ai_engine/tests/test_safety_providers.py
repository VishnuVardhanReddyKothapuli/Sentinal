"""Regression coverage for binary NSFW scores and auxiliary signal isolation."""

import unittest
from unittest.mock import MagicMock, patch

from ai_engine import providers


def binary(normal, nsfw):
    return [{"label": "normal", "score": normal}, {"label": "nsfw", "score": nsfw}]


class SafetyProviderTests(unittest.TestCase):
    def classify(self, predictions, auxiliary=None):
        frames = [object() for _ in predictions]
        with patch.object(providers, "_classifier", return_value=MagicMock(return_value=predictions)), \
                patch.object(providers, "get_capabilities", return_value={"suggestive": auxiliary is not None}), \
                patch.object(providers, "classify_auxiliary", return_value=auxiliary):
            return providers.classify(frames)

    def test_prompt_relative_explicit_cannot_override_binary_nsfw(self):
        # Captured from cached-model inference on the user's original uploads.
        # No personal image fixture is needed to reproduce the aggregation bug.
        cases = [
            ("clothed driver", 0.999748170375824, 0.00025179775548167527,
             [0.11029534786939621, 0.5953680276870728, 0.293049693107605, 0.0012868910562247038],
             {"safe": 99.97, "explicit": 0.03, "suggestive": 29.3, "gore": 0.13}),
            ("certificate", 0.999725878238678, 0.00027408936875872314,
             [0.03891894221305847, 0.7935047149658203, 0.1308201253414154, 0.03675621747970581],
             {"safe": 99.97, "explicit": 0.03, "suggestive": 13.08, "gore": 3.68}),
        ]
        for name, normal, nsfw, auxiliary, expected in cases:
            with self.subTest(media=name):
                scores, index = self.classify([binary(normal, nsfw)], [auxiliary])
                self.assertEqual(scores, expected)
                self.assertEqual(index, 0)

    def test_auxiliary_safe_cannot_hide_binary_nsfw(self):
        scores, _ = self.classify([binary(0.01, 0.99)], [[0.99, 0.005, 0.004, 0.001]])
        self.assertEqual(scores["safe"], 1)
        self.assertEqual(scores["explicit"], 99)

    def test_video_preserves_each_risk_and_selects_actual_riskiest_frame(self):
        scores, index = self.classify(
            [binary(0.99, 0.01), binary(0.2, 0.8), binary(0.98, 0.02)],
            [[0.01, 0.98, 0.005, 0.005], [0.9, 0.01, 0.04, 0.05], [0.02, 0.02, 0.01, 0.95]],
        )
        self.assertEqual(scores, {"safe": 20, "explicit": 80, "suggestive": 4, "gore": 95})
        self.assertEqual(index, 2)

    def test_auxiliary_failure_preserves_binary_result(self):
        with patch.object(providers, "_classifier", return_value=MagicMock(return_value=[binary(0.98, 0.02)])), \
                patch.object(providers, "get_capabilities", return_value={"suggestive": True}), \
                patch.object(providers, "classify_auxiliary", side_effect=RuntimeError("offline")):
            scores, index = providers.classify([object()])
        self.assertEqual(scores, {"safe": 98, "explicit": 2, "suggestive": None, "gore": None})
        self.assertEqual(index, 0)

    def test_malformed_auxiliary_results_do_not_discard_binary_result(self):
        for auxiliary in ([], [[0.1, 0.9]], [[0.1, 0.7, float("nan"), 0.2]], [[0.1, 0.7, -0.1, 0.3]]):
            with self.subTest(auxiliary=auxiliary):
                scores, _ = self.classify([binary(0.98, 0.02)], auxiliary)
                self.assertEqual(scores, {"safe": 98, "explicit": 2, "suggestive": None, "gore": None})

    def test_no_auxiliary_does_not_fabricate_missing_category_scores(self):
        scores, _ = self.classify([binary(0.98, 0.02)])
        self.assertEqual(scores, {"safe": 98, "explicit": 2, "suggestive": None, "gore": None})

    def test_single_frame_flat_predictions_are_supported(self):
        with patch.object(providers, "_classifier", return_value=MagicMock(return_value=binary(0.97, 0.03))), \
                patch.object(providers, "get_capabilities", return_value={"suggestive": False}):
            scores, index = providers.classify([object()])
        self.assertEqual(scores["explicit"], 3)
        self.assertEqual(index, 0)

    def test_missing_binary_frame_cannot_claim_complete_video_analysis(self):
        with patch.object(providers, "_classifier", return_value=MagicMock(return_value=[binary(0.99, 0.01)])):
            with self.assertRaisesRegex(RuntimeError, "number of frame results"):
                providers.classify([object(), object()])

    def test_empty_frames_rejected_before_loading_model(self):
        with patch.object(providers, "_classifier") as classifier:
            with self.assertRaises(ValueError):
                providers.classify([])
        classifier.assert_not_called()

    def test_invalid_binary_scores_and_labels_fail_truthfully(self):
        for predictions in ([{"label": "LABEL_0", "score": 1}], binary(float("nan"), 0.1), binary(0.9, 1.1)):
            with self.subTest(predictions=predictions):
                with self.assertRaises(RuntimeError):
                    self.classify([predictions])


if __name__ == "__main__":
    unittest.main()

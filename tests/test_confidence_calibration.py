"""
Test Suite for Confidence Calibration Buckets & Calibration Error Score.
"""

import pytest
from backend.evaluation import BenchmarkEvaluator


def test_confidence_calibration_buckets():
    evaluator = BenchmarkEvaluator()

    pairs = [
        # (confidence, is_correct)
        (95.0, True),
        (92.0, True),
        (98.0, True),
        (90.0, True),
        (75.0, True),
        (80.0, True),
        (60.0, True),
        (40.0, False)
    ]

    buckets, cal_score = evaluator.compute_confidence_calibration(pairs)

    assert len(buckets) == 4
    labels = [b["label"] for b in buckets]
    assert labels == ["0-49", "50-69", "70-89", "90-100"]

    # 90-100 bucket has 4 predictions, all correct
    b_high = [b for b in buckets if b["label"] == "90-100"][0]
    assert b_high["predictions"] == 4
    assert b_high["correct"] == 4
    assert b_high["accuracy"] == 100.0

    # Overall calibration score is high
    assert cal_score >= 80.0

"""
Test Suite for Commerce Readiness Benchmark & Confusion Matrix Generation.
"""

import pytest
from backend.evaluation import BenchmarkEvaluator


def test_commerce_confusion_matrix_generation():
    evaluator = BenchmarkEvaluator()

    pairs = [
        ("READY_FOR_COMMERCE", "READY_FOR_COMMERCE"),
        ("READY_FOR_COMMERCE", "READY_FOR_COMMERCE"),
        ("REVIEW_REQUIRED", "REVIEW_REQUIRED"),
        ("NOT_READY", "NOT_READY")
    ]

    conf_data = evaluator.compute_confusion_matrix(pairs)

    matrix = conf_data["matrix"]
    assert matrix["READY_FOR_COMMERCE"]["READY_FOR_COMMERCE"] == 2
    assert matrix["REVIEW_REQUIRED"]["REVIEW_REQUIRED"] == 1
    assert matrix["NOT_READY"]["NOT_READY"] == 1
    assert matrix["READY_FOR_COMMERCE"]["REVIEW_REQUIRED"] == 0

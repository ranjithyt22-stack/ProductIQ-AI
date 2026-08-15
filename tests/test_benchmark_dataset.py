"""
Test Suite for Benchmark Dataset Integrity and Ground-Truth Schemas.
"""

import os
import json
import pytest
from backend.evaluation import BenchmarkEvaluator


def test_benchmark_dataset_contains_all_10_products():
    evaluator = BenchmarkEvaluator()
    cases = evaluator.load_benchmark_cases()

    assert len(cases) == 10, f"Expected 10 benchmark products, got {len(cases)}"

    expected_ids = [
        "BENCH-001", "BENCH-002", "BENCH-003", "BENCH-004", "BENCH-005",
        "BENCH-006", "BENCH-007", "BENCH-008", "BENCH-009", "BENCH-010"
    ]

    actual_ids = [c["product_id"] for c in cases]
    for exp_id in expected_ids:
        assert exp_id in actual_ids, f"Missing benchmark product: {exp_id}"


def test_benchmark_ground_truth_and_source_coherence():
    evaluator = BenchmarkEvaluator()
    cases = evaluator.load_benchmark_cases()

    for case in cases:
        gt = case["ground_truth"]
        src_text = case["source_text"]

        assert gt.get("product_name"), f"Missing product_name in {case['product_id']}"
        assert gt.get("manufacturer"), f"Missing manufacturer in {case['product_id']}"
        assert gt.get("product_code"), f"Missing product_code in {case['product_id']}"
        assert gt.get("category"), f"Missing category in {case['product_id']}"
        assert len(gt.get("specifications", [])) >= 5, f"Expected >= 5 specs for {case['product_id']}"
        assert len(gt.get("negative_test_attributes", [])) >= 2, f"Expected >= 2 negative probes for {case['product_id']}"

        # Ensure source document is not empty
        assert len(src_text) > 100, f"Source text empty or too short for {case['product_id']}"

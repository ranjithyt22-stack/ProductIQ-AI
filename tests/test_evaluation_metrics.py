"""
Test Suite for Deterministic AI Evaluation Metrics (Precision, Recall, F1, Value Accuracy, Unit Accuracy).
"""

import pytest
from backend.evaluation import safe_div, match_attribute_name, BenchmarkEvaluator
from backend.models import MatchStatus


def test_safe_div():
    assert safe_div(10.0, 2.0) == 5.0
    assert safe_div(0.0, 10.0) == 0.0
    assert safe_div(10.0, 0.0, default=1.0) == 1.0
    assert safe_div(0.0, 0.0, default=0.0) == 0.0


def test_match_attribute_name():
    assert match_attribute_name("Bore Diameter", "bore_diameter") is True
    assert match_attribute_name("Operating Pressure", "Operating Pressure Range") is True
    assert match_attribute_name("stroke_length", "Stroke-Length") is True
    assert match_attribute_name("Rated Power", "Operating Voltage") is False


def test_single_product_evaluation_metrics():
    evaluator = BenchmarkEvaluator()

    gt = {
        "product_id": "TEST-001",
        "product_name": "Test Actuator",
        "category": "Actuator",
        "specifications": [
            {"name": "Stroke", "value": "100", "unit": "mm", "page": 1, "verbatim_evidence": "Stroke: 100 mm"},
            {"name": "Pressure", "value": "10", "unit": "bar", "page": 1, "verbatim_evidence": "Pressure: 10 bar"}
        ],
        "negative_test_attributes": ["Wireless Module"],
        "expected_readiness": "READY_FOR_COMMERCE"
    }

    # Perfectly matching prediction (with 1 MPa equivalent to 10 bar)
    pred_perfect = {
        "product": {"product_name": "Test Actuator"},
        "specifications": [
            {"name": "Stroke", "value": "100", "unit": "mm", "page": 1, "evidence": "Stroke: 100 mm", "match_status": MatchStatus.VERIFIED, "confidence": 95.0},
            {"name": "Pressure", "value": "1", "unit": "MPa", "page": 1, "evidence": "Pressure: 1 MPa", "match_status": MatchStatus.VERIFIED, "confidence": 95.0}
        ],
        "quality_score": {"status_category": "READY_FOR_COMMERCE"}
    }

    res = evaluator.evaluate_single_product(gt, pred_perfect)

    assert res["tp_count"] == 2
    assert res["fp_count"] == 0
    assert res["fn_count"] == 0
    assert res["extraction_precision"] == 100.0
    assert res["extraction_recall"] == 100.0
    assert res["extraction_f1"] == 100.0
    assert res["value_accuracy"] == 100.0
    assert res["evidence_coverage"] == 100.0
    assert res["hallucination_rate"] == 0.0
    assert res["commerce_readiness_correct"] is True

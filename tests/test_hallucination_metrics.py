"""
Test Suite for AI Hallucination Rate & Negative Control Probing.
"""

import pytest
from backend.evaluation import BenchmarkEvaluator
from backend.models import MatchStatus


def test_hallucination_detected_on_invented_negative_probe():
    evaluator = BenchmarkEvaluator()

    gt = {
        "product_id": "TEST-PROBE",
        "product_name": "Industrial Sensor",
        "category": "Sensor",
        "specifications": [
            {"name": "Temperature Range", "value": "-40 to 125", "unit": "degC"}
        ],
        "negative_test_attributes": ["Warranty Period", "Explosion Proof Rating"],
        "expected_readiness": "READY_FOR_COMMERCE"
    }

    # Model fabricates "Warranty Period = 1 year"
    pred_with_hallucination = {
        "product": {"product_name": "Industrial Sensor"},
        "specifications": [
            {"name": "Temperature Range", "value": "-40 to 125", "unit": "degC", "match_status": MatchStatus.VERIFIED, "evidence": "-40 to 125 degC", "confidence": 95.0},
            {"name": "Warranty Period", "value": "1 year", "unit": None, "match_status": MatchStatus.UNVERIFIED, "confidence": 50.0}
        ],
        "quality_score": {"status_category": "READY_FOR_COMMERCE"}
    }

    res = evaluator.evaluate_single_product(gt, pred_with_hallucination)

    assert res["hallucination_rate"] > 0.0
    assert len(res["hallucination_items"]) == 1
    assert res["hallucination_items"][0]["attribute_name"] == "Warranty Period"


def test_zero_hallucination_when_negative_probe_is_omitted():
    evaluator = BenchmarkEvaluator()

    gt = {
        "product_id": "TEST-CLEAN",
        "product_name": "Industrial Sensor",
        "category": "Sensor",
        "specifications": [
            {"name": "Temperature Range", "value": "-40 to 125", "unit": "degC"}
        ],
        "negative_test_attributes": ["Warranty Period", "Explosion Proof Rating"],
        "expected_readiness": "READY_FOR_COMMERCE"
    }

    # Clean prediction: does not fabricate unmentioned attributes
    pred_clean = {
        "product": {"product_name": "Industrial Sensor"},
        "specifications": [
            {"name": "Temperature Range", "value": "-40 to 125", "unit": "degC", "match_status": MatchStatus.VERIFIED, "evidence": "-40 to 125 degC", "confidence": 95.0}
        ],
        "quality_score": {"status_category": "READY_FOR_COMMERCE"}
    }

    res = evaluator.evaluate_single_product(gt, pred_clean)
    assert res["hallucination_rate"] == 0.0
    assert len(res["hallucination_items"]) == 0

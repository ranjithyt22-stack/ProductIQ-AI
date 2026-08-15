"""
Test Suite: Conflict Gated Commerce Readiness
Verifies that unresolved CRITICAL or HIGH conflicts strictly block READY_FOR_COMMERCE status,
and that resolving conflicts unlocks commerce readiness.
"""

import pytest
from backend.models import (
    ProductInfo, SpecificationAttribute, ValidationResult,
    ConflictRecord, ConflictSeverity, ConflictStatus,
    CommerceReadinessStatus, MatchStatus
)
from backend.scoring import calculate_quality_score


def test_open_critical_conflict_blocks_commerce_readiness():
    """An open CRITICAL conflict must force status_category to REVIEW_REQUIRED."""
    prod = ProductInfo(
        product_name="Pneumatic Cylinder",
        manufacturer="Acme",
        product_code="PC-50-100",
        category="Pneumatics",
        description="Industrial cylinder"
    )

    specs = [
        SpecificationAttribute(
            name="Operating Pressure",
            value="10",
            unit="bar",
            confidence=95.0,
            match_status=MatchStatus.VERIFIED,
            evidence="10 bar max"
        ),
        SpecificationAttribute(
            name="Bore",
            value="50",
            unit="mm",
            confidence=95.0,
            match_status=MatchStatus.VERIFIED,
            evidence="50 mm bore"
        )
    ]

    validations = [ValidationResult(rule="Field Check", status="PASS", severity="LOW", message="Valid", field="Bore")]

    critical_conf = ConflictRecord(
        conflict_id="c1",
        product_id="P1",
        attribute_name="Operating Pressure",
        severity=ConflictSeverity.CRITICAL,
        status=ConflictStatus.OPEN,
        confidence=90
    )

    score = calculate_quality_score(prod, specs, validations, conflicts=[critical_conf])
    assert score.status_category == CommerceReadinessStatus.REVIEW_REQUIRED


def test_resolved_conflict_allows_commerce_readiness():
    """Once conflict is resolved and scores are high, product achieves READY_FOR_COMMERCE."""
    prod = ProductInfo(
        product_name="Pneumatic Cylinder",
        manufacturer="Acme",
        product_code="PC-50-100",
        category="Pneumatics",
        description="Industrial cylinder"
    )

    specs = [
        SpecificationAttribute(
            name="Operating Pressure",
            value="10",
            unit="bar",
            confidence=95.0,
            match_status=MatchStatus.VERIFIED,
            evidence="10 bar max"
        ),
        SpecificationAttribute(
            name="Bore",
            value="50",
            unit="mm",
            confidence=95.0,
            match_status=MatchStatus.VERIFIED,
            evidence="50 mm bore"
        )
    ]

    validations = [ValidationResult(rule="Field Check", status="PASS", severity="LOW", message="Valid", field="Bore")]


    resolved_conf = ConflictRecord(
        conflict_id="c1",
        product_id="P1",
        attribute_name="Operating Pressure",
        severity=ConflictSeverity.CRITICAL,
        status=ConflictStatus.RESOLVED,
        confidence=90
    )

    score = calculate_quality_score(prod, specs, validations, conflicts=[resolved_conf])
    assert score.status_category == CommerceReadinessStatus.READY_FOR_COMMERCE

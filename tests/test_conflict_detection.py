"""
Test Suite: Cross-Source Conflict Detection
Verifies deterministic multi-source conflict detection, classification,
severity assignment, and dynamic conflict confidence scoring across 5 product categories.
"""

import pytest
from backend.models import (
    SpecificationAttribute, ProductInfo, ConflictType,
    ConflictSeverity, ConflictStatus, SourceReliability, MatchStatus
)
from backend.conflicts import detect_product_conflicts, determine_conflict_severity, calculate_conflict_confidence


def test_conflict_detection_value_mismatch_pneumatic_cylinder():
    """Tests value mismatch detection on Pneumatic Cylinder operating pressure."""
    specs = [
        SpecificationAttribute(
            name="Operating Pressure",
            value="10",
            unit="bar",
            source_name="Datasheet PDF",
            source_type="pdf",
            source_reliability=SourceReliability.OFFICIAL_DATASHEET,
            page=2,
            evidence="Operating pressure 10 bar max",
            confidence=95.0,
            match_status=MatchStatus.VERIFIED
        ),
        SpecificationAttribute(
            name="Operating Pressure",
            value="16",
            unit="bar",
            source_name="Manufacturer Webpage",
            source_type="url",
            source_reliability=SourceReliability.OFFICIAL_WEBSITE,
            page=1,
            evidence="Rated max pressure 16 bar",
            confidence=90.0,
            match_status=MatchStatus.VERIFIED
        )
    ]

    conflicts = detect_product_conflicts(product_id="PIQ-CYL-01", specifications=specs)
    assert len(conflicts) == 1
    c = conflicts[0]
    assert c.attribute_name == "Operating Pressure"
    assert c.conflict_type == ConflictType.VALUE_MISMATCH
    assert c.severity == ConflictSeverity.CRITICAL
    assert c.status == ConflictStatus.OPEN
    assert c.value_a == "10"
    assert c.value_b == "16"
    assert c.confidence >= 85


def test_conflict_detection_unit_mismatch_temperature_sensor():
    """Tests unit mismatch on Temperature Sensor range."""
    specs = [
        SpecificationAttribute(
            name="Temperature Range",
            value="-50 to 200",
            unit="deg C",
            source_name="Sensor Catalog",
            source_reliability=SourceReliability.MANUFACTURER_CATALOG,
            confidence=88.0,
            match_status=MatchStatus.VERIFIED
        ),
        SpecificationAttribute(
            name="Temperature Range",
            value="-58 to 392",
            unit="deg F",
            source_name="Distributor Page",
            source_reliability=SourceReliability.THIRD_PARTY,
            confidence=80.0,
            match_status=MatchStatus.PARTIALLY_VERIFIED
        )
    ]

    conflicts = detect_product_conflicts(product_id="PIQ-TS-01", specifications=specs)
    assert len(conflicts) == 1
    c = conflicts[0]
    assert c.conflict_type in [ConflictType.UNIT_MISMATCH, ConflictType.VALUE_MISMATCH]
    assert c.severity == ConflictSeverity.CRITICAL


def test_conflict_detection_duplicate_attribute_same_source():
    """Tests duplicate conflicting attribute within the same document source."""
    specs = [
        SpecificationAttribute(
            name="Stroke Length",
            value="100",
            unit="mm",
            source_name="Manual.pdf",
            source_reliability=SourceReliability.OFFICIAL_DATASHEET,
            confidence=90.0
        ),
        SpecificationAttribute(
            name="Stroke Length",
            value="150",
            unit="mm",
            source_name="Manual.pdf",
            source_reliability=SourceReliability.OFFICIAL_DATASHEET,
            confidence=90.0
        )
    ]

    conflicts = detect_product_conflicts(product_id="PIQ-CYL-02", specifications=specs)
    assert len(conflicts) == 1
    assert conflicts[0].conflict_type == ConflictType.DUPLICATE_ATTRIBUTE
    assert conflicts[0].severity == ConflictSeverity.HIGH


def test_conflict_detection_identity_conflict():
    """Tests product identity conflict between user-input SKU and datasheet SKU."""
    prod_info = ProductInfo(
        product_name="Heavy Duty AC Motor",
        manufacturer="PowerDrive Corp",
        product_code="EM-3PH-7.5KW"
    )
    user_metadata = {
        "manufacturer": "PowerDrive Corp",
        "product_code": "EM-3PH-11KW"
    }

    conflicts = detect_product_conflicts(
        product_id="PIQ-MTR-01",
        specifications=[],
        product_info=prod_info,
        user_metadata=user_metadata
    )
    assert len(conflicts) == 1
    c = conflicts[0]
    assert c.conflict_type == ConflictType.IDENTITY_CONFLICT
    assert c.severity == ConflictSeverity.CRITICAL


def test_severity_levels():
    """Tests deterministic severity categorization across technical domains."""
    assert determine_conflict_severity("Operating Pressure", ConflictType.VALUE_MISMATCH) == ConflictSeverity.CRITICAL
    assert determine_conflict_severity("Rated Voltage", ConflictType.VALUE_MISMATCH) == ConflictSeverity.CRITICAL
    assert determine_conflict_severity("Max Temperature", ConflictType.VALUE_MISMATCH) == ConflictSeverity.CRITICAL
    assert determine_conflict_severity("Bore Diameter", ConflictType.VALUE_MISMATCH) == ConflictSeverity.HIGH
    assert determine_conflict_severity("Dynamic Load Rating", ConflictType.VALUE_MISMATCH) == ConflictSeverity.HIGH
    assert determine_conflict_severity("Port Size", ConflictType.VALUE_MISMATCH) == ConflictSeverity.MEDIUM
    assert determine_conflict_severity("Body Finish", ConflictType.VALUE_MISMATCH) == ConflictSeverity.LOW


def test_calculate_conflict_confidence():
    """Tests calculated dynamic confidence scoring."""
    # Both official datasheets -> very high conflict confidence
    conf_high = calculate_conflict_confidence(
        SourceReliability.OFFICIAL_DATASHEET,
        SourceReliability.OFFICIAL_DATASHEET,
        ev_score_a=1.0,
        ev_score_b=1.0
    )
    assert conf_high >= 90

    # User input vs third party -> moderate confidence
    conf_mod = calculate_conflict_confidence(
        SourceReliability.USER_INPUT,
        SourceReliability.THIRD_PARTY,
        ev_score_a=0.7,
        ev_score_b=0.7
    )
    assert conf_mod < conf_high

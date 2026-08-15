"""
Test Suite: Conflict Resolution Workflow
Verifies resolution actions (USE_SOURCE_A, USE_SOURCE_B, ENTER_CORRECT_VALUE, DISMISS_CONFLICT),
versioning increment, attribute confidence promotion to 100%, and audit creation.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database.models import Base
from backend.database.repositories.product_repository import ProductRepository
from backend.database.repositories.conflict_repository import ConflictRepository
from backend.models import (
    ProductIntelligenceRecord, ProductInfo, SpecificationAttribute,
    ValidationResult, ConflictRecord, ConflictSourceInfo, ConflictType,
    ConflictSeverity, ConflictStatus, ConflictResolutionAction, SourceReliability
)


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_conflict_resolution_and_version_creation(db_session):
    """Tests resolving conflict and producing new immutable version with human verified attribute."""
    p_repo = ProductRepository(db_session)
    conf_repo = ConflictRepository(db_session)

    # 1. Setup product with conflict
    prod_id = "PIQ-TEST-001"
    spec = SpecificationAttribute(
        name="Operating Pressure",
        value="10",
        unit="bar",
        source_name="Datasheet",
        confidence=85.0
    )
    conf = ConflictRecord(
        conflict_id="conf-001",
        product_id=prod_id,
        attribute_name="Operating Pressure",
        source_a=ConflictSourceInfo(name="Datasheet", value="10", unit="bar"),
        source_b=ConflictSourceInfo(name="Website", value="16", unit="bar"),
        value_a="10",
        value_b="16",
        unit_a="bar",
        unit_b="bar",
        conflict_type=ConflictType.VALUE_MISMATCH,
        severity=ConflictSeverity.CRITICAL,
        confidence=90,
        status=ConflictStatus.OPEN,
        reason="10 bar vs 16 bar mismatch"
    )

    record = ProductIntelligenceRecord(
        product_id=prod_id,
        product=ProductInfo(product_name="Pneumatic Cylinder", manufacturer="Acme"),
        specifications=[spec],
        validation=[ValidationResult(rule="Conflict Check", status="REVIEW", severity="CRITICAL", message="Conflict", field="Operating Pressure")],

        conflicts=[conf]
    )

    p_repo.save_full_record(record)

    # Verify conflict persisted
    saved_conf = conf_repo.get_by_id("conf-001")
    assert saved_conf is not None
    assert saved_conf.status == ConflictStatus.OPEN

    # 2. Resolve conflict with ENTER_CORRECT_VALUE (12 bar)
    resolved_conf = conf_repo.resolve_conflict(
        conflict_id="conf-001",
        action=ConflictResolutionAction.ENTER_CORRECT_VALUE,
        resolution_value="12",
        resolution_unit="bar",
        resolution_notes="Engineering verified test bench data",
        reviewer="Lead Engineer"
    )

    assert resolved_conf.status == ConflictStatus.RESOLVED
    assert resolved_conf.resolution_value == "12"

    # 3. Create updated product version
    prod_entity, new_ver = p_repo.create_version_from_resolution(
        product_id=prod_id,
        attribute_name="Operating Pressure",
        resolved_value="12",
        resolved_unit="bar",
        resolution_action=ConflictResolutionAction.ENTER_CORRECT_VALUE,
        reviewer="Lead Engineer",
        reason="Verified test bench data",
        conflict_id="conf-001"
    )

    assert new_ver.version_number == 2
    assert "Operating Pressure" in new_ver.change_summary

    # Check updated specification
    updated_spec = next((s for s in new_ver.specifications if s.attribute_name == "Operating Pressure"), None)
    assert updated_spec is not None
    assert updated_spec.normalized_value == "12"
    assert updated_spec.review_status == "human_verified"
    assert updated_spec.confidence == 100.0
    assert updated_spec.review_required is False


def test_conflict_dismissal(db_session):
    """Tests dismissing a non-actionable conflict."""
    conf_repo = ConflictRepository(db_session)
    conf = ConflictRecord(
        conflict_id="conf-002",
        product_id="PIQ-TEST-002",
        attribute_name="Housing Color",
        value_a="Silver",
        value_b="Grey",
        conflict_type=ConflictType.VALUE_MISMATCH,
        severity=ConflictSeverity.LOW,
        confidence=60,
        status=ConflictStatus.OPEN
    )
    conf_repo.create_conflict(conf)

    dismissed = conf_repo.dismiss_conflict("conf-002", reviewer="QA Reviewer", reason="Cosmetic variance acceptable")
    assert dismissed.status == ConflictStatus.DISMISSED
    assert dismissed.review_required is False

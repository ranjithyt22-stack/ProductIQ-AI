"""
Test Suite: Review Resolution Audit Trail
Verifies immutable audit logging of human review and conflict resolution decisions.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database.models import Base
from backend.database.repositories.review_repository import ReviewRepository


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_review_audit_logging_and_retrieval(db_session):
    """Tests creating and querying immutable audit records."""
    r_repo = ReviewRepository(db_session)

    # 1. Record an audit log
    audit = r_repo.record_audit(
        product_id="PIQ-VALVE-01",
        version_id="PIQ-VALVE-01-v2",
        attribute_name="Pressure Rating",
        reviewer="Lead Engineer John",
        action="ENTER_CORRECT_VALUE",
        old_status="OPEN",
        new_status="RESOLVED",
        old_value="10 bar",
        new_value="16 bar",
        selected_source="Test Bench Report",
        reason="Hydraulic pressure test certificate #9924 confirmed 16 bar rating",
        notes="Verified with lab team",
        conflict_id="conf-99"
    )

    assert audit.audit_id.startswith("aud_")
    assert audit.product_id == "PIQ-VALVE-01"
    assert audit.reviewer == "Lead Engineer John"
    assert audit.old_value == "10 bar"
    assert audit.new_value == "16 bar"

    # 2. Query by product ID
    audits_prod = r_repo.get_audits_by_product_id("PIQ-VALVE-01")
    assert len(audits_prod) == 1
    assert audits_prod[0].action == "ENTER_CORRECT_VALUE"

    # 3. Query by conflict ID
    audits_conf = r_repo.get_audits_by_conflict_id("conf-99")
    assert len(audits_conf) == 1
    assert audits_conf[0].attribute_name == "Pressure Rating"

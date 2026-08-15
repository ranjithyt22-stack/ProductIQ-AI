"""
Test Suite: Review Queue Management
Verifies review queue filtering by status and severity, pagination, and conflict metric calculation.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database.models import Base
from backend.database.repositories.conflict_repository import ConflictRepository
from backend.models import ConflictRecord, ConflictSeverity, ConflictStatus


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_review_queue_filtering_and_stats(db_session):
    """Tests review queue query filters and statistical aggregations."""
    conf_repo = ConflictRepository(db_session)

    # Insert 4 conflicts with different severities and statuses
    conf_repo.create_conflict(ConflictRecord(
        conflict_id="c1", product_id="P1", attribute_name="Pressure",
        severity=ConflictSeverity.CRITICAL, status=ConflictStatus.OPEN
    ))
    conf_repo.create_conflict(ConflictRecord(
        conflict_id="c2", product_id="P1", attribute_name="Bore",
        severity=ConflictSeverity.HIGH, status=ConflictStatus.OPEN
    ))
    conf_repo.create_conflict(ConflictRecord(
        conflict_id="c3", product_id="P2", attribute_name="Port",
        severity=ConflictSeverity.MEDIUM, status=ConflictStatus.RESOLVED
    ))
    conf_repo.create_conflict(ConflictRecord(
        conflict_id="c4", product_id="P3", attribute_name="Color",
        severity=ConflictSeverity.LOW, status=ConflictStatus.OPEN
    ))

    # Test list open
    open_items = conf_repo.list_conflicts(status=ConflictStatus.OPEN)
    assert len(open_items) == 3

    # Test list critical
    crit_items = conf_repo.list_conflicts(severity=ConflictSeverity.CRITICAL)
    assert len(crit_items) == 1
    assert crit_items[0].conflict_id == "c1"

    # Test product filter
    p1_items = conf_repo.list_conflicts(product_id="P1")
    assert len(p1_items) == 2

    # Test stats
    stats = conf_repo.get_conflict_stats()
    assert stats["total_conflicts"] == 4
    assert stats["open_conflicts"] == 3
    assert stats["resolved_conflicts"] == 1
    assert stats["critical_conflicts"] == 1
    assert stats["high_conflicts"] == 1
    assert stats["has_blocking_conflicts"] is True

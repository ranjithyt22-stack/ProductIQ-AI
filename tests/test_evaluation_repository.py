"""
Test Suite for Database Persistence of Evaluation Runs, Metrics, and Product Results.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database.models import Base
from backend.database.repositories.evaluation_repository import EvaluationRepository


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


def test_evaluation_repository_lifecycle(db_session):
    repo = EvaluationRepository(db_session)

    run = repo.create_run(
        evaluation_id="eval_test_001",
        dataset_name="Industrial Benchmark v1",
        overall_score=94.5,
        extraction_f1=93.0,
        evidence_coverage=98.0,
        hallucination_rate=0.0
    )
    db_session.commit()

    retrieved = repo.get_by_id("eval_test_001")
    assert retrieved is not None
    assert retrieved.overall_score == 94.5

    # Add Product Result
    prod_res = repo.add_product_result(
        evaluation_id="eval_test_001",
        product_id="BENCH-001",
        product_name="Pneumatic Cylinder",
        category="Pneumatic",
        tp_count=5,
        fp_count=0,
        fn_count=0,
        extraction_precision=100.0,
        extraction_recall=100.0,
        extraction_f1=100.0,
        value_accuracy=100.0,
        unit_accuracy=100.0,
        evidence_coverage=100.0,
        hallucination_rate=0.0,
        validation_f1=95.0,
        conflict_f1=95.0,
        commerce_readiness_correct=True,
        expected_readiness="READY_FOR_COMMERCE",
        actual_readiness="READY_FOR_COMMERCE"
    )
    db_session.commit()

    results = repo.get_product_results("eval_test_001")
    assert len(results) == 1
    assert results[0].product_id == "BENCH-001"

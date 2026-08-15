"""
Evaluation Repository for ProductIQ AI.
Handles persistence, querying, metrics tracking, and product result summaries for AI benchmark evaluation runs.
"""

import json
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

from backend.database.models import EvaluationRunEntity, EvaluationProductResultEntity, EvaluationMetricEntity


def _utcnow() -> datetime:
    return datetime.utcnow()


class EvaluationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_run(
        self,
        evaluation_id: str,
        dataset_name: str = "Industrial Benchmark v1",
        dataset_version: str = "1.0",
        model_provider: str = "Ollama",
        model_name: str = "llama3.2:3b",
        model_version: str = "latest",
        status: str = "COMPLETED",
        quality_gate_status: str = "PASS",
        total_products: int = 0,
        total_attributes: int = 0,
        overall_score: float = 0.0,
        extraction_precision: float = 0.0,
        extraction_recall: float = 0.0,
        extraction_f1: float = 0.0,
        value_accuracy: float = 0.0,
        unit_accuracy: float = 0.0,
        evidence_coverage: float = 0.0,
        hallucination_rate: float = 0.0,
        validation_f1: float = 0.0,
        conflict_f1: float = 0.0,
        commerce_readiness_accuracy: float = 0.0,
        confidence_calibration_score: float = 0.0,
        summary_json: Optional[str] = None,
        confusion_matrix_json: Optional[str] = None,
        calibration_data_json: Optional[str] = None
    ) -> EvaluationRunEntity:
        """Creates a new evaluation run entity."""
        run = EvaluationRunEntity(
            evaluation_id=evaluation_id,
            dataset_name=dataset_name,
            dataset_version=dataset_version,
            model_provider=model_provider,
            model_name=model_name,
            model_version=model_version,
            status=status,
            quality_gate_status=quality_gate_status,
            total_products=total_products,
            total_attributes=total_attributes,
            overall_score=overall_score,
            extraction_precision=extraction_precision,
            extraction_recall=extraction_recall,
            extraction_f1=extraction_f1,
            value_accuracy=value_accuracy,
            unit_accuracy=unit_accuracy,
            evidence_coverage=evidence_coverage,
            hallucination_rate=hallucination_rate,
            validation_f1=validation_f1,
            conflict_f1=conflict_f1,
            commerce_readiness_accuracy=commerce_readiness_accuracy,
            confidence_calibration_score=confidence_calibration_score,
            summary_json=summary_json,
            confusion_matrix_json=confusion_matrix_json,
            calibration_data_json=calibration_data_json
        )
        self.db.add(run)
        self.db.flush()
        return run

    def add_product_result(
        self,
        evaluation_id: str,
        product_id: str,
        product_name: str,
        category: str,
        tp_count: int,
        fp_count: int,
        fn_count: int,
        extraction_precision: float,
        extraction_recall: float,
        extraction_f1: float,
        value_accuracy: float,
        unit_accuracy: float,
        evidence_coverage: float,
        hallucination_rate: float,
        validation_f1: float,
        conflict_f1: float,
        commerce_readiness_correct: bool,
        expected_readiness: str,
        actual_readiness: str,
        details: Optional[Dict[str, Any]] = None
    ) -> EvaluationProductResultEntity:
        """Adds a per-product evaluation result row."""
        result_id = f"res_{uuid.uuid4().hex[:10]}"
        entity = EvaluationProductResultEntity(
            result_id=result_id,
            evaluation_id=evaluation_id,
            product_id=product_id,
            product_name=product_name,
            category=category,
            tp_count=tp_count,
            fp_count=fp_count,
            fn_count=fn_count,
            extraction_precision=extraction_precision,
            extraction_recall=extraction_recall,
            extraction_f1=extraction_f1,
            value_accuracy=value_accuracy,
            unit_accuracy=unit_accuracy,
            evidence_coverage=evidence_coverage,
            hallucination_rate=hallucination_rate,
            validation_f1=validation_f1,
            conflict_f1=conflict_f1,
            commerce_readiness_correct=commerce_readiness_correct,
            expected_readiness=expected_readiness,
            actual_readiness=actual_readiness,
            details_json=json.dumps(details or {})
        )
        self.db.add(entity)
        self.db.flush()
        return entity

    def add_metric(
        self,
        evaluation_id: str,
        metric_name: str,
        metric_value: float,
        metric_category: str,
        threshold_value: Optional[float] = None,
        passed_gate: bool = True,
        notes: Optional[str] = None
    ) -> EvaluationMetricEntity:
        """Adds an individual metric evaluation record."""
        metric_id = f"met_{uuid.uuid4().hex[:10]}"
        entity = EvaluationMetricEntity(
            metric_id=metric_id,
            evaluation_id=evaluation_id,
            metric_name=metric_name,
            metric_value=metric_value,
            metric_category=metric_category,
            threshold_value=threshold_value,
            passed_gate=passed_gate,
            notes=notes
        )
        self.db.add(entity)
        self.db.flush()
        return entity

    def get_by_id(self, evaluation_id: str) -> Optional[EvaluationRunEntity]:
        """Retrieves a single evaluation run by ID."""
        return self.db.query(EvaluationRunEntity).filter(EvaluationRunEntity.evaluation_id == evaluation_id).first()

    def get_latest(self) -> Optional[EvaluationRunEntity]:
        """Retrieves the most recent evaluation run."""
        return self.db.query(EvaluationRunEntity).order_by(EvaluationRunEntity.created_at.desc()).first()

    def list_runs(self, limit: int = 50, offset: int = 0) -> List[EvaluationRunEntity]:
        """Lists evaluation run history in descending chronological order."""
        return (
            self.db.query(EvaluationRunEntity)
            .order_by(EvaluationRunEntity.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def get_product_results(self, evaluation_id: str) -> List[EvaluationProductResultEntity]:
        """Retrieves per-product results for a specific run."""
        return (
            self.db.query(EvaluationProductResultEntity)
            .filter(EvaluationProductResultEntity.evaluation_id == evaluation_id)
            .order_by(EvaluationProductResultEntity.product_id)
            .all()
        )

    def get_metrics(self, evaluation_id: str) -> List[EvaluationMetricEntity]:
        """Retrieves categorized metrics for a specific run."""
        return (
            self.db.query(EvaluationMetricEntity)
            .filter(EvaluationMetricEntity.evaluation_id == evaluation_id)
            .order_by(EvaluationMetricEntity.metric_category, EvaluationMetricEntity.metric_name)
            .all()
        )

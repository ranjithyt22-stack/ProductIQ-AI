"""
Job repository for ProductIQ AI.
Handles tracking and status queries for background processing jobs.
"""

import json
import uuid
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from backend.database.models import ProcessingJobEntity


class JobRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_job(self, job_type: str, input_payload: Optional[Dict[str, Any]] = None) -> ProcessingJobEntity:
        """Initializes a new processing job in QUEUED status."""
        job_id = f"job_{uuid.uuid4().hex[:12]}"
        payload_str = json.dumps(input_payload) if input_payload else None
        entity = ProcessingJobEntity(
            job_id=job_id,
            job_type=job_type,
            status="QUEUED",
            input_payload_json=payload_str
        )
        self.db.add(entity)
        self.db.commit()
        return entity

    def update_job_status(
        self,
        job_id: str,
        status: str,
        result_summary: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ) -> Optional[ProcessingJobEntity]:
        """Updates the status and result of a processing job."""
        job = self.db.query(ProcessingJobEntity).filter(ProcessingJobEntity.job_id == job_id).first()
        if job:
            job.status = status
            if result_summary:
                job.result_summary_json = json.dumps(result_summary)
            if error_message:
                job.error_message = error_message
            self.db.commit()
        return job

    def get_job(self, job_id: str) -> Optional[ProcessingJobEntity]:
        """Retrieves a job by its unique ID."""
        return self.db.query(ProcessingJobEntity).filter(ProcessingJobEntity.job_id == job_id).first()

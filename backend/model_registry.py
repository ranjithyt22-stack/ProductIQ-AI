"""
Model Registry & Versioning for ProductIQ AI.
Tracks local inference models, runtime specifications, performance benchmarks, and approval lifecycle.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from backend.database.models import ModelRegistryEntity


DEFAULT_MODELS = [
    {
        "model_id": "mod_llama32_3b",
        "model_name": "llama3.2:3b",
        "version": "1.0",
        "provider": "Ollama",
        "runtime": "Local (CPU/GPU)",
        "status": "Production",
        "overall_score": 97.3,
        "extraction_f1": 100.0,
        "hallucination_rate": 0.0,
        "evidence_coverage": 100.0,
        "description": "Default local production model for structured industrial product intelligence extraction.",
        "parameters_count": "3.2B"
    },
    {
        "model_id": "mod_mistral_7b",
        "model_name": "mistral:7b",
        "version": "0.3",
        "provider": "Ollama",
        "runtime": "Local (GPU)",
        "status": "Approved",
        "overall_score": 95.8,
        "extraction_f1": 96.5,
        "hallucination_rate": 0.5,
        "evidence_coverage": 97.0,
        "description": "Heavyweight industrial model for complex multi-page technical catalog parsing.",
        "parameters_count": "7.3B"
    },
    {
        "model_id": "mod_qwen25_7b",
        "model_name": "qwen2.5:7b",
        "version": "1.0",
        "provider": "Ollama",
        "runtime": "Local (GPU)",
        "status": "Testing",
        "overall_score": 96.1,
        "extraction_f1": 97.0,
        "hallucination_rate": 0.2,
        "evidence_coverage": 98.5,
        "description": "Experimental multi-lingual technical datasheet extraction model.",
        "parameters_count": "7.6B"
    }
]


def seed_default_models(db: Session) -> None:
    """Seeds default models if registry is empty."""
    for m in DEFAULT_MODELS:
        existing = db.query(ModelRegistryEntity).filter(ModelRegistryEntity.model_id == m["model_id"]).first()
        if not existing:
            entity = ModelRegistryEntity(
                model_id=m["model_id"],
                model_name=m["model_name"],
                version=m["version"],
                provider=m["provider"],
                runtime=m["runtime"],
                status=m["status"],
                overall_score=m["overall_score"],
                extraction_f1=m["extraction_f1"],
                hallucination_rate=m["hallucination_rate"],
                evidence_coverage=m["evidence_coverage"],
                description=m["description"],
                parameters_count=m["parameters_count"]
            )
            db.add(entity)
    db.commit()


def list_registered_models(db: Session) -> List[Dict[str, Any]]:
    """Lists all models registered in the system."""
    seed_default_models(db)
    models = db.query(ModelRegistryEntity).order_by(ModelRegistryEntity.created_at.asc()).all()
    return [m.to_dict() for m in models]


def get_model_by_id(db: Session, model_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves a single model by ID."""
    seed_default_models(db)
    model = db.query(ModelRegistryEntity).filter(ModelRegistryEntity.model_id == model_id).first()
    return model.to_dict() if model else None


def register_or_update_model(db: Session, model_data: Dict[str, Any]) -> Dict[str, Any]:
    """Registers a new model or updates an existing model."""
    m_id = model_data.get("model_id") or f"mod_{model_data.get('model_name', 'custom').replace(':', '_')}"
    existing = db.query(ModelRegistryEntity).filter(ModelRegistryEntity.model_id == m_id).first()

    if existing:
        for k, v in model_data.items():
            if hasattr(existing, k) and k != "id":
                setattr(existing, k, v)
        existing.updated_at = datetime.utcnow()
    else:
        existing = ModelRegistryEntity(
            model_id=m_id,
            model_name=model_data.get("model_name", "custom_model"),
            version=model_data.get("version", "1.0"),
            provider=model_data.get("provider", "Ollama"),
            runtime=model_data.get("runtime", "Local"),
            status=model_data.get("status", "Testing"),
            overall_score=model_data.get("overall_score", 0.0),
            extraction_f1=model_data.get("extraction_f1", 0.0),
            hallucination_rate=model_data.get("hallucination_rate", 0.0),
            evidence_coverage=model_data.get("evidence_coverage", 0.0),
            description=model_data.get("description", ""),
            parameters_count=model_data.get("parameters_count", "N/A")
        )
        db.add(existing)

    db.commit()
    return existing.to_dict()

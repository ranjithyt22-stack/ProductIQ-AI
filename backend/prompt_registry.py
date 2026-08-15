"""
Prompt Registry & Versioning for ProductIQ AI.
Maintains versioned, auditable templates for extraction, enrichment, validation, and conflict detection.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from backend.database.models import PromptRegistryEntity


DEFAULT_PROMPTS = [
    {
        "prompt_id": "prompt_extract_v10",
        "prompt_name": "Industrial Product Extraction Prompt",
        "prompt_type": "EXTRACTION",
        "version": "1.0",
        "purpose": "Extract structured product identity, technical specifications, and units with strict anti-hallucination constraints.",
        "template_text": "Extract industrial product specifications into deterministic JSON. Never invent attributes not mentioned in text.",
        "status": "Production",
        "author": "ProductIQ Core Team"
    },
    {
        "prompt_id": "prompt_enrich_v10",
        "prompt_name": "B2B Search Term & Category Enrichment Prompt",
        "prompt_type": "ENRICHMENT",
        "version": "1.0",
        "purpose": "Generate taxonomy paths, synonym search terms, and industrial application keywords.",
        "template_text": "Generate B2B search terms and applications based strictly on the verified product name and category.",
        "status": "Production",
        "author": "ProductIQ Core Team"
    },
    {
        "prompt_id": "prompt_conflict_v10",
        "prompt_name": "Cross-Source Conflict Arbitration Prompt",
        "prompt_type": "CONFLICT",
        "version": "1.0",
        "purpose": "Identify discrepancies across multiple supplier sources and suggest reconciliation pathways.",
        "template_text": "Compare source attributes, normalize units, and classify conflict severity.",
        "status": "Production",
        "author": "ProductIQ Core Team"
    }
]


def seed_default_prompts(db: Session) -> None:
    """Seeds default prompt templates if registry is empty."""
    for p in DEFAULT_PROMPTS:
        existing = db.query(PromptRegistryEntity).filter(PromptRegistryEntity.prompt_id == p["prompt_id"]).first()
        if not existing:
            entity = PromptRegistryEntity(
                prompt_id=p["prompt_id"],
                prompt_name=p["prompt_name"],
                prompt_type=p["prompt_type"],
                version=p["version"],
                purpose=p["purpose"],
                template_text=p["template_text"],
                status=p["status"],
                author=p["author"]
            )
            db.add(entity)
    db.commit()


def list_registered_prompts(db: Session) -> List[Dict[str, Any]]:
    """Lists all versioned prompt templates."""
    seed_default_prompts(db)
    prompts = db.query(PromptRegistryEntity).order_by(PromptRegistryEntity.created_at.asc()).all()
    return [p.to_dict() for p in prompts]


def get_prompt_by_id(db: Session, prompt_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves a single prompt template by ID."""
    seed_default_prompts(db)
    prompt = db.query(PromptRegistryEntity).filter(PromptRegistryEntity.prompt_id == prompt_id).first()
    return prompt.to_dict() if prompt else None


def register_or_update_prompt(db: Session, prompt_data: Dict[str, Any]) -> Dict[str, Any]:
    """Registers a new prompt or updates an existing prompt."""
    p_id = prompt_data.get("prompt_id") or f"prompt_{prompt_data.get('prompt_type', 'general').lower()}_v{prompt_data.get('version', '10').replace('.', '')}"
    existing = db.query(PromptRegistryEntity).filter(PromptRegistryEntity.prompt_id == p_id).first()

    if existing:
        for k, v in prompt_data.items():
            if hasattr(existing, k) and k != "id":
                setattr(existing, k, v)
        existing.updated_at = datetime.utcnow()
    else:
        existing = PromptRegistryEntity(
            prompt_id=p_id,
            prompt_name=prompt_data.get("prompt_name", "New Prompt Template"),
            prompt_type=prompt_data.get("prompt_type", "EXTRACTION"),
            version=prompt_data.get("version", "1.0"),
            purpose=prompt_data.get("purpose", ""),
            template_text=prompt_data.get("template_text", ""),
            status=prompt_data.get("status", "Testing"),
            author=prompt_data.get("author", "Engineer")
        )
        db.add(existing)

    db.commit()
    return existing.to_dict()

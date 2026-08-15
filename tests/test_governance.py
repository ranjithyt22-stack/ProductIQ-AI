"""
Unit and Integration Tests for AI Governance, Model Registry, and Prompt Versioning.
"""

import pytest
from backend.database.connection import get_db_context
from backend.model_registry import list_registered_models, register_or_update_model, get_model_by_id
from backend.prompt_registry import list_registered_prompts, register_or_update_prompt, get_prompt_by_id
from backend.governance import get_governance_overview


def test_model_registry_lifecycle():
    with get_db_context() as db:
        models = list_registered_models(db)
        assert len(models) >= 3
        prod_model = next((m for m in models if m["model_name"] == "llama3.2:3b"), None)
        assert prod_model is not None
        assert prod_model["status"] == "Production"
        assert prod_model["provider"] == "Ollama"

        # Register custom test model
        new_mod = register_or_update_model(db, {
            "model_id": "mod_custom_test",
            "model_name": "custom-eval:3b",
            "version": "1.1",
            "provider": "Ollama",
            "status": "Testing",
            "overall_score": 94.2
        })
        assert new_mod["model_id"] == "mod_custom_test"

        fetched = get_model_by_id(db, "mod_custom_test")
        assert fetched is not None
        assert fetched["version"] == "1.1"


def test_prompt_registry_lifecycle():
    with get_db_context() as db:
        prompts = list_registered_prompts(db)
        assert len(prompts) >= 3
        extract_p = next((p for p in prompts if p["prompt_type"] == "EXTRACTION"), None)
        assert extract_p is not None
        assert extract_p["status"] == "Production"

        # Register custom test prompt
        new_p = register_or_update_prompt(db, {
            "prompt_id": "prompt_test_v20",
            "prompt_name": "Test Extraction Template",
            "prompt_type": "EXTRACTION",
            "version": "2.0",
            "status": "Testing"
        })
        assert new_p["prompt_id"] == "prompt_test_v20"

        fetched = get_prompt_by_id(db, "prompt_test_v20")
        assert fetched is not None
        assert fetched["version"] == "2.0"


def test_governance_overview_report():
    with get_db_context() as db:
        gov = get_governance_overview(db)
        assert "active_model" in gov
        assert "active_prompt" in gov
        assert "governance_pillars" in gov
        assert gov["compliance_status"] == "COMPLIANT"
        assert len(gov["governance_pillars"]) >= 4

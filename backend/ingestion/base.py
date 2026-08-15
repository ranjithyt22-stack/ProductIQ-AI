"""
Base interface and custom exceptions for ProductIQ AI source adapters.
"""

from abc import ABC, abstractmethod
from typing import Any
from backend.ingestion.models import SourceDocument


class IngestionError(ValueError):
    """Custom exception raised when source ingestion fails or validation fails."""
    pass


class BaseSourceAdapter(ABC):
    """Abstract base class for all source adapters."""

    @abstractmethod
    def ingest(self, source_input: Any) -> SourceDocument:
        """Ingests raw source input and returns a normalized SourceDocument."""
        pass

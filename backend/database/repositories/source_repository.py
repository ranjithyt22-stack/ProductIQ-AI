"""
Source repository for ProductIQ AI.
Handles storage, retrieval, and cryptographic hash deduplication of ingested multi-source assets.
"""

import hashlib
from typing import List, Optional
from sqlalchemy.orm import Session
from backend.database.models import ProductSourceEntity


class SourceRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_source(
        self,
        source_id: str,
        source_type: str,
        source_name: str,
        product_id: Optional[str] = None,
        version_id: Optional[str] = None,
        source_uri: Optional[str] = None,
        raw_content: Optional[str] = None,
        metadata_json: Optional[str] = None
    ) -> ProductSourceEntity:
        """Stores a new product source."""
        source_hash = None
        if raw_content:
            source_hash = hashlib.sha256(raw_content.encode("utf-8")).hexdigest()

        entity = ProductSourceEntity(
            source_id=source_id,
            product_id=product_id,
            version_id=version_id,
            source_type=source_type.upper(),
            source_name=source_name,
            source_uri=source_uri,
            source_hash=source_hash,
            content_preview=raw_content[:1000] if raw_content else None,
            metadata_json=metadata_json
        )
        self.db.add(entity)
        self.db.flush()
        return entity

    def get_by_source_id(self, source_id: str) -> Optional[ProductSourceEntity]:
        """Retrieves a source by source_id."""
        return self.db.query(ProductSourceEntity).filter(ProductSourceEntity.source_id == source_id).first()

    def get_by_product_id(self, product_id: str) -> List[ProductSourceEntity]:
        """Retrieves all sources associated with a product."""
        return self.db.query(ProductSourceEntity).filter(ProductSourceEntity.product_id == product_id).all()

    def get_by_version_id(self, version_id: str) -> List[ProductSourceEntity]:
        """Retrieves sources for a specific version."""
        return self.db.query(ProductSourceEntity).filter(ProductSourceEntity.version_id == version_id).all()

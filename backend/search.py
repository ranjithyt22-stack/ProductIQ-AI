"""
Deterministic Multi-Attribute Global Search Engine for ProductIQ AI.
Searches stored products by name, part number, manufacturer, specifications, and commerce readiness.
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from backend.database.models import ProductEntity, ProductSpecificationEntity, ProductVersionEntity


def search_products(
    db: Session,
    query: Optional[str] = None,
    category: Optional[str] = None,
    manufacturer: Optional[str] = None,
    commerce_status: Optional[str] = None,
    min_confidence: Optional[float] = None,
    limit: int = 50,
    offset: int = 0
) -> Dict[str, Any]:
    """Executes multi-attribute filtered search across catalog database."""
    q = db.query(ProductEntity)

    if category:
        q = q.filter(ProductEntity.category.ilike(f"%{category}%"))
    if manufacturer:
        q = q.filter(ProductEntity.manufacturer.ilike(f"%{manufacturer}%"))
    if commerce_status:
        q = q.filter(ProductEntity.commerce_readiness == commerce_status)

    if query:
        clean_q = query.strip()
        # Match product name, manufacturer, product code, description, or specification attribute name
        spec_product_ids = (
            db.query(ProductVersionEntity.product_id)
            .join(ProductSpecificationEntity, ProductSpecificationEntity.version_id == ProductVersionEntity.version_id)
            .filter(
                or_(
                    ProductSpecificationEntity.attribute_name.ilike(f"%{clean_q}%"),
                    ProductSpecificationEntity.normalized_value.ilike(f"%{clean_q}%"),
                    ProductSpecificationEntity.raw_value.ilike(f"%{clean_q}%")
                )
            )
            .subquery()
        )

        q = q.filter(
            or_(
                ProductEntity.product_name.ilike(f"%{clean_q}%"),
                ProductEntity.manufacturer.ilike(f"%{clean_q}%"),
                ProductEntity.product_code.ilike(f"%{clean_q}%"),
                ProductEntity.category.ilike(f"%{clean_q}%"),
                ProductEntity.description.ilike(f"%{clean_q}%"),
                ProductEntity.product_id.in_(spec_product_ids)
            )
        )

    total_count = q.count()
    products = q.order_by(ProductEntity.created_at.desc()).offset(offset).limit(limit).all()

    results = []
    for p in products:
        p_dict = p.to_dict()
        if p.versions:
            latest_v = p.versions[0]
            p_dict["specifications_count"] = len(latest_v.specifications) if latest_v.specifications else 0
            p_dict["latest_version"] = latest_v.version_number
        else:
            p_dict["specifications_count"] = 0
            p_dict["latest_version"] = 1
        results.append(p_dict)

    return {
        "query": query,
        "total_count": total_count,
        "count": len(results),
        "products": results
    }

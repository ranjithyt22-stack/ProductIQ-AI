from typing import List, Dict
from backend.ingestion.models import SourceDocument


def detect_conflicts(sources: List[SourceDocument]) -> List[Dict]:
    """Detect simple conflicts across source documents.
    Currently checks for duplicate values in metadata keys like 'title' or 'url'.
    Returns a list of conflict dicts with keys: field, value, source_ids.
    """
    conflicts = []
    # Gather metadata values per field
    field_map: Dict[str, Dict[str, List[str]]] = {}
    for src in sources:
        for key, val in src.metadata.items():
            if isinstance(val, (str, int, float)):
                field_map.setdefault(key, {}).setdefault(str(val), []).append(src.source_id)
    for field, val_map in field_map.items():
        for val, src_ids in val_map.items():
            if len(src_ids) > 1:
                conflicts.append({
                    "field": field,
                    "value": val,
                    "source_ids": src_ids,
                })
    return conflicts

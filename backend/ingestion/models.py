"""
Normalized, provenance-preserving inputs consumed by the ProductIQ AI pipeline.
"""

import time
import hashlib
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional


@dataclass
class SourceDocument:
    source_id: str
    source_type: str
    source_name: str
    content: str
    source_uri: Optional[str] = None
    local_path: Optional[str] = None
    pages: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    retrieved_at: float = field(default_factory=time.time)
    hash: str = ""
    mime_type: Optional[str] = None

    def __post_init__(self):
        if not self.hash and self.content:
            self.hash = hashlib.sha256(self.content.encode("utf-8", errors="replace")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

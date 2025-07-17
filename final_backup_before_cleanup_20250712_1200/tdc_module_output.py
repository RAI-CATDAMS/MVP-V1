from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime

@dataclass
class ModuleOutput:
    module_id: Optional[str] = None  # e.g., 'tdc_ai1', 'tdc_ai2', etc.
    module_name: str = ""
    score: Optional[float] = None
    flags: List[str] = field(default_factory=list)
    notes: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    confidence: Optional[float] = None
    recommended_action: Optional[str] = None
    evidence: List[Dict[str, Any]] = field(default_factory=list)
    schema_version: int = 1
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "module_id": self.module_id,
            "module_name": self.module_name,
            "score": self.score,
            "flags": self.flags,
            "notes": self.notes,
            "timestamp": self.timestamp,
            "confidence": self.confidence,
            "recommended_action": self.recommended_action,
            "evidence": self.evidence,
            "schema_version": self.schema_version,
            "extra": self.extra,
        } 
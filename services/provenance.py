"""
Provenance tracking system for audit trails.
Captures step-level citations, data sources, and confidence scores.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class ProvenanceRecord:
    """Single provenance record for audit trail."""
    step: str
    field: str
    value: Any
    source_ref: str
    confidence: float
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


class ProvenanceTracker:
    """Tracks provenance records for the entire workflow."""
    
    def __init__(self):
        """Initialize empty provenance tracker."""
        self.records: List[ProvenanceRecord] = []
    
    def add_record(
        self,
        step: str,
        field: str,
        value: Any,
        source_ref: str,
        confidence: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add a new provenance record.
        
        Args:
            step: Name of the workflow step
            field: Field name being tracked
            value: Value extracted/generated
            source_ref: Reference to source (e.g., "page_3_line_15", "ocr_text")
            confidence: Confidence score (0.0 to 1.0)
            metadata: Additional metadata
        """
        record = ProvenanceRecord(
            step=step,
            field=field,
            value=value,
            source_ref=source_ref,
            confidence=confidence,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        self.records.append(record)
    
    def get_records_by_step(self, step: str) -> List[ProvenanceRecord]:
        """Get all records for a specific step."""
        return [r for r in self.records if r.step == step]
    
    def get_records_by_field(self, field: str) -> List[ProvenanceRecord]:
        """Get all records for a specific field."""
        return [r for r in self.records if r.field == field]
    
    def get_latest_value(self, field: str) -> Optional[Any]:
        """Get the most recent value for a field."""
        field_records = self.get_records_by_field(field)
        if not field_records:
            return None
        return sorted(field_records, key=lambda r: r.timestamp)[-1].value
    
    def get_confidence_summary(self) -> Dict[str, float]:
        """Get average confidence scores by field."""
        field_confidences = {}
        for record in self.records:
            if record.field not in field_confidences:
                field_confidences[record.field] = []
            field_confidences[record.field].append(record.confidence)
        
        return {
            field: sum(confidences) / len(confidences)
            for field, confidences in field_confidences.items()
        }
    
    def export_to_dict(self) -> List[Dict[str, Any]]:
        """Export all records to dictionary format."""
        return [record.to_dict() for record in self.records]
    
    def clear(self) -> None:
        """Clear all provenance records."""
        self.records.clear()


# Global instance for easy access
_provenance_tracker: Optional[ProvenanceTracker] = None


def get_provenance_tracker() -> ProvenanceTracker:
    """Get or create global provenance tracker instance."""
    global _provenance_tracker
    if _provenance_tracker is None:
        _provenance_tracker = ProvenanceTracker()
    return _provenance_tracker


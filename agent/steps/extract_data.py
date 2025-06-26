"""
ExtractData step for processing uploaded documents and extracting tax information.
"""

from typing import Dict, Any
from agent.workflow import BaseStep
from services.extract import DataExtractor
from services.provenance import get_provenance_tracker


class ExtractData(BaseStep):
    """Step for extracting data from uploaded documents."""
    
    def __init__(self):
        """Initialize ExtractData step."""
        super().__init__(
            name="ExtractData",
            description="Extract financial data from uploaded documents using PDF parsing and OCR"
        )
        self.extractor = DataExtractor()
        self.provenance_tracker = get_provenance_tracker()
    
    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute data extraction from uploaded files.
        
        Args:
            context: Workflow context containing uploaded files
            
        Returns:
            Updated context with extracted data
        """
        uploaded_files = context.get("uploaded_files", [])
        if not uploaded_files:
            raise ValueError("No files uploaded for processing")
        
        extracted_data = {}
        tax_data = {}
        
        for file_info in uploaded_files:
            file_path = file_info["path"]
            file_name = file_info["name"]
            
            # Extract data from file
            file_data = self.extractor.extract_from_file(file_path)
            extracted_data[file_name] = file_data
            
            # Extract tax-specific data
            file_tax_data = self.extractor.extract_tax_specific_data(file_data)
            
            # Merge tax data (take first non-None value for each field)
            for field, value in file_tax_data.items():
                if value is not None and field not in tax_data:
                    tax_data[field] = value
        
        # Update context with extracted data
        context["extracted_data"] = extracted_data
        context["tax_data"] = tax_data
        
        # Track overall extraction provenance
        self.provenance_tracker.add_record(
            step=self.name,
            field="extraction_summary",
            value=f"Processed {len(uploaded_files)} files",
            source_ref="extract_data_step",
            confidence=0.9,
            metadata={
                "files_processed": len(uploaded_files),
                "file_names": [f["name"] for f in uploaded_files],
                "tax_fields_found": len([v for v in tax_data.values() if v is not None])
            }
        )
        
        return context


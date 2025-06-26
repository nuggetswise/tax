"""
Data extraction service for tax documents.
Handles PDF parsing, OCR, and CSV/Excel file processing.
"""

import os
import pandas as pd
from typing import Dict, List, Any, Optional, Union
import PyPDF2
import pdfplumber
import pytesseract
from PIL import Image
import io
import base64
from services.provenance import get_provenance_tracker


class DataExtractor:
    """Extracts data from various document formats."""
    
    def __init__(self):
        """Initialize data extractor."""
        self.provenance_tracker = get_provenance_tracker()
    
    def extract_from_file(self, file_path: str, file_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract data from a file based on its type.
        
        Args:
            file_path: Path to the file
            file_type: File type (auto-detected if None)
            
        Returns:
            Dictionary containing extracted data and metadata
        """
        if file_type is None:
            file_type = self._detect_file_type(file_path)
        
        if file_type == "pdf":
            return self._extract_from_pdf(file_path)
        elif file_type in ["csv", "excel"]:
            return self._extract_from_spreadsheet(file_path, file_type)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    
    def _detect_file_type(self, file_path: str) -> str:
        """Detect file type based on extension."""
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".pdf":
            return "pdf"
        elif ext == ".csv":
            return "csv"
        elif ext in [".xlsx", ".xls"]:
            return "excel"
        else:
            raise ValueError(f"Unsupported file extension: {ext}")
    
    def _extract_from_pdf(self, file_path: str) -> Dict[str, Any]:
        """
        Extract text and data from PDF using multiple methods.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Dictionary with extracted text, tables, and metadata
        """
        result = {
            "text": "",
            "tables": [],
            "pages": [],
            "metadata": {},
            "confidence_scores": {}
        }
        
        # Method 1: PDFPlumber for text and tables
        try:
            with pdfplumber.open(file_path) as pdf:
                result["metadata"]["num_pages"] = len(pdf.pages)
                
                for page_num, page in enumerate(pdf.pages):
                    page_data = {
                        "page_number": page_num + 1,
                        "text": page.extract_text() or "",
                        "tables": page.extract_tables() or [],
                        "images": []
                    }
                    
                    # Extract images if present
                    if page.images:
                        for img in page.images:
                            page_data["images"].append({
                                "bbox": img["bbox"],
                                "width": img["width"],
                                "height": img["height"]
                            })
                    
                    result["pages"].append(page_data)
                    result["text"] += page_data["text"] + "\n"
                    result["tables"].extend(page_data["tables"])
                
                # Track provenance
                self.provenance_tracker.add_record(
                    step="extract_data",
                    field="pdf_text",
                    value=len(result["text"]),
                    source_ref=f"pdfplumber_{file_path}",
                    confidence=0.9,
                    metadata={"method": "pdfplumber", "pages": len(result["pages"])}
                )
                
        except Exception as e:
            result["metadata"]["pdfplumber_error"] = str(e)
        
        # Method 2: PyPDF2 for additional metadata
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                result["metadata"]["pdf_info"] = pdf_reader.metadata
                result["metadata"]["num_pages_pypdf2"] = len(pdf_reader.pages)
                
        except Exception as e:
            result["metadata"]["pypdf2_error"] = str(e)
        
        # Method 3: OCR for images if text extraction was poor
        if len(result["text"].strip()) < 100:  # Low text content
            result["ocr_text"] = self._extract_ocr_from_pdf(file_path)
            
            # Track OCR provenance
            if result["ocr_text"]:
                self.provenance_tracker.add_record(
                    step="extract_data",
                    field="ocr_text",
                    value=len(result["ocr_text"]),
                    source_ref=f"tesseract_{file_path}",
                    confidence=0.7,  # OCR typically lower confidence
                    metadata={"method": "tesseract_ocr"}
                )
        
        return result
    
    def _extract_ocr_from_pdf(self, file_path: str) -> str:
        """
        Extract text from PDF using OCR.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted text from OCR
        """
        try:
            with pdfplumber.open(file_path) as pdf:
                ocr_text = ""
                for page in pdf.pages:
                    # Convert page to image for OCR
                    img = page.to_image()
                    if img:
                        # Extract text using Tesseract
                        page_text = pytesseract.image_to_string(img.original)
                        ocr_text += page_text + "\n"
                return ocr_text
        except Exception as e:
            return f"OCR extraction failed: {str(e)}"
    
    def _extract_from_spreadsheet(self, file_path: str, file_type: str) -> Dict[str, Any]:
        """
        Extract data from CSV or Excel files.
        
        Args:
            file_path: Path to spreadsheet file
            file_type: "csv" or "excel"
            
        Returns:
            Dictionary with extracted data and metadata
        """
        try:
            if file_type == "csv":
                df = pd.read_csv(file_path)
            else:  # excel
                df = pd.read_excel(file_path)
            
            result = {
                "dataframe": df,
                "columns": df.columns.tolist(),
                "shape": df.shape,
                "dtypes": df.dtypes.to_dict(),
                "summary_stats": df.describe().to_dict(),
                "file_type": file_type
            }
            
            # Track provenance
            self.provenance_tracker.add_record(
                step="extract_data",
                field="spreadsheet_data",
                value=f"{df.shape[0]} rows, {df.shape[1]} columns",
                source_ref=f"{file_type}_{file_path}",
                confidence=1.0,
                metadata={"file_type": file_type, "columns": df.columns.tolist()}
            )
            
            return result
            
        except Exception as e:
            raise ValueError(f"Failed to extract from {file_type} file: {str(e)}")
    
    def extract_tax_specific_data(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract tax-specific data from general extracted content.
        
        Args:
            extracted_data: Raw extracted data from document
            
        Returns:
            Dictionary with tax-specific fields
        """
        tax_data = {
            "gross_receipts": None,
            "cost_of_goods_sold": None,
            "operating_expenses": None,
            "net_income": None,
            "total_assets": None,
            "total_liabilities": None,
            "equity": None
        }
        
        # If we have dataframe data (CSV/Excel), extract from that first
        if "dataframe" in extracted_data:
            df = extracted_data["dataframe"]
            columns = df.columns.tolist()
            
            # Extract from CSV/Excel data
            if "Account" in columns and "Debit" in columns and "Credit" in columns:
                # Process general ledger format
                for _, row in df.iterrows():
                    account = str(row.get("Account", "")).lower()
                    debit = row.get("Debit", 0) or 0
                    credit = row.get("Credit", 0) or 0
                    
                    # Map accounts to tax fields
                    if "gross" in account and "receipt" in account:
                        tax_data["gross_receipts"] = credit
                    elif "cost" in account and "goods" in account:
                        tax_data["cost_of_goods_sold"] = debit
                    elif "salar" in account or "wage" in account:
                        if tax_data["operating_expenses"] is None:
                            tax_data["operating_expenses"] = 0
                        tax_data["operating_expenses"] += debit
                    elif "rent" in account or "utilit" in account or "insur" in account:
                        if tax_data["operating_expenses"] is None:
                            tax_data["operating_expenses"] = 0
                        tax_data["operating_expenses"] += debit
                    elif "depreciat" in account:
                        if tax_data["operating_expenses"] is None:
                            tax_data["operating_expenses"] = 0
                        tax_data["operating_expenses"] += debit
                    elif "interest" in account and "income" in account:
                        # This would be other income, not gross receipts
                        pass
            
            # Track provenance for dataframe extraction
            for field, value in tax_data.items():
                if value is not None:
                    self.provenance_tracker.add_record(
                        step="extract_data",
                        field=field,
                        value=value,
                        source_ref="dataframe_extraction",
                        confidence=0.95,
                        metadata={"extraction_method": "dataframe_mapping", "columns": columns}
                    )
        
        # Also try text extraction as fallback
        text = extracted_data.get("text", "").lower()
        
        # Look for common patterns in text
        patterns = {
            "gross_receipts": [r"gross receipts[:\s]*\$?([\d,]+\.?\d*)", r"revenue[:\s]*\$?([\d,]+\.?\d*)"],
            "cost_of_goods_sold": [r"cost of goods sold[:\s]*\$?([\d,]+\.?\d*)", r"cogs[:\s]*\$?([\d,]+\.?\d*)"],
            "operating_expenses": [r"operating expenses[:\s]*\$?([\d,]+\.?\d*)", r"expenses[:\s]*\$?([\d,]+\.?\d*)"],
            "net_income": [r"net income[:\s]*\$?([\d,]+\.?\d*)", r"profit[:\s]*\$?([\d,]+\.?\d*)"],
            "total_assets": [r"total assets[:\s]*\$?([\d,]+\.?\d*)", r"assets[:\s]*\$?([\d,]+\.?\d*)"],
            "total_liabilities": [r"total liabilities[:\s]*\$?([\d,]+\.?\d*)", r"liabilities[:\s]*\$?([\d,]+\.?\d*)"],
            "equity": [r"equity[:\s]*\$?([\d,]+\.?\d*)", r"owner['']s equity[:\s]*\$?([\d,]+\.?\d*)"]
        }
        
        import re
        for field, pattern_list in patterns.items():
            # Only extract if we don't already have a value from dataframe
            if tax_data[field] is None:
                for pattern in pattern_list:
                    match = re.search(pattern, text)
                    if match:
                        value_str = match.group(1).replace(",", "")
                        try:
                            tax_data[field] = float(value_str)
                            break
                        except ValueError:
                            continue
        
        # Track provenance for text extraction
        for field, value in tax_data.items():
            if value is not None:
                # Only track if we haven't already tracked this field
                existing_records = [r for r in self.provenance_tracker.export_to_dict() 
                                  if r.get("field") == field and r.get("step") == "extract_data"]
                if not existing_records:
                    self.provenance_tracker.add_record(
                        step="extract_data",
                        field=field,
                        value=value,
                        source_ref="pattern_matching",
                        confidence=0.8,
                        metadata={"extraction_method": "regex_pattern"}
                    )
        
        return tax_data


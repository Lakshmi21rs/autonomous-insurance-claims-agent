import re
import os
from extractor import FNOLExtractor
from validator import FNOLValidator
from router import ClaimsRouter


class InsuranceClaimsAgent:
    def __init__(self):
        self.extractor = FNOLExtractor()
        self.validator = FNOLValidator()
        self.router = ClaimsRouter()

    def process(self, filepath: str) -> dict:
        
        text = self._read_file(filepath) #Read document

        
        extracted = self.extractor.extract(text) #Extract fields

        
        missing_fields, warnings = self.validator.validate(extracted) #Validate and find missing/inconsistent fields

        
        route, reasoning = self.router.route(extracted, missing_fields) #Route claim

        return {
            "extractedFields": extracted,
            "missingFields": missing_fields,
            "warnings": warnings,
            "recommendedRoute": route,
            "reasoning": reasoning
        }

    def _read_file(self, filepath: str) -> str:
        ext = os.path.splitext(filepath)[1].lower()
        if ext == ".txt":
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        elif ext == ".pdf":
            return self._read_pdf(filepath)
        else:
            raise ValueError(f"Unsupported file type: {ext}")

    def _read_pdf(self, filepath: str) -> str:
        try:
            import pdfplumber
            text = ""
            with pdfplumber.open(filepath) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text
        except ImportError:
            raise ImportError(
                "pdfplumber is required for PDF support. Install it with: pip install pdfplumber"
            )

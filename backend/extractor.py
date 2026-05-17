import re
from datetime import datetime


class FNOLExtractor:
    """
    Extracts key fields from FNOL (First Notice of Loss) documents
    using pattern matching and heuristics.
    """

    def extract(self, text: str) -> dict:
        lines = text.splitlines()
        lowered = text.lower()

        return {
            # Policy Information
            "policyNumber": self._find_field(text, [
                r"policy\s*(?:number|no|#)\s*[:\-]?\s*([A-Z0-9\-]+)",
                r"pol\s*(?:no|#)\s*[:\-]?\s*([A-Z0-9\-]+)"
            ]),
            "policyholderName": self._find_field(text, [
                r"policyholder(?:\s*name)?\s*[:\-]?\s*([A-Za-z\s]+?)(?:\n|policy|date|dob)",
                r"insured(?:\s*name)?\s*[:\-]?\s*([A-Za-z\s]+?)(?:\n|policy|date|dob)",
                r"name\s*of\s*insured\s*[:\-]?\s*([A-Za-z\s]+?)(?:\n|policy)"
            ], clean=True),
            "effectiveDateStart": self._find_date(text, [
                r"effective\s*(?:date|from)\s*[:\-]?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})",
                r"policy\s*effective\s*[:\-]?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})",
                r"coverage\s*start\s*[:\-]?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})"
            ]),
            "effectiveDateEnd": self._find_date(text, [
                r"expir(?:y|ation|es)\s*(?:date)?\s*[:\-]?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})",
                r"policy\s*(?:end|expiry)\s*[:\-]?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})",
                r"coverage\s*end\s*[:\-]?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})"
            ]),

            # Incident Information
            "incidentDate": self._find_date(text, [
                r"(?:incident|accident|loss|event)\s*date\s*[:\-]?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})",
                r"date\s*of\s*(?:incident|accident|loss)\s*[:\-]?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})",
                r"occurred\s*on\s*[:\-]?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})"
            ]),
            "incidentTime": self._find_field(text, [
                r"(?:incident|accident|loss|event)\s*time\s*[:\-]?\s*(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?)",
                r"time\s*of\s*(?:incident|accident|loss)\s*[:\-]?\s*(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?)",
                r"at\s+(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm))"
            ]),
            "incidentLocation": self._find_field(text, [
                r"(?:incident|accident|loss)?\s*location\s*[:\-]?\s*(.+?)(?:\n|incident|date)",
                r"address\s*(?:of\s*incident)?\s*[:\-]?\s*(.+?)(?:\n|incident|date)",
                r"place\s*of\s*(?:incident|accident)\s*[:\-]?\s*(.+?)(?:\n)"
            ], clean=True),
            "incidentDescription": self._find_description(text),

            # Involved Parties
            "claimantName": self._find_field(text, [
                r"claimant(?:\s*name)?\s*[:\-]?\s*([A-Za-z\s]+?)(?:\n|policy|date|contact)",
                r"filed\s*by\s*[:\-]?\s*([A-Za-z\s]+?)(?:\n|date|policy)"
            ], clean=True),
            "thirdParties": self._find_field(text, [
                r"third\s*part(?:y|ies)(?:\s*involved)?\s*[:\-]?\s*(.+?)(?:\n\n|\n[A-Z])",
                r"other\s*part(?:y|ies)\s*[:\-]?\s*(.+?)(?:\n\n|\n[A-Z])"
            ], clean=True),
            "contactDetails": self._find_field(text, [
                r"contact(?:\s*(?:details?|info(?:rmation)?|number|phone))?\s*[:\-]?\s*(.+?)(?:\n\n|\n[A-Z])",
                r"phone\s*[:\-]?\s*([\d\s\-\+\(\)]+)",
                r"email\s*[:\-]?\s*([\w\.\-]+@[\w\.\-]+)"
            ], clean=True),

            # Asset Details
            "assetType": self._find_field(text, [
                r"asset\s*type\s*[:\-]?\s*(.+?)(?:\n|asset|vehicle|property)",
                r"type\s*of\s*(?:asset|vehicle|property)\s*[:\-]?\s*(.+?)(?:\n)",
                r"vehicle\s*type\s*[:\-]?\s*(.+?)(?:\n)"
            ], clean=True),
            "assetId": self._find_field(text, [
                r"asset\s*(?:id|identifier|number)\s*[:\-]?\s*([A-Z0-9\-]+)",
                r"vin\s*[:\-]?\s*([A-Z0-9]{10,17})",
                r"vehicle\s*(?:id|identification|number)\s*[:\-]?\s*([A-Z0-9\-]+)",
                r"registration\s*(?:number|no)?\s*[:\-]?\s*([A-Z0-9\-]+)"
            ]),
            "estimatedDamage": self._find_damage(text),

            # Other Mandatory Fields
            "claimType": self._find_claim_type(text),
            "attachments": self._find_field(text, [
                r"attachments?\s*[:\-]?\s*(.+?)(?:\n\n|\n[A-Z])",
                r"documents?\s*attached\s*[:\-]?\s*(.+?)(?:\n\n|\n[A-Z])",
                r"supporting\s*documents?\s*[:\-]?\s*(.+?)(?:\n\n|\n[A-Z])"
            ], clean=True),
            "initialEstimate": self._find_damage(text, fields=[
                r"initial\s*estimate\s*[:\-]?\s*[\$₹£€]?\s*([\d,]+(?:\.\d{1,2})?)",
                r"estimated\s*(?:total\s*)?(?:loss|cost|amount)\s*[:\-]?\s*[\$₹£€]?\s*([\d,]+(?:\.\d{1,2})?)"
            ])
        }

    # ──────────────────────────── helpers ──────────────────────────────

    def _find_field(self, text: str, patterns: list, clean: bool = False):
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                value = match.group(1).strip()
                if clean:
                    value = re.sub(r"\s+", " ", value).strip(" .,;:")
                if len(value) > 1:
                    return value
        return None

    def _find_date(self, text: str, patterns: list):
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                raw = match.group(1).strip()
                return self._normalize_date(raw)
        return None

    def _normalize_date(self, raw: str) -> str:
        for fmt in ("%m/%d/%Y", "%d/%m/%Y", "%m-%d-%Y", "%d-%m-%Y",
                    "%m/%d/%y", "%d/%m/%y", "%Y-%m-%d"):
            try:
                return datetime.strptime(raw, fmt).strftime("%Y-%m-%d")
            except ValueError:
                continue
        return raw

    def _find_description(self, text: str) -> str:
        patterns = [
            r"(?:incident|accident|loss|claim)?\s*description\s*[:\-]?\s*(.+?)(?:\n\n|involved parties|asset details|claim type|$)",
            r"description\s*of\s*(?:incident|accident|loss|damage)\s*[:\-]?\s*(.+?)(?:\n\n|involved|asset|claim|$)",
            r"what\s*happened\s*[:\-]?\s*(.+?)(?:\n\n|involved|asset|claim|$)"
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                value = match.group(1).strip()
                value = re.sub(r"\s+", " ", value)
                if len(value) > 5:
                    return value
        return None

    def _find_damage(self, text: str, fields: list = None) -> str:
        if fields is None:
            fields = [
                r"estimated\s*damage\s*[:\-]?\s*[\$₹£€]?\s*([\d,]+(?:\.\d{1,2})?)",
                r"damage\s*estimate\s*[:\-]?\s*[\$₹£€]?\s*([\d,]+(?:\.\d{1,2})?)",
                r"estimated\s*(?:repair\s*)?cost\s*[:\-]?\s*[\$₹£€]?\s*([\d,]+(?:\.\d{1,2})?)",
                r"total\s*(?:loss|damage)\s*[:\-]?\s*[\$₹£€]?\s*([\d,]+(?:\.\d{1,2})?)"
            ]
        for pattern in fields:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                raw = match.group(1).replace(",", "").strip()
                try:
                    return float(raw)
                except ValueError:
                    return raw
        return None

    def _find_claim_type(self, text: str) -> str:
        patterns = [
            r"claim\s*type\s*[:\-]?\s*(.+?)(?:\n|attachment|estimate|$)",
            r"type\s*of\s*claim\s*[:\-]?\s*(.+?)(?:\n|attachment|estimate|$)"
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(1).strip().lower()
                # Normalize to standard types
                if any(w in value for w in ["injury", "bodily", "personal", "medical"]):
                    return "injury"
                if any(w in value for w in ["property", "structural", "building", "home"]):
                    return "property_damage"
                if any(w in value for w in ["vehicle", "auto", "car", "collision"]):
                    return "vehicle_damage"
                if any(w in value for w in ["theft", "stolen", "burglary"]):
                    return "theft"
                if any(w in value for w in ["fire", "burn"]):
                    return "fire"
                if any(w in value for w in ["flood", "water", "leak"]):
                    return "flood"
                if any(w in value for w in ["liability", "third"]):
                    return "liability"
                return match.group(1).strip()

        # Infer from description/text if not explicitly stated
        lowered = text.lower()
        if any(w in lowered for w in ["injured", "injury", "bodily harm", "hospitalized", "medical"]):
            return "injury"
        if any(w in lowered for w in ["vehicle", "car", "collision", "rear-end", "accident on"]):
            return "vehicle_damage"
        if any(w in lowered for w in ["fire", "burned", "flames"]):
            return "fire"
        if any(w in lowered for w in ["flood", "water damage", "pipe burst"]):
            return "flood"
        if any(w in lowered for w in ["theft", "stolen", "burglary", "break-in"]):
            return "theft"
        if any(w in lowered for w in ["property damage", "building", "structural"]):
            return "property_damage"
        return None

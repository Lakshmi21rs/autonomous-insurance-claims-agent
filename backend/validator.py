from datetime import datetime


MANDATORY_FIELDS = [
    ("policyNumber", "Policy Number"),
    ("policyholderName", "Policyholder Name"),
    ("incidentDate", "Incident Date"),
    ("incidentLocation", "Incident Location"),
    ("incidentDescription", "Incident Description"),
    ("claimantName", "Claimant Name"),
    ("assetType", "Asset Type"),
    ("estimatedDamage", "Estimated Damage"),
    ("claimType", "Claim Type"),
    ("initialEstimate", "Initial Estimate"),
]


class FNOLValidator:
    """
    Validates extracted FNOL fields.
    Returns list of missing mandatory fields and consistency warnings.
    """

    def validate(self, fields: dict) -> tuple:
        missing = []
        warnings = []

        # Check mandatory fields
        for key, label in MANDATORY_FIELDS:
            value = fields.get(key)
            if value is None or (isinstance(value, str) and value.strip() == ""):
                missing.append(label)

        # Consistency checks
        warnings.extend(self._check_date_consistency(fields))
        warnings.extend(self._check_estimate_consistency(fields))
        warnings.extend(self._check_policy_validity(fields))

        return missing, warnings

    def _check_date_consistency(self, fields: dict) -> list:
        issues = []
        try:
            incident_raw = fields.get("incidentDate")
            start_raw = fields.get("effectiveDateStart")
            end_raw = fields.get("effectiveDateEnd")

            if incident_raw and start_raw:
                incident = datetime.strptime(incident_raw, "%Y-%m-%d")
                start = datetime.strptime(start_raw, "%Y-%m-%d")
                if incident < start:
                    issues.append(
                        f"Incident date ({incident_raw}) is before policy effective start ({start_raw})"
                    )

            if incident_raw and end_raw:
                incident = datetime.strptime(incident_raw, "%Y-%m-%d")
                end = datetime.strptime(end_raw, "%Y-%m-%d")
                if incident > end:
                    issues.append(
                        f"Incident date ({incident_raw}) is after policy expiry ({end_raw})"
                    )

            if start_raw and end_raw:
                start = datetime.strptime(start_raw, "%Y-%m-%d")
                end = datetime.strptime(end_raw, "%Y-%m-%d")
                if start > end:
                    issues.append(
                        f"Policy start date ({start_raw}) is after end date ({end_raw}) — inconsistent policy period"
                    )
        except (ValueError, TypeError):
            pass

        return issues

    def _check_estimate_consistency(self, fields: dict) -> list:
        issues = []
        estimated = fields.get("estimatedDamage")
        initial = fields.get("initialEstimate")

        if estimated is not None and initial is not None:
            try:
                est = float(estimated)
                ini = float(initial)
                # Flag if they differ by more than 20%
                if est > 0 and abs(est - ini) / est > 0.20:
                    issues.append(
                        f"Estimated damage ({estimated}) and initial estimate ({initial}) differ significantly (>20%)"
                    )
            except (ValueError, TypeError):
                pass

        return issues

    def _check_policy_validity(self, fields: dict) -> list:
        issues = []
        policy_num = fields.get("policyNumber")
        if policy_num:
            # Basic format check: must contain alphanumerics
            import re
            if not re.match(r"^[A-Z0-9][A-Z0-9\-]{3,}$", policy_num.upper()):
                issues.append(
                    f"Policy number '{policy_num}' appears to have an unusual format"
                )
        return issues

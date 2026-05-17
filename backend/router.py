FRAUD_KEYWORDS = [
    "fraud", "fraudulent", "staged", "inconsistent", "suspicious",
    "fabricated", "false claim", "misrepresent", "exaggerated",
    "inflated", "colluded", "collusion"
]

FAST_TRACK_THRESHOLD = 25000


class ClaimsRouter:
    """
    Routes claims to the appropriate workflow based on routing rules:
    - Estimated damage < 25,000  →  Fast-track
    - Any mandatory field missing →  Manual review
    - Fraud keywords in description → Investigation Flag
    - Claim type = injury          → Specialist Queue
    Priority: Investigation Flag > Specialist Queue > Manual Review > Fast-track
    """

    def route(self, fields: dict, missing_fields: list) -> tuple:
        reasons = []
        routes = []

        # Rule 1: 
        description = fields.get("incidentDescription") or ""
        found_keywords = [kw for kw in FRAUD_KEYWORDS if kw.lower() in description.lower()]
        if found_keywords:
            routes.append("investigation_flag")
            reasons.append(
                f"Fraud/suspicious keywords detected in incident description: "
                f"{', '.join(repr(k) for k in found_keywords)}. "
                f"Claim requires immediate investigation."
            )

        # Rule 2: 
        claim_type = (fields.get("claimType") or "").lower()
        if claim_type == "injury":
            routes.append("specialist_queue")
            reasons.append(
                "Claim type is 'injury'. Routing to Specialist Queue for medical and legal assessment."
            )

        # Rule 3: 
        if missing_fields:
            routes.append("manual_review")
            reasons.append(
                f"The following mandatory fields are missing: {', '.join(missing_fields)}. "
                f"Manual review required to obtain complete information."
            )

        # Rule 4: 
        if not routes:
            damage = fields.get("estimatedDamage")
            try:
                damage_val = float(damage)
                if damage_val < FAST_TRACK_THRESHOLD:
                    routes.append("fast_track")
                    reasons.append(
                        f"Estimated damage ({damage_val:,.2f}) is below threshold of "
                        f"{FAST_TRACK_THRESHOLD:,}. No missing fields or flags detected. "
                        f"Eligible for fast-track processing."
                    )
                else:
                    routes.append("standard_review")
                    reasons.append(
                        f"Estimated damage ({damage_val:,.2f}) meets or exceeds the fast-track "
                        f"threshold of {FAST_TRACK_THRESHOLD:,}. Routing to standard review."
                    )
            except (TypeError, ValueError):
                routes.append("manual_review")
                reasons.append(
                    "Estimated damage value could not be parsed. Manual review required."
                )

        # Determine final route (priority order)
        priority = ["investigation_flag", "specialist_queue", "manual_review", "standard_review", "fast_track"]
        final_route = next((r for r in priority if r in routes), "manual_review")

        # output return
        route_labels = {
            "investigation_flag": "Investigation Flag",
            "specialist_queue": "Specialist Queue",
            "manual_review": "Manual Review",
            "standard_review": "Standard Review",
            "fast_track": "Fast-Track"
        }

        reasoning_text = " | ".join(reasons)
        return route_labels.get(final_route, final_route), reasoning_text

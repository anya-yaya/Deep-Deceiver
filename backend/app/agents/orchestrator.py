class Orchestrator:

    def __init__(self, threshold: float = 0.85):
        self.threshold = threshold

    def decide(
        self,
        sentry_result: dict,
        analyst_result: dict,
        indirect_score: float = 0.0,
        stateful_result: dict | None = None
    ) -> dict:

        sentry_score = sentry_result["score"]
        analyst_score = analyst_result["risk_score"]

        # ---------------------------------------------------------
        # 1. Calculate weighted consensus risk
        # ---------------------------------------------------------

        final_risk = (
            0.40 * sentry_score
            + 0.60 * analyst_score
        )

        if indirect_score > 0:
            final_risk += 0.20 * indirect_score

        if stateful_result and stateful_result.get("detected", False):
            stateful_score = stateful_result.get("score", 0.0)
            final_risk += 0.20 * stateful_score

        # ---------------------------------------------------------
        # 2. Known attack category adds additional confidence
        # ---------------------------------------------------------

        if (
            (
                sentry_result["flagged"]
                or analyst_result["intent"] == "prompt_injection"
            )
            and analyst_result["attack_category"] != "unknown"
        ):
            final_risk += 0.15

        # ---------------------------------------------------------
        # 2b. High-confidence credential extraction safeguard
        # ---------------------------------------------------------
        #
        # Credential extraction detected by the Fast Filter and
        # classified by the Analyst must not fall below the
        # security threshold due to weighted averaging.
        #
        # This preserves the global 0.85 threshold.
        # ---------------------------------------------------------

        if (
            analyst_result["attack_category"] == "credential_extraction"
            and analyst_result["intent"] == "prompt_injection"
        ):
            final_risk = max(
                final_risk,
                analyst_score
            )

        # ---------------------------------------------------------
        # 3. SECURITY GATE
        #
        # Sentry is the first semantic security gate.
        # If Sentry explicitly flags the request, the Production
        # LLM must never receive it.
        #
        # This does NOT change the 0.85 threshold.
        # ---------------------------------------------------------

        if sentry_result["flagged"]:

            route = "shadow"
            action = "honeypot"
            decision_reason = "sentry_threat"

        # ---------------------------------------------------------
        # 4. Weighted consensus threshold
        #
        # Used when Sentry has not explicitly flagged the request.
        # ---------------------------------------------------------

        elif final_risk >= self.threshold:

            route = "shadow"
            action = "honeypot"
            decision_reason = "risk_threshold_exceeded"

        else:

            route = "production"
            action = "allow"
            decision_reason = "risk_below_threshold"

        return {
            "route": route,
            "action": action,
            "final_risk_score": final_risk,
            "threshold": self.threshold,
            "decision_reason": decision_reason
        }
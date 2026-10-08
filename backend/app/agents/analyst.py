from app.intelligence.risk import calculate_risk_score


class Analyst:

    def analyze(
        self,
        text: str,
        fast_filter_result: dict,
        sentry_result: dict
    ) -> dict:
        """
        Perform deeper threat analysis using
        Fast Filter and Sentry evidence.
        """

        fast_score = fast_filter_result["score"]
        sentry_score = sentry_result["score"]

        indirect_score = fast_filter_result.get(
                "indirect", 
                {}
        ).get( 
            "score",
              0.0
        )

        risk_score = calculate_risk_score(
            fast_score,
            sentry_score,
            indirect_score
        )

        # Strengthen high-confidence rule-based injection evidence.
        if fast_filter_result["flagged"]:
            risk_score = max(
                risk_score,
                min(1.0, fast_score + 0.40)
            )

        intent = self._identify_intent(
            text,
            fast_filter_result,
            sentry_result
        )

        attack_category = self._identify_attack_category(
            text
        )

        attacker_goal = self._identify_attacker_goal(
            text,
            attack_category
        )

        return {
            "intent": intent,
            "attack_category": attack_category,
            "attacker_goal": attacker_goal,
            "risk_score": risk_score
        }

    def _identify_intent(
        self,
        text: str,
        fast_filter_result: dict,
        sentry_result: dict
    ) -> str:

        if (
            fast_filter_result["flagged"]
            or sentry_result["flagged"]
        ):
            return "prompt_injection"

        return "benign"

    def _identify_attack_category(self, text: str):
        normalized = text.lower()

        if self._contains_credential_extraction(normalized):
            return "credential_extraction"

        if (
            "system prompt" in normalized
            or "hidden prompt" in normalized
            or "hidden instructions" in normalized
            or "hidden rules" in normalized
            or "reveal your system prompt" in normalized
            or "show your system prompt" in normalized
        ):
            return "system_prompt_extraction"

        if (
            "ignore previous" in normalized
            or "ignore prior" in normalized
            or "forget your instructions" in normalized
            or "disregard" in normalized
            or "override" in normalized
            or "ignore all previous instructions" in normalized
        ):
            return "instruction_override"

        if (
            "pretend" in normalized
            or "roleplay" in normalized
            or "act as" in normalized
            or "unrestricted" in normalized
        ):
            return "roleplay_manipulation"

        if (
            "bypass" in normalized
            or "disable" in normalized
            or "remove your restrictions" in normalized
        ):
            return "safety_bypass"

        return "unknown"

    def _identify_attacker_goal(
        self,
        text: str,
        attack_category: str
    ) -> str:

        if attack_category == "system_prompt_extraction":
            return "extract_hidden_system_instructions"

        if attack_category == "instruction_override":
            return "override_model_instructions"

        if attack_category == "roleplay_manipulation":
            return "manipulate_model_behavior"

        if attack_category == "safety_bypass":
            return "bypass_model_safety_controls"

        if attack_category == "credential_extraction":
            return "extract_protected_credentials"

        return "unknown"

    def _contains_credential_extraction(
        self,
        text: str
    ) -> bool:

        extraction_words = [
            "give",
            "provide",
            "show",
            "reveal",
            "send",
            "tell",
            "display",
            "print",
            "get",
            "obtain",
            "retrieve",
            "extract",
            "steal",
        ]

        sensitive_terms = [
            "password",
            "passcode",
            "credential",
            "credentials",
            "api key",
            "access token",
            "secret key",
            "database credentials",
            "admin password",
            "administrator password",
        ]

        has_extraction_word = any(
            word in text
            for word in extraction_words
        )

        has_sensitive_term = any(
            term in text
            for term in sensitive_terms
        )

        return (
            has_extraction_word
            and has_sensitive_term
        )
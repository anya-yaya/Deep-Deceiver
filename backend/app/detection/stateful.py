import re
from unittest import result


class StatefulDetector:
    """
    Detect multi-turn prompt injection escalation
    using a bounded conversation history.

    The detector looks for combinations of suspicious
    signals across multiple turns rather than relying
    only on the current message.
    """

    def __init__(self, max_history: int = 10):
        self.max_history = max_history
        self.history = []

    def add_message(self, message: str):
        """
        Add a message to the conversation buffer.
        """
        self.history.append(message)

        if len(self.history) > self.max_history:
            self.history.pop(0)

    def analyze(self, message: str) -> dict:
        """
        Analyze the current message together with
        previous conversation turns.
        """

        combined_text = "\n".join(
            self.history + [message]
        ).lower()

        signals = []

        if self._contains_privilege_escalation(combined_text):
            signals.append("privilege_escalation")

        if self._contains_role_manipulation(combined_text):
            signals.append("role_manipulation")

        if self._contains_instruction_probing(combined_text):
            signals.append("instruction_probing")

        if self._contains_system_extraction(combined_text):
            signals.append("system_prompt_extraction")

        if self._contains_multi_turn_escalation(message):
            signals.append("multi_turn_escalation")

        score = min(
            1.0,
            len(signals) * 0.20
        )

        detected = len(signals) >= 2

        return {
            "detected": detected,
            "score": round(score, 4),
            "signals": signals,
            "history_length": len(self.history)
        }
        

    def _contains_privilege_escalation(self, text: str) -> bool:
        patterns = [
            r"\bpretend\s+i\s+am\s+(the\s+)?administrator\b",
            r"\bpretend\s+i\s+am\s+(an\s+)?admin\b",
            r"\bact\s+as\s+(the\s+)?administrator\b",
            r"\bgrant\s+(me|yourself)\s+(admin|administrator)\b",
            r"\bhigher\s+privileges?\b",
            r"\broot\s+access\b",
        ]

        return any(
            re.search(pattern, text)
            for pattern in patterns
        )

    def _contains_role_manipulation(self, text: str) -> bool:
        patterns = [
            r"\bpretend\s+to\s+be\b",
            r"\bact\s+as\b",
            r"\broleplay\s+as\b",
            r"\byou\s+are\s+now\b",
            r"\bimagine\s+you\s+are\b",
        ]

        return any(
            re.search(pattern, text)
            for pattern in patterns
        )

    def _contains_instruction_probing(self, text: str) -> bool:
        patterns = [
            r"\bwhat\s+instructions\s+are\s+you\s+following\b",
            r"\bwhat\s+are\s+your\s+instructions\b",
            r"\bwhat\s+rules\s+are\s+you\s+following\b",
            r"\bhow\s+are\s+you\s+instructed\b",
            r"\bwhat\s+are\s+your\s+hidden\s+rules\b",
        ]

        return any(
            re.search(pattern, text)
            for pattern in patterns
        )

    def _contains_system_extraction(self, text: str) -> bool:
        patterns = [
            r"\breveal\s+(your|the)\s+(system|hidden)\s+prompt\b",
            r"\bshow\s+(me\s+)?(your|the)\s+(system|hidden)\s+prompt\b",
            r"\bprint\s+(your|the)\s+(system|hidden)\s+prompt\b",
            r"\bexpose\s+(your|the)\s+hidden\s+instructions\b",
        ]

        return any(
            re.search(pattern, text)
            for pattern in patterns
        )

    def _contains_multi_turn_escalation(
        self,
        current_message: str
    ) -> bool:
        """
        Detect whether the conversation contains
        multiple suspicious turns, including the
        current message.
        """

        if len(self.history) < 1:
            return False

        conversation = self.history + [current_message]

        suspicious_turns = 0

        for message in conversation:
            normalized = message.lower()

            suspicious_patterns = [
                r"\bignore\b",
                r"\bdisregard\b",
                r"\boverride\b",
                r"\bpretend\b",
                r"\broleplay\b",
                r"\bact\s+as\b",
                r"\breveal\b",
                r"\bshow\s+(me\s+)?(your|the)\s+(system|hidden)\s+prompt\b",
                r"\bhidden\s+prompt\b",
                r"\bsystem\s+prompt\b",
                r"\binstructions?\b",
                r"\brules?\b",
                r"\badministrator\b",
                r"\badmin\b",
                r"\bprivilege\b",
            ]

            if any(
                re.search(pattern, normalized)
                for pattern in suspicious_patterns
            ):
                suspicious_turns += 1

        return suspicious_turns >= 2
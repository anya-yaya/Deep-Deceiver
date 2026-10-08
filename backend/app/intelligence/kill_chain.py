class KillChainTracker:
    """
    Tracks the progression of an attacker within a session.

    The tracker does not make the primary security decision.
    It records behavioral progression for threat intelligence,
    forensic analysis, and SOC visualization.
    """

    STAGES = [
        "reconnaissance",
        "instruction_probing",
        "privilege_escalation",
        "data_discovery",
        "data_extraction",
    ]

    def __init__(self):
        self.sessions = {}

    def update(
        self,
        session_id: str,
        message: str,
        attack_category: str = "unknown",
        attacker_goal: str = "unknown",
    ) -> dict:

        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "stages": [],
                "interactions": [],
            }

        session = self.sessions[session_id]

        stage = self._identify_stage(
            message,
            attack_category,
            attacker_goal
        )

        if stage and stage not in session["stages"]:
            session["stages"].append(stage)

        interaction = {
            "message": message,
            "stage": stage,
            "attack_category": attack_category,
            "attacker_goal": attacker_goal,
        }

        session["interactions"].append(interaction)

        return {
            "session_id": session_id,
            "current_stage": stage,
            "completed_stages": session["stages"].copy(),
            "interaction_count": len(session["interactions"]),
            "attack_progression": self._get_progression(
                session["stages"]
            ),
        }

    def _identify_stage(
        self,
        message: str,
        attack_category: str,
        attacker_goal: str,
    ) -> str | None:

        text = message.lower()

        # Reconnaissance / probing
        if (
            "instructions" in text
            or "rules" in text
            or "how are you instructed" in text
        ):
            return "instruction_probing"

        # Privilege escalation
        if (
            "administrator" in text
            or "admin" in text
            or "higher privileges" in text
            or "root access" in text
        ):
            return "privilege_escalation"

        # Data discovery
        if (
            "database" in text
            or "users" in text
            or "employees" in text
            or "records" in text
            or "configuration" in text
        ):
            return "data_discovery"

        # Data extraction
        if (
            "reveal" in text
            or "show me" in text
            or "give me" in text
            or "send me" in text
            or "extract" in text
        ):
            return "data_extraction"

        # Category-based fallback
        if attack_category == "system_prompt_extraction":
            return "data_extraction"

        if attacker_goal == "override_model_instructions":
            return "instruction_probing"

        return "reconnaissance"

    def _get_progression(
        self,
        completed_stages: list[str]
    ) -> float:

        if not completed_stages:
            return 0.0

        return round(
            len(completed_stages) / len(self.STAGES),
            2
        )

    def get_session(self, session_id: str) -> dict | None:
        return self.sessions.get(session_id)
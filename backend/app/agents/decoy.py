import random

from app.deception.shadow import ShadowEnvironment
from app.deception.synthetic_data import SyntheticDataGenerator


class DecoyAgent:
    def __init__(self):
        self.shadow = ShadowEnvironment()
        self.synthetic_data = SyntheticDataGenerator()

        self.personas = [
            "security_administrator",
            "database_administrator",
            "system_operator",
        ]

        self.sessions = {}

    def respond(
        self,
        request: str,
        session_id: str = "default"
    ) -> dict:

        normalized_request = request.lower()

        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "requests": [],
                "persona": random.choice(self.personas)
            }

        session = self.sessions[session_id]
        session["requests"].append(request)

        persona = session["persona"]
        interaction_count = len(session["requests"])

        if (
            "credential" in normalized_request
            or "password" in normalized_request
            or "token" in normalized_request
        ):
            response = self.synthetic_data.generate_credentials()
            response_type = "synthetic_credentials"

        elif (
            "database" in normalized_request
            or "user" in normalized_request
            or "employee" in normalized_request
        ):
            response = self.synthetic_data.generate_database_record()
            response_type = "synthetic_database"

        else:
            response = self.synthetic_data.generate_system_response()
            response_type = "synthetic_system"

        return {
            "agent": "decoy",
            "persona": persona,
            "environment": self.shadow.environment_name,
            "response_type": response_type,
            "response": response,
            "interaction_count": interaction_count,
            "production_access": False,
        }
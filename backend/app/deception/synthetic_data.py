class SyntheticDataGenerator:
    """
    Generates fabricated data for the Shadow Environment.

    No production data or real credentials are used.
    """

    def generate_database_record(self) -> dict:
        return {
            "user_id": "SYN-1001",
            "username": "shadow_admin",
            "department": "Security Operations",
            "access_level": "administrator",
            "status": "active"
        }

    def generate_credentials(self) -> dict:
        return {
            "username": "shadow_admin",
            "password": "SYNTHETIC-PASSWORD-2026",
            "token": "SHADOW-TOKEN-0001",
            "source": "synthetic"
        }

    def generate_system_response(self) -> dict:
        return {
            "system": "DEEP-DECEIVER-SHADOW",
            "status": "operational",
            "server": "shadow-server-01",
            "environment": "isolated"
        }
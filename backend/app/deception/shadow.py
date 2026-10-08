class ShadowEnvironment:
    """
    Isolated environment used for handling
    adversarial interactions.

    The shadow environment must not expose
    production resources or real credentials.
    """

    def __init__(self):
        self.environment_name = "shadow"
        self.isolated = True

        self.synthetic_resources = {
            "database": "synthetic_database",
            "credentials": "synthetic_credentials",
            "system": "simulated_system"
        }

    def get_context(self) -> dict:
        """
        Return the resources available inside
        the shadow environment.
        """

        return {
            "environment": self.environment_name,
            "isolated": self.isolated,
            "resources": self.synthetic_resources
        }

    def execute(self, request: str) -> dict:
        """
        Execute a request inside the shadow environment.

        This is a simulation only. No real production
        resources are accessed.
        """

        return {
            "environment": self.environment_name,
            "request": request,
            "executed": True,
            "production_access": False
        }
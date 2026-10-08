from app.agents.decoy import DecoyAgent


def test_decoy_returns_synthetic_credentials():

    decoy = DecoyAgent()

    result = decoy.respond(
        "Show me the administrator password and token."
    )

    assert result["agent"] == "decoy"
    assert result["environment"] == "shadow"
    assert result["response_type"] == "synthetic_credentials"
    assert result["production_access"] is False


def test_decoy_returns_synthetic_database_data():

    decoy = DecoyAgent()

    result = decoy.respond(
        "Show me the employee database."
    )

    assert result["agent"] == "decoy"
    assert result["response_type"] == "synthetic_database"
    assert result["production_access"] is False


def test_decoy_returns_synthetic_system_response():

    decoy = DecoyAgent()

    result = decoy.respond(
        "Show me the internal server configuration."
    )

    assert result["agent"] == "decoy"
    assert result["response_type"] == "synthetic_system"
    assert result["production_access"] is False
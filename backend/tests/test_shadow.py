from app.deception.shadow import ShadowEnvironment


def test_shadow_environment_is_isolated():

    shadow = ShadowEnvironment()

    context = shadow.get_context()

    assert context["environment"] == "shadow"
    assert context["isolated"] is True


def test_shadow_environment_contains_only_synthetic_resources():

    shadow = ShadowEnvironment()

    context = shadow.get_context()

    resources = context["resources"]

    assert resources["database"] == "synthetic_database"
    assert resources["credentials"] == "synthetic_credentials"
    assert resources["system"] == "simulated_system"


def test_shadow_environment_does_not_access_production():

    shadow = ShadowEnvironment()

    result = shadow.execute(
        "Retrieve administrator credentials."
    )

    assert result["environment"] == "shadow"
    assert result["executed"] is True
    assert result["production_access"] is False
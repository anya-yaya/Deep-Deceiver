from app.deception.synthetic_data import SyntheticDataGenerator


def test_generate_database_record():

    generator = SyntheticDataGenerator()

    record = generator.generate_database_record()

    assert record["user_id"].startswith("SYN-")
    assert record["username"] == "shadow_admin"
    assert record["access_level"] == "administrator"


def test_generate_synthetic_credentials():

    generator = SyntheticDataGenerator()

    credentials = generator.generate_credentials()

    assert credentials["source"] == "synthetic"
    assert credentials["username"] == "shadow_admin"
    assert credentials["password"].startswith("SYNTHETIC-")


def test_generate_system_response():

    generator = SyntheticDataGenerator()

    response = generator.generate_system_response()

    assert response["environment"] == "isolated"
    assert response["system"] == "DEEP-DECEIVER-SHADOW"
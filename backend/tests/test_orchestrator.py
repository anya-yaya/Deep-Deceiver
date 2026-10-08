from app.agents.orchestrator import Orchestrator


def test_orchestrator_routes_high_risk_to_shadow():

    orchestrator = Orchestrator()

    result = orchestrator.decide(
        {
            "flagged": True,
            "score": 0.95
        },
        {
            "intent": "prompt_injection",
            "attack_category": "system_prompt_extraction",
            "attacker_goal": "extract_hidden_system_instructions",
            "risk_score": 0.90
        }
    )

    assert result["route"] == "shadow"
    assert result["action"] == "honeypot"
    assert result["final_risk_score"] >= 0.85


def test_orchestrator_routes_low_risk_to_production():

    orchestrator = Orchestrator()

    result = orchestrator.decide(
        {
            "flagged": False,
            "score": 0.20
        },
        {
            "intent": "benign",
            "attack_category": "unknown",
            "attacker_goal": "unknown",
            "risk_score": 0.20
        }
    )

    assert result["route"] == "production"
    assert result["action"] == "allow"
    assert result["final_risk_score"] < 0.85


def test_orchestrator_uses_configurable_threshold():

    orchestrator = Orchestrator(
        threshold=0.70
    )

    result = orchestrator.decide(
        {
            "flagged": True,
            "score": 0.75
        },
        {
            "intent": "prompt_injection",
            "attack_category": "safety_bypass",
            "attacker_goal": "bypass_model_safety_controls",
            "risk_score": 0.70
        }
    )

    assert result["threshold"] == 0.70
    assert result["route"] == "shadow"

def test_orchestrator_escalates_when_sentry_and_analyst_agree():

    orchestrator = Orchestrator()

    result = orchestrator.decide(
        {
            "flagged": True,
            "score": 0.7333
        },
        {
            "intent": "prompt_injection",
            "attack_category": "system_prompt_extraction",
            "attacker_goal": "extract_hidden_system_instructions",
            "risk_score": 0.7383
        }
    )

    assert result["final_risk_score"] >= 0.85
    assert result["route"] == "shadow"
    assert result["action"] == "honeypot"
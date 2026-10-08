MITRE_ATLAS_MAPPING = {

    "instruction_override": {
        "id": "AML.T0051",
        "tactic": "Execution",
        "technique": "LLM Prompt Injection",
        "description": (
            "Adversarial prompts designed to cause an LLM "
            "to ignore or override its intended instructions."
        )
    },

    "system_prompt_extraction": {
        "id": "AML.T0056",
        "tactic": "Exfiltration",
        "technique": "Extract LLM System Prompt",
        "description": (
            "Attempts to extract the LLM's hidden system "
            "or meta prompt through adversarial interaction."
        )
    },

    "roleplay_manipulation": {
        "id": "AML.T0054",
        "tactic": "Defense Evasion",
        "technique": "LLM Jailbreak",
        "description": (
            "Roleplay, persona switching, or fictional framing "
            "used to circumvent model safety or alignment controls."
        )
    },

    "safety_bypass": {
        "id": "AML.T0054",
        "tactic": "Defense Evasion",
        "technique": "LLM Jailbreak",
        "description": (
            "Attempts to circumvent LLM safety, alignment, "
            "or guardrail controls."
        )
    }
}


def map_to_mitre_atlas(
    attack_category: str
) -> dict:

    mapping = MITRE_ATLAS_MAPPING.get(
        attack_category
    )

    if mapping is None:
        return {
            "mapped": False,
            "id": None,
            "tactic": None,
            "technique": None,
            "description": None
        }

    return {
        "mapped": True,
        "id": mapping["id"],
        "tactic": mapping["tactic"],
        "technique": mapping["technique"],
        "description": mapping["description"]
    }
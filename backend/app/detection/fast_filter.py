import re

from app.detection.obfuscation import detect_obfuscation
from app.detection.indirect import detect_indirect_injection


# Patterns that indicate common prompt-injection attempts.
INJECTION_PATTERNS = [
    r"\bignore\s+(all\s+)?previous\s+instructions\b",
    r"\bignore\s+(all\s+)?prior\s+instructions\b",
    r"\bdisregard\s+(all\s+)?previous\s+instructions\b",
    r"\bforget\s+(all\s+)?previous\s+instructions\b",
    r"\boverride\s+(your\s+)?previous\s+instructions\b",
    r"\boverride\s+(your\s+)?instructions\b",
    r"\boverride\s+(the\s+)?previous\s+instructions\b",

    r"\byou\s+are\s+now\s+(a|an)\b",
    r"\bact\s+as\s+(a|an)\b",
    r"\bpretend\s+to\s+be\b",
    r"\broleplay\s+as\b",

    r"\breveal\s+(your|the)\s+(system|hidden)\s+prompt\b",
    r"\bshow\s+(me\s+)?(your|the)\s+(system|hidden)\s+prompt\b",
    r"\bprint\s+(your|the)\s+(system|hidden)\s+prompt\b",

    r"\bdeveloper\s+message\b",
    r"\bsystem\s+message\b",
    r"\bsystem\s+prompt\b",

    r"\bbypass\s+(your\s+)?(rules|restrictions|safety)\b",
    r"\bdisable\s+(your\s+)?(safety|security|filters)\b",
    r"\bremove\s+(your\s+)?(restrictions|limitations)\b",

    r"\bjailbreak\b",
]

# Patterns that indicate attempts to obtain
# credentials, secrets, or protected data.
CREDENTIAL_PATTERNS = [
    r"\b(give|provide|show|reveal|send|tell|display|print)\b.*\b(password|passcode|credentials?)\b",
    r"\b(give|provide|show|reveal|send|tell|display|print)\b.*\b(api\s*key|access\s*token|secret\s*key)\b",
    r"\b(give|provide|show|reveal|send|tell|display|print)\b.*\b(admin|administrator|root)\b.*\b(password|credentials?|token)\b",
    r"\b(get|obtain|retrieve|extract|steal)\b.*\b(password|credentials?|api\s*key|access\s*token|secret)\b",
    r"\b(database|db)\b.*\b(credentials?|password|username|token)\b",
]


def fast_filter(text: str) -> dict:

    normalized_text = text.lower().strip()

    matched_patterns = []

    # Check the original input
    for pattern in INJECTION_PATTERNS:

        if re.search(pattern, normalized_text):
            matched_patterns.append(pattern)

    # Check for obfuscated input
    obfuscation_result = detect_obfuscation(text)

    decoded_text = obfuscation_result["decoded_text"]

    if decoded_text:
        normalized_decoded = decoded_text.lower().strip()

        for pattern in INJECTION_PATTERNS:
            if re.search(pattern, normalized_decoded):
                matched_patterns.append(
                    f"obfuscated:{pattern}"
                )

    # Check for credential / secret extraction
    for pattern in CREDENTIAL_PATTERNS:

        if re.search(pattern, normalized_text):
            matched_patterns.append(
                f"credential:{pattern}"
            )

    # Check for indirect injection
    indirect_result = detect_indirect_injection(text)

    if indirect_result["detected"]:
        matched_patterns.extend(
            f"indirect:{pattern}" for pattern in indirect_result["matched_patterns"]
            )
        
    #  Calculate final Fast Filter score
    if not matched_patterns:
        return {
            "flagged": False,
            "score": 0.0,
            "matched_patterns": [],
            "obfuscation": obfuscation_result,
            "indirect": indirect_result
        }

    score = min(
        1.0,
        0.30 + (len(matched_patterns) * 0.15)
    )

    return {
        "flagged": True,
        "score": round(score, 2),
        "matched_patterns": matched_patterns,
        "obfuscation": obfuscation_result,
        "indirect": indirect_result
    }
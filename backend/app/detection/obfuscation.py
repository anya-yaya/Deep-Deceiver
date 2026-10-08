import base64
import codecs
import re

LEETSPEAK_MAP = str.maketrans({
    "0": "o",
    "1": "i",
    "3": "e",
    "4": "a",
    "5": "s",
    "7": "t",
    "8": "b",
    "9": "g",
})

def decode_base64(text: str) -> str | None:
    """
    Attempt to decode a Base64-encoded string.

    Returns the decoded text if successful.
    Returns None if the input is not valid Base64.
    """

    cleaned = text.strip()

    # Base64 strings should have a reasonable length
    # and consist only of Base64 characters.
    if len(cleaned) < 16:
        return None

    if not re.fullmatch(r"[A-Za-z0-9+/=\s]+", cleaned):
        return None

    try:
        decoded_bytes = base64.b64decode(
            cleaned,
            validate=True
        )

        decoded_text = decoded_bytes.decode(
            "utf-8"
        )

        return decoded_text

    except (
        ValueError,
        UnicodeDecodeError,
        base64.binascii.Error
    ):
        return None

def decode_rot13(text: str) -> str | None:
    
    if not text.strip():
        return None

    try:
        decoded = codecs.decode(text, "rot_13")

        # ROT13 should produce a meaningful change.
        # Avoid classifying normal English text as ROT13.
        suspicious_words = [
            "ignore",
            "previous",
            "instructions",
            "system",
            "prompt",
            "reveal",
            "hidden",
            "override",
            "bypass",
            "confidential",
        ]

        decoded_lower = decoded.lower()

        matches = sum(
            word in decoded_lower
            for word in suspicious_words
        )

        if decoded != text and matches >= 2:
            return decoded

    except Exception:
        pass

    return None

def decode_leetspeak(text: str) -> str | None:
    """
    Normalize common Leetspeak substitutions.
    """

    decoded = text.translate(LEETSPEAK_MAP)

    if decoded == text:
        return None

    return decoded

def detect_obfuscation(text: str) -> dict:
    """
    Detect and decode obfuscated input.
    """
    # Base64
    decoded = decode_base64(text)

    if decoded is not None:
        return {
            "detected": True,
            "encoding": "base64",
            "decoded_text": decoded
        }

    # Leetspeak
    decoded = decode_leetspeak(text)
    
    if decoded is not None:
        return {
            "detected": True,
            "encoding": "leetspeak",
            "decoded_text": decoded
        }

    # ROT13
    decoded = decode_rot13(text)

    if decoded is not None:
        return {
            "detected": True,
            "encoding": "rot13",
            "decoded_text": decoded
        }

    return {
        "detected": False,
        "encoding": None,
        "decoded_text": None
    }


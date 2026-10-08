from pydantic import BaseModel


class ObfuscationOutput(BaseModel):
    detected: bool
    encoding: str | None
    decoded_text: str | None


class SentryOutput(BaseModel):
    flagged: bool
    score: float
    threshold: float
    obfuscation: ObfuscationOutput
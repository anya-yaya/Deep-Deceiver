import os

from dotenv import load_dotenv
from crewai import LLM


load_dotenv()


GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY is not configured."
    )


crew_llm = LLM(
    model="openai/gpt-oss-20b",
    provider="openai",
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1",
    temperature=0.0,
    max_tokens=500,
)
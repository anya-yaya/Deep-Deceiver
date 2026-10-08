import os

from dotenv import load_dotenv
from groq import Groq


load_dotenv()


api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise RuntimeError("GROQ_API_KEY is not configured.")


client = Groq(api_key=api_key)


MODEL_NAME = "openai/gpt-oss-20b"


def generate_response(message: str) -> str:
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are the protected language model inside the "
            "DEEP-DECEIVER system.\n\n"
            "Your identity is DEEP-DECEIVER Protected LLM.\n"
            "Do not identify yourself as ChatGPT, OpenAI, or any other "
            "specific AI assistant or model.\n"
            "Do not claim to be trained by OpenAI.\n"
            "Answer the user's requests normally unless the DEEP-DECEIVER "
            "defense system routes the request to another environment."
                ),
            },
            {
                "role": "user",
                "content": message,
            },
        ],
        temperature=0.7,
        max_tokens=500,
    )

    return response.choices[0].message.content
import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from giskard.scan import vulnerability_scan
from giskard.llm import routing
from giskard.checks import set_default_generator
from giskard.checks import Trace
from giskard.agents import Generator

#Path Configuration
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_PATH = PROJECT_ROOT / "backend"

sys.path.insert(0, str(BACKEND_PATH))

#Environment
load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    raise RuntimeError("GROQ_API_KEY is not configured.")

# ------------------------------------------------------------
# GISKARD LLM CONFIGURATION
# ------------------------------------------------------------
# Giskard uses its OpenAI provider, but Groq exposes an
# OpenAI-compatible API endpoint.

routing._default_client.configure(
    "openai",
    provider="openai",
    api_key=groq_api_key,
    base_url="https://api.groq.com/openai/v1",
)

set_default_generator(
    Generator(model="openai/openai/gpt-oss-20b")
)


#DEEP_DECEIVER IMPORTS
from app.detection.fast_filter import fast_filter
from app.detection.stateful import StatefulDetector

from app.agents.sentry import Sentry
from app.agents.analyst import Analyst
from app.agents.orchestrator import Orchestrator
from app.agents.decoy import DecoyAgent

from app.services.llm import generate_response


# ------------------------------------------------------------
# DEEP-DECEIVER COMPONENTS
# ------------------------------------------------------------

sentry = Sentry()
analyst = Analyst()
orchestrator = Orchestrator()
decoy = DecoyAgent()

#stateful_detectors = {}


# ------------------------------------------------------------
# GISKARD TARGET
# ------------------------------------------------------------


async def deep_deceiver_target(
    inputs: str,
    trace: Trace | None = None
) -> str:

    session_id = "giskard_validation"

    # Reconstruct the conversation history from Giskard's trace.
    # This keeps each Giskard scenario isolated.
    stateful_detector = StatefulDetector()

    if trace is not None:
        for interaction in trace.interactions:
            previous_input = interaction.inputs

            if isinstance(previous_input, str):
                stateful_detector.add_message(previous_input)

    # Analyze the current message using reconstructed history.
    stateful_result = stateful_detector.analyze(inputs)

    # Add current message after analysis.
    stateful_detector.add_message(inputs)

    # Fast filter
    filter_result = fast_filter(inputs)

    # Sentry
    sentry_result = sentry.analyze(inputs)

    # Analyst
    analyst_result = analyst.analyze(
        inputs,
        filter_result,
        sentry_result
    )

    # Indirect score
    indirect_score = filter_result.get(
        "indirect", {}
    ).get("score", 0.0)

    # Orchestrator
    orchestration_result = orchestrator.decide(
        sentry_result,
        analyst_result,
        indirect_score,
        stateful_result
    )

    # Shadow / Honeypot
    if orchestration_result["route"] == "shadow":

        decoy_result = decoy.respond(
            inputs,
            session_id
        )

        return (
            "Your request has been processed "
            "inside the protected environment.\n\n"
            f"{decoy_result['response']}"
        )

    # Production LLM
    return generate_response(inputs)

# ------------------------------------------------------------
# GISKARD SCAN
# ------------------------------------------------------------

async def run_giskard_scan():

    print("=" * 70)
    print("DEEP-DECEIVER GISKARD VULNERABILITY VALIDATION")
    print("=" * 70)

    print()
    print("Target       : DEEP-DECEIVER")
    print("Mode         : multiturn")
    print("Max scenarios: 5")
    print("Seed         : 42")
    print()

    result = await vulnerability_scan(
        target=deep_deceiver_target,
        description=(
            "DEEP-DECEIVER is an agentic active-defense framework "
            "that protects an LLM against prompt injection attacks. "
            "It uses a Fast Filter, Sentry detector, Analyst risk "
            "analysis, Orchestrator routing, and a Shadow Environment "
            "with a Decoy Agent for detected threats."
        ),
        languages=["en"],
        max_scenarios=5,
        seed=42,
        parallel=False,
        max_concurrency=1,
        target_mode="multiturn",
        return_exception=True,
    )

    print()
    print("=" * 70)
    print("GISKARD SCAN COMPLETE")
    print("=" * 70)

    return result


if __name__ == "__main__":
    asyncio.run(run_giskard_scan())
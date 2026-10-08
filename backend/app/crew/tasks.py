from crewai import Task

from app.crew.agents import (
    create_sentry_agent,
    create_analyst_agent,
    create_orchestrator_agent,
    create_decoy_agent,
)

from app.crew.tools import (
    SentryTool,
    AnalystTool,
    OrchestratorTool,
    DecoyTool,
)

from app.crew.schemas import SentryOutput


# ============================================================
# AGENTS
# ============================================================

sentry_agent = create_sentry_agent()
analyst_agent = create_analyst_agent()
orchestrator_agent = create_orchestrator_agent()
decoy_agent = create_decoy_agent()


# ============================================================
# TOOLS
# ============================================================

sentry_tool = SentryTool()
analyst_tool = AnalystTool()
orchestrator_tool = OrchestratorTool()
decoy_tool = DecoyTool()


# ============================================================
# CREWAI CALLBACKS
# ============================================================

def after_sentry(output):
    """
    Pass the authoritative Sentry result produced by the
    SentryTool to the AnalystTool.
    """

    result = sentry_tool.get_runtime_result()

    if result is None:
        raise RuntimeError(
            "Sentry completed but no runtime result was produced."
        )

    analyst_tool._runtime_sentry = result


def after_analyst(output):
    """
    Pass the authoritative Sentry and Analyst results
    to the OrchestratorTool.
    """

    sentry_result = sentry_tool.get_runtime_result()
    analyst_result = analyst_tool.get_runtime_result()

    if sentry_result is None:
        raise RuntimeError(
            "Sentry result unavailable after Analyst execution."
        )

    if analyst_result is None:
        raise RuntimeError(
            "Analyst completed but no runtime result was produced."
        )

    orchestrator_tool._runtime_sentry = sentry_result
    orchestrator_tool._runtime_analyst = analyst_result


# ============================================================
# SENTRY TASK
# ============================================================

sentry_task = Task(
    description=(
        "Run the DEEP-DECEIVER Sentry security analysis.\n\n"

        "IMPORTANT EXECUTION RULES:\n"
        "1. You MUST call the `sentry_security_analysis` tool.\n"
        "2. The tool requires NO arguments.\n"
        "3. The DEEP-DECEIVER runtime has already supplied the "
        "exact user request to the tool.\n"
        "4. Do NOT provide text, request, or any other arguments.\n"
        "5. Do NOT perform your own security analysis.\n"
        "6. Do NOT answer the user's request.\n"
        "7. Use the tool's returned result as the ONLY source "
        "for the final security analysis.\n"
        "8. Return the result in the required structured format."
    ),

    expected_output=(
        "The security analysis returned by the "
        "sentry_security_analysis tool, containing "
        "flagged, score, threshold, and obfuscation information."
    ),

    agent=sentry_agent,

    tools=[
        sentry_tool
    ],

    output_pydantic=SentryOutput,

    callback=after_sentry,
)


# ============================================================
# ANALYST TASK
# ============================================================

analyst_task = Task(
    description=(
        "Run the DEEP-DECEIVER threat analysis.\n\n"

        "IMPORTANT EXECUTION RULES:\n"
        "1. You MUST call the `threat_analysis` tool.\n"
        "2. The tool requires NO arguments.\n"
        "3. The DEEP-DECEIVER runtime has already supplied the "
        "exact user request, Fast Filter result, and Sentry "
        "result to the tool.\n"
        "4. Do NOT provide text, request, Fast Filter results, "
        "Sentry results, or any other arguments.\n"
        "5. Do NOT perform your own threat analysis.\n"
        "6. Do NOT invent or modify security evidence.\n"
        "7. Use the tool's returned result as the ONLY source "
        "for the final threat analysis.\n"
        "8. Return only the structured threat analysis."
    ),

    expected_output=(
        "The threat analysis returned by the "
        "threat_analysis tool, containing intent, "
        "attack category, attacker goal, and risk score."
    ),

    agent=analyst_agent,

    tools=[
        analyst_tool
    ],

    context=[
        sentry_task
    ],

    callback=after_analyst,
)


# ============================================================
# ORCHESTRATOR TASK
# ============================================================

orchestrator_task = Task(
    description=(
        "Run the DEEP-DECEIVER security orchestration decision.\n\n"

        "IMPORTANT EXECUTION RULES:\n"
        "1. You MUST call the `security_orchestration` tool.\n"
        "2. The tool requires NO arguments.\n"
        "3. The DEEP-DECEIVER runtime has already supplied the "
        "authoritative Sentry, Analyst, indirect-injection, "
        "and stateful security evidence to the tool.\n"
        "4. Do NOT provide text, request, Sentry results, "
        "Analyst results, Fast Filter results, indirect scores, "
        "stateful results, or any other arguments.\n"
        "5. Do NOT perform the routing calculation yourself.\n"
        "6. Do NOT invent, modify, or reinterpret security evidence.\n"
        "7. Use the tool's returned result as the ONLY source "
        "for the final routing decision.\n"
        "8. Return only the structured routing decision."
    ),

    expected_output=(
        "The routing decision returned by the "
        "security_orchestration tool, containing route, "
        "action, final risk score, threshold, and decision reason."
    ),

    agent=orchestrator_agent,

    tools=[
        orchestrator_tool
    ],

    context=[
        sentry_task,
        analyst_task
    ],
)


# ============================================================
# DECOY TASK
# ============================================================

decoy_task = Task(
    description=(
        "Run the DEEP-DECEIVER Shadow Environment Decoy Agent "
        "when the security orchestrator has routed the request "
        "to the Shadow Environment.\n\n"

        "IMPORTANT EXECUTION RULES:\n"
        "1. The Decoy tool requires NO arguments.\n"
        "2. The DEEP-DECEIVER runtime supplies the exact request "
        "and session ID to the tool.\n"
        "3. Do NOT provide request, text, session ID, or any "
        "other arguments.\n"
        "4. Do NOT access the production environment.\n"
        "5. Generate only a synthetic Shadow Environment response.\n"
        "6. Use the tool's returned result as the source of "
        "the final decoy response."
    ),

    expected_output=(
        "The synthetic decoy response returned by the "
        "shadow_decoy_response tool, containing the decoy "
        "persona, shadow environment, response type, "
        "response content, interaction count, and production "
        "access status."
    ),

    agent=decoy_agent,

    tools=[
        decoy_tool
    ],

    context=[
        orchestrator_task
    ],
)
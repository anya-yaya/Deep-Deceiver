from crewai import Crew, Process

from app.crew.tasks import (
    sentry_agent,
    analyst_agent,
    orchestrator_agent,
    sentry_task,
    analyst_task,
    orchestrator_task,
)


# ---------------------------------------------------------
# SECURITY ANALYSIS CREW
# ---------------------------------------------------------
# Runs for every request.
#
# Fast Filter remains outside CrewAI.
# CrewAI handles:
#     Sentry → Analyst → Orchestrator
#
# Decoy is intentionally NOT included here because it must
# only execute when the Orchestrator selects the Shadow
# Environment.
# ---------------------------------------------------------

security_analysis_crew = Crew(
    name="DEEP-DECEIVER Security Analysis Crew",
    agents=[
        sentry_agent,
        analyst_agent,
        orchestrator_agent,
    ],
    tasks=[
        sentry_task,
        analyst_task,
        orchestrator_task,
    ],
    process=Process.sequential,
    verbose=True,
    memory=False,
)
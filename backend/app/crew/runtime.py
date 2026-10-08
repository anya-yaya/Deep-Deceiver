from app.crew.crew import security_analysis_crew

from app.crew.tasks import (
    sentry_tool,
    analyst_tool,
    orchestrator_tool,
)

from app.crew.tools import DecoyTool


class DEEPDeceiverCrewRuntime:

    def __init__(self):
        self.sentry_tool = sentry_tool
        self.analyst_tool = analyst_tool
        self.orchestrator_tool = orchestrator_tool
        self.decoy_tool = DecoyTool()

    def analyze(
        self,
        text: str,
        fast_filter_result: dict,
        stateful_result: dict | None = None,
    ) -> dict:

        # ---------------------------------------------------------
        # RESET PREVIOUS RUNTIME RESULTS
        # ---------------------------------------------------------

        self.sentry_tool._runtime_result = None
        self.analyst_tool._runtime_result = None
        self.orchestrator_tool._runtime_result = None

        self.sentry_tool._runtime_text = text

        # ---------------------------------------------------------
        # AUTHORITATIVE FAST FILTER CONTEXT
        # ---------------------------------------------------------

        self.analyst_tool._runtime_text = text
        self.analyst_tool._runtime_fast_filter = fast_filter_result
        self.analyst_tool._runtime_sentry = None

        # ---------------------------------------------------------
        # AUTHORITATIVE ORCHESTRATOR CONTEXT
        # ---------------------------------------------------------

        indirect_score = (
            fast_filter_result
            .get("indirect", {})
            .get("score", 0.0)
        )

        self.orchestrator_tool._runtime_sentry = None
        self.orchestrator_tool._runtime_analyst = None
        self.orchestrator_tool._runtime_indirect_score = indirect_score
        self.orchestrator_tool._runtime_stateful = stateful_result

        # ---------------------------------------------------------
        # CREWAI EXECUTION
        #
        # Sentry → callback → Analyst → callback → Orchestrator
        # ---------------------------------------------------------

        crew_result = security_analysis_crew.kickoff(
            inputs={
                "text": text,
                "fast_filter_result": fast_filter_result,
                "stateful_result": stateful_result,
            }
        )

        # ---------------------------------------------------------
        # GET RESULTS FROM THE ACTUAL CREWAI TOOL EXECUTIONS
        # ---------------------------------------------------------

        sentry_result = self.sentry_tool.get_runtime_result()
        analyst_result = self.analyst_tool.get_runtime_result()
        orchestration_result = (
            self.orchestrator_tool.get_runtime_result()
        )

        # ---------------------------------------------------------
        # VALIDATION
        # ---------------------------------------------------------

        if sentry_result is None:
            raise RuntimeError(
                "CrewAI Sentry stage did not produce a runtime result."
            )

        if analyst_result is None:
            raise RuntimeError(
                "CrewAI Analyst stage did not produce a runtime result."
            )

        if orchestration_result is None:
            raise RuntimeError(
                "CrewAI Orchestrator stage did not produce a runtime result."
            )

        # ---------------------------------------------------------
        # RETURN AUTHORITATIVE RESULTS
        # ---------------------------------------------------------

        return {
            "crew_result": crew_result,
            "sentry": sentry_result,
            "analyst": analyst_result,
            "orchestrator": orchestration_result,
        }

    def decoy_response(
        self,
        request: str,
        session_id: str = "default",
    ) -> dict:

        self.decoy_tool.set_runtime_context(
            request=request,
            session_id=session_id,
        )

        return self.decoy_tool.run(
            request=request,
            session_id=session_id,
        )
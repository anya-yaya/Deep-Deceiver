from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field, PrivateAttr

from app.agents.sentry import Sentry
from app.agents.analyst import Analyst
from app.agents.orchestrator import Orchestrator
from app.agents.decoy import DecoyAgent


# ============================================================
# COMMON OPTIONAL INPUT SCHEMA
# ============================================================

class RuntimeToolInput(BaseModel):
    """
    Optional tool input used only to provide CrewAI/Groq with
    a valid JSON schema.

    The DEEP-DECEIVER runtime remains authoritative.
    The value of this field is NOT used for security decisions.
    """

    context: str | None = Field(
        default=None,
        description=(
            "Optional execution context. This value is ignored by "
            "the security runtime because the authoritative context "
            "is supplied internally by DEEP-DECEIVER."
        ),
    )


# ============================================================
# SENTRY TOOL
# ============================================================

class SentryTool(BaseTool):
    name: str = "sentry_security_analysis"

    description: str = (
        "Run the DEEP-DECEIVER Sentry security analysis on the "
        "exact user request supplied by the runtime. "
        "An optional context field may be provided, but it is "
        "not used for the security decision."
    )

    args_schema: Type[BaseModel] = RuntimeToolInput

    _runtime_text: str | None = PrivateAttr(default=None)
    _runtime_result: dict | None = PrivateAttr(default=None)

    def set_runtime_text(self, text: str) -> None:
        self._runtime_text = text

    def _run(
        self,
        context: str | None = None,
    ) -> dict:

        if self._runtime_text is None:
            raise RuntimeError(
                "Sentry runtime text is unavailable."
            )

        sentry = Sentry()

        result = sentry.analyze(
            self._runtime_text
        )

        self._runtime_result = result

        return result

    def get_runtime_result(self) -> dict | None:
        return self._runtime_result


# ============================================================
# ANALYST TOOL
# ============================================================

class AnalystTool(BaseTool):
    name: str = "threat_analysis"

    description: str = (
        "Run the DEEP-DECEIVER threat analysis using the "
        "authoritative Fast Filter and Sentry results stored "
        "by the runtime. An optional context field may be "
        "provided, but it is not used for the security decision."
    )

    args_schema: Type[BaseModel] = RuntimeToolInput

    _runtime_text: str | None = PrivateAttr(default=None)
    _runtime_fast_filter: dict | None = PrivateAttr(default=None)
    _runtime_sentry: dict | None = PrivateAttr(default=None)
    _runtime_result: dict | None = PrivateAttr(default=None)

    def set_runtime_context(
        self,
        text: str,
        fast_filter_result: dict,
        sentry_result: dict,
    ) -> None:

        self._runtime_text = text
        self._runtime_fast_filter = fast_filter_result
        self._runtime_sentry = sentry_result

    def _run(
        self,
        context: str | None = None,
    ) -> dict:

        if self._runtime_text is None:
            raise RuntimeError(
                "Analyst runtime text is unavailable."
            )

        if self._runtime_fast_filter is None:
            raise RuntimeError(
                "Authoritative Fast Filter result is unavailable."
            )

        if self._runtime_sentry is None:
            raise RuntimeError(
                "Authoritative Sentry result is unavailable."
            )

        analyst = Analyst()

        result = analyst.analyze(
            self._runtime_text,
            self._runtime_fast_filter,
            self._runtime_sentry,
        )

        self._runtime_result = result

        return result

    def get_runtime_result(self) -> dict | None:
        return self._runtime_result


# ============================================================
# ORCHESTRATOR TOOL
# ============================================================

class OrchestratorTool(BaseTool):
    name: str = "security_orchestration"

    description: str = (
        "Run the DEEP-DECEIVER security orchestration decision "
        "using the authoritative Sentry, Analyst, indirect "
        "injection, and stateful results stored by the runtime. "
        "An optional context field may be provided, but it is "
        "not used for the security decision."
    )

    args_schema: Type[BaseModel] = RuntimeToolInput

    _runtime_sentry: dict | None = PrivateAttr(default=None)
    _runtime_analyst: dict | None = PrivateAttr(default=None)
    _runtime_indirect_score: float = PrivateAttr(default=0.0)
    _runtime_stateful: dict | None = PrivateAttr(default=None)
    _runtime_result: dict | None = PrivateAttr(default=None)

    def set_runtime_context(
        self,
        sentry_result: dict,
        analyst_result: dict,
        indirect_score: float = 0.0,
        stateful_result: dict | None = None,
    ) -> None:

        self._runtime_sentry = sentry_result
        self._runtime_analyst = analyst_result
        self._runtime_indirect_score = indirect_score
        self._runtime_stateful = stateful_result

    def _run(
        self,
        context: str | None = None,
    ) -> dict:

        if self._runtime_sentry is None:
            raise RuntimeError(
                "Authoritative Sentry result is unavailable."
            )

        if self._runtime_analyst is None:
            raise RuntimeError(
                "Authoritative Analyst result is unavailable."
            )

        orchestrator = Orchestrator()

        result = orchestrator.decide(
            self._runtime_sentry,
            self._runtime_analyst,
            self._runtime_indirect_score,
            self._runtime_stateful,
        )

        self._runtime_result = result

        return result

    def get_runtime_result(self) -> dict | None:
        return self._runtime_result


# ============================================================
# DECOY TOOL
# ============================================================

class DecoyTool(BaseTool):
    name: str = "shadow_decoy_response"

    description: str = (
        "Generate a synthetic response inside the isolated "
        "DEEP-DECEIVER Shadow Environment using the exact "
        "request and session ID supplied by the runtime. "
        "An optional context field may be provided, but the "
        "runtime request and session ID remain authoritative."
    )

    args_schema: Type[BaseModel] = RuntimeToolInput

    _decoy: DecoyAgent = PrivateAttr()
    _runtime_request: str | None = PrivateAttr(default=None)
    _runtime_session_id: str | None = PrivateAttr(default=None)
    _runtime_result: dict | None = PrivateAttr(default=None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._decoy = DecoyAgent()

    def set_runtime_context(
        self,
        request: str,
        session_id: str = "default",
    ) -> None:

        self._runtime_request = request
        self._runtime_session_id = session_id

    def _run(
        self,
        context: str | None = None,
    ) -> dict:

        if self._runtime_request is None:
            raise RuntimeError(
                "Decoy runtime request is unavailable."
            )

        session_id = (
            self._runtime_session_id
            if self._runtime_session_id is not None
            else "default"
        )

        result = self._decoy.respond(
            self._runtime_request,
            session_id,
        )

        self._runtime_result = result

        return result

    def get_runtime_result(self) -> dict | None:
        return self._runtime_result
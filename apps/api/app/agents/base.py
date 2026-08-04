"""
Base Agent — abstract class for all AI agents in the multi-agent system.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from pydantic import BaseModel


class AgentContext(BaseModel):
    """Context passed between agents during a workflow execution."""
    workflow_id: str = ""
    user_id: str = ""
    keyword: str = ""
    niche: str = ""
    audience: str = ""
    tone: str = "professional"
    goal: str = "engagement"
    generated_titles: list[dict] = []
    generated_descriptions: list[str] = []
    generated_keywords: list[str] = []
    generated_hashtags: list[str] = []
    generated_images: list[str] = []
    seo_score: float = 0.0
    quality_score: float = 0.0
    quality_flags: list[dict] = []
    trend_data: dict[str, Any] = {}
    strategy_recommendations: list[dict] = []
    errors: list[str] = []


class AgentResult(BaseModel):
    """Result returned by an agent after execution."""
    success: bool = True
    agent_name: str = ""
    workflow_id: str = ""
    output: dict[str, Any] = {}
    suggestions: list[str] = []
    error: Optional[str] = None
    processing_time_ms: float = 0.0


class BaseAgent(ABC):
    """Abstract base agent with logging, timing, and context management."""

    def __init__(self):
        self.name = self.__class__.__name__.replace("Agent", "")
        self.log: list[dict] = []

    @abstractmethod
    async def execute(self, context: AgentContext) -> AgentResult:
        """Execute the agent's primary task. Must be implemented by subclasses."""
        ...

    async def run(self, context: AgentContext) -> AgentResult:
        """Wrapper that times execution and logs the run."""
        start = datetime.now(timezone.utc)
        self._log("started", context)
        try:
            result = await self.execute(context)
            result.agent_name = self.name
            result.workflow_id = context.workflow_id
            elapsed = (datetime.now(timezone.utc) - start).total_seconds() * 1000
            result.processing_time_ms = round(elapsed, 2)
            self._log("completed", context, result)
            return result
        except Exception as e:
            elapsed = (datetime.now(timezone.utc) - start).total_seconds() * 1000
            self._log("failed", context, error=str(e))
            return AgentResult(
                success=False,
                agent_name=self.name,
                workflow_id=context.workflow_id,
                error=str(e),
                processing_time_ms=round(elapsed, 2),
            )

    def _log(self, status: str, context: AgentContext, result: Optional[AgentResult] = None, error: str = "") -> None:
        """Append a log entry for auditability."""
        self.log.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent": self.name,
            "status": status,
            "workflow_id": context.workflow_id,
            "keyword": context.keyword,
            "error": error,
        })
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.domain.events import StoryEvent


@dataclass(slots=True)
class CapabilitySpec:
    name: str
    site: str
    description: str
    input_schema: dict[str, Any]
    read_only: bool


@dataclass(slots=True)
class ActionRequest:
    action_id: str
    capability: str
    actor_id: str
    payload: dict[str, Any]
    idempotency_key: str


@dataclass(slots=True)
class ActionResult:
    action_id: str
    capability: str
    status: str
    output: dict[str, Any] = field(default_factory=dict)
    facts: list[str] = field(default_factory=list)
    events: list[StoryEvent] = field(default_factory=list)
    error_code: str | None = None
    error_message: str | None = None


@dataclass(slots=True)
class StoryStep:
    step_id: str
    capability: str
    actor_id: str
    payload: dict[str, Any]
    depends_on: list[str] = field(default_factory=list)
    rationale: str = ""


@dataclass(slots=True)
class StoryPlan:
    story_id: str
    goal: str
    steps: list[StoryStep]


@dataclass(slots=True)
class SchedulerRunReport:
    story_id: str
    goal: str
    status: str
    results: list[ActionResult] = field(default_factory=list)
    pending_steps: list[str] = field(default_factory=list)

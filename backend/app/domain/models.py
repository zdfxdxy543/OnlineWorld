from __future__ import annotations

from dataclasses import dataclass, field

from app.domain.events import StoryEvent


@dataclass(slots=True)
class AgentProfile:
    agent_id: str
    display_name: str
    role: str
    goals: list[str]


@dataclass(slots=True)
class WorldResource:
    resource_id: str
    resource_type: str
    title: str
    access_code: str
    owner_agent_id: str
    site_id: str
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class WorldSnapshot:
    current_tick: int
    current_time_label: str
    active_sites: list[str]
    recent_events: list[StoryEvent]


@dataclass(slots=True)
class DraftPostPlan:
    draft_id: str
    site_id: str
    topic: str
    agent: AgentProfile
    referenced_resource: WorldResource | None
    facts: list[str]
    event_trace: list[StoryEvent]


@dataclass(slots=True)
class GeneratedPostDraft:
    draft_id: str
    content: str
    consistency_passed: bool
    violations: list[str]
    event_trace: list[StoryEvent]
    referenced_resource: WorldResource | None
    facts: list[str]

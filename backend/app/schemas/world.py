from __future__ import annotations

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    app_name: str
    environment: str
    database_url: str
    llm_provider: str


class EventTraceItem(BaseModel):
    name: str
    detail: str
    metadata: dict[str, str]
    occurred_at: str


class WorldSummaryResponse(BaseModel):
    current_tick: int
    current_time_label: str
    active_sites: list[str]
    recent_events: list[EventTraceItem]


class DemoPostRequest(BaseModel):
    agent_id: str = Field(default="agent-001")
    site_id: str = Field(default="forum.main")
    topic: str = Field(default="在共享网盘里上传了今天的观察记录")
    attach_cloud_file: bool = True


class ReferencedResourceResponse(BaseModel):
    resource_id: str
    resource_type: str
    title: str
    access_code: str
    owner_agent_id: str
    site_id: str
    metadata: dict[str, str]


class DemoPostResponse(BaseModel):
    draft_id: str
    content: str
    consistency_passed: bool
    violations: list[str]
    facts: list[str]
    referenced_resource: ReferencedResourceResponse | None
    event_trace: list[EventTraceItem]

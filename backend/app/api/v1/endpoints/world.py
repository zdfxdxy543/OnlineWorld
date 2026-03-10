from __future__ import annotations

from fastapi import APIRouter, Request

from app.domain.events import StoryEvent
from app.domain.models import GeneratedPostDraft, WorldResource, WorldSnapshot
from app.schemas.world import (
    DemoPostRequest,
    DemoPostResponse,
    EventTraceItem,
    ReferencedResourceResponse,
    WorldSummaryResponse,
)

router = APIRouter()


def _map_event(event: StoryEvent) -> EventTraceItem:
    return EventTraceItem(
        name=event.name,
        detail=event.detail,
        metadata=event.metadata,
        occurred_at=event.occurred_at,
    )


def _map_resource(resource: WorldResource | None) -> ReferencedResourceResponse | None:
    if resource is None:
        return None
    return ReferencedResourceResponse(
        resource_id=resource.resource_id,
        resource_type=resource.resource_type,
        title=resource.title,
        access_code=resource.access_code,
        owner_agent_id=resource.owner_agent_id,
        site_id=resource.site_id,
        metadata=resource.metadata,
    )


def _map_world_summary(snapshot: WorldSnapshot) -> WorldSummaryResponse:
    return WorldSummaryResponse(
        current_tick=snapshot.current_tick,
        current_time_label=snapshot.current_time_label,
        active_sites=snapshot.active_sites,
        recent_events=[_map_event(event) for event in snapshot.recent_events],
    )


def _map_draft(draft: GeneratedPostDraft) -> DemoPostResponse:
    return DemoPostResponse(
        draft_id=draft.draft_id,
        content=draft.content,
        consistency_passed=draft.consistency_passed,
        violations=draft.violations,
        facts=draft.facts,
        referenced_resource=_map_resource(draft.referenced_resource),
        event_trace=[_map_event(event) for event in draft.event_trace],
    )


@router.get("/summary", response_model=WorldSummaryResponse)
def get_world_summary(request: Request) -> WorldSummaryResponse:
    container = request.app.state.container
    snapshot = container.world_service.get_summary()
    return _map_world_summary(snapshot)


@router.post("/demo-post", response_model=DemoPostResponse)
def create_demo_post(payload: DemoPostRequest, request: Request) -> DemoPostResponse:
    container = request.app.state.container
    draft = container.world_service.create_demo_post(payload)
    return _map_draft(draft)

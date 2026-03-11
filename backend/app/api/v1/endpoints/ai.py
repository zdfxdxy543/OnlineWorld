from __future__ import annotations

import json
from itertools import count

from fastapi import APIRouter, HTTPException, Request

from app.schemas.ai import (
    ActionExecuteRequest,
    ActionExecuteResponse,
    ActorSummaryResponse,
    CapabilitySpecResponse,
    SchedulerRunRequest,
    SchedulerRunResponse,
    StoryEventResponse,
)
from app.simulation.protocol import ActionRequest, ActionResult

router = APIRouter()
_action_counter = count(1)


def _map_events(items) -> list[StoryEventResponse]:
    return [
        StoryEventResponse(
            name=item.name,
            detail=item.detail,
            metadata=item.metadata,
            occurred_at=item.occurred_at,
        )
        for item in items
    ]


def _map_action_result(item: ActionResult) -> ActionExecuteResponse:
    return ActionExecuteResponse(
        action_id=item.action_id,
        capability=item.capability,
        status=item.status,
        output=item.output,
        facts=item.facts,
        events=_map_events(item.events),
        pipeline=item.pipeline,
        error_code=item.error_code,
        error_message=item.error_message,
    )


@router.get("/capabilities", response_model=list[CapabilitySpecResponse])
def list_capabilities(request: Request) -> list[CapabilitySpecResponse]:
    items = request.app.state.container.tool_registry.list_capabilities()
    return [
        CapabilitySpecResponse(
            name=item.name,
            site=item.site,
            description=item.description,
            input_schema=item.input_schema,
            read_only=item.read_only,
        )
        for item in items
    ]


@router.get("/actors", response_model=list[ActorSummaryResponse])
def list_actors(request: Request) -> list[ActorSummaryResponse]:
    world_service = request.app.state.container.world_service
    agents = world_service.list_agents()
    result: list[ActorSummaryResponse] = []
    for agent in agents:
        try:
            personality_traits = json.loads(agent.personality_traits_json)
        except json.JSONDecodeError:
            personality_traits = []
        try:
            values = json.loads(agent.values_json)
        except json.JSONDecodeError:
            values = []
        try:
            hobbies = json.loads(agent.hobbies_json)
        except json.JSONDecodeError:
            hobbies = []

        result.append(
            ActorSummaryResponse(
                id=agent.agent_id,
                name=agent.display_name,
                status=agent.status,
                gender=agent.gender,
                age_range=agent.age_range,
                occupation=agent.occupation,
                residence_city=agent.residence_city,
                native_language=agent.native_language,
                personality_traits=personality_traits,
                values=values,
                hobbies=hobbies,
            )
        )
    return result


@router.post("/execute", response_model=ActionExecuteResponse)
def execute_action(payload: ActionExecuteRequest, request: Request) -> ActionExecuteResponse:
    world_service = request.app.state.container.world_service
    if not world_service.agent_exists(payload.actor_id):
        raise HTTPException(status_code=404, detail=f"Actor not found in SQL agents: {payload.actor_id}")

    action_request = ActionRequest(
        action_id=f"manual-action-{next(_action_counter):05d}",
        capability=payload.capability,
        actor_id=payload.actor_id,
        payload=payload.payload,
        idempotency_key=payload.idempotency_key,
    )
    result = request.app.state.container.tool_registry.execute(action_request)
    return _map_action_result(result)


@router.post("/scheduler/run", response_model=SchedulerRunResponse)
def run_scheduler(payload: SchedulerRunRequest, request: Request) -> SchedulerRunResponse:
    world_service = request.app.state.container.world_service
    settings = request.app.state.container.settings
    spawned_actor = world_service.maybe_spawn_random_agent(settings.scheduler_new_actor_probability)

    actor_ids = payload.actors
    if not actor_ids:
        if spawned_actor is not None:
            actor_ids = [spawned_actor.agent_id]
        else:
            actor_ids = [item.agent_id for item in world_service.list_agents()[:1]]

    if not actor_ids:
        raise HTTPException(status_code=400, detail="No SQL-backed actors available")

    unknown_actors = [actor_id for actor_id in actor_ids if not world_service.agent_exists(actor_id)]
    if unknown_actors:
        raise HTTPException(
            status_code=404,
            detail=f"Actors not found in SQL agents: {', '.join(unknown_actors)}",
        )

    report = request.app.state.container.story_scheduler.run(goal=payload.goal, actors=actor_ids)
    return SchedulerRunResponse(
        story_id=report.story_id,
        goal=report.goal,
        status=report.status,
        results=[_map_action_result(item) for item in report.results],
        pending_steps=report.pending_steps,
        planner_name=report.planner_name,
        planner_source=report.planner_source,
        fallback_used=report.fallback_used,
        planner_detail=report.planner_detail,
        spawned_actor_id=spawned_actor.agent_id if spawned_actor else None,
        spawn_triggered=spawned_actor is not None,
    )

from __future__ import annotations

from itertools import count
import re
from typing import Any

from app.domain.events import StoryEvent
from app.simulation.planner import AbstractStoryPlanner
from app.simulation.protocol import ActionRequest, ActionResult, SchedulerRunReport
from app.simulation.tool_registry import ToolRegistry


class StoryScheduler:
    def __init__(self, planner: AbstractStoryPlanner, tool_registry: ToolRegistry) -> None:
        self.planner = planner
        self.tool_registry = tool_registry
        self._action_counter = count(1)

    def run(self, *, goal: str, actors: list[str]) -> SchedulerRunReport:
        allowed_actors = set(actors)
        capabilities = self.tool_registry.list_capabilities()
        plan = self.planner.build_story_plan(goal=goal, actors=actors, capabilities=capabilities)
        completed_steps: set[str] = set()
        remaining_steps = {step.step_id: step for step in plan.steps}
        results: list[ActionResult] = []
        step_results: dict[str, ActionResult] = {}

        progressed = True
        while remaining_steps and progressed:
            progressed = False
            for step_id in list(remaining_steps.keys()):
                step = remaining_steps[step_id]
                if any(dep not in completed_steps for dep in step.depends_on):
                    continue

                if step.actor_id not in allowed_actors:
                    failure = ActionResult(
                        action_id=f"action-{next(self._action_counter):05d}",
                        capability=step.capability,
                        status="failed",
                        error_code="invalid_actor",
                        error_message=f"Step actor is not allowed or missing from SQL users: {step.actor_id}",
                        events=[
                            StoryEvent(
                                name="AgentIntentCreated",
                                detail="调度器已下发结构化动作请求。",
                                metadata={"story_id": plan.story_id, "step_id": step.step_id},
                            )
                        ],
                    )
                    results.append(failure)
                    return SchedulerRunReport(
                        story_id=plan.story_id,
                        goal=goal,
                        status="failed",
                        results=results,
                        pending_steps=list(remaining_steps.keys()),
                    )

                try:
                    resolved_payload = self._resolve_payload(step.payload, step_results)
                except ValueError as error:
                    failure = ActionResult(
                        action_id=f"action-{next(self._action_counter):05d}",
                        capability=step.capability,
                        status="failed",
                        error_code="unresolved_reference",
                        error_message=str(error),
                        events=[
                            StoryEvent(
                                name="AgentIntentCreated",
                                detail="调度器已下发结构化动作请求。",
                                metadata={"story_id": plan.story_id, "step_id": step.step_id},
                            )
                        ],
                    )
                    results.append(failure)
                    return SchedulerRunReport(
                        story_id=plan.story_id,
                        goal=goal,
                        status="failed",
                        results=results,
                        pending_steps=list(remaining_steps.keys()),
                    )

                action_id = f"action-{next(self._action_counter):05d}"
                request = ActionRequest(
                    action_id=action_id,
                    capability=step.capability,
                    actor_id=step.actor_id,
                    payload=resolved_payload,
                    idempotency_key=f"{plan.story_id}:{step.step_id}",
                )
                result = self.tool_registry.execute(request)
                result.events.insert(
                    0,
                    StoryEvent(
                        name="AgentIntentCreated",
                        detail="调度器已下发结构化动作请求。",
                        metadata={"story_id": plan.story_id, "step_id": step.step_id},
                    ),
                )
                results.append(result)

                if result.status == "success":
                    completed_steps.add(step_id)
                    step_results[step_id] = result
                    remaining_steps.pop(step_id)
                    progressed = True
                else:
                    return SchedulerRunReport(
                        story_id=plan.story_id,
                        goal=goal,
                        status="failed",
                        results=results,
                        pending_steps=list(remaining_steps.keys()),
                    )

        status = "success" if not remaining_steps else "partial"
        return SchedulerRunReport(
            story_id=plan.story_id,
            goal=goal,
            status=status,
            results=results,
            pending_steps=list(remaining_steps.keys()),
        )

    def _resolve_payload(self, payload: dict[str, Any], step_results: dict[str, ActionResult]) -> dict[str, Any]:
        return {key: self._resolve_value(value, step_results) for key, value in payload.items()}

    def _resolve_value(self, value: Any, step_results: dict[str, ActionResult]) -> Any:
        if isinstance(value, dict):
            return {key: self._resolve_value(item, step_results) for key, item in value.items()}
        if isinstance(value, list):
            return [self._resolve_value(item, step_results) for item in value]
        if not isinstance(value, str):
            return value

        stripped = value.strip()
        if not stripped:
            return value

        if stripped.startswith("${") and stripped.endswith("}"):
            stripped = stripped[2:-1]

        if stripped.startswith("$"):
            return self._resolve_reference_path(stripped[1:], step_results)

        legacy_match = re.match(r"^(thread|board|post)_from_(step[_-]\d+)$", stripped)
        if legacy_match:
            kind = legacy_match.group(1)
            step_id = legacy_match.group(2)
            return self._resolve_legacy_reference(kind, step_id, step_results)

        return value

    def _resolve_reference_path(self, reference: str, step_results: dict[str, ActionResult]) -> Any:
        parts = reference.split(".")
        if len(parts) < 2:
            raise ValueError(f"Invalid reference syntax: ${reference}")

        step_id = parts[0]
        result = step_results.get(step_id)
        if result is None:
            raise ValueError(f"Reference step not completed: {step_id}")

        current: Any = {"output": result.output, "facts": result.facts}
        for token in parts[1:]:
            current = self._extract_token(current, token, reference)
        return current

    def _extract_token(self, current: Any, token: str, reference: str) -> Any:
        token_match = re.match(r"^(\w+)(?:\[(\d+)\])?$", token)
        if not token_match:
            raise ValueError(f"Invalid reference token '{token}' in ${reference}")

        key = token_match.group(1)
        index = token_match.group(2)

        if not isinstance(current, dict) or key not in current:
            raise ValueError(f"Reference key '{key}' not found in ${reference}")

        next_value = current[key]
        if index is not None:
            if not isinstance(next_value, list):
                raise ValueError(f"Reference target '{key}' is not a list in ${reference}")
            item_index = int(index)
            if item_index >= len(next_value):
                raise ValueError(f"Reference index out of range in ${reference}")
            return next_value[item_index]
        return next_value

    def _resolve_legacy_reference(self, kind: str, step_id: str, step_results: dict[str, ActionResult]) -> Any:
        result = step_results.get(step_id)
        if result is None:
            raise ValueError(f"Reference step not completed: {step_id}")

        if kind == "thread":
            return (
                result.output.get("thread_id")
                or result.output.get("thread", {}).get("id")
                or self._get_first_list_item_value(result.output.get("threads"), "id")
            )
        if kind == "board":
            return result.output.get("board", {}).get("slug") or result.output.get("board_id")
        if kind == "post":
            return result.output.get("post_id") or result.output.get("post", {}).get("id")
        raise ValueError(f"Unsupported legacy reference kind: {kind}")

    @staticmethod
    def _get_first_list_item_value(items: Any, key: str) -> Any:
        if not isinstance(items, list) or not items:
            return None
        first = items[0]
        if not isinstance(first, dict):
            return None
        return first.get(key)

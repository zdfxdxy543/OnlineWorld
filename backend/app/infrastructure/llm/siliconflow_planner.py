from __future__ import annotations

import json
from itertools import count
from urllib import error, request

from app.simulation.planner import AbstractStoryPlanner, RuleBasedStoryPlanner
from app.simulation.protocol import CapabilitySpec, StoryPlan, StoryStep


class SiliconFlowStoryPlanner(AbstractStoryPlanner):
    def __init__(
        self,
        *,
        api_key: str,
        model_name: str,
        base_url: str,
        fallback: RuleBasedStoryPlanner,
    ) -> None:
        self.api_key = api_key
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")
        self.fallback = fallback
        self._story_counter = count(1)

    def build_story_plan(
        self,
        *,
        goal: str,
        actors: list[str],
        capabilities: list[CapabilitySpec],
    ) -> StoryPlan:
        payload = self._build_payload(goal=goal, actors=actors, capabilities=capabilities)
        parsed = self._call_model(payload)
        if parsed is None:
            return self.fallback.build_story_plan(goal=goal, actors=actors, capabilities=capabilities)

        steps_data = parsed.get("steps", [])
        steps: list[StoryStep] = []
        for index, item in enumerate(steps_data, start=1):
            capability = str(item.get("capability", "")).strip()
            actor_id = str(item.get("actor_id", actors[0] if actors else "aria")).strip()
            payload_data = item.get("payload", {})
            depends_on = item.get("depends_on", [])
            rationale = str(item.get("rationale", "")).strip()
            if not capability or not isinstance(payload_data, dict):
                continue
            if not isinstance(depends_on, list):
                depends_on = []
            steps.append(
                StoryStep(
                    step_id=str(item.get("step_id", f"step-{index}")),
                    capability=capability,
                    actor_id=actor_id,
                    payload=payload_data,
                    depends_on=[str(dep) for dep in depends_on],
                    rationale=rationale,
                )
            )

        if not steps:
            return self.fallback.build_story_plan(goal=goal, actors=actors, capabilities=capabilities)

        story_id = str(parsed.get("story_id", f"sf-story-{next(self._story_counter):04d}"))
        return StoryPlan(story_id=story_id, goal=goal, steps=steps)

    def _build_payload(self, *, goal: str, actors: list[str], capabilities: list[CapabilitySpec]) -> dict:
        capability_lines = []
        for item in capabilities:
            capability_lines.append(
                {
                    "name": item.name,
                    "site": item.site,
                    "description": item.description,
                    "read_only": item.read_only,
                    "input_schema": item.input_schema,
                }
            )

        system_prompt = (
            "You are a story planner for a multi-site AI society simulation. "
            "Return ONLY JSON with fields: story_id, steps[]. "
            "Each step must include: step_id, capability, actor_id, payload, depends_on, rationale. "
            "Only use provided capabilities. Ensure causality and cross-site consistency. "
            "If an input_schema includes allowed_* values, you MUST use one of those exact values. "
            "Do not invent board slugs, thread ids, site ids, or capability names. "
            "When a later step needs an object from an earlier step, reference it explicitly using '$step_id.output.field' syntax. "
            "Example: use '$step_1.output.threads[0].id' or '$step_2.output.thread_id' instead of invented placeholders. "
            "For any publishable text such as title/content, write the final in-world forum text directly. "
            "Do not include prompt language like '生成一个', '请生成', '你是', '输出JSON', or any meta instructions in the content fields."
        )

        user_prompt = {
            "goal": goal,
            "actors": actors,
            "capabilities": capability_lines,
        }

        return {
            "model": self.model_name,
            "temperature": 0.2,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(user_prompt, ensure_ascii=True)},
            ],
            "response_format": {"type": "json_object"},
        }

    def _call_model(self, payload: dict) -> dict | None:
        endpoint = f"{self.base_url}/chat/completions"
        body = json.dumps(payload).encode("utf-8")
        http_request = request.Request(
            endpoint,
            data=body,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with request.urlopen(http_request, timeout=30) as response:
                response_text = response.read().decode("utf-8")
        except (TimeoutError, error.URLError, error.HTTPError):
            return None

        try:
            data = json.loads(response_text)
            content = data["choices"][0]["message"]["content"]
            if isinstance(content, str):
                return json.loads(content)
            if isinstance(content, dict):
                return content
            return None
        except (KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError):
            return None

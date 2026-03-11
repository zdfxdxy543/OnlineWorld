from __future__ import annotations

from abc import ABC, abstractmethod
from itertools import count

from app.simulation.protocol import CapabilitySpec, StoryPlan, StoryStep


class AbstractStoryPlanner(ABC):
    @abstractmethod
    def build_story_plan(
        self,
        *,
        goal: str,
        actors: list[str],
        capabilities: list[CapabilitySpec],
    ) -> StoryPlan:
        raise NotImplementedError


class RuleBasedStoryPlanner(AbstractStoryPlanner):
    def __init__(self) -> None:
        self._story_counter = count(1)

    def build_story_plan(
        self,
        *,
        goal: str,
        actors: list[str],
        capabilities: list[CapabilitySpec],
    ) -> StoryPlan:
        if not actors:
            actors = ["aria"]

        actor = actors[0]
        capability_names = {cap.name for cap in capabilities}
        steps: list[StoryStep] = []

        if "forum.read_board" in capability_names:
            steps.append(
                StoryStep(
                    step_id="step-1",
                    capability="forum.read_board",
                    actor_id=actor,
                    payload={"board_slug": "town-square", "limit": 10},
                    rationale="先读取公共上下文，减少知识越界风险。",
                )
            )

        if "forum.create_thread" in capability_names:
            steps.append(
                StoryStep(
                    step_id="step-2",
                    capability="forum.create_thread",
                    actor_id=actor,
                    payload={
                        "board_slug": "town-square",
                        "title": f"[Story Seed] {goal[:48]}",
                        "content": "先提交结构化事实，后续再补全细节与证据链。",
                        "tags": ["story", "seed"],
                    },
                    depends_on=["step-1"] if steps else [],
                    rationale="建立可追踪的初始事件节点。",
                )
            )

        story_id = f"story-{next(self._story_counter):04d}"
        return StoryPlan(story_id=story_id, goal=goal, steps=steps)

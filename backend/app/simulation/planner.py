from __future__ import annotations

from abc import ABC, abstractmethod
from itertools import count
import re

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
    _SUSPICIOUS_SCENARIOS = [
        {
            "file_title": "Warehouse Movement Log",
            "file_name": "warehouse_timeline.txt",
            "purpose": "Archive late-night movement, light changes, and timing anomalies near the old warehouse.",
            "thread_title": "[Evidence] Warehouse lights after curfew",
            "thread_content": "Collected notes suggest repeated movement around the old warehouse after closing hours.",
            "tags": ["evidence", "warehouse", "timeline"],
        },
        {
            "file_title": "Dockside Transfer Notes",
            "file_name": "dock_transfer_log.txt",
            "purpose": "Record suspicious dockside handoff timing and vehicle movement for later cross-checking.",
            "thread_title": "[Evidence] Unscheduled dockside handoff",
            "thread_content": "I compiled a short record of an unscheduled transfer near the dock. The timing does not match routine deliveries.",
            "tags": ["evidence", "dock", "transfer"],
        },
        {
            "file_title": "Witness Corridor Memo",
            "file_name": "witness_corridor_memo.txt",
            "purpose": "Preserve witness-style notes about repeated hallway meetings and abrupt departures.",
            "thread_title": "[Witness Notes] Repeated corridor meetings",
            "thread_content": "This memo collects consistent observations about the same pair meeting briefly and leaving by separate exits.",
            "tags": ["witness", "memo", "suspicious"],
        },
        {
            "file_title": "Transit Timeline Extract",
            "file_name": "transit_timeline.txt",
            "purpose": "Track suspicious transit timing gaps and cross-reference them against reported sightings.",
            "thread_title": "[Timeline] Transit gap around reported sighting",
            "thread_content": "The timeline below highlights a service gap that overlaps with the reported sighting window.",
            "tags": ["timeline", "transit", "evidence"],
        },
    ]

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
        story_number = next(self._story_counter)
        scenario = self._select_suspicious_scenario(goal=goal, story_number=story_number)

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

        if {"netdisk.upload_file", "netdisk.create_share_link", "forum.create_thread"}.issubset(capability_names):
            steps.append(
                StoryStep(
                    step_id="step-2",
                    capability="netdisk.upload_file",
                    actor_id=actor,
                    payload={
                        "title": scenario["file_title"],
                        "purpose": scenario["purpose"],
                        "file_name": scenario["file_name"],
                    },
                    depends_on=["step-1"] if steps else [],
                    rationale="先生成可追溯证据文件。",
                )
            )
            steps.append(
                StoryStep(
                    step_id="step-3",
                    capability="netdisk.create_share_link",
                    actor_id=actor,
                    payload={
                        "resource_id": "$step-2.output.resource_id",
                    },
                    depends_on=["step-2"],
                    rationale="创建分享链接与提取码供论坛引用。",
                )
            )
            steps.append(
                StoryStep(
                    step_id="step-4",
                    capability="forum.create_thread",
                    actor_id=actor,
                    payload={
                        "board_slug": "town-square",
                        "title": scenario["thread_title"],
                        "content": scenario["thread_content"],
                        "tags": scenario["tags"],
                        "netdisk_share_id": "$step-3.output.share_id",
                        "netdisk_access_code": "$step-3.output.access_code",
                    },
                    depends_on=["step-3"],
                    rationale="在帖子中引用真实可访问的网盘证据。",
                )
            )
        elif "forum.create_thread" in capability_names:
            steps.append(
                StoryStep(
                    step_id="step-2",
                    capability="forum.create_thread",
                    actor_id=actor,
                    payload={
                        "board_slug": "town-square",
                        "title": scenario["thread_title"],
                        "content": scenario["thread_content"],
                        "tags": scenario["tags"],
                    },
                    depends_on=["step-1"] if steps else [],
                    rationale="建立可追踪的初始事件节点。",
                )
            )

        story_id = f"story-{story_number:04d}"
        return StoryPlan(
            story_id=story_id,
            goal=goal,
            steps=steps,
            planner_name="rule_based",
            planner_source="local_rule",
            fallback_used=False,
            planner_detail="Plan generated by the built-in deterministic rule-based planner.",
        )

    def _select_suspicious_scenario(self, *, goal: str, story_number: int) -> dict[str, object]:
        normalized_goal = re.sub(r"\s+", " ", goal.strip().lower())
        keyword_map = {
            "warehouse": 0,
            "dock": 1,
            "witness": 2,
            "transit": 3,
            "station": 3,
        }
        for keyword, index in keyword_map.items():
            if keyword in normalized_goal:
                return self._SUSPICIOUS_SCENARIOS[index]

        if any(phrase in normalized_goal for phrase in ["generate a story", "something suspicious", "suspicious"]):
            return self._SUSPICIOUS_SCENARIOS[(story_number - 1) % len(self._SUSPICIOUS_SCENARIOS)]

        return {
            "file_title": "Field Notes Archive",
            "file_name": "field_notes.txt",
            "purpose": f"Preserve notes related to: {goal.strip() or 'unusual activity'}.",
            "thread_title": "[Story Seed] Unusual activity under review",
            "thread_content": "I collected a short set of notes about an unusual pattern worth reviewing.",
            "tags": ["story", "seed"],
        }

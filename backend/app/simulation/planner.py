from __future__ import annotations

from abc import ABC, abstractmethod
from itertools import count
import random
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


class LifeEventStoryPlanner(AbstractStoryPlanner):
    _LIFE_EVENTS = [
        {
            "title": "[Daily] Morning Market Was Crowded",
            "content": "The market opened early and lines were longer than usual. Prices stayed stable, but everyone discussed the weather shift.",
            "tags": ["daily", "market", "community"],
        },
        {
            "title": "[Daily] Neighborhood Cleanup This Weekend",
            "content": "Several neighbors proposed a cleanup walk this weekend. People are sharing tools and meeting points.",
            "tags": ["daily", "neighborhood", "event"],
        },
        {
            "title": "[Daily] Bus Schedule Updated Near Station",
            "content": "The station posted a minor schedule update. Commuters are comparing the new timing and planning alternatives.",
            "tags": ["daily", "transit", "notice"],
        },
        {
            "title": "[Daily] Community Kitchen Added Evening Slot",
            "content": "The community kitchen added an evening slot this week. Volunteers are coordinating ingredient pickup.",
            "tags": ["daily", "community", "kitchen"],
        },
    ]

    def __init__(
        self,
        *,
        netdisk_probability: float = 0.15,
        news_probability: float = 0.10,
    ) -> None:
        self._story_counter = count(1)
        self.netdisk_probability = max(0.0, min(1.0, netdisk_probability))
        self.news_probability = max(0.0, min(1.0, news_probability))

    def build_story_plan(
        self,
        *,
        goal: str,
        actors: list[str],
        capabilities: list[CapabilitySpec],
    ) -> StoryPlan:
        if not actors:
            actors = ["aria"]

        capability_names = {cap.name for cap in capabilities}
        story_number = next(self._story_counter)
        event = self._LIFE_EVENTS[(story_number - 1) % len(self._LIFE_EVENTS)]
        if goal.strip():
            event = {
                "title": "[Daily] Community Update",
                "content": f"Residents are discussing: {goal.strip()}",
                "tags": ["daily", "community"],
            }

        primary_actor = actors[0]
        secondary_actor = actors[1] if len(actors) > 1 else primary_actor
        tertiary_actor = actors[2] if len(actors) > 2 else secondary_actor

        rng = random.Random(f"life-{story_number}-{goal.strip().lower()}-{','.join(actors)}")
        steps: list[StoryStep] = []

        if "forum.create_thread" not in capability_names:
            return StoryPlan(
                story_id=f"life-story-{story_number:04d}",
                goal=goal,
                steps=[],
                planner_name="life_event_rule",
                planner_source="local_rule",
                fallback_used=False,
                planner_detail="No forum.create_thread capability available for life-event planner.",
            )

        steps.append(
            StoryStep(
                step_id="step-1",
                capability="forum.create_thread",
                actor_id=primary_actor,
                payload={
                    "board_slug": "town-square",
                    "title": event["title"],
                    "content": event["content"],
                    "tags": event["tags"],
                },
                rationale="发布一个生活化主题帖，作为讨论起点。",
            )
        )

        next_index = 2
        reply_count = 2 if len(actors) >= 3 else 1
        if "forum.reply_thread" in capability_names:
            reply_actors = [secondary_actor, tertiary_actor][:reply_count]
            for reply_actor in reply_actors:
                steps.append(
                    StoryStep(
                        step_id=f"step-{next_index}",
                        capability="forum.reply_thread",
                        actor_id=reply_actor,
                        payload={
                            "thread_id": "$step-1.output.thread_id",
                            "content": "Share one practical detail from daily experience and one suggestion for neighbors.",
                        },
                        depends_on=[f"step-{next_index - 1}"] if next_index > 2 else ["step-1"],
                        rationale="让不同角色参与生活讨论，增加真实互动感。",
                    )
                )
                next_index += 1

        share_step_id: str | None = None
        if (
            {"netdisk.upload_file", "netdisk.create_share_link", "forum.create_thread"}.issubset(capability_names)
            and rng.random() < self.netdisk_probability
        ):
            upload_step_id = f"step-{next_index}"
            steps.append(
                StoryStep(
                    step_id=upload_step_id,
                    capability="netdisk.upload_file",
                    actor_id=primary_actor,
                    payload={
                        "title": "Daily Notes Attachment",
                        "purpose": "Store a simple life-event note for anyone who wants details.",
                        "file_name": "daily_notes.txt",
                    },
                    depends_on=[steps[-1].step_id],
                    rationale="低概率附加网盘材料，保留生活主题为主。",
                )
            )
            next_index += 1

            share_step_id = f"step-{next_index}"
            steps.append(
                StoryStep(
                    step_id=share_step_id,
                    capability="netdisk.create_share_link",
                    actor_id=primary_actor,
                    payload={"resource_id": f"${upload_step_id}.output.resource_id"},
                    depends_on=[upload_step_id],
                    rationale="创建低频分享链接，供后续引用。",
                )
            )
            next_index += 1

            steps.append(
                StoryStep(
                    step_id=f"step-{next_index}",
                    capability="forum.create_thread",
                    actor_id=secondary_actor,
                    payload={
                        "board_slug": "town-square",
                        "title": "[Daily Follow-up] Details and Community Responses",
                        "content": "Follow-up summary for residents who asked for more context.",
                        "tags": ["daily", "follow-up"],
                        "netdisk_share_id": f"${share_step_id}.output.share_id",
                        "netdisk_access_code": f"${share_step_id}.output.access_code",
                    },
                    depends_on=[share_step_id],
                    rationale="将网盘引用放在后续帖，避免主流程过重。",
                )
            )
            next_index += 1

        if "news.publish_article" in capability_names and rng.random() < self.news_probability:
            news_dep = steps[-1].step_id
            related_share_ids = [f"${share_step_id}.output.share_id"] if share_step_id else []
            steps.append(
                StoryStep(
                    step_id=f"step-{next_index}",
                    capability="news.publish_article",
                    actor_id=tertiary_actor,
                    payload={
                        "title": "Community Brief: Daily Events Roundup",
                        "content": "Short daily roundup based on ongoing forum discussions.",
                        "category": "community",
                        "is_pinned": False,
                        "related_thread_ids": ["$step-1.output.thread_id"],
                        "related_share_ids": related_share_ids,
                    },
                    depends_on=[news_dep],
                    rationale="低概率生成新闻摘要，保持论坛生活流为主。",
                )
            )

        return StoryPlan(
            story_id=f"life-story-{story_number:04d}",
            goal=goal,
            steps=steps,
            planner_name="life_event_rule",
            planner_source="local_rule",
            fallback_used=False,
            planner_detail="Simple life-event planner with low netdisk/news trigger probabilities.",
        )

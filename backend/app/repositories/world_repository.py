from __future__ import annotations

from abc import ABC, abstractmethod
from itertools import count
import random

from app.domain.events import StoryEvent
from app.domain.models import AgentProfile, AgentSummary, WorldResource, WorldSnapshot


class AbstractWorldRepository(ABC):
    @abstractmethod
    def get_world_snapshot(self) -> WorldSnapshot:
        raise NotImplementedError

    @abstractmethod
    def get_agent(self, agent_id: str) -> AgentProfile:
        raise NotImplementedError

    @abstractmethod
    def list_agents(self) -> list[AgentSummary]:
        raise NotImplementedError

    @abstractmethod
    def agent_exists(self, agent_id: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def create_cloud_resource(self, *, owner_agent_id: str, site_id: str, title: str) -> WorldResource:
        raise NotImplementedError

    @abstractmethod
    def create_random_agent(self) -> AgentSummary:
        raise NotImplementedError


class InMemoryWorldRepository(AbstractWorldRepository):
    def __init__(self) -> None:
        self._resource_counter = count(1)
        self._agent_counter = count(1)
        self._agents = {
            "agent-001": AgentProfile(
                agent_id="agent-001",
                display_name="林澄",
                role="论坛观察者",
                goals=["记录异常线索", "保持低调", "验证消息来源"],
            ),
            "agent-002": AgentProfile(
                agent_id="agent-002",
                display_name="周原",
                role="二手市场卖家",
                goals=["扩大影响力", "搜集匿名传闻"],
            ),
        }
        self._resources: dict[str, WorldResource] = {}

    def get_world_snapshot(self) -> WorldSnapshot:
        recent_events = [
            StoryEvent(
                name="WorldBootstrapped",
                detail="世界状态初始化完成，论坛与交易站已开放。",
                metadata={"sites": "forum.main,market.square,message.direct"},
            )
        ]
        return WorldSnapshot(
            current_tick=1,
            current_time_label="Day 1 / 08:00",
            active_sites=["forum.main", "market.square", "message.direct"],
            recent_events=recent_events,
        )

    def get_agent(self, agent_id: str) -> AgentProfile:
        if agent_id not in self._agents:
            raise KeyError(f"Agent not found: {agent_id}")
        return self._agents[agent_id]

    def list_agents(self) -> list[AgentSummary]:
        return [
            AgentSummary(
                agent_id=agent.agent_id,
                display_name=agent.display_name,
                status="Online",
                gender="unknown",
                age_range="unknown",
                occupation=agent.role,
                residence_city="unknown",
                native_language="zh-CN",
                personality_traits_json="[]",
                values_json="[]",
                hobbies_json="[]",
            )
            for agent in self._agents.values()
        ]

    def agent_exists(self, agent_id: str) -> bool:
        return agent_id in self._agents

    def create_cloud_resource(self, *, owner_agent_id: str, site_id: str, title: str) -> WorldResource:
        index = next(self._resource_counter)
        resource_id = f"cloud-{index:04d}"
        access_code = f"K{index:03d}X"
        resource = WorldResource(
            resource_id=resource_id,
            resource_type="cloud_file",
            title=title,
            access_code=access_code,
            owner_agent_id=owner_agent_id,
            site_id=site_id,
            metadata={
                "download_hint": f"https://files.local/{resource_id}",
                "visibility": "shared-with-link",
            },
        )
        self._resources[resource_id] = resource
        return resource

    def create_random_agent(self) -> AgentSummary:
        index = next(self._agent_counter)
        agent_id = f"npc-{index:04d}"
        display_name = f"路人_{index:04d}"
        role = random.choice(["夜班保安", "网吧店员", "物流调度", "二手店主"])
        status = random.choice(["Online", "Away", "Busy"])
        self._agents[agent_id] = AgentProfile(
            agent_id=agent_id,
            display_name=display_name,
            role=role,
            goals=["获取最新消息", "保护个人利益"],
        )
        return AgentSummary(
            agent_id=agent_id,
            display_name=display_name,
            status=status,
            gender="unknown",
            age_range="25-34",
            occupation=role,
            residence_city="unknown",
            native_language="zh-CN",
            personality_traits_json='["alert", "pragmatic"]',
            values_json='["stability", "privacy"]',
            hobbies_json='["forums", "late-night browsing"]',
        )

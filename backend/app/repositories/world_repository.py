from __future__ import annotations

from abc import ABC, abstractmethod
from itertools import count

from app.domain.events import StoryEvent
from app.domain.models import AgentProfile, WorldResource, WorldSnapshot


class AbstractWorldRepository(ABC):
    @abstractmethod
    def get_world_snapshot(self) -> WorldSnapshot:
        raise NotImplementedError

    @abstractmethod
    def get_agent(self, agent_id: str) -> AgentProfile:
        raise NotImplementedError

    @abstractmethod
    def create_cloud_resource(self, *, owner_agent_id: str, site_id: str, title: str) -> WorldResource:
        raise NotImplementedError


class InMemoryWorldRepository(AbstractWorldRepository):
    def __init__(self) -> None:
        self._resource_counter = count(1)
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

from __future__ import annotations

from dataclasses import dataclass

from app.consistency.checker import ConsistencyChecker
from app.core.config import Settings
from app.infrastructure.db.forum_repository import SQLiteForumRepository
from app.infrastructure.db.netdisk_repository import SQLiteNetdiskRepository
from app.infrastructure.db.session import DatabaseSessionManager
from app.infrastructure.db.world_repository import SQLiteWorldRepository
from app.infrastructure.llm.base import AbstractLLMClient
from app.infrastructure.llm.siliconflow_client import SiliconFlowLLMClient
from app.infrastructure.llm.structured_content import (
    AbstractStructuredContentGenerator,
    SiliconFlowStructuredContentGenerator,
)
from app.infrastructure.llm.siliconflow_planner import SiliconFlowStoryPlanner
from app.repositories.forum_repository import AbstractForumRepository
from app.services.forum_service import ForumService
from app.services.generation_service import GenerationService
from app.services.netdisk_service import NetdiskService
from app.services.world_service import WorldService
from app.simulation.engine import SimulationEngine
from app.simulation.planner import AbstractStoryPlanner, RuleBasedStoryPlanner
from app.simulation.scheduler import StoryScheduler
from app.simulation.tool_registry import ToolRegistry
from app.simulation.tools.forum_pipeline import ForumPipelineToolExecutor
from app.simulation.tools.netdisk_pipeline import NetdiskPipelineToolExecutor


@dataclass(slots=True)
class ServiceContainer:
    settings: Settings
    database_session_manager: DatabaseSessionManager
    world_service: WorldService
    forum_service: ForumService
    netdisk_service: NetdiskService
    tool_registry: ToolRegistry
    story_scheduler: StoryScheduler


def build_container(settings: Settings) -> ServiceContainer:
    if settings.llm_provider.lower() != "siliconflow":
        raise RuntimeError(
            f"Unsupported LLM_PROVIDER={settings.llm_provider}. Strict mode requires LLM_PROVIDER=siliconflow."
        )
    if not settings.siliconflow_api_key:
        raise RuntimeError("LLM_PROVIDER=siliconflow but SILICONFLOW_API_KEY is missing")

    database_session_manager = DatabaseSessionManager(settings.database_url)
    forum_repository: AbstractForumRepository = SQLiteForumRepository(database_session_manager)
    forum_repository.initialize()
    database_session_manager.mark_initialized()

    world_repository = SQLiteWorldRepository(database_session_manager)
    world_repository.initialize()
    simulation_engine = SimulationEngine(world_repository)
    consistency_checker = ConsistencyChecker()
    llm_client: AbstractLLMClient = SiliconFlowLLMClient(
        api_key=settings.siliconflow_api_key,
        model_name=settings.llm_model,
        base_url=settings.siliconflow_base_url,
        max_attempts=3,
    )
    generation_service = GenerationService(llm_client, consistency_checker)
    world_service = WorldService(world_repository, simulation_engine, generation_service)
    forum_service = ForumService(forum_repository)
    netdisk_repository = SQLiteNetdiskRepository(database_session_manager)
    netdisk_repository.initialize()
    netdisk_service = NetdiskService(netdisk_repository, storage_dir=settings.netdisk_storage_dir)

    content_generator: AbstractStructuredContentGenerator = SiliconFlowStructuredContentGenerator(
        api_key=settings.siliconflow_api_key,
        model_name=settings.llm_model,
        base_url=settings.siliconflow_base_url,
        max_attempts=3,
    )

    tool_registry = ToolRegistry(
        executors=[
            NetdiskPipelineToolExecutor(netdisk_service, content_generator),
            ForumPipelineToolExecutor(forum_service, consistency_checker, netdisk_service, content_generator),
        ]
    )

    planner: AbstractStoryPlanner = SiliconFlowStoryPlanner(
        api_key=settings.siliconflow_api_key,
        model_name=settings.siliconflow_planner_model,
        base_url=settings.siliconflow_base_url,
        max_attempts=3,
    )

    story_scheduler = StoryScheduler(planner=planner, tool_registry=tool_registry)

    return ServiceContainer(
        settings=settings,
        database_session_manager=database_session_manager,
        world_service=world_service,
        forum_service=forum_service,
        netdisk_service=netdisk_service,
        tool_registry=tool_registry,
        story_scheduler=story_scheduler,
    )

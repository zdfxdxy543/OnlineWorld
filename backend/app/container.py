from __future__ import annotations

from dataclasses import dataclass

from app.consistency.checker import ConsistencyChecker
from app.core.config import Settings
from app.infrastructure.db.forum_repository import SQLiteForumRepository
from app.infrastructure.db.session import DatabaseSessionManager
from app.infrastructure.db.world_repository import SQLiteWorldRepository
from app.infrastructure.llm.mock_client import MockLLMClient
from app.infrastructure.llm.siliconflow_planner import SiliconFlowStoryPlanner
from app.repositories.forum_repository import AbstractForumRepository
from app.services.forum_service import ForumService
from app.services.generation_service import GenerationService
from app.services.world_service import WorldService
from app.simulation.engine import SimulationEngine
from app.simulation.planner import AbstractStoryPlanner, RuleBasedStoryPlanner
from app.simulation.scheduler import StoryScheduler
from app.simulation.tool_registry import ToolRegistry
from app.simulation.tools.forum_tools import ForumToolExecutor


@dataclass(slots=True)
class ServiceContainer:
    settings: Settings
    database_session_manager: DatabaseSessionManager
    world_service: WorldService
    forum_service: ForumService
    tool_registry: ToolRegistry
    story_scheduler: StoryScheduler


def build_container(settings: Settings) -> ServiceContainer:
    database_session_manager = DatabaseSessionManager(settings.database_url)
    forum_repository: AbstractForumRepository = SQLiteForumRepository(database_session_manager)
    forum_repository.initialize()
    database_session_manager.mark_initialized()

    world_repository = SQLiteWorldRepository(database_session_manager)
    world_repository.initialize()
    simulation_engine = SimulationEngine(world_repository)
    consistency_checker = ConsistencyChecker()
    llm_client = MockLLMClient(settings.llm_model)
    generation_service = GenerationService(llm_client, consistency_checker)
    world_service = WorldService(world_repository, simulation_engine, generation_service)
    forum_service = ForumService(forum_repository)
    tool_registry = ToolRegistry(executors=[ForumToolExecutor(forum_service)])

    fallback_planner = RuleBasedStoryPlanner()
    planner: AbstractStoryPlanner = fallback_planner
    if settings.llm_provider.lower() == "siliconflow" and settings.siliconflow_api_key:
        planner = SiliconFlowStoryPlanner(
            api_key=settings.siliconflow_api_key,
            model_name=settings.siliconflow_planner_model,
            base_url=settings.siliconflow_base_url,
            fallback=fallback_planner,
        )

    story_scheduler = StoryScheduler(planner=planner, tool_registry=tool_registry)

    return ServiceContainer(
        settings=settings,
        database_session_manager=database_session_manager,
        world_service=world_service,
        forum_service=forum_service,
        tool_registry=tool_registry,
        story_scheduler=story_scheduler,
    )

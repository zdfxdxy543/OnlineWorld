from __future__ import annotations

from dataclasses import dataclass

from app.consistency.checker import ConsistencyChecker
from app.core.config import Settings
from app.infrastructure.db.session import DatabaseSessionManager
from app.infrastructure.llm.mock_client import MockLLMClient
from app.repositories.world_repository import InMemoryWorldRepository
from app.services.generation_service import GenerationService
from app.services.world_service import WorldService
from app.simulation.engine import SimulationEngine


@dataclass(slots=True)
class ServiceContainer:
    settings: Settings
    database_session_manager: DatabaseSessionManager
    world_service: WorldService


def build_container(settings: Settings) -> ServiceContainer:
    world_repository = InMemoryWorldRepository()
    simulation_engine = SimulationEngine(world_repository)
    consistency_checker = ConsistencyChecker()
    llm_client = MockLLMClient(settings.llm_model)
    generation_service = GenerationService(llm_client, consistency_checker)
    world_service = WorldService(world_repository, simulation_engine, generation_service)
    database_session_manager = DatabaseSessionManager(settings.database_url)
    return ServiceContainer(
        settings=settings,
        database_session_manager=database_session_manager,
        world_service=world_service,
    )

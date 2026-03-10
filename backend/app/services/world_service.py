from __future__ import annotations

from app.domain.models import GeneratedPostDraft, WorldSnapshot
from app.schemas.world import DemoPostRequest
from app.services.generation_service import GenerationService
from app.simulation.engine import SimulationEngine
from app.repositories.world_repository import AbstractWorldRepository


class WorldService:
    def __init__(
        self,
        world_repository: AbstractWorldRepository,
        simulation_engine: SimulationEngine,
        generation_service: GenerationService,
    ) -> None:
        self.world_repository = world_repository
        self.simulation_engine = simulation_engine
        self.generation_service = generation_service

    def get_summary(self) -> WorldSnapshot:
        return self.world_repository.get_world_snapshot()

    def create_demo_post(self, payload: DemoPostRequest) -> GeneratedPostDraft:
        plan = self.simulation_engine.prepare_demo_post(
            agent_id=payload.agent_id,
            site_id=payload.site_id,
            topic=payload.topic,
            attach_cloud_file=payload.attach_cloud_file,
        )
        return self.generation_service.generate_post(plan)

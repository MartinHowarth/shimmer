import asyncio
import logging

from typing import Optional

from ..entity.entity import Entity
from .definition import StagedEntityDefinition

log = logging.getLogger(__name__)


class StagedEntity(Entity):
    def __init__(self, definition: StagedEntityDefinition) -> None:
        super(StagedEntity, self).__init__(definition)
        self.current_stage: int = 0
        self.complete: bool = False
        self.stage_blocker: Optional[asyncio.Event] = None
        self.stage_advancement_time_s: float = 0

    def advance_one_stage(self) -> None:
        self.current_stage += 1
        if self.current_stage == self.definition.num_stages:
            self.complete = True

    async def _update(self, dt_s: float):
        # Wait for next stage to be unblocked.
        await self.stage_blocker.wait()

        log.debug(f"{self.definition.name} entered stage {self.current_stage}.")
        await asyncio.sleep(self.definition.stage_time_s)
        log.debug(f"{self.definition.name} ready for next stage.")

        # Clear the event so it can be re-used for the next stage.
        self.stage_blocker.clear()
        self.advance_one_stage()

        if self.complete:
            self.running = False

    async def run(self) -> None:
        self.stage_blocker = asyncio.Event()
        await super(StagedEntity, self).run()
        log.debug(f"{self.definition.name} is complete.")

    def __str__(self) -> str:
        if self.complete:
            text = f"{self.definition.name}: Done"
        else:
            text = f"{self.definition.name}: {self.current_stage}"
        return text

"""An Entitiy that advances through various stages."""

import asyncio
import logging

from typing import Optional

from ..entity.entity import Entity
from .definition import StagedEntityDefinition

log = logging.getLogger(__name__)


class StagedEntity(Entity):
    """
    An Entitiy that advances through various stages.

    The entity waits for an external actor to unblock it before it can move onto the next stage.
    """

    definition: StagedEntityDefinition

    def __init__(self, definition: StagedEntityDefinition) -> None:
        """Create a StagedEntity."""
        super(StagedEntity, self).__init__(definition)
        self.current_stage: int = 0
        self.complete: bool = False
        self.stage_blocker: Optional[asyncio.Event] = None
        self.stage_advancement_time_s: float = 0

    def advance_one_stage(self) -> None:
        """Step forward to the next stage."""
        self.current_stage += 1
        if self.current_stage == self.definition.num_stages:
            self.complete = True

    async def _update(self, dt_s: float) -> None:
        """Handles waiting for stage unblocking and waiting for stage completion time."""
        if self.stage_blocker is None:
            # We shouldn't have `_update` called unless `run` is called, which sets up the
            # stage blocker, but added this check for safety.
            return

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
        """The loop of this Entity that schedules its updates."""
        self.stage_blocker = asyncio.Event()
        await super(StagedEntity, self).run()
        log.debug(f"{self.definition.name} is complete.")

    def __str__(self) -> str:
        """String representation of a StagedEntity."""
        if self.complete:
            text = f"{self.definition.name}: Done"
        else:
            text = f"{self.definition.name}: {self.current_stage}"
        return text

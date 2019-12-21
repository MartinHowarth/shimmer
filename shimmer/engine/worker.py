"""An Entity that does work on another entity."""

import asyncio
import logging

from shimmer.engine.entity.entity import Entity
from shimmer.engine.entity.definition import EntityDefinition
from shimmer.engine.staged_entity.entity import StagedEntity

log = logging.getLogger(__name__)


class Worker(Entity):
    """An Entity that does work on another entity."""

    def __init__(self, target: StagedEntity) -> None:
        """
        Create a Worker.

        :param target: The target entity to work on.
        """
        super(Worker, self).__init__(EntityDefinition(name="worker"))
        self.target = target
        self.rest_period = 0

    async def _update(self, dt_s: float) -> None:
        """Action to perform on every update tick."""
        if self.target.stage_blocker and not self.target.stage_blocker.is_set():
            log.debug(f"Starting work on {self.target.definition.name}")
            await asyncio.sleep(self.target.stage_advancement_time_s)
            self.target.stage_blocker.set()
            log.debug(f"Finished working on {self.target.definition.name}")
            await asyncio.sleep(self.rest_period)
        else:
            log.debug(f"Worker {id(self)!r} has no work to do.")

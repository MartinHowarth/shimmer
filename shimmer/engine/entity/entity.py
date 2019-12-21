"""An entity is an object that regularly runs its defined actions."""

import asyncio
import logging
import time

from .definition import EntityDefinition

log = logging.getLogger(__name__)


class Entity:
    """
    An object that regularly defines its configured actions.

    Requires an EntityManager to manage it.
    """

    def __init__(self, definition: EntityDefinition) -> None:
        """
        Create a new Entity.

        :param definition: Definition for the entity to use.
        """
        self.definition = definition
        self.running = False
        self._update_interval_s: float = 1
        self._last_update_time_s: float = 0

    @property
    def seconds_since_last_update(self) -> float:
        """
        Number of seconds since this entity was last updated.

        Useful as the update interval is a target and will not be exactly adhered to.
        """
        return time.monotonic() - self._last_update_time_s

    async def _update(self, dt_s: float) -> None:
        """
        Perform the regular actions of this entity.

        :param dt_s: Seconds since the last update was completed.
        """
        pass

    async def run(self) -> None:
        """The loop of this Entity that schedules its updates."""
        self.running = True
        while self.running:
            self._last_update_time_s = time.monotonic()
            if (
                sleep_time_s := self._update_interval_s - self.seconds_since_last_update
                > 0
            ) :
                await asyncio.sleep(sleep_time_s)
            await self._update(self.seconds_since_last_update)

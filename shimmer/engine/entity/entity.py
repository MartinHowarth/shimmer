import asyncio
import logging
import time

from .definition import EntityDefinition

log = logging.getLogger(__name__)


class Entity:
    def __init__(self, definition: EntityDefinition) -> None:
        self.definition = definition
        self.running = False
        self._update_interval_s: float = 1
        self._last_update_time_s: float = 0

    @property
    def seconds_since_last_update(self) -> float:
        return time.monotonic() - self._last_update_time_s

    async def _update(self, dt_s: float):
        pass

    async def run(self) -> None:
        self.running = True
        while self.running:
            self._last_update_time_s = time.monotonic()
            if (
                sleep_time_s := self._update_interval_s - self.seconds_since_last_update
                > 0
            ) :
                await asyncio.sleep(sleep_time_s)
            await self._update(self.seconds_since_last_update)

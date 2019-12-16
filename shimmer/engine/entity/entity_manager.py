"""Manager for many entities. Handles async scheduling of Entities."""

import asyncio
import janus

from typing import List, Optional

from shimmer.engine.entity.entity import Entity


class AsyncManager:
    """
    Async manager for Entitys.

    Provides a sync-async interface to interact with Entities.
    """

    def __init__(self) -> None:
        """Create an AsyncManager."""
        self.entities: List[Entity] = []
        self.running = False
        self.__to_be_started: Optional[janus.Queue[Entity]] = None
        self.__loop: Optional[asyncio.AbstractEventLoop] = None

    def set_event_loop(self, loop: asyncio.BaseEventLoop):
        """Set the event loop on this manager, and initialise it."""
        self.__loop = loop
        self.__to_be_started = janus.Queue(loop=loop)

    def raise_if_not_ready(self):
        """Raise an exception if this manager has not been initialised fully yet."""
        if self.__loop is None or self.__to_be_started is None:
            raise RuntimeError("AsyncManager has no event loop set!")

    async def run(self):
        """
        Start running all entities managed by this manager.

        Blocks until `self.running` is set to False. This method is intended to be started in a
        thread.
        """
        self.raise_if_not_ready()

        self.running = True
        while self.running:
            new_entity = await self.__to_be_started.async_q.get()
            asyncio.create_task(new_entity.run())
            self.entities.append(new_entity)

    def add_new(self, entity: Entity):
        """
        Queue a new entity to be added to this manager.

        This is a synchronous interface into the managers async internals.
        """
        if self.__loop is None or self.__to_be_started is None:
            raise RuntimeError("AsyncManager has no event loop set!")

        self.__to_be_started.sync_q.put(entity)

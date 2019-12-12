import asyncio
import janus

from typing import List, Optional

from shimmer.engine.entity.entity import Entity


class AsyncManager:
    def __init__(self) -> None:
        self.entities: List[Entity] = []
        self.running = False
        self.__to_be_started: Optional[janus.Queue[Entity]] = None
        self.__loop: Optional[asyncio.AbstractEventLoop] = None

    def __str__(self):
        return str(self.entities)

    def set_event_loop(self, loop):
        self.__loop = loop
        self.__to_be_started = janus.Queue(loop=loop)

    def raise_if_not_ready(self):
        if self.__loop is None or self.__to_be_started is None:
            raise RuntimeError("AsyncManager has no event loop set!")

    async def run(self):
        if self.__loop is None or self.__to_be_started is None:
            raise RuntimeError("AsyncManager has no event loop set!")

        self.running = True
        while self.running:
            new_entity = await self.__to_be_started.async_q.get()
            asyncio.create_task(new_entity.run())
            self.entities.append(new_entity)

    async def display(self):
        while True:
            print(str(self))
            await asyncio.sleep(1)

    def add_new(self, entity: Entity):
        if self.__loop is None or self.__to_be_started is None:
            raise RuntimeError("AsyncManager has no event loop set!")

        self.__to_be_started.sync_q.put(entity)

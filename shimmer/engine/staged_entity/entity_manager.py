from collections import defaultdict
from typing import Dict, List, cast

from .entity import StagedEntity
from shimmer.engine.entity.entity_manager import AsyncManager


class StagedEntityManager(AsyncManager):
    entities: List[StagedEntity]

    def __init__(self):
        super(StagedEntityManager, self).__init__()

    #     self.entities = cast(List[StagedEntity], self.entities)

    def summary(self) -> Dict[int, int]:
        summary: Dict[int, int] = defaultdict(int)
        for entity in self.entities:
            if entity.complete:
                summary[-1] += 1
            else:
                summary[entity.current_stage] += 1
        return summary

    def __str__(self) -> str:
        return str(self.summary())

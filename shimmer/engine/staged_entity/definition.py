from dataclasses import dataclass

from ..entity.definition import EntityDefinition


@dataclass
class StagedEntityDefinition(EntityDefinition):
    num_stages: int
    total_time_s: int

    @property
    def stage_time_s(self):
        return self.total_time_s / self.num_stages

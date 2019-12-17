"""Definition of a StagedEntity."""

from dataclasses import dataclass

from ..entity.definition import EntityDefinition


@dataclass
class StagedEntityDefinition(EntityDefinition):
    """Definition of a StagedEntity."""

    num_stages: int
    total_time_s: int

    @property
    def stage_time_s(self):
        """Seconds taken for each stage to complete, assuming all stages are of equal length."""
        return self.total_time_s / self.num_stages

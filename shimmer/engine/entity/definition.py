"""Base definition an entity."""

from dataclasses import dataclass


@dataclass
class EntityDefinition:
    """Base set of parameters that define an entity."""

    name: str

from dataclasses import dataclass


@dataclass
class FloatRange:
    min: float
    max: float

    def contains(self, value: float) -> bool:
        return (value <= self.max) and (value >= self.min)

    def __contains__(self, item: float) -> bool:
        return self.contains(item)

    def len(self) -> float:
        return self.max - self.min


@dataclass
class WidgetDefinition:
    name: str

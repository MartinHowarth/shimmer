from dataclasses import dataclass
from typing import Any

from .base import WidgetDefinition, FloatRange


@dataclass
class GaugeDefinition(WidgetDefinition):
    full_range: FloatRange
    low_range: FloatRange
    high_range: FloatRange
    value: float = 0

    @property
    def low_fraction_start(self) -> float:
        return self.low_range.min / self.full_range.len()

    @property
    def high_fraction_start(self) -> float:
        return self.high_range.min / self.full_range.len()

    @property
    def value_fraction_start(self) -> float:
        return self.value / self.full_range.len()

    @property
    def low_fraction_len(self) -> float:
        return self.low_range.len() / self.full_range.len()

    @property
    def high_fraction_len(self) -> float:
        return self.high_range.len() / self.full_range.len()

    def __setattr__(self, key: str, value: Any) -> None:
        if key == "value":
            if value < self.full_range.min:
                value = self.full_range.min
            elif value > self.full_range.max:
                value = self.full_range.max
        super(GaugeDefinition, self).__setattr__(key, value)

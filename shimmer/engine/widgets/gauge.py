"""Definition of a Gauge."""

from dataclasses import dataclass
from typing import Any

from .base import FloatRange


@dataclass
class GaugeDefinition:
    """
    Definition of a value-constrained indicator.

    The value of the gauge is constrained to within `full_range`.

    `high_range` and `low_range` are subsections of the gauge used to indicate optimal values
     of the gauge.
    """

    full_range: FloatRange
    low_range: FloatRange
    high_range: FloatRange
    value: float = 0

    @property
    def low_fraction_start(self) -> float:
        """Fractional position of lowest point of the low range in the full range."""
        return self.low_range.min / self.full_range.len()

    @property
    def high_fraction_start(self) -> float:
        """Fractional position of lowest point of the high range in the full range."""
        return self.high_range.min / self.full_range.len()

    @property
    def value_fraction_start(self) -> float:
        """Fractional position of the value in the full range."""
        return self.value / self.full_range.len()

    @property
    def low_fraction_len(self) -> float:
        """Fraction of the full range that the "low_range" covers."""
        return self.low_range.len() / self.full_range.len()

    @property
    def high_fraction_len(self) -> float:
        """Fraction of the full range that the "high_range" covers."""
        return self.high_range.len() / self.full_range.len()

    def __setattr__(self, key: str, value: Any) -> None:
        """Constrain the value of the gauge to within its full_range."""
        if key == "value":
            if value < self.full_range.min:
                value = self.full_range.min
            elif value > self.full_range.max:
                value = self.full_range.max
        super(GaugeDefinition, self).__setattr__(key, value)

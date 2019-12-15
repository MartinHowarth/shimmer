"""Modules defining methods common to widgets."""

from dataclasses import dataclass


@dataclass
class FloatRange:
    """Definition of a range of floats."""

    min: float
    max: float

    def contains(self, value: float) -> bool:
        """Return True if the value is within the min/max (inclusive) of this range."""
        return (value <= self.max) and (value >= self.min)

    def __contains__(self, item: float) -> bool:
        """Return True if the value is within the min/max (inclusive) of this range."""
        return self.contains(item)

    def len(self) -> float:
        """Returnsthe difference between max and min."""
        return self.max - self.min

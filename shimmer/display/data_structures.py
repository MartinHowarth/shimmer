"""Data structures to aid definition of graphics objects."""

from dataclasses import dataclass
from typing import Tuple


@dataclass
class Color:
    """Definition of an RGB + alpha color."""

    r: int
    g: int
    b: int
    a: int = 255

    def as_tuple(self) -> Tuple[int, int, int]:
        """Return the RGB values as a tuple."""
        return self.r, self.g, self.b

    def as_tuple_alpha(self) -> Tuple[int, int, int, int]:
        """Return the RGB + alpha values as a tuple."""
        return self.r, self.g, self.b, self.a

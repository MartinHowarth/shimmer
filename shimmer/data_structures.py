"""Data structures to aid definition of graphics objects."""

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
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


White = Color(255, 255, 255)
ActiveGreen = Color(0, 200, 255)
PassiveBlue = Color(0, 120, 255)
ActiveBlue = Color(0, 200, 255)
MutedBlue = Color(0, 80, 255)

Black = Color(0, 0, 0)
LightGrey = Color(160, 160, 190)
Grey = Color(130, 130, 170)
DarkGrey = Color(100, 100, 150)

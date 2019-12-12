from dataclasses import dataclass
from typing import Tuple


@dataclass
class Color:
    r: int
    g: int
    b: int
    a: int = 255

    def as_tuple(self) -> Tuple[int, int, int]:
        return self.r, self.g, self.b

    def as_tuple_alpha(self) -> Tuple[int, int, int, int]:
        return self.r, self.g, self.b, self.a

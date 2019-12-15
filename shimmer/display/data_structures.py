"""Data structures to aid definition of graphics objects."""

from dataclasses import dataclass, asdict
from enum import Enum
from typing import Tuple, Dict, Any, List, Optional


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


White = Color(255, 255, 255)


@dataclass
class Font:
    """Definition of a text Font. See `pyglet.text.Label` for full parameter decriptions."""

    font_name: str
    font_size: int
    bold: bool = False
    italic: bool = False
    color: Color = White
    dpi: int = None  # Resolution of the font. Defaults to 96.

    def to_pyglet_label_kwargs(self) -> Dict[str, Any]:
        """Convert this definition into cocos/pyglet compatible kwargs."""
        _dict = asdict(self, dict_factory=shimmer_dict_factory)
        # We want `color` to be a tuple rather than a dict.
        _dict["color"] = self.color.as_tuple_alpha()
        return _dict


Calibri = Font("calibri", 16)
ComicSans = Font("comic sans", 16)


class HorizontalAlignment(Enum):
    """Enum of possible values for horizontal alignment in pyglet."""

    left = "left"
    right = "right"
    center = "center"


class VerticalAlignment(Enum):
    """Enum of possible values for vertical alignment in pyglet."""

    bottom = "bottom"
    baseline = "baseline"
    center = "center"
    top = "top"


@dataclass
class LabelDefinition:
    """
    Definition of a text label. All parameters match cocos/pyglet Label paremeters.

    Create a cocos Label from this definition using:
        `cocos.text.Label(**label_definition.to_pyglet_label_kwargs())`
    """

    text: str
    font: Font

    # Maximum width of the text box. Text is wrapped to fit within this width.
    # Set to None to force single line text of arbitrary width.
    width: Optional[int] = 300

    # Maximum height of the text box. If None, height is set as needed based on length of text.
    height: Optional[int] = None

    # Alignment of the text
    align: HorizontalAlignment = HorizontalAlignment.left
    multiline: bool = False

    # Transformation anchor points.
    anchor_x: HorizontalAlignment = HorizontalAlignment.left
    anchor_y: VerticalAlignment = VerticalAlignment.bottom

    def __post_init__(self):
        if self.width is None:
            self.multiline = False
        else:
            self.multiline = True

    def to_pyglet_label_kwargs(self) -> Dict[str, Any]:
        """Convert this definition into cocos/pyglet compatible kwargs."""
        _dict = asdict(self, dict_factory=shimmer_dict_factory)

        # Convert Font correctly, and then flatten the result into a non-nested dict.
        _dict.update(self.font.to_pyglet_label_kwargs())
        del _dict["font"]
        return _dict


def shimmer_dict_factory(items: List[Tuple[Any, Any]]) -> Dict[Any, Any]:
    """
    Custom dict factory for use with `as_dict` on shimmer dataclasses.

    Converts the following fields:
        - Enums to the corresponding value.
    """
    _dict = dict(items)
    for key, value in _dict.items():
        if isinstance(value, Enum):
            _dict[key] = value.value
    return _dict

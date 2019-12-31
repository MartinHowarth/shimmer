"""Data structures to aid definition of graphics objects."""

from dataclasses import dataclass, asdict
from enum import Enum
from pyglet.font import load as load_font
from typing import Tuple, Dict, Any, List, Optional


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

LightGrey = Color(160, 160, 190)
Grey = Color(130, 130, 170)
DarkGrey = Color(100, 100, 150)


@dataclass(frozen=True)
class FontDefinition:
    """Definition of a text Font. See `pyglet.text.Label` for full parameter decriptions."""

    font_name: str
    font_size: int
    bold: bool = False
    italic: bool = False
    color: Color = White
    dpi: Optional[int] = None  # Resolution of the font. Defaults to 96.

    def to_pyglet_label_kwargs(self) -> Dict[str, Any]:
        """Convert this definition into cocos/pyglet compatible kwargs."""
        _dict = asdict(self, dict_factory=shimmer_dict_factory)
        # We want `color` to be a tuple rather than a dict.
        _dict["color"] = self.color.as_tuple_alpha()
        return _dict

    @property
    def height(self) -> int:
        """
        Discover the height of this Font.

        This is a relatively expensive call, so cache it if you need to use it often.
        """
        font = load_font(
            self.font_name, self.font_size, self.bold, self.italic, self.dpi
        )
        return font.ascent - font.descent


Calibri = FontDefinition("calibri", 16)
ComicSans = FontDefinition("comic sans", 16)


class HorizontalAlignment(Enum):
    """Enum of possible values for horizontal alignment in pyglet."""

    left = "left"
    right = "right"
    center = "center"


class VerticalAlignment(Enum):
    """Enum of possible values for vertical alignment in pyglet."""

    bottom = "bottom"
    center = "center"
    top = "top"


class VerticalTextAlignment(Enum):
    """Enum of possible values for vertical alignment of text in pyglet."""

    bottom = "bottom"
    center = "center"
    top = "top"
    # Baseline is the bottom of the first line of text, as opposed to `bottom` which is
    # the bottom of the pyglet text layout.
    baseline = "baseline"


class ZIndexEnum(Enum):
    """Indicators of where in the stack of cocos children to add a child."""

    top = "top"
    bottom = "bottom"


@dataclass(frozen=True)
class LabelDefinition:
    """
    Definition of a text label. All parameters match pyglet Label parameters.

    Create a cocos Label from this definition using:
        `cocos.text.Label(**label_definition.to_pyglet_label_kwargs())`

    Note that thse values are for the pyglet text layout, rather than the cocos Label.
    The pyglet text layout is a property of the Label called `element.
    """

    text: str
    font: FontDefinition = Calibri

    # Maximum width of the text box. Text is wrapped to fit within this width.
    # Set to None to force single line text of arbitrary width.
    width: Optional[int] = 300

    # Maximum height of the text box. If None, height is set as needed based on length of text and
    # whether it is multiline or not.
    height: Optional[int] = None

    # Alignment of the text
    align: HorizontalAlignment = HorizontalAlignment.left

    # Used to override default multiline behaviour which is based on whether `width` is set or not.
    # Use `is_multiline()` to determine whether to use multiline or not.
    multiline: Optional[bool] = None

    # Transformation anchor points.
    anchor_x: HorizontalAlignment = HorizontalAlignment.left
    anchor_y: VerticalTextAlignment = VerticalTextAlignment.bottom

    def is_multiline(self) -> bool:
        """Determine whether this label should be multiline or not if user hasn't specified."""
        if self.multiline is None:
            return self.width is not None
        return self.multiline

    def to_pyglet_label_kwargs(self) -> Dict[str, Any]:
        """Convert this definition into cocos/pyglet compatible kwargs."""
        _dict = asdict(self, dict_factory=shimmer_dict_factory)
        _dict["multiline"] = self.is_multiline()

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

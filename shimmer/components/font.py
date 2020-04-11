"""Module defining text fonts."""
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any

from pyglet.font import load as load_font

from shimmer.data_structures import Color, White


@dataclass(frozen=True)
class FontDefinition:
    """Definition of a text Font. See `pyglet.text.Label` for full parameter descriptions."""

    font_name: str
    font_size: int
    bold: bool = False
    italic: bool = False
    color: Color = White
    dpi: Optional[int] = None  # Resolution of the font. Defaults to 96.

    def to_pyglet_label_kwargs(self) -> Dict[str, Any]:
        """Convert this definition into cocos/pyglet compatible kwargs."""
        _dict = asdict(self)
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

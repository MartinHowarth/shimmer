"""A settings menu button for choosing the window resolution."""
from dataclasses import replace, dataclass
from itertools import cycle
from typing import Optional, List

import pyglet

import cocos
from shimmer.components.mouse_box import EVENT_HANDLED
from ..widgets.button import Button, ButtonDefinition


@dataclass(frozen=True)
class ScreenResolution:
    """A screen resolution."""

    width: int
    height: int


def get_possible_screen_modes() -> List[pyglet.canvas.base.ScreenMode]:
    """Discover the possible modes for the screen (i.e. monitor) that this game is using."""
    return cocos.director.director.window.screen.get_modes()


def get_possible_screen_resolutions() -> List[ScreenResolution]:
    """
    Discover the possible resolutions for the screen (i.e. monitor) that this game is using.

    Resulting list is ordered from lowest to highest width.
    """
    resolutions = []
    for mode in get_possible_screen_modes():
        resolutions.append(ScreenResolution(width=mode.width, height=mode.height))

    # Now filter out repeats coming from modes with the same resolution but different
    # refresh rates.
    resolutions = list(set(resolutions))
    resolutions.sort(key=lambda _resolution: _resolution.width)
    return resolutions


def get_current_resolution() -> ScreenResolution:
    """Get the current resolution of the game window."""
    resolution_tuple = cocos.director.director.window.get_size()
    return ScreenResolution(width=resolution_tuple[0], height=resolution_tuple[1])


class ResolutionCycleButton(Button):
    """A button that changes the game window size through the supported screen resolutions."""

    text_template = "Resolution: {width}x{height}"

    def __init__(self, definition: Optional[ButtonDefinition] = None):
        """
        Create a button that changes the screen resolution in a cycle.

        :param definition: Definition of the button style to use.
        """
        current_resolution = get_current_resolution()
        possible_resolutions = get_possible_screen_resolutions()
        current_resolution_index = possible_resolutions.index(current_resolution)
        resolutions_ordered = (
            possible_resolutions[current_resolution_index + 1 :]
            + possible_resolutions[: current_resolution_index + 1]
        )
        self.resolution_generator = cycle(resolutions_ordered)

        label = self.get_display_text_for_screen_resolution(current_resolution)

        if definition is None:
            definition = ButtonDefinition()

        definition = replace(definition, on_press=self.set_next_resolution, text=label,)
        super(ResolutionCycleButton, self).__init__(definition)

    def get_display_text_for_screen_resolution(
        self, resolution: ScreenResolution
    ) -> str:
        """Generate the display text for this button based on the given ScreenResolution."""
        return self.text_template.format(
            width=resolution.width, height=resolution.height
        )

    def set_next_resolution(self, *_, **__):
        """Set the game window to be the next possible screen resolution in the cycle."""
        next_resolution = next(self.resolution_generator)
        self.set_text(self.get_display_text_for_screen_resolution(next_resolution))
        cocos.director.director.window.set_size(
            next_resolution.width, next_resolution.height
        )
        return EVENT_HANDLED

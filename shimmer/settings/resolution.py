"""A settings menu button for choosing the window resolution."""
from dataclasses import dataclass
from functools import partial
from typing import List

import pyglet

import cocos
from ..components.box import DynamicSizeBehaviourEnum
from ..components.mouse_box import EVENT_HANDLED
from ..widgets.button import Button, ButtonDefinition
from ..widgets.pop_out_menu import (
    DropDownMenuDefinition,
    PopOutMenu,
)


@dataclass(frozen=True)
class ScreenResolution:
    """A screen resolution."""

    width: int
    height: int

    def __str__(self) -> str:
        """String representation of a screen resolution."""
        return f"Resolution: {self.width}x{self.height}"


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


def set_resolution(resolution: ScreenResolution) -> None:
    """Set the resolution of the game window."""
    cocos.director.director.window.set_size(resolution.width, resolution.height)


class ResolutionDropDownMenu(PopOutMenu):
    """A drop down menu for setting the screen resolution."""

    def __init__(self):
        """Create a new ResolutionDropDownMenu."""
        current_resolution = get_current_resolution()
        definition = DropDownMenuDefinition(
            name=str(current_resolution),
            items=self.create_menu_items(),
            scrollable=True,
        )
        super(ResolutionDropDownMenu, self).__init__(definition)

    def create_menu_items(self) -> List[Button]:
        """Create a button for each resolution setting."""
        menu_items = []

        for resolution in get_possible_screen_resolutions():
            button = Button(
                ButtonDefinition(
                    text=str(resolution),
                    on_press=partial(self.set_resolution, resolution=resolution),
                    height=30,
                    width=None,
                    dynamic_size_behaviour=DynamicSizeBehaviourEnum.match_parent,
                    log_id=str(resolution),
                )
            )
            menu_items.append(button)
        return menu_items

    def set_resolution(self, *_, resolution, **__):
        """Set the game window to be the next possible screen resolution in the cycle."""
        self.info(f"Setting resolution to {resolution}.")
        self.menu_button.set_text(str(resolution))
        set_resolution(resolution)
        return EVENT_HANDLED

"""A settings menu toggle button for enabling/disabling fullscreen."""
from dataclasses import replace
from typing import Optional

import cocos
from shimmer.components.mouse_box import EVENT_HANDLED
from ..widgets.button import ToggleButton, ButtonDefinition


class FullscreenToggleButton(ToggleButton):
    def __init__(self, definition: Optional[ButtonDefinition] = None):
        """
        Create a button that toggles fullscreen on/off.

        :param definition: Definition of the button style to use.
        """
        self._enabled_text = "Fullscreen: On"
        self._disabled_text = "Fullscreen: Off"
        label = self._enabled_text if self.currently_fullscreen else self._disabled_text

        if definition is None:
            definition = ButtonDefinition()

        definition = replace(
            definition,
            on_press=self.enter_fullscreen,
            on_release=self.exit_fullscreen,
            text=label,
        )
        super(FullscreenToggleButton, self).__init__(definition)
        if self.currently_fullscreen:
            self._is_toggled = True

    @property
    def currently_fullscreen(self) -> bool:
        """Return True if the window is currently fullscreen, otherwise False."""
        return cocos.director.director.window.fullscreen

    def enter_fullscreen(self, *_, **__):
        """Enable fullscreen on the current pyglet window."""
        self.set_text(self._enabled_text)
        cocos.director.director.window.set_fullscreen(True)
        return EVENT_HANDLED

    def exit_fullscreen(self, *_, **__):
        """Disable fullscreen on the current pyglet window."""
        self.set_text(self._disabled_text)
        cocos.director.director.window.set_fullscreen(False)
        return EVENT_HANDLED

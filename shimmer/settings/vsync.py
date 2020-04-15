"""A settings menu toggle button for enabling/disabling vsync."""
from dataclasses import replace
from typing import Optional

import cocos
from shimmer.components.mouse_box import EVENT_HANDLED
from ..widgets.button import ToggleButton, ButtonDefinition


class VsyncToggleButton(ToggleButton):
    def __init__(self, definition: Optional[ButtonDefinition] = None):
        """
        Create a button that toggles vsync on/off.

        :param definition: Definition of the button style to use.
        """
        self._enabled_text = "VSync: On"
        self._disabled_text = "VSync: Off"
        label = self._enabled_text if self.vsync_is_enabled else self._disabled_text

        if definition is None:
            definition = ButtonDefinition()

        definition = replace(
            definition,
            on_press=self.enable_vsync,
            on_release=self.disable_vsync,
            text=label,
        )
        super(VsyncToggleButton, self).__init__(definition)
        if self.vsync_is_enabled:
            self._is_toggled = True

    @property
    def vsync_is_enabled(self) -> bool:
        """Return True if Vsync is currently enabled, otherwise False."""
        return cocos.director.director.window.context.get_vsync()

    def enable_vsync(self, *_, **__):
        """Enable vsync on the current pyglet window."""
        self.set_text(self._enabled_text)
        cocos.director.director.window.set_vsync(True)
        return EVENT_HANDLED

    def disable_vsync(self, *_, **__):
        """Disable vsync on the current pyglet window."""
        self.set_text(self._disabled_text)
        cocos.director.director.window.set_vsync(False)
        return EVENT_HANDLED

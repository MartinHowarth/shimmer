"""Module defining a close button that removes its parent Node from the scene when clicked."""

from dataclasses import replace

from shimmer.display.data_structures import Color
from shimmer.display.helpers import bundle_callables
from shimmer.display.widgets.button import ButtonDefinition, Button


CloseButtonDefinitionBase = ButtonDefinition(
    text="X", base_color=Color(200, 0, 127), hover_color=Color(255, 0, 127)
)


class CloseButton(Button):
    """Standard close button that removes its parent CocosNode when clicked."""

    def __init__(self, definition: ButtonDefinition):
        """Create a CloseButton."""
        if definition.on_release is not None:
            on_release = bundle_callables(definition.on_release, self._kill_parent)
        else:
            on_release = self._kill_parent
        defn = replace(definition, on_release=on_release)
        super(CloseButton, self).__init__(defn)

    def _kill_parent(self, *_, **__):
        """Kill the parent of this button, which will kill all its children too."""
        self.parent.kill()

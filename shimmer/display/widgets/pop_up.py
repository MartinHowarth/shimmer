"""Boxes that pop up on certain events."""
import cocos
import logging

from abc import abstractmethod

from ..components.box import Box
from ..components.mouse_box import MouseBox, MouseBoxDefinition


log = logging.getLogger(__name__)


class PopUpAnchor(MouseBox):
    def __init__(self, pop_up: Box, rect: cocos.rect.Rect):
        self.pop_up: Box = pop_up
        super(PopUpAnchor, self).__init__(self.definition(), rect)

    def create_pop_up(self, *_, **__):
        log.debug(f"Created pop up {self.pop_up}.")
        self.add(self.pop_up)

    def delete_pop_up(self, *_, **__):
        log.debug(f"Deleted pop up {self.pop_up}.")
        self.remove(self.pop_up)

    @abstractmethod
    def definition(self) -> MouseBoxDefinition:
        pass


class PopUpOnHover(PopUpAnchor):
    def definition(self) -> MouseBoxDefinition:
        return MouseBoxDefinition(
            on_hover=self.create_pop_up, on_unhover=self.delete_pop_up
        )


class PopUpWhileClicked(PopUpAnchor):
    def definition(self) -> MouseBoxDefinition:
        return MouseBoxDefinition(
            on_press=self.create_pop_up, on_release=self.delete_pop_up
        )


class PopUpToggleOnClick(PopUpAnchor):
    def __init__(self, pop_up: Box, rect: cocos.rect.Rect):
        super(PopUpToggleOnClick, self).__init__(pop_up, rect)
        self._toggled = False

    def toggle_pop_up(self, *_, **__):
        if self._toggled:
            self.delete_pop_up()
        else:
            self.create_pop_up()
        self._toggled = not self._toggled

    def definition(self) -> MouseBoxDefinition:
        return MouseBoxDefinition(on_press=self.toggle_pop_up)

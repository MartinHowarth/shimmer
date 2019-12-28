"""
Module defining components that make up a selection system.

This is a system that allows users to define a box using the mouse and get
a list of selectable Boxes inside that.

For example, this is used to make a unit system where the user can select
multiple units at once to give them orders.
"""

import cocos
import logging
import pyglet

from dataclasses import dataclass, replace
from typing import Optional, Set, cast, Callable

from shimmer.display.helpers import bitwise_contains
from .box import Box, BoxDefinition
from .drawing import RectDrawingBoxDefinition, RectDrawingBox, MouseDefinedRect
from ..inspections import get_all_nodes_of_type, get_boxes_that_intersect_with_rect


log = logging.getLogger(__name__)


@dataclass(frozen=True)
class SelectableBoxDefinition(BoxDefinition):
    """
    Definition of a box that is selectable.

    You can specify callbacks for each event type that occurs when a selection is being made.

    Callbacks will receive a MouseDefinedRect detailing the selection that was made, which
    (for example) allows you to determine what action to take based on whicih mouse button
    or keyboard modifiers was used to make the selection.

    If the highlight or selection is set directly without a mouse drawn selection, then
    the callback will receive None instead.
    """

    on_highlight: Optional[Callable[[Optional[MouseDefinedRect]], None]] = None
    on_unhighlight: Optional[Callable[[Optional[MouseDefinedRect]], None]] = None
    on_select: Optional[Callable[[Optional[MouseDefinedRect]], None]] = None
    on_deselect: Optional[Callable[[Optional[MouseDefinedRect]], None]] = None

    # If None, then default behaviour is to call `on_deselect` if no modifier
    # specified in `additive_modifiers` is used.
    # Should return True if the Box remains selected, otherwise False.
    on_new_selection_start: Optional[Callable[[MouseDefinedRect], bool]] = None

    # Bitwise sum of the pyglet representations of modifier keys (e.g. SHIFT) that cause
    # additional selection drawings to add to the currently selected set.
    # If the modifier isn't used, then when a new selection is started, the previous
    # selection will be deselected.
    # If multiple modifiers are allowed, then any one of them can be used to trigger
    # additive behaviour (i.e. not all are required).
    # Set to 0 to exclude all modifiers.
    additive_modifiers: int = pyglet.window.key.MOD_SHIFT


class SelectableBox(Box):
    """
    A Box that can be selected.

    Typical usage is to add this Box to another Box that you want to be selectable
    using the mouse. Define callbacks in the definition to control what happens when this
    Box is selected or highlighted.

    See SelectionDrawingBox to define the area in which boxes can be selected using the mouse.
    """

    def __init__(self, definition: SelectableBoxDefinition):
        """
        Create a new SelectableBox.

        :param definition: Definition of the actions to take when this Box is interacted with.
        """
        super(SelectableBox, self).__init__(definition)
        self.definition: SelectableBoxDefinition = definition
        self._selected: bool = False
        self._highlighted: bool = False

    @property
    def selected(self) -> bool:
        """True if this box is currently Selected."""
        return self._selected

    @selected.setter
    def selected(self, value: bool) -> None:
        """
        Set whether this box is selected or not.

        Calls `on_select` or `on_deselect` callbacks if value is changed.
        """
        if value and not self._selected:
            self.on_select()
        elif not value and self._selected:
            self.on_deselect()

    @property
    def highlighted(self) -> bool:
        """True if this box is currently highlighted."""
        return self._highlighted

    @highlighted.setter
    def highlighted(self, value: bool) -> None:
        """
        Set whether this box is highlighted or not.

        Calls `on_highlight` or `on_unhighlight` callbacks if value is changed.
        """
        if value and not self._highlighted:
            self.on_highlight()
        elif not value and self._highlighted:
            self.on_unhighlight()

    def on_highlight(self, selection_rect: Optional[MouseDefinedRect] = None) -> None:
        """
        Called when a selection is not complete, but includes this Box.

        For example, this may be used when a user is definition a selection by
        dragging the mouse, and that selection is drawn overlapping this box's rect.
        """
        log.debug(f"{self} has been selection highlighted.")
        self._highlighted = True
        if self.definition.on_highlight is not None:
            self.definition.on_highlight(selection_rect)

    def on_unhighlight(self, selection_rect: Optional[MouseDefinedRect] = None) -> None:
        """Called when a selection is not complete, and no longer includes this Box."""
        log.debug(f"{self} has been selection unhighlighted.")
        self._highlighted = False
        if self.definition.on_unhighlight is not None:
            self.definition.on_unhighlight(selection_rect)

    def on_select(self, selection_rect: Optional[MouseDefinedRect] = None) -> None:
        """
        Called when a selection including this Box is completed.

        It is not guaranteed that `on_unhighlight` will be called before `on_select` is called.
        """
        log.debug(f"{self} has been selected.")
        self._selected = True
        if self.definition.on_select is not None:
            self.definition.on_select(selection_rect)

    def on_deselect(self, selection_rect: Optional[MouseDefinedRect] = None) -> None:
        """
        Called when the selection of this Box is removed.

        :param selection_rect: Rect of the selection event that occurred to trigger deselection.
            Typically will not intersect with this Box.
        """
        log.debug(f"{self} has been deselected.")
        self._selected = False
        if self.definition.on_deselect is not None:
            self.definition.on_deselect(selection_rect)

    def on_new_selection_start(self, selection_rect: MouseDefinedRect) -> bool:
        """
        Called when a new selection box starts being drawn if this Box is already selected.

        Default behaviour is to call on_deselect if the modifier key is not being used.

        :param selection_rect: The selection rect that is just being started. Typically will
            not intersect with this Box.
        :return: True if this box remains selected, otherwise False.
        """
        if self.definition.on_new_selection_start is None:
            if not bitwise_contains(
                selection_rect.modifiers, self.definition.additive_modifiers
            ):
                self.on_deselect(selection_rect)
                return False
            return True
        return self.definition.on_new_selection_start(selection_rect)


class SelectionDrawingBox(RectDrawingBox):
    """
    A box that within its boundaries, any SelectableBox can be selected.

    This allows the user to drag to highlight or select many boxes at once.
    For example, this allows creation of a unit selection system.
    """

    def __init__(
        self,
        definition: Optional[RectDrawingBoxDefinition] = None,
        rect: Optional[cocos.rect.Rect] = None,
    ):
        """
        Create a new SelectionDrawingBox.

        :param definition: Definition of this drawing box. The callbacks will be overridden.
        :param rect: Definition of the rectangle that a drag selection can be made within.
            If None, defaults to the entire window.
        """
        if definition is None:
            definition = RectDrawingBoxDefinition()

        definition = replace(
            definition,
            on_start=self.cache_selectable_boxes,
            on_change=self.handle_incomplete_selection_change,
            on_complete=self.handle_complete_selection,
        )
        super(SelectionDrawingBox, self).__init__(definition, rect)
        self._cache: Set[SelectableBox] = set()
        self._pending_selection: Set[SelectableBox] = set()
        self._current_selection: Set[SelectableBox] = set()

    def cache_selectable_boxes(self, defined_rect: MouseDefinedRect) -> None:
        """
        Cache the possible selectable boxes to speed up selection detection.

        This stores a reference to all SelectableBoxes in the current scene, so we don't
        have to re-find them on every selection box change.

        This does mean that new SelectableBoxes created while a selection is being made will
        be missed, but that is unlikely - so prefer the faster speed of using a cache.
        """
        self._cache = set(get_all_nodes_of_type(SelectableBox))
        self._pending_selection = set()

        # Tell each box in the last completed selection that we are starting a new selection.
        # Those boxes might want to deselect themselves.
        # Remove those which do deselect themselves from the current selection, and keep the rest.
        to_remove = list()
        for box in self._current_selection:
            still_selected = box.on_new_selection_start(defined_rect)
            if not still_selected:
                to_remove.append(box)

        for box in to_remove:
            self._current_selection.remove(box)

    def handle_incomplete_selection_change(
        self, defined_rect: MouseDefinedRect
    ) -> None:
        """
        Called when the pending selection changes (i.e. mouse dragged).

        Call on_highlight on each SelectableBox that is now in the selection area,
        and on_unhighlight on each SelectableBox that is no longer in the selection area.
        """
        intersected_boxes = set(
            get_boxes_that_intersect_with_rect(
                self._cache, defined_rect.as_world_rect()
            )
        )
        intersected_boxes = cast(Set[SelectableBox], intersected_boxes)

        # For every box in the intersection, but not in the current selection, highlight it.
        for box in intersected_boxes.difference(self._pending_selection):
            self._pending_selection.add(box)
            if not box.selected:
                box.on_highlight(defined_rect)

        # For every box in the current selection, but not in the intersection, unhighlight it.
        for box in self._pending_selection.difference(intersected_boxes):
            self._pending_selection.remove(box)
            if not box.selected:
                box.on_unhighlight(defined_rect)

    def handle_complete_selection(self, defined_rect: MouseDefinedRect) -> None:
        """
        Called when the selection is completed (i.e. mouse released).

        Call on_select on each SelectableBox that is now in the selection area,
        and on_unhighlight on each SelectableBox that is no longer in the selection area.
        """
        intersected_boxes = set(
            get_boxes_that_intersect_with_rect(
                self._cache, defined_rect.as_world_rect()
            )
        )
        intersected_boxes = cast(Set[SelectableBox], intersected_boxes)

        self._current_selection.update(intersected_boxes)

        # For every box in the pending selection, but not in the final selection, unhighlight it.
        for box in intersected_boxes.difference(self._pending_selection):
            if box.highlighted and not box.selected:
                box.on_unhighlight(defined_rect)
        self._pending_selection = set()

        # Tell each Box that is has been selected.
        for box in self._current_selection:
            if not box.selected:
                box.on_select(defined_rect)

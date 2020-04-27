"""
Module defining a scrollable Box.

This is a box showing a viewport onto its children, meaning that only part of the
children are visible at once. It also includes scrollbars to move the visible section
around.

For example, this can be used to create scrolling text boxes where not all of the
text is visible at once.
"""

from dataclasses import dataclass, replace
from typing import Optional, Tuple

import cocos
from .slider import Slider, SliderDefinition, OrientationEnum
from ..alignment import RightTop, LeftBottom
from ..components.box import BoxDefinition, Box, DynamicSizeBehaviourEnum
from ..components.view_port_box import ViewPortBox


@dataclass(frozen=True)
class ScrollableBoxDefinition(BoxDefinition):
    """
    Definition of a ScrollableBox.

    :param vertically_scrollable: If True, a vertical scrollbar will be shown to control the
        vertical position of the visible area.
    :param horizontally_scrollable: If True, a horizontal scrollbar will be shown to control the
        horizontal position of the visible area.
    :param slider_definition: Definition of the scrollbars to include.
        The width parameter controls the size of the vertical scrollbar.
        The height parameter controls the size of the horizontal scrollbar.
    """

    vertically_scrollable: bool = True
    horizontally_scrollable: bool = False
    slider_definition: SliderDefinition = SliderDefinition(width=20, height=20)

    def __post_init__(self):
        if self.vertically_scrollable and self.height is None:
            raise ValueError(
                f"Cannot have a ScrollableBox with dynamic height and vertical scrolling."
            )
        if self.horizontally_scrollable and self.width is None:
            raise ValueError(
                f"Cannot have a ScrollableBox with dynamic width and horizontal scrolling."
            )


class ScrollableBox(Box):
    """A ViewPortBox with scroll bars to show and control the position of the view port."""

    definition_type = ScrollableBoxDefinition
    # TODO add mouse wheel support

    def __init__(self, definition: Optional[ScrollableBoxDefinition] = None):
        """Create a new ScrollableBox."""
        super(ScrollableBox, self).__init__(definition)
        self.definition: ScrollableBoxDefinition = self.definition

        self.vertical_scrollbar: Optional[Slider] = None
        self.horizontal_scrollbar: Optional[Slider] = None

        width, height = self._calculate_view_port_dimensions()
        self.view_port_box = ViewPortBox(
            BoxDefinition(
                width=width,
                height=height,
                dynamic_size_behaviour=DynamicSizeBehaviourEnum.match_parent,
            )
        )
        self.add_to_self(self.view_port_box)

        if self.definition.vertically_scrollable:
            self.vertical_scrollbar = self._create_vertical_slider()
            self.add_to_self(self.vertical_scrollbar)
            # Start with the slider at the top as this is usually the default for vertical sliders.
            self.vertical_scrollbar.value = self.definition.slider_definition.maximum

        if self.definition.horizontally_scrollable:
            self.horizontal_scrollbar = self._create_horizontal_slider()
            self.add_to_self(self.horizontal_scrollbar)

        self.arrange_children()

    def add(
        self,
        child: cocos.cocosnode.CocosNode,
        z: int = 0,
        name: Optional[str] = None,
        no_resize: bool = False,
    ) -> None:
        """
        Add children to the visible portion of this ScrollableBox.

        This actually adds the children to the ViewPortBox that provides the partial visibility
        behaviour.

        See Box.add for parameter details.
        """
        self.view_port_box.add(child, z, name, no_resize)
        self.arrange_children()

    def remove(
        self, child: cocos.cocosnode.CocosNode, no_resize: bool = False,
    ) -> None:
        """
        Remove children from the visible portion of this ScrollableBox.

        This actually removes the children from the ViewPortBox that provides the partial visibility
        behaviour.

        See Box.remove for parameter details.
        """
        self.view_port_box.remove(child, no_resize)

    def add_to_self(
        self,
        child: cocos.cocosnode.CocosNode,
        z: int = 0,
        name: Optional[str] = None,
        no_resize: bool = False,
    ) -> None:
        """Renaming of the usual `self.add` method."""
        super(ScrollableBox, self).add(child, z, name, no_resize)

    def remove_from_self(
        self, child: cocos.cocosnode.CocosNode, no_resize: bool = False
    ) -> None:
        """Renaming of the usual `self.remove` method."""
        super(ScrollableBox, self).remove(child, no_resize)

    def on_size_change(self):
        """When the size of this box changes, update its components to account for the change."""
        width, height = self._calculate_view_port_dimensions()
        self.view_port_box.set_size(width, height)
        super(ScrollableBox, self).on_size_change()

    def arrange_children(self):
        if self.horizontal_scrollbar is not None:
            self.horizontal_scrollbar.position = (0, 0)
            # Pretend to scroll to force the actual viewport positioning to be handled for us.
            self.on_horizontal_scroll(self.horizontal_scrollbar.value)
        if self.vertical_scrollbar is not None:
            if self.horizontal_scrollbar is not None:
                self.vertical_scrollbar.align_anchor_with_other_anchor(
                    self.horizontal_scrollbar, RightTop, LeftBottom
                )
            else:
                self.vertical_scrollbar.x = (
                    self.rect.width - self.definition.slider_definition.width
                )
            # Pretend to scroll to force the actual viewport positioning to be handled for us.
            self.on_vertical_scroll(self.vertical_scrollbar.value)
        super(ScrollableBox, self).arrange_children()

    def _calculate_view_port_dimensions(self) -> Tuple[int, int]:
        """
        Create the view port that is used to display the contents of this scrollable box.

        Note: This will be used as the dimensions of the actual viewport, not the parent
              ViewPortBox.
        """
        if (
            self.definition.horizontally_scrollable
            and self.definition.vertically_scrollable
        ):
            # Use max to ensure we don't end up with a negative size.
            height = max(self.rect.height - self.definition.slider_definition.height, 0)
            width = max(self.rect.width - self.definition.slider_definition.width, 0)
        elif (
            self.definition.horizontally_scrollable
            and not self.definition.vertically_scrollable
        ):
            height = None
            width = self.rect.width
        elif (
            not self.definition.horizontally_scrollable
            and self.definition.vertically_scrollable
        ):
            height = self.rect.height
            width = None
        else:
            width, height = None, None

        return width, height

    def _create_horizontal_slider(self) -> Optional[Slider]:
        # Leave space for the other scrollbar so they don't overlap in the corner.
        if self.definition.vertically_scrollable:
            width = self.rect.width - self.definition.slider_definition.width
        else:
            width = self.rect.width

        slider = Slider(
            replace(
                self.definition.slider_definition,
                width=width,
                height=self.definition.slider_definition.height,
                on_change=self.on_horizontal_scroll,
                orientation=OrientationEnum.horizontal,
            )
        )
        slider.value = self.definition.slider_definition.minimum
        return slider

    def _create_vertical_slider(self) -> Slider:
        # Leave space for the other scrollbar so they don't overlap in the corner.
        if self.definition.horizontally_scrollable:
            height = self.rect.height - self.definition.slider_definition.height
        else:
            height = self.rect.height

        slider = Slider(
            replace(
                self.definition.slider_definition,
                width=self.definition.slider_definition.width,
                height=height,
                on_change=self.on_vertical_scroll,
                orientation=OrientationEnum.vertical,
            )
        )
        slider.value = self.definition.slider_definition.minimum
        return slider

    def on_horizontal_scroll(self, slider_value: float) -> None:
        """
        Called when horizontal scrolling occurs to make a different section of the children visible.

        Moves the ViewPortBox child to the position represented by the fractional value of the
        given value. The `view_port_box` is moved by an opposite amount to the actual viewport of
        that box. This causes the visible portion of `self.view_port_box` to remain in the same
        place, but the children that are shown within the view port are moved relative to it.
        This gives the appearance of scrolling behaviour.

        :param slider_value: Float between 0 and 1 indicating the fractional position of the
            viewport relative to the children of this box.
        """
        relative_pos = int(
            slider_value
            * (self.view_port_box.rect.width - self.view_port_box.viewport.rect.width)
        )
        self.view_port_box.x = -relative_pos
        self.view_port_box.viewport.x = relative_pos

    def on_vertical_scroll(self, slider_value: float) -> None:
        """
        Called when vertical scrolling occurs to make a different section of the children visible.

        Moves the ViewPortBox child to the position represented by the fractional value of the
        given value. The `view_port_box` is moved by an opposite amount to the actual viewport of
        that box. This causes the visible portion of `self.view_port_box` to remain in the same
        place, but the children that are shown within the view port are moved relative to it.
        This gives the appearance of scrolling behaviour.

        :param slider_value: Float between 0 and 1 indicating the fractional position of the
            viewport relative to the children of this box.
        """
        relative_pos = int(
            slider_value
            * (self.view_port_box.rect.height - self.view_port_box.viewport.rect.height)
        )
        # Leave space for the horizontal scrollbar that sits below the viewport, if it exists
        base_pos = (
            self.definition.slider_definition.height
            if self.definition.horizontally_scrollable
            else 0
        )
        self.view_port_box.y = base_pos - relative_pos
        self.view_port_box.viewport.y = relative_pos

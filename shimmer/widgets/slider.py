"""
Module defining a slider.

A slider is an interactable box that can be used to set and display a value.
"""


from dataclasses import dataclass, replace
from enum import Enum, auto
from typing import Sequence, Optional, Callable, Tuple

from .button import ButtonDefinition, Button, EVENT_HANDLED
from ..alignment import RightTop, LeftBottom
from ..components.box import BoxDefinition, Box, DynamicSizeBehaviourEnum
from ..components.draggable_box import DraggableBox, DraggableBoxDefinition
from ..data_structures import LightGrey, Grey, DarkGrey, Color, White


class OrientationEnum(Enum):
    """Enum of the possible orientations of a Slider."""

    horizontal = auto()
    vertical = auto()


@dataclass(frozen=True)
class SliderButtonTextDefinition:
    """Definition of the text to display on the buttons that control the slider."""

    vertical_increment: Optional[str] = "^"
    vertical_decrement: Optional[str] = "v"
    horizontal_increment: Optional[str] = ">"
    horizontal_decrement: Optional[str] = "<"


DefaultSliderButtonStyle = ButtonDefinition(
    base_color=LightGrey, hover_color=Grey, depressed_color=DarkGrey,
)


@dataclass(frozen=True)
class SliderDefinition(BoxDefinition):
    """
    Definition of a slider which allows the user to pick a value in a range.

    :param minimum: The minimum value of the slider.
    :param maximum: The maximum value of the slider.
    :param increment: The amount the slider value changes when a slider button is pressed.
        Users may drag the slider to a value that is not a multiple of this increment.
    :param graduations: Sequence of allowed values for the scroll bar to take.
        If the user drags to a different value, the slider will snap to the closest graduation.
    :param on_change: Callback called when the value of the scrollbar changes.
    :param orientation: The orientation of the slider. Horizontal or vertical.
    :param button_style: If not None then buttons to increment/decrement the slider will be shown
        using the given ButtonDefinition to define the style.
    :param button_text_definition: The text to display on the increment/decrement buttons.
        Defaults to basic arrows: <>^v
    """

    minimum: float = 0.0
    maximum: float = 1.0
    increment: float = 0.1
    on_change: Optional[Callable[[float], None]] = None
    graduations: Optional[Sequence[float]] = None
    orientation: OrientationEnum = OrientationEnum.vertical
    button_style: Optional[ButtonDefinition] = DefaultSliderButtonStyle
    background_color: Color = White
    button_text_definition: SliderButtonTextDefinition = SliderButtonTextDefinition()

    @property
    def range(self) -> float:
        """The difference between the maximal and minimal value of the slider."""
        return self.maximum - self.minimum

    def __post_init__(self):
        """Validate the definition on creation."""
        if self.minimum >= self.maximum:
            raise ValueError(f"{self.minimum=} cannot be greater than {self.maximum=}.")
        if self.graduations is not None and min(self.graduations) < self.minimum:
            raise ValueError(
                f"{self.graduations=} cannot include values lower than {self.minimum=}"
            )
        if self.graduations is not None and max(self.graduations) > self.maximum:
            raise ValueError(
                f"{self.graduations=} cannot include values greater than {self.maximum=}"
            )

    @property
    def is_vertical(self) -> bool:
        """True if the slider is vertically orientated."""
        return self.orientation == OrientationEnum.vertical

    @property
    def is_horizontal(self) -> bool:
        """True if the slider is horizontally orientated."""
        return self.orientation == OrientationEnum.horizontal

    @property
    def increment_button_text(self) -> str:
        return (
            self.button_text_definition.horizontal_increment
            if self.is_horizontal
            else self.button_text_definition.vertical_increment
        )

    @property
    def decrement_button_text(self) -> str:
        return (
            self.button_text_definition.horizontal_decrement
            if self.is_horizontal
            else self.button_text_definition.vertical_decrement
        )


class Slider(Box):
    """
    An interactable slider that can be used to set and display a value.

    Includes:
      - A button to increment the slider.
      - A button to decrement the slider.
      - A draggable box to display and edit the value of the slider.

    May be horizontal or vertically orientated based on the SliderDefinition given.
    """

    definition_type = SliderDefinition

    def __init__(self, definition: SliderDefinition):
        """Create a new Slider."""
        super().__init__(definition)
        self.definition: SliderDefinition = self.definition

        self._value: float = 0
        self._drag_box_minmax_position: Tuple[int, int] = (0, 0)

        widget_width, widget_height = self._widget_size()
        self.debug(f"{widget_height=}, {widget_width=}")
        self.increment_button = Button(
            replace(
                self.definition.button_style,
                text=self.definition.increment_button_text,
                on_press=self._increment_mouse_callback,
                width=widget_width,
                height=widget_height,
            )
        )
        self.add(self.increment_button)
        self.increment_button.align_anchor_with_other_anchor(self, RightTop)

        self.decrement_button = Button(
            replace(
                self.definition.button_style,
                text=self.definition.decrement_button_text,
                on_press=self._decrement_mouse_callback,
                width=widget_width,
                height=widget_height,
            )
        )
        self.add(self.decrement_button)
        self.decrement_button.align_anchor_with_other_anchor(self, LeftBottom)

        self.drag_box = DraggableBox(
            DraggableBoxDefinition(
                width=widget_width,
                height=widget_height,
                on_drag=self.read_slider_position,
                dynamic_size_behaviour=DynamicSizeBehaviourEnum.match_parent,
                bounding_box=self,
                background_color=self.definition.button_style.depressed_color,
            )
        )
        self.add(self.drag_box)
        self._calculate_drag_box_minmax_position()
        self.update_slider_position()
        self.info(f"self size is {self.rect=}")

    @property
    def value(self) -> float:
        """Get the current value of this Slider."""
        return self._value

    @value.setter
    def value(self, slider_value: float) -> None:
        """
        Set the value of the slider.

        Enforces the defined value boundaries.

        Updates the position of the slider indicator (the drag box) to represent the new value.
        """
        # Bound the value within the min/max.
        if slider_value > self.definition.maximum:
            self.trace(f"Bounded to maximum, attempt was {slider_value=}")
            slider_value = self.definition.maximum
        elif slider_value < self.definition.minimum:
            self.trace(f"Bounding to minimum, attempt was {slider_value=}")
            slider_value = self.definition.minimum

        def abs_difference(graduation):
            return abs(slider_value - graduation)

        # Now snap to the nearest graduation.
        if self.definition.graduations is not None:
            slider_value = min(self.definition.graduations, key=abs_difference)
            self.trace(f"Bounded to graduation {slider_value=}")

        self._value = slider_value

        if self.definition.on_change is not None:
            self.definition.on_change(self._value)

        self.update_slider_position()

    def on_size_change(self):
        """
        Called when the size of this Slider changes.

        Updates the display of the slider to match the new size without changing value.
        """
        super(Slider, self).on_size_change()
        self._calculate_drag_box_minmax_position()
        self.update_slider_position()

    def _calculate_drag_box_minmax_position(self):
        """
        Calculate and store the minimal and maximal position of the drag box.

        This is used to translate between the drag box position and the slider value.

        This must be recalculated on re-size operations.
        """
        if self.definition.orientation == OrientationEnum.vertical:
            minimum = self.decrement_button.rect.height
            maximum = (
                self.rect.height
                - self.increment_button.rect.height
                - self.decrement_button.rect.height
                - self.drag_box.rect.height
            )
        else:
            minimum = self.decrement_button.rect.width
            maximum = (
                self.rect.width
                - self.increment_button.rect.width
                - self.decrement_button.rect.width
                - self.drag_box.rect.width
            )

        self._drag_box_minmax_position = (minimum, maximum)

    def _widget_size(self) -> Tuple[int, int]:
        """Returns the size of the buttons and draggable box of the slider."""
        # Set the width, height of the buttons to be square and matching the size of the
        # slider in the relevant direction based on orientation.
        # Leave one direction as dynamically matching parent and fix the other at the original
        # size of the slider.
        if self.definition.orientation == OrientationEnum.vertical:
            width, height = self.rect.width, self.rect.width
        else:
            width, height = self.rect.height, self.rect.height
        return width, height

    def _increment_mouse_callback(self, *_, **__):
        """Callback to ignore mouse event params and just increment the slider."""
        self.increment()
        return EVENT_HANDLED

    def _decrement_mouse_callback(self, *_, **__):
        """Callback to ignore mouse event params and just decrement the slider."""
        self.decrement()
        return EVENT_HANDLED

    def increment(self, amount: Optional[float] = None) -> float:
        """
        Increase the value of the slider by the given amount.

        If no amount if given then the defined default increment is added.
        """
        if amount is None:
            amount = self.definition.increment

        self.value += amount
        return self.value

    def decrement(self, amount: Optional[float] = None) -> float:
        """
        Reduce the value of the slider by the given amount.

        If no amount if given then the defined default increment is subtracted.
        """
        if amount is None:
            amount = self.definition.increment

        self.value -= amount
        return self.value

    def read_slider_position(self, *_, **__):
        """Convert the drag box position into the slider value."""
        if self.definition.orientation == OrientationEnum.vertical:
            drag_position = self.drag_box.y
        else:
            drag_position = self.drag_box.x

        # Convert that position into a ratio of the minimum/maximum positions of the slider.
        # Ensure to account for the fact that the maximum position is less than the full slider
        # size by the increment button and the size of the drag slider itself.
        minimum, maximum = self._drag_box_minmax_position
        ratio = (drag_position - minimum) / maximum

        self.value = self.definition.minimum + (ratio * self.definition.range)

    def update_slider_position(self):
        """
        Set the position of the slider drag box to correspond with the current value.

        Inverse of `read_slider_position`.
        """
        ratio = (self.value - self.definition.minimum) / self.definition.range
        minimum, maximum = self._drag_box_minmax_position
        drag_position = (ratio * maximum) + minimum

        if self.definition.orientation == OrientationEnum.vertical:
            self.drag_box.y = drag_position
        else:
            self.drag_box.x = drag_position

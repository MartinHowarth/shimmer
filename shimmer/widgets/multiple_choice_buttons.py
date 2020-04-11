"""Module defining a set of Buttons representing a multiple choice question."""

from collections import defaultdict
from dataclasses import dataclass, field, replace
from typing import Optional, Union, Dict, Set, Any

from shimmer.components.box import BoxDefinition, Box
from shimmer.components.box_layout import (
    BoxLayoutDefinition,
    BoxRow,
    BoxColumn,
    create_box_layout,
)
from shimmer.components.mouse_box import MouseClickEventCallable
from shimmer.helpers import bundle_callables
from shimmer.widgets.button import ButtonDefinition, ToggleButton
from shimmer.widgets.question_definition import MultipleChoiceQuestionDefinition


@dataclass(frozen=True)
class MultipleChoiceButtonsDefinition(BoxDefinition):
    """Definition of a set of multiple choice buttons."""

    question: MultipleChoiceQuestionDefinition = MultipleChoiceQuestionDefinition(
        text=""
    )

    # The style of the buttons to display. The text field will be ignored.
    button: ButtonDefinition = field(default_factory=ButtonDefinition)

    # How to arrange the multiple buttons.
    layout: BoxLayoutDefinition = field(default_factory=BoxLayoutDefinition)


class MultipleChoiceButtons(Box):
    """A set of buttons that together represent multiple options to the user."""

    def __init__(self, definition: MultipleChoiceButtonsDefinition):
        """Create a MultipleChoiceButtons."""
        super(MultipleChoiceButtons, self).__init__(definition)
        self.definition: MultipleChoiceButtonsDefinition = self.definition
        self._layout: Optional[Union[BoxRow, BoxColumn]] = None
        self._buttons: Dict[Union[str, Box], ToggleButton] = {}
        self._current_selection: Dict[Union[str, Box], bool] = defaultdict(bool)
        self.update_layout()
        self.set_to_defaults()

    @property
    def currently_selected(self) -> Set[Union[str, Box]]:
        """Return a set of the currently selected options."""
        return set(
            item[0]
            for item in filter(
                lambda item: item[1] is True, self._current_selection.items()
            )
        )

    def set_to_defaults(self) -> None:
        """
        Set all toggle buttons to match the defined default state.

        Will call each buttons callback if their state changes.
        """
        for choice, button in self._buttons.items():
            if choice in self.definition.question.defaults:
                button.is_toggled = True
            else:
                button.is_toggled = False

    def _create_choice_callback_wrapper(
        self,
        chosen: Union[str, Box],
        existing_on_press: Optional[MouseClickEventCallable],
    ) -> MouseClickEventCallable:
        """
        Create callback to notify this multiple choice of a button press.

        Also calls the existing on_select method if it exists.

        :param chosen: The choice represented by the button.
        :param existing_on_press: Optional on_select callback that already is defined on the button.
        """

        def inner(box: ToggleButton, *_: Any, **__: Any) -> None:
            self._handle_button_select_or_deselect(chosen, box)

        if existing_on_press:
            return bundle_callables(inner, existing_on_press)
        else:
            return inner

    def _handle_button_select_or_deselect(
        self, chosen: Union[str, Box], button: ToggleButton
    ) -> None:
        """
        Called when a child button is selected.

        :param chosen: The choice represented by the button.
        :param button: The button that was selected.
        """
        self._current_selection[chosen] = button.is_toggled

        if self.definition.question.on_change is not None:
            self.definition.question.on_change(self.currently_selected)

        # If only 1 button is allowed to be selected, deselect all other ones.
        # This will actually call back into here for each deselection as they will call their
        # toggle change callback. However, we limit recursion based on whether the button has been
        # set to True, which every other button won't be.
        if not self.definition.question.allow_multiple and button.is_toggled:
            for choice, button in self._buttons.items():
                if choice != chosen:
                    button.is_toggled = False

    def _create_buttons(self):
        """Create the set of buttons for each choice."""
        buttons = []
        for choice in self.definition.question.choices:
            if isinstance(choice, str):
                text = choice
            else:
                text = ""

            defn = replace(
                self.definition.button,
                text=text,
                on_press=self._create_choice_callback_wrapper(
                    choice, self.definition.button.on_press
                ),
                on_release=self._create_choice_callback_wrapper(
                    choice, self.definition.button.on_release
                ),
            )
            button = ToggleButton(defn)
            if isinstance(choice, Box):
                button.add(choice, z=-100)
            buttons.append(button)
        self._buttons = dict(zip(self.definition.question.choices, buttons))
        return buttons

    def update_layout(self):
        """Recreate the buttons and the layout of this multiple choice."""
        if self._layout is not None:
            self.remove(self._layout)

        self._layout = create_box_layout(self.definition.layout, self._create_buttons())
        self.add(self._layout)

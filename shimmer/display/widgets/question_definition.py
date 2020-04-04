"""Widgets for asking questions of the user."""

from dataclasses import dataclass, field
from typing import Sequence, Optional, Protocol, Set, Union, Any

from .text_box import EditableTextBoxDefinition
from ..components.box import Box


class NoArgumentsCallback(Protocol):
    """Protocol defining the signature of a callback that takes no arguments."""

    def __call__(self) -> None:
        """Function signature of a basic callback."""
        pass


class OnQuestionChangeCallback(Protocol):
    """Protocol defining the signature of a callback when a question answer changes."""

    def __call__(self, answer: Any) -> None:
        """Function signature of a basic callback."""
        pass


class MultipleChoiceSelectionChangedCallback(Protocol):
    """Protocol defining the signature of a callback when a multiple choice option is selected."""

    def __call__(
        self,
        currently_selected: Set[Union[str, Box]],
        changed_choice: Union[str, Box],
        choice_state: bool,
    ) -> None:
        """Function signature of a multiple choice response callback."""
        pass


@dataclass(frozen=True)
class QuestionDefinition:
    """Definition of a question requesting user input."""

    text: str

    # Whenever the user makes a change to the question result, this function is called.
    # This is called with the current result of the question. For example this could be:
    #    - The set of multiple choice answer selected.
    #    - The current text in a text input box.
    on_change: Optional[OnQuestionChangeCallback] = None

    # If `confirmation_required`, Ok/Cancel buttons are displayed alongside the question.
    # This function is called when the Ok button is pressed.
    on_confirm: Optional[NoArgumentsCallback] = None

    # Callback that is called if a question is cancelled.
    # For example, this could be when a Window displaying a question is closed using the X button.
    on_cancel: Optional[NoArgumentsCallback] = None

    @property
    def confirmation_required(self) -> bool:
        """
        True if the question requires confirmation, otherwise False.

        Typically, if this is True, Ok/Cancel buttons will be displayed.

        If False, then typically the question will be a multiple-choice question where
        selecting one choice is sufficient to answer the question without further confirmation.
        """
        return self.on_confirm is not None


@dataclass(frozen=True)
class MultipleChoiceQuestionDefinition(QuestionDefinition):
    """
    Definition of a question with a defined set of answers.

    Users may select multiple answers if `allow_multiple` is set to True.
    """

    # The choices to include. The order of this list is the order in which the choices will be
    # presented to the user (e.g. from left to right).
    choices: Sequence[Union[str, Box]] = field(default_factory=list)

    # Whether to allow multiple options to be selected at once.
    allow_multiple: bool = False

    # Set of choices that will be selected on creation.
    defaults: Set[Union[str, Box]] = field(default_factory=set)

    def __post_init__(self):
        """Validate the definition."""
        if not self.allow_multiple:
            if len(self.defaults) > 1:
                raise ValueError(
                    "Cannot have multiple defaults if `allow_multiple` is False."
                )
        if not self.defaults.issubset(set(self.choices)):
            invalid_defaults = self.defaults.difference(set(self.choices))
            raise ValueError(
                f"All defaults must be in choices. Invalid defaults: {invalid_defaults}"
            )


@dataclass(frozen=True)
class TextInputQuestionDefinition(QuestionDefinition):
    """Definition of a question that asks for the user to input text."""

    text_box_definition: EditableTextBoxDefinition = EditableTextBoxDefinition()

    @property
    def confirmation_required(self) -> bool:
        """Always require confirmation to indicate that text entry has completed."""
        return True

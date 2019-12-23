"""Widgets for asking questions of the user."""

from dataclasses import dataclass, field
from typing import Sequence, Optional, Protocol, Set


class QuestionCancelledCallback(Protocol):
    """Protocol defining the signature of a callback when a question is cancelled."""

    def __call__(self) -> None:
        """Function signature of a question cancelled callback."""
        pass


class MultipleChoiceResponseCallback(Protocol):
    """Protocol defining the signature of a callback when a multiple choice option is selected."""

    def __call__(
        self, currently_selected: Set[str], changed_choice: str, choice_state: bool,
    ) -> None:
        """Function signature of a multiple choice response callback."""
        pass


@dataclass(frozen=True)
class QuestionDefinition:
    """Definition of a question requesting user input."""

    text: str

    # Callback that is called if a question is cancelled.
    # For example, this could be when a Window displaying a question is closed using the X button.
    on_cancel: Optional[QuestionCancelledCallback] = None


@dataclass(frozen=True)
class MultipleChoiceQuestionDefinition(QuestionDefinition):
    """
    Definition of a question with a defined set of answers.

    Users may select multiple answers if `allow_multiple` is set to True.
    """

    # The choices to include. Ordering impacts the way the question answer will be presented to the
    # user.
    choices: Sequence[str] = field(default_factory=list)

    # Whether to allow multiple options to be selected at once.
    allow_multiple: bool = False

    # Set of choices that will be selected on creation.
    defaults: Set[str] = field(default_factory=set)

    # Callback to call when the selection changes.
    # Arguments are:
    #  - List of the choices that are currently selected.
    #  - The choice that has changed state.
    #  - The current state of that choice.
    on_select: Optional[MultipleChoiceResponseCallback] = None

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

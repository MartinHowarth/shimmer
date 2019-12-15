"""Common methods for programmable code blocks."""

from dataclasses import dataclass
from inspect import signature
from typing import Set, Callable, Generator, Optional

from .definition import Program


@dataclass
class Programmable:
    """
    Definition of a user-editable program.

    The `methods` are the valid methods that the user can choose to use.

    The `program` contains the actual program definition.
    """

    methods: Set[Callable]
    program: Optional[Program] = None

    @property
    def bool_methods(self) -> Generator[Callable, None, None]:
        """
        Return the set of `methods` that return a bool value.

        This is used to only present boolean methods to users for use in If/Elif/While statements.
        """
        for method in self.methods:
            if issubclass(signature(method).return_annotation, bool):
                yield method

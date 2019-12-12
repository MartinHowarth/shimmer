from dataclasses import dataclass
from inspect import signature
from typing import Set, Callable, Generator, Optional

from .definition import Program


@dataclass
class Programmable:
    methods: Set[Callable]
    program: Optional[Program] = None

    @property
    def bool_methods(self) -> Generator[Callable, None, None]:
        for method in self.methods:
            if issubclass(signature(method).return_annotation, bool):
                yield method

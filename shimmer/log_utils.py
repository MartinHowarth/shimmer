"""Useful methods for enhancing logging."""

import logging

from functools import update_wrapper
from typing import Callable


def log_exceptions(logger: logging.Logger) -> Callable[[Callable], Callable]:
    """
    Decorator that logs any exceptions raised by the decorated method.

    Useful for debugging callbacks from user input (e.g. any pyglet event) because otherwise they
    silently fail.

    :param logger: The Logger to use to log the exception.
    """

    def outer(func):
        """The actual decorator."""

        def wrapper(*args, **kwargs):
            """The wrapper for the function."""
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.exception(e)

        wrapped = update_wrapper(wrapper, func)
        return wrapped

    return outer

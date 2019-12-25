"""Methods to enable addition/removal of Boxes to other MouseBoxes on mouse events."""
import logging

from typing import Callable, Any

from shimmer.display.components.box import Box
from shimmer.display.components.mouse_box import MouseBox


log = logging.getLogger(__name__)


def create_pop_up_later(pop_up: Box) -> Callable:
    """
    Create a closure to add the given Box to the parent when activated.

    Intended to be used as a method in a MouseBoxDefinition.

    :param pop_up: Box to add as a child to the parent on configured mouse event.
    :return: Method to trigger pop_up attachment.
    """

    def create_pop_up(box: MouseBox, *_: Any, **__: Any) -> None:
        """Actually attach the pop up to the parent."""
        log.debug(f"Created pop up {pop_up} attached to {box}.")
        box.add(pop_up)

    return create_pop_up


def remove_pop_up_later(pop_up: Box) -> Callable:
    """
    Create a closure to remove the given Box to the parent when activated.

    Intended to be used as a method in a MouseBoxDefinition.

    :param pop_up: Box to remove the pop_up from the parent on configured mouse event.
    :return: Method to trigger pop_up removal.
    """

    def remove_pop_up(box: MouseBox, *_: Any, **__: Any) -> None:
        """Actually remove the pop up from the parent."""
        log.debug(f"Removed pop up {pop_up} from {box}.")
        box.remove(pop_up)

    return remove_pop_up


def toggle_pop_up_later(pop_up: Box) -> Callable:
    """
    Create a closure to add and remove the given Box to the parent when activated.

    On first activation the pop_up is added as a child to the parent. On second activation it is
    removed. This addition/removal repeats for further activations.

    Intended to be used as a method in a MouseBoxDefinition.

    :param pop_up: Box to toggle the pop_up from the parent on configured mouse event.
    :return: Method to trigger pop_up toggling.
    """
    toggled = False

    def toggle_pop_up(box: MouseBox, *_: Any, **__: Any) -> None:
        """Attach or remove the pop_up from the parent, alternating on each call."""
        nonlocal toggled
        if toggled:
            log.debug(f"Toggled remove pop up {pop_up} from {box}.")
            box.remove(pop_up)
        else:
            log.debug(f"Toggled create pop up {pop_up} from {box}.")
            box.add(pop_up)
        toggled = not toggled

    return toggle_pop_up

"""Module defining keyboard handlers."""

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from functools import reduce
from typing import Optional, Callable, List, Dict, Iterable, Union

from more_itertools import powerset
from pyglet.event import EVENT_UNHANDLED, EVENT_HANDLED
from pyglet.window.key import (
    symbol_string,
    modifiers_string,
    MOD_NUMLOCK,
    MOD_CAPSLOCK,
    MOD_SCROLLLOCK,
)

import cocos
from .helpers import bitwise_add

NO_MOD = 0

log = logging.getLogger(__name__)


def defaultdict_key_map() -> Dict[int, Dict[Union[int, str], List]]:
    """Return a defaultdict for a key map structure."""
    return defaultdict(lambda: defaultdict(list))


@dataclass(frozen=True)
class ChordDefinition:
    """
    Definition of a key plus a set of modifiers.

    :param key: Scancode of the key. See pyglet.window.key for definitions.
    :param modifiers: Bitwise sum of the modifiers. See pyglet.window.key for definitions.
        Defaults to no modifier.
    :param ignore_modifiers: Tuple of modifiers to ignore. This is useful for ignoring the
        state of common always-on modifiers such as NUMLOCK.
        Defaults to ignoring NUMLOCK, CAPSLOCK and SCROLLLOCK.
    """

    key: int
    modifiers: int = 0
    ignore_modifiers: Iterable[int] = (MOD_NUMLOCK, MOD_CAPSLOCK, MOD_SCROLLLOCK)

    @classmethod
    def build_from_modifier_list(
        cls, key: int, modifiers: List[int]
    ) -> "ChordDefinition":
        """
        Build a Chord from a list of modifiers.

        Combines the modifiers into a single int representing their combined state.
        """
        modifier = reduce(bitwise_add, modifiers)
        return cls(key=key, modifiers=modifier)

    def __str__(self) -> str:
        """
        Return a human readable version of this chord.

        For example:
        ```
        str(ChordDefinition(key=pyglet.window.key.A, modifiers=MOD_CTRL|MOD_SHIFT))
          = "SHIFT+CTRL+A"
        ```
        """
        symbol_str: str = symbol_string(self.key)
        if self.modifiers == 0:
            return symbol_str

        modifier_str: str = modifiers_string(self.modifiers)
        split_modifier_strs: List[str] = modifier_str.split("|")
        stripped_modifier_strs: Iterable[str] = map(
            lambda mod_s: mod_s.replace("MOD_", ""), split_modifier_strs
        )
        return "+".join(stripped_modifier_strs) + "+" + symbol_str


@dataclass(frozen=True)
class KeyboardActionDefinition:
    """
    Definition of callbacks to call when a chord is pressed.

    Optionally takes multiple chords which all trigger the same action.

    A chord can either be a ChordDefinition, which is a specific arrangement of key + modifiers.
    Or it can be a single string character. This is useful when you want to distinguish
    between capital and lowercase letters without handling `MOD_SHIFT` yourself.

    Also note that text events may repeat if the user holds the key down, based on system settings.

    :param chords: List of ChordDefinitions or characters that can trigger the callbacks.
    :param on_select: Called when one of the chords is pressed, or a character is pressed.
    :param on_release: Called when one of the chords is released, or a character is pressed.
    """

    chords: List[Union[ChordDefinition, str]] = field(default_factory=list)

    on_press: Optional[Callable[[], Optional[bool]]] = None
    on_release: Optional[Callable[[], Optional[bool]]] = None


@dataclass
class KeyboardHandlerDefinition:
    """
    Definition of mapping from keyboard inputs to handlers.

    :param key_map: Mapping from chords or characters to actions to take.
        Note that it is probably easier to build the key_map using the methods on this definition,
        such as `add_keyboard_action`, rather than building it yourself.

        The following example shows how the `a` key can have different effects depending on
        the modifier used.

            map = {
                NO_MOD = {
                    A = [KeyboardActionDefinition(on_select=do_one)],
                    ...
                },
                MOD_SHIFT = {
                    A = [KeyboardActionDefinition(on_select=do_two)],
                    ...
                },
                MOD_CTRL | MOD_SHIFT = {
                    A = [KeyboardActionDefinition(on_select=do_three)],
                    ...
                },
                ...
            }
    :param on_text: Called with the string representation of the keyboard press.
    :param on_text_motion: Called with the pyglet representation of text motion.
    :param on_text_motion_select: Called with the pyglet representation of text motion selection.
    :param focus_required: If True, then this handler only responds to keyboard events
        when it has keyboard focus (i.e. `has_keyboard_focus = True`).
    """

    key_map: Dict[int, Dict[Union[int, str], List[KeyboardActionDefinition]]] = field(
        default_factory=defaultdict_key_map
    )
    on_text: Optional[Callable[[str], Optional[bool]]] = None
    on_text_motion: Optional[Callable[[int], Optional[bool]]] = None
    on_text_motion_select: Optional[Callable[[int], Optional[bool]]] = None
    focus_required: bool = True

    def add_keyboard_action(self, keyboard_action: KeyboardActionDefinition) -> None:
        """Add a KeyboardActionDefinition to this keymap."""
        for chord in keyboard_action.chords:
            if isinstance(chord, str):
                modifier_map = self.key_map[NO_MOD]
                if keyboard_action not in modifier_map[chord]:
                    modifier_map[chord].append(keyboard_action)
            else:
                # Add the action definition to every possible combination of the chord modifier
                # and the ignore modifiers. This works because if an ignored modifier is pressed,
                # then the action will be found in the relevant combined modifier dict.
                for mod_set in powerset(chord.ignore_modifiers):
                    modifiers = reduce(bitwise_add, (chord.modifiers, *mod_set))
                    modifier_map = self.key_map[modifiers]
                    if keyboard_action not in modifier_map[chord.key]:
                        modifier_map[chord.key].append(keyboard_action)

    def remove_keyboard_action(self, keyboard_action: KeyboardActionDefinition) -> None:
        """Remove a KeyboardActionDefinition from this keymap."""
        for chord in keyboard_action.chords:
            if isinstance(chord, str):
                modifier_map = self.key_map[NO_MOD]
                if keyboard_action in modifier_map[chord]:
                    modifier_map[chord].remove(keyboard_action)
            else:
                # Remove the action definition from every possible combination of the chord
                # modifier and the ignore modifiers.
                for mod_set in powerset(chord.ignore_modifiers):
                    modifiers = reduce(bitwise_add, (chord.modifiers, *mod_set))
                    modifier_map = self.key_map[modifiers]
                    if keyboard_action in modifier_map[chord.key]:
                        modifier_map[chord.key].remove(keyboard_action)

    def add_keyboard_action_simple(
        self,
        key: Union[int, str],
        action: Callable[[], Optional[bool]],
        modifiers: int = 0,
    ) -> KeyboardActionDefinition:
        """
        Simplified version of `add_keyboard_action`.

        Adds a single callback to occur on key press for the given key.

        :param key: The pyglet keyboard key integer; or text character.
        :param action: The function to call when the key is pressed.
        :param modifiers: The pyglet keyboard modifier integer.
        :return: The `KeyboardActionDefinition` created.
        """
        if isinstance(key, int):
            definition = KeyboardActionDefinition(
                chords=[ChordDefinition(key=key, modifiers=modifiers)], on_press=action,
            )
        else:
            definition = KeyboardActionDefinition(chords=[key], on_press=action,)
        self.add_keyboard_action(definition)
        return definition


class KeyboardHandler(cocos.cocosnode.CocosNode):
    """
    KeyboardHandler is a cocosnode that handles keyboard events.

    The handler has reference to a KeyboardHandlerDefinition which defines what actions to take
    when keys (plus optional modifiers) are pressed or released.

    Multiple KeyboardHandlers can exist at once. They will receive keyboard events
    following the normal cocosnode event handler rules.
    """

    def __init__(self, definition: KeyboardHandlerDefinition):
        """
        Create a new KeyboardHandler.

        :param definition: The definition of key to action mapping.
        """
        super(KeyboardHandler, self).__init__()
        self.has_keyboard_focus: bool = False
        self.definition = definition

    def on_enter(self):
        """Called every time just before the node enters the stage."""
        cocos.director.director.window.push_handlers(self)
        super(KeyboardHandler, self).on_enter()

    def on_exit(self):
        """Called every time just before the node exits the stage."""
        cocos.director.director.window.remove_handlers(self)
        super(KeyboardHandler, self).on_exit()

    @property
    def should_handle_keyboard_event(self) -> bool:
        """Return True if this KeyboardHandler should handle keyboard events, otherwise False."""
        return not self.definition.focus_required or self.has_keyboard_focus

    def set_focused(self):
        """Set this handler to be focused."""
        self.has_keyboard_focus = True

    def set_unfocused(self):
        """Set this handler to not be focused."""
        self.has_keyboard_focus = False

    def on_key_press(self, symbol: int, modifiers: int) -> Optional[bool]:
        """
        Called when the user presses a key.

        :param symbol: Integer representation of the key that was pressed.
            See pyglet.window.key for key code definitions.
        :param modifiers: Bitwise sum of the modifiers that are currently pressed.
            See pyglet.window.key for key code definitions.
        :return: True if the event was handled by any KeyboardAction, otherwise None.
        """
        if not self.should_handle_keyboard_event:
            return EVENT_UNHANDLED

        results = []
        modifier_map = self.definition.key_map[modifiers]
        for handler in modifier_map[symbol]:
            if handler.on_press is not None:
                results.append(handler.on_press())

        if EVENT_HANDLED in results:
            log.debug(f"on_key_press consumed by {self}")
            return EVENT_HANDLED
        return EVENT_UNHANDLED

    def on_key_release(self, symbol: int, modifiers: int) -> Optional[bool]:
        """
        Called when the user releases a key.

        :param symbol: Integer representation of the key that was releases.
            See pyglet.window.key for key code definitions.
        :param modifiers: Bitwise sum of the modifiers that are currently released.
            See pyglet.window.key for key code definitions.
        :return: True if the event was handled by any KeyboardAction, otherwise None.
        """
        if not self.should_handle_keyboard_event:
            return EVENT_UNHANDLED

        results = []
        modifier_map = self.definition.key_map[modifiers]
        for handler in modifier_map[symbol]:
            if handler.on_release is not None:
                results.append(handler.on_release())

        if EVENT_HANDLED in results:
            log.debug(f"on_key_release consumed by {self}")
            return EVENT_HANDLED
        return EVENT_UNHANDLED

    def on_text(self, text: str) -> Optional[bool]:
        """
        Called with the character that the user pressed.

        If `on_text` is set in the definition, that callback takes precedence over the keymap.

        This is called with the string representation of the key that was pressed,
        accounting for modifiers. For example, lowercase and capital letters are handled.

        Typically this is called after on_key_press and before on_key_release,
        but may also be called multiple times if the key is held down (key repeating);
        or called without key presses if another input method was used (e.g., a pen input).

        :param text: Single character string that was pressed.
        :return: True if the event was handled by any KeyboardAction, otherwise None.
        """
        if not self.should_handle_keyboard_event:
            return EVENT_UNHANDLED

        if self.definition.on_text is not None:
            result = self.definition.on_text(text)
            if result is EVENT_HANDLED:
                log.debug(f"on_text({text!r}) consumed by {self}")
                return EVENT_HANDLED

        results = []
        modifier_map = self.definition.key_map[NO_MOD]
        for handler in modifier_map[text]:
            if handler.on_press is not None:
                results.append(handler.on_press())
            if handler.on_release is not None:
                results.append(handler.on_release())

        if EVENT_HANDLED in results:
            log.debug(f"on_text({text!r}) consumed by {self}")
            return EVENT_HANDLED
        return EVENT_UNHANDLED

    def _should_handle_on_text_motion(self, motion: int) -> bool:
        """
        Determine if this Box should attempt to handle the mouse press event.

        :param motion: Int indicating which text motion has occurred.
        :return: True if this node should handle the text motion event.
        """
        return (
            self.should_handle_keyboard_event
            and self.definition.on_text_motion is not None
        )

    def _should_handle_on_text_motion_select(self, motion: int) -> bool:
        """
        Determine if this Box should attempt to handle the mouse press event.

        :param motion: Int indicating which text motion has occurred.
        :return: True if this node should handle the text motion select event.
        """
        return (
            self.should_handle_keyboard_event
            and self.definition.on_text_motion_select is not None
        )

    def on_text_motion(self, motion: int) -> Optional[bool]:
        """
        Called when text motion inputs are pressed.

        This handles typical text motion combination inputs, such as ctrl+home.

        See https://pyglet-current.readthedocs.io/en/latest/programming_guide/keyboard.html#motion-events.  # noqa

        :param motion: The pyglet constant representing the text motion that occurred.
        """
        if not self._should_handle_on_text_motion(motion):
            return EVENT_UNHANDLED

        if self.definition.on_text_motion is not None:
            self.definition.on_text_motion(motion)
            return EVENT_HANDLED
        return EVENT_UNHANDLED

    def on_text_motion_select(self, motion: int) -> Optional[bool]:
        """
        Called when text motion inputs are pressed.

        This handles typical text motion combination inputs, such as ctrl+home.

        See https://pyglet-current.readthedocs.io/en/latest/programming_guide/keyboard.html#motion-events.  # noqa

        :param motion: The pyglet constant representing the text motion that occurred.
        """
        if not self._should_handle_on_text_motion_select(motion):
            return EVENT_UNHANDLED

        if self.definition.on_text_motion_select is not None:
            self.definition.on_text_motion_select(motion)
            return EVENT_HANDLED
        return EVENT_UNHANDLED


def add_simple_keyboard_handler(
    parent: cocos.cocosnode.CocosNode,
    key: Union[int, str],
    action: Callable[[], Optional[bool]],
) -> KeyboardHandler:
    """
    Add a simple keyboard handler to the given parent.

    This allows the node to trigger the given action when the given key is pressed, regardless
    of which keyboard modifiers are currently pressed.

    This requires that the parent has been made focusable because this is intended to add a
    node-specific keyboard action, rather than a global action. This can be done by either adding
    a FocusBox to the parent or using the simpler `make_focusable` method.
    """
    keyboard_handler_definition = KeyboardHandlerDefinition(focus_required=True)
    keyboard_handler_definition.add_keyboard_action_simple(key, action)
    keyboard_handler = KeyboardHandler(keyboard_handler_definition)
    parent.add(keyboard_handler)
    return keyboard_handler

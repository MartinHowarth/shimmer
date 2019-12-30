"""Module defining keyboard handlers."""

import cocos

from collections import defaultdict
from dataclasses import dataclass, field
from more_itertools import powerset
from functools import reduce
from pyglet.event import EVENT_UNHANDLED, EVENT_HANDLED
from pyglet.window.key import (
    symbol_string,
    modifiers_string,
    MOD_NUMLOCK,
    MOD_CAPSLOCK,
    MOD_SCROLLLOCK,
)
from typing import Optional, Callable, List, Dict, Iterable, Union

from .helpers import bitwise_add


NO_MOD = 0


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

    Note that for character (aka text) presses, on_press and on_release will be called
    immediately - there is no "release" event for text.

    Also note that text events may repeat rapidly if the user holds the key down.

    :param chords: List of ChordDefinitions or characters that can trigger the callbacks.
    :param on_press: Called when one of the chords is pressed, or a character is pressed.
    :param on_release: Called when one of the chords is released, or a character is pressed.
    """

    chords: List[Union[ChordDefinition, str]] = field(default_factory=list)

    on_press: Optional[Callable[[], Optional[bool]]] = None
    on_release: Optional[Callable[[], Optional[bool]]] = None


@dataclass
class KeyMap:
    """
    Definition of mapping from keyboard inputs to handlers.

    Stored in the `map` attribute in the following structure. This example shows
    how the `a` key can have different effects depending on the modifier used.

        map = {
            NO_MOD = {
                A = [KeyboardActionDefinition(on_press=do_one)],
                ...
            },
            MOD_SHIFT = {
                A = [KeyboardActionDefinition(on_press=do_two)],
                ...
            },
            MOD_CTRL | MOD_SHIFT = {
                A = [KeyboardActionDefinition(on_press=do_three)],
                ...
            },
            ...
        }
    """

    map: Dict[int, Dict[Union[int, str], List[KeyboardActionDefinition]]] = field(
        default_factory=defaultdict_key_map
    )

    def add_keyboard_action(self, keyboard_action: KeyboardActionDefinition) -> None:
        """Add a KeyboardActionDefinition to this keymap."""
        for chord in keyboard_action.chords:
            if isinstance(chord, str):
                modifier_map = self.map[NO_MOD]
                if keyboard_action not in modifier_map[chord]:
                    modifier_map[chord].append(keyboard_action)
            else:
                # Add the action definition to every possible combination of the chord modifier
                # and the ignore modifiers. This works because if an ignored modifier is pressed,
                # then the action will be found in the relevant combined modifier dict.
                for mod_set in powerset(chord.ignore_modifiers):
                    modifiers = reduce(bitwise_add, (chord.modifiers, *mod_set))
                    modifier_map = self.map[modifiers]
                    if keyboard_action not in modifier_map[chord.key]:
                        modifier_map[chord.key].append(keyboard_action)

    def remove_keyboard_action(self, keyboard_action: KeyboardActionDefinition) -> None:
        """Remove a KeyboardActionDefinition from this keymap."""
        for chord in keyboard_action.chords:
            if isinstance(chord, str):
                modifier_map = self.map[NO_MOD]
                if keyboard_action in modifier_map[chord]:
                    modifier_map[chord].remove(keyboard_action)
            else:
                # Remove the action definition from every possible combination of the chord
                # modifier and the ignore modifiers.
                for mod_set in powerset(chord.ignore_modifiers):
                    modifiers = reduce(bitwise_add, (chord.modifiers, *mod_set))
                    modifier_map = self.map[modifiers]
                    if keyboard_action in modifier_map[chord.key]:
                        modifier_map[chord.key].remove(keyboard_action)


class KeyboardHandler(cocos.cocosnode.CocosNode):
    """
    KeyboardHandler is a cocosnode that handles keyboard events.

    The handler has reference to a KeyMap which defines what actions to take
    when keys (plus optional modifiers) are pressed or released.

    Multiple KeyboardHandlers can exist at once. They will receive keyboard events
    following the normal cocosnode event handler rules.
    """

    def __init__(self, keymap: KeyMap):
        """
        Create a new KeyboardHandler.

        :param keymap: The definition of key to action mapping.
        """
        super(KeyboardHandler, self).__init__()
        self.keymap = keymap

    def on_enter(self):
        """Called every time just before the node enters the stage."""
        cocos.director.director.window.push_handlers(self)
        super(KeyboardHandler, self).on_enter()

    def on_exit(self):
        """Called every time just before the node exits the stage."""
        cocos.director.director.window.remove_handlers(self)
        super(KeyboardHandler, self).on_exit()

    def on_key_press(self, symbol: int, modifiers: int) -> Optional[bool]:
        """
        Called when the user presses a key.

        :param symbol: Integer representation of the key that was pressed.
            See pyglet.window.key for key code definitions.
        :param modifiers: Bitwise sum of the modifiers that are currently pressed.
            See pyglet.window.key for key code definitions.
        :return: True if the event was handled by any KeyboardAction, otherwise None.
        """
        results = []
        modifier_map = self.keymap.map[modifiers]
        for handler in modifier_map[symbol]:
            if handler.on_press is not None:
                results.append(handler.on_press())

        if EVENT_HANDLED in results:
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
        results = []
        modifier_map = self.keymap.map[modifiers]
        for handler in modifier_map[symbol]:
            if handler.on_release is not None:
                results.append(handler.on_release())

        if EVENT_HANDLED in results:
            return EVENT_HANDLED
        return EVENT_UNHANDLED

    def on_text(self, text: str) -> Optional[bool]:
        """
        Called when the user inputs some text.

        This is called with the string representation of the key that was pressed,
        accounting for modifiers. For example, lowercase and capital letters are handled.

        Typically this is called after on_key_press and before on_key_release,
        but may also be called multiple times if the key is held down (key repeating);
        or called without key presses if another input method was used (e.g., a pen input).

        :param text: Single character string that was pressed.
        :return: True if the event was handled by any KeyboardAction, otherwise None.
        """
        results = []
        modifier_map = self.keymap.map[NO_MOD]
        for handler in modifier_map[text]:
            if handler.on_press is not None:
                results.append(handler.on_press())
            if handler.on_release is not None:
                results.append(handler.on_release())

        if EVENT_HANDLED in results:
            return EVENT_HANDLED
        return EVENT_UNHANDLED

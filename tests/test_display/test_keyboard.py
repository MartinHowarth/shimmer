"""Tests for the keyboard handler."""

from mock import MagicMock
from pyglet.event import EVENT_UNHANDLED, EVENT_HANDLED
from pyglet.window import key
from typing import no_type_check

from shimmer.display.helpers import bitwise_add
from shimmer.display.keyboard import (
    ChordDefinition,
    KeyboardActionDefinition,
    KeyMap,
    KeyboardHandler,
    NO_MOD,
)


def dummy_keyboard_handler():
    """Create a dummy keyboard handler."""
    a = ChordDefinition(key.A, NO_MOD, ignore_modifiers=tuple())
    b = ChordDefinition(key.B, NO_MOD, ignore_modifiers=tuple())
    shift_a = ChordDefinition(key.A, key.MOD_SHIFT, ignore_modifiers=tuple())
    shift_ctrl_a = ChordDefinition(
        key.A, key.MOD_SHIFT | key.MOD_CTRL, ignore_modifiers=tuple()
    )
    keyboard_action = KeyboardActionDefinition(
        chords=[a], on_press=MagicMock(), on_release=MagicMock()
    )
    keyboard_action1 = KeyboardActionDefinition(
        chords=[a, shift_a], on_press=MagicMock(), on_release=MagicMock()
    )
    keyboard_action2 = KeyboardActionDefinition(
        chords=[b, shift_ctrl_a], on_press=MagicMock(), on_release=MagicMock()
    )
    keymap = KeyMap()
    keymap.add_keyboard_action(keyboard_action)
    keymap.add_keyboard_action(keyboard_action1)
    keymap.add_keyboard_action(keyboard_action2)

    handler = KeyboardHandler(keymap)
    return handler, keyboard_action, keyboard_action1, keyboard_action2


def test_chord_definition_build_from_modifier_list():
    """Test `build_from_modifier_list` of ChordDefinition."""
    chord = ChordDefinition.build_from_modifier_list(
        key.A, [key.MOD_SHIFT, key.MOD_CTRL]
    )
    assert chord.key == key.A
    assert chord.modifiers == 3


def test_chord_definition_to_str(subtests):
    """Test converting chord definition to string."""
    with subtests.test("Test string conversion with no modifiers."):
        chord = ChordDefinition(key=key.A)
        assert str(chord) == "A"

    with subtests.test("Test string conversion with one modifier."):
        chord = ChordDefinition(key=key.A, modifiers=1)
        assert str(chord) == "SHIFT+A"

    with subtests.test("Test string conversion with two modifiers."):
        chord = ChordDefinition(key=key.A, modifiers=3)
        assert str(chord) == "SHIFT+CTRL+A"


def test_keymap_add_keyboard_action(subtests):
    """Test adding keyboard actions to a keymap."""
    a = ChordDefinition(key.A, NO_MOD, ignore_modifiers=tuple())
    b = ChordDefinition(key.B, NO_MOD, ignore_modifiers=tuple())
    shift_a = ChordDefinition(key.A, key.MOD_SHIFT, ignore_modifiers=tuple())
    shift_ctrl_a = ChordDefinition(
        key.A, key.MOD_SHIFT | key.MOD_CTRL, ignore_modifiers=tuple()
    )

    with subtests.test("Test adding an action with a single chord."):
        keymap = KeyMap()
        keyboard_action = KeyboardActionDefinition(chords=[a])
        keymap.add_keyboard_action(keyboard_action)

        assert keymap.map == {NO_MOD: {key.A: [keyboard_action]}}

    with subtests.test(
        "Test adding an action with two chords using different modifiers."
    ):
        keymap = KeyMap()
        keyboard_action = KeyboardActionDefinition(chords=[shift_ctrl_a, shift_a])
        keymap.add_keyboard_action(keyboard_action)

        assert keymap.map == {
            key.MOD_SHIFT: {key.A: [keyboard_action]},
            key.MOD_SHIFT | key.MOD_CTRL: {key.A: [keyboard_action]},
        }

    with subtests.test("Test adding an action with two chords using different keys."):
        keymap = KeyMap()
        keyboard_action = KeyboardActionDefinition(chords=[a, b])
        keymap.add_keyboard_action(keyboard_action)

        assert keymap.map == {
            NO_MOD: {key.A: [keyboard_action], key.B: [keyboard_action]},
        }

    with subtests.test("Test adding an two actions with the same chord."):
        keymap = KeyMap()
        keyboard_action = KeyboardActionDefinition(chords=[a, b])
        # Include a dummy function definition otherwise the actions compare as identical.
        keyboard_action2 = KeyboardActionDefinition(
            chords=[a, b], on_press=lambda: True
        )
        keymap.add_keyboard_action(keyboard_action)
        keymap.add_keyboard_action(keyboard_action2)

        assert keymap.map == {
            NO_MOD: {
                key.A: [keyboard_action, keyboard_action2],
                key.B: [keyboard_action, keyboard_action2],
            },
        }

    with subtests.test("Test adding the same action a second time does nothing."):
        keymap = KeyMap()
        keyboard_action = KeyboardActionDefinition(chords=[a])
        keymap.add_keyboard_action(keyboard_action)
        keymap.add_keyboard_action(keyboard_action)

        assert keymap.map == {
            NO_MOD: {key.A: [keyboard_action]},
        }


def test_keymap_remove_keyboard_action(subtests):
    """Test removing keyboard actions from a keymap."""
    a = ChordDefinition(key.A, NO_MOD, ignore_modifiers=tuple())
    b = ChordDefinition(key.B, NO_MOD, ignore_modifiers=tuple())
    shift_a = ChordDefinition(key.A, key.MOD_SHIFT, ignore_modifiers=tuple())
    shift_ctrl_a = ChordDefinition(
        key.A, key.MOD_SHIFT | key.MOD_CTRL, ignore_modifiers=tuple()
    )
    keyboard_action = KeyboardActionDefinition(chords=[a])
    keyboard_action1 = KeyboardActionDefinition(chords=[a, shift_a])
    keyboard_action2 = KeyboardActionDefinition(chords=[b, shift_ctrl_a])

    def make_keymap():
        _keymap = KeyMap()
        _keymap.add_keyboard_action(keyboard_action)
        _keymap.add_keyboard_action(keyboard_action1)
        _keymap.add_keyboard_action(keyboard_action2)
        return _keymap

    with subtests.test("Test removing an action with a single chord."):
        keymap = make_keymap()
        keymap.remove_keyboard_action(keyboard_action)
        assert keymap.map == {
            NO_MOD: {key.A: [keyboard_action1], key.B: [keyboard_action2]},
            key.MOD_SHIFT: {key.A: [keyboard_action1]},
            key.MOD_SHIFT | key.MOD_CTRL: {key.A: [keyboard_action2]},
        }

    with subtests.test("Test removing an action with multiple chords."):
        keymap = make_keymap()
        keymap.remove_keyboard_action(keyboard_action2)
        assert keymap.map == {
            NO_MOD: {key.A: [keyboard_action, keyboard_action1], key.B: []},
            key.MOD_SHIFT: {key.A: [keyboard_action1]},
            key.MOD_SHIFT | key.MOD_CTRL: {key.A: []},
        }


@no_type_check  # Ignore typing because Mocks don't type nicely.
def test_key_handler_on_press(subtests, mock_gui, mock_keyboard):
    """Test that KeyHandler handles key press events correctly."""
    (
        handler,
        keyboard_action,
        keyboard_action1,
        keyboard_action2,
    ) = dummy_keyboard_handler()

    with subtests.test(
        "Single keyboard event calls no actions if key is not configured."
    ):
        mock_keyboard.press(handler, key.Z)
        keyboard_action.on_press.assert_not_called()
        keyboard_action1.on_press.assert_not_called()
        keyboard_action2.on_press.assert_not_called()

    with subtests.test("Single key press calls two actions."):
        mock_keyboard.press(handler, key.A)
        keyboard_action.on_press.assert_called_once()
        keyboard_action1.on_press.assert_called_once()
        keyboard_action2.on_press.assert_not_called()

    keyboard_action.on_press.reset_mock()
    keyboard_action1.on_press.reset_mock()

    with subtests.test("Key press with modifiers calls correct actions."):
        mock_keyboard.press(handler, key.A, bitwise_add(key.MOD_SHIFT, key.MOD_CTRL))
        keyboard_action.on_press.assert_not_called()
        keyboard_action1.on_press.assert_not_called()
        keyboard_action2.on_press.assert_called_once()

    keyboard_action2.on_press.reset_mock()

    with subtests.test("Same action can be called by two different key presses."):
        mock_keyboard.press(handler, key.A, bitwise_add(key.MOD_SHIFT, key.MOD_CTRL))
        keyboard_action2.on_press.assert_called_once()
        mock_keyboard.press(handler, key.B)
        assert keyboard_action2.on_press.call_count == 2


@no_type_check  # Ignore typing because Mocks don't type nicely.
def test_key_handler_on_release(subtests, mock_gui, mock_keyboard):
    """Test that KeyHandler handles key release events correctly."""
    (
        handler,
        keyboard_action,
        keyboard_action1,
        keyboard_action2,
    ) = dummy_keyboard_handler()

    with subtests.test(
        "Single keyboard event calls no actions if key is not configured."
    ):
        mock_keyboard.release(handler, key.Z)
        keyboard_action.on_release.assert_not_called()
        keyboard_action1.on_release.assert_not_called()
        keyboard_action2.on_release.assert_not_called()

    with subtests.test("Single key release calls two actions."):
        mock_keyboard.release(handler, key.A)
        keyboard_action.on_release.assert_called_once()
        keyboard_action1.on_release.assert_called_once()
        keyboard_action2.on_release.assert_not_called()

    keyboard_action.on_release.reset_mock()
    keyboard_action1.on_release.reset_mock()

    with subtests.test("Key release with modifiers calls correct actions."):
        mock_keyboard.release(handler, key.A, bitwise_add(key.MOD_SHIFT, key.MOD_CTRL))
        keyboard_action.on_release.assert_not_called()
        keyboard_action1.on_release.assert_not_called()
        keyboard_action2.on_release.assert_called_once()

    keyboard_action2.on_release.reset_mock()

    with subtests.test("Same action can be called by two different key releases."):
        mock_keyboard.release(handler, key.A, bitwise_add(key.MOD_SHIFT, key.MOD_CTRL))
        keyboard_action2.on_release.assert_called_once()
        mock_keyboard.release(handler, key.B)
        assert keyboard_action2.on_release.call_count == 2


@no_type_check  # Ignore typing because Mocks don't type nicely.
def test_key_handler_with_text_action(subtests, mock_gui, mock_keyboard):
    """Test KeyboardAction definition with text rather than a Chord works correctly."""
    keyboard_action = KeyboardActionDefinition(
        chords=["a", "A"], on_press=MagicMock(), on_release=MagicMock()
    )
    keymap = KeyMap()
    keymap.add_keyboard_action(keyboard_action)
    handler = KeyboardHandler(keymap)

    with subtests.test("Test that the first text chord can trigger the action."):
        mock_keyboard.text(handler, "a")
        keyboard_action.on_press.assert_called_once()
        keyboard_action.on_release.assert_called_once()

    keyboard_action.on_press.reset_mock()
    keyboard_action.on_release.reset_mock()

    with subtests.test("Test that the second text chord can trigger the action."):
        mock_keyboard.text(handler, "A")
        keyboard_action.on_press.assert_called_once()
        keyboard_action.on_release.assert_called_once()


@no_type_check  # Ignore typing because Mocks don't type nicely.
def test_ignore_modifiers_with_no_modifier(subtests, mock_gui, mock_keyboard):
    """Test ignore_modifiers on ChordDefinition with no modifiers is handled correctly."""
    chord = ChordDefinition(
        key=key.A,
        modifiers=NO_MOD,
        ignore_modifiers=(key.MOD_NUMLOCK, key.MOD_CAPSLOCK),
    )
    keyboard_action = KeyboardActionDefinition(
        chords=[chord], on_press=MagicMock(), on_release=MagicMock()
    )
    keymap = KeyMap()
    keymap.add_keyboard_action(keyboard_action)
    handler = KeyboardHandler(keymap)

    with subtests.test("Test ignore modifiers with no modifiers at all."):
        mock_keyboard.press(handler, key.A, NO_MOD)
        keyboard_action.on_press.assert_called_once()

    keyboard_action.on_press.reset_mock()

    with subtests.test("Test ignore modifiers with one ignored modifier."):
        mock_keyboard.press(handler, key.A, key.MOD_NUMLOCK)
        keyboard_action.on_press.assert_called_once()

    keyboard_action.on_press.reset_mock()

    with subtests.test("Test ignore modifiers with two ignored modifiers."):
        mock_keyboard.press(
            handler, key.A, bitwise_add(key.MOD_NUMLOCK, key.MOD_CAPSLOCK)
        )
        keyboard_action.on_press.assert_called_once()

    keyboard_action.on_press.reset_mock()

    with subtests.test("Test ignore modifiers with non-matching modifier."):
        # SHIFT is not ignored, but doesn't match the chord so shouldn't cause an event.
        mock_keyboard.press(handler, key.A, bitwise_add(key.MOD_SHIFT, key.MOD_NUMLOCK))
        keyboard_action.on_press.assert_not_called()


@no_type_check  # Ignore typing because Mocks don't type nicely.
def test_ignore_modifiers_with_modifier(subtests, mock_gui, mock_keyboard):
    """Test ignore_modifiers on ChordDefinition with modifiers is handled correctly."""
    chord = ChordDefinition(
        key=key.A,
        modifiers=key.MOD_SHIFT,
        ignore_modifiers=(key.MOD_NUMLOCK, key.MOD_CAPSLOCK),
    )
    keyboard_action = KeyboardActionDefinition(
        chords=[chord], on_press=MagicMock(), on_release=MagicMock()
    )
    keymap = KeyMap()
    keymap.add_keyboard_action(keyboard_action)
    handler = KeyboardHandler(keymap)

    with subtests.test("Test ignore modifiers with no modifiers at all."):
        # Matching modifier not supplied.
        mock_keyboard.press(handler, key.A, NO_MOD)
        keyboard_action.on_press.assert_not_called()

    with subtests.test(
        "Test ignore modifiers with one ignored modifier and no required modifier."
    ):
        # Matching modifier not supplied.
        mock_keyboard.press(handler, key.A, key.MOD_NUMLOCK)
        keyboard_action.on_press.assert_not_called()

    with subtests.test("Test ignore modifiers with matching required modifier."):
        mock_keyboard.press(
            handler, key.A, bitwise_add(key.MOD_SHIFT, key.MOD_CAPSLOCK)
        )
        keyboard_action.on_press.assert_called_once()

    keyboard_action.on_press.reset_mock()

    with subtests.test("Test ignore modifiers with only matching required modifier."):
        mock_keyboard.press(handler, key.A, key.MOD_SHIFT)
        keyboard_action.on_press.assert_called_once()


@no_type_check  # Ignore typing because Mocks don't type nicely.
def test_key_handler_return_handled(subtests, mock_gui, mock_keyboard):
    """Test KeyboardAction definition with text rather than a Chord works correctly."""
    keyboard_action_handled = KeyboardActionDefinition(
        chords=["a"], on_press=MagicMock(return_value=True)
    )
    keyboard_action_unhandled = KeyboardActionDefinition(
        chords=["a"], on_press=MagicMock(return_value=None)
    )
    keyboard_action_other = KeyboardActionDefinition(
        chords=["b"], on_press=MagicMock(return_value=None)
    )
    keymap = KeyMap()
    keymap.add_keyboard_action(keyboard_action_handled)
    keymap.add_keyboard_action(keyboard_action_unhandled)
    keymap.add_keyboard_action(keyboard_action_other)
    handler = KeyboardHandler(keymap)

    with subtests.test("Check if any handler returns True, then the event is handled."):
        assert mock_keyboard.text(handler, "a") is EVENT_HANDLED
        keyboard_action_handled.on_press.assert_called_once()
        keyboard_action_unhandled.on_press.assert_called_once()

    with subtests.test(
        "Check if no handler returns True, then the event is unhandled."
    ):
        assert mock_keyboard.text(handler, "b") is EVENT_UNHANDLED
        keyboard_action_other.on_press.assert_called_once()

"""Definition of a mock keyboard for use in testing."""

from typing import Optional

from shimmer.keyboard import KeyboardHandler


class MockKeyboard:
    """
    A mock of a physical keyboard.

    Used to simulate keyboard events in tests.
    """

    def press(
        self, handler: KeyboardHandler, symbol: int, modifiers: int = 0
    ) -> Optional[bool]:
        """Press the given key and modifiers and send it to the handler."""
        return handler.on_key_press(symbol, modifiers)

    def release(
        self, handler: KeyboardHandler, symbol: int, modifiers: int = 0
    ) -> Optional[bool]:
        """Release the given key and modifiers and send it to the handler."""
        return handler.on_key_release(symbol, modifiers)

    def tap(self, handler: KeyboardHandler, symbol: int, modifiers: int = 0) -> None:
        """Press and release the given key and modifiers and send it to the handler."""
        self.press(handler, symbol, modifiers)
        # Technically `text` should be called here as well to simulate what actually happens,
        # but it's not worth replicating the pyglet behaviour here to map from key+modifiers to
        # text.
        self.release(handler, symbol, modifiers)

    def text(self, handler: KeyboardHandler, text: str) -> Optional[bool]:
        """
        Simulate pyglet handling text input and passing it to us as a text character.

        Useful for capital vs lowercase testing as SHIFT+a will trigger both an
        on_key_press event with MOD_SHIFT and key.A; and an on_text event with "A".
        I.e. saves you from having to work out what SHIFT+a means.
        """
        return handler.on_text(text)

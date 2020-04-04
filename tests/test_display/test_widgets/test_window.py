"""Graphical tests for the Window widget."""

from shimmer.display.widgets.window import Window, WindowDefinition


def test_window(run_gui):
    """A draggable window should be shown; and the X button should close the window."""
    window = Window(WindowDefinition(width=300, height=200))
    assert run_gui(test_window, window)


def test_window_on_close_callback(run_gui, updatable_text_box):
    """A window should be shown and the X button should update the placeholder text."""
    text_box, update_text_box = updatable_text_box

    def callback(*_, **__):
        update_text_box("Closed!")

    window = Window(WindowDefinition(width=300, height=200, on_close=callback))
    assert run_gui(test_window_on_close_callback, text_box, window)

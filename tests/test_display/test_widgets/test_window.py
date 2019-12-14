import cocos

from shimmer.display.widgets.window import Window


def test_window(run_gui):
    """A draggable window should be shown; and the X button should close the window."""
    window = Window(cocos.rect.Rect(0, 0, 300, 300))
    assert run_gui(test_window, window)
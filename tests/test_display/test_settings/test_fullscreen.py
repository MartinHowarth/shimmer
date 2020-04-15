"""Tests for the fullscreen setting."""

from shimmer.settings.fullscreen import FullscreenToggleButton


def test_fullscreen_setting(run_gui):
    """A toggle button should be shown which controls the fullscreen setting."""
    fullscreen_control = FullscreenToggleButton()
    assert run_gui(test_fullscreen_setting, fullscreen_control)

"""Tests for the screen resolution setting."""

from shimmer.settings.resolution import ResolutionCycleButton


def test_resolution_cycled(run_gui):
    """A button should be shown which cycles through screen resolutions."""
    resolution_control = ResolutionCycleButton()

    assert run_gui(test_resolution_cycled, resolution_control)

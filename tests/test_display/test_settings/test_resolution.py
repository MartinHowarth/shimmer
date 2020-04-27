"""Tests for the screen resolution setting."""

from shimmer.settings.resolution import ResolutionDropDownMenu


def test_resolution_drop_down_menu(run_gui):
    """A drop down menu of screen resolutions should control the screen resolution."""
    # TODO fix drop down not appearing at all!
    resolution_control = ResolutionDropDownMenu()
    # Ensure there is enough space to expand the menu.
    resolution_control.position = 0, 300

    assert run_gui(test_resolution_drop_down_menu, resolution_control)

"""Tests for the vsync setting."""

from shimmer.settings.vsync import VsyncToggleButton


def test_vsync_setting(run_gui):
    """
    A toggle button should be shown which controls the vsync setting.
    When enabled, the frame rate should match your monitor refresh rate. Otherwise it should
    be unlimited.
    """
    vsync_control = VsyncToggleButton()

    assert run_gui(test_vsync_setting, vsync_control)

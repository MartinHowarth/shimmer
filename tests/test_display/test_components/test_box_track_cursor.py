"""Test a Box that tracks the cursor."""

from shimmer.display.data_structures import Color
from shimmer.display.components.box_track_cursor import (
    BoxTrackCursor,
    BoxTrackCursorDefinition,
)


def test_box_track_cursor(run_gui):
    """A grey box should follow the cursor, with an offset to the top-right."""
    box = BoxTrackCursor(
        BoxTrackCursorDefinition(
            width=200, height=100, offset=(30, 10), background_color=Color(40, 40, 40)
        )
    )
    assert run_gui(test_box_track_cursor, box)

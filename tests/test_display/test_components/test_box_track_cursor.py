"""Test a Box that tracks the cursor."""

from shimmer.components.box_track_cursor import (
    BoxTrackCursor,
    BoxTrackCursorDefinition,
)
from shimmer.data_structures import Color


def test_box_track_cursor(run_gui):
    """A grey box should follow the cursor, with an offset to the top-right."""
    box = BoxTrackCursor(
        BoxTrackCursorDefinition(
            width=200, height=100, offset=(30, 10), background_color=Color(40, 40, 40)
        )
    )
    assert run_gui(test_box_track_cursor, box)

"""Tests for the alignment module."""

import pytest

from shimmer.alignment import CenterCenter, RightBottom, LeftTop


@pytest.mark.parametrize(
    "anchor,exp_width,exp_height",
    [(CenterCenter, 50, 50), (RightBottom, 100, 0), (LeftTop, 0, 100)],
)
def test_get_coord_in_rect(anchor, exp_width, exp_height):
    """Test PositionalAnchor.get_coord_in_rect method."""
    assert anchor.get_coord_in_rect(100, 100) == (exp_width, exp_height)

"""Tests for the helper functions."""

from pyglet.window.key import MOD_SHIFT, MOD_CTRL, MOD_ALT, MOD_NUMLOCK

from shimmer.display.helpers import bitwise_contains, bitwise_add, bitwise_remove


def test_bitwise_add(subtests):
    """Test that the bitwise_add function works as intended."""
    assert bitwise_add(MOD_SHIFT, MOD_CTRL) == 3
    assert bitwise_add(MOD_CTRL, MOD_SHIFT) == 3
    assert bitwise_add(MOD_SHIFT, MOD_ALT) == 5
    assert bitwise_add(MOD_SHIFT, bitwise_add(MOD_CTRL, MOD_ALT)) == 7

    with subtests.test("Adding to itself results in itself"):
        assert bitwise_add(MOD_SHIFT, MOD_SHIFT) == MOD_SHIFT


def test_bitwise_remove(subtests):
    """Test that the bitwise_remove function works as intended."""
    shift_ctrl = bitwise_add(MOD_SHIFT, MOD_CTRL)

    with subtests.test("Removing one mask from another works."):
        assert bitwise_remove(shift_ctrl, MOD_SHIFT) == MOD_CTRL
        assert bitwise_remove(shift_ctrl, MOD_CTRL) == MOD_SHIFT

    with subtests.test("Removing a bit that isn't contained results in no change."):
        assert bitwise_remove(shift_ctrl, MOD_ALT) == shift_ctrl

    with subtests.test("Can remove a single mask to get 0."):
        assert bitwise_remove(MOD_SHIFT, MOD_SHIFT) == 0


def test_bitwise_contains(subtests):
    """Test that the bitwise_contains function works as intended."""
    shift_alt = bitwise_add(MOD_SHIFT, MOD_ALT)

    with subtests.test("Comparing single bits works."):
        assert bitwise_contains(MOD_SHIFT, MOD_SHIFT) is True
        assert bitwise_contains(MOD_SHIFT, MOD_CTRL) is False

    with subtests.test("A single bit matches a multi-bit mask."):
        assert bitwise_contains(shift_alt, MOD_SHIFT) is True
        assert bitwise_contains(shift_alt, MOD_CTRL) is False
        assert bitwise_contains(shift_alt, MOD_ALT) is True

    with subtests.test("A multi-bit mask matches a single bit"):
        assert bitwise_contains(MOD_SHIFT, shift_alt) is True

    with subtests.test("A multi-bit mask matches a multi-bit mask."):
        assert bitwise_contains(shift_alt, shift_alt) is True
        shift_ctrl = bitwise_add(MOD_SHIFT, MOD_CTRL)
        assert bitwise_contains(shift_alt, shift_ctrl) is True

    with subtests.test(
        "A multi-bit mask with no overlap does not match another multi-bit mask"
    ):
        alt_numlock = bitwise_add(MOD_ALT, MOD_NUMLOCK)
        assert bitwise_contains(shift_ctrl, alt_numlock) is False

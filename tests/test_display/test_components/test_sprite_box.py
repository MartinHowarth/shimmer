"""Test module for SpriteBox."""

from pathlib import Path

import pyglet
import pytest

from shimmer.components.sprite_box import SpriteBox, SpriteBoxDefinition


@pytest.fixture
def cat_path_relative(cat_path: Path) -> Path:
    """Path to kitten.png relative to the current working directory."""
    cwd = Path.cwd()
    relative_path = str(cat_path).replace(str(cwd), "")
    relative_path = relative_path.lstrip("\\/")
    return Path(relative_path)


def test_sprite_box_native_size(run_gui, cat_image, subtests):
    """Test SpriteBox without scaling the image."""
    layer = SpriteBox(SpriteBoxDefinition(image=cat_image))

    with subtests.test(
        f"Check that the size of the SpriteBox matches the original image size."
    ):
        assert layer.rect.width == 577
        assert layer.rect.height == 433

    assert run_gui(test_sprite_box_native_size, layer)


def test_sprite_box_scaled(run_gui, cat_image):
    """Test SpriteBox scaled and stretched to 100x200."""
    layer = SpriteBox(SpriteBoxDefinition(image=cat_image, width=100, height=200))

    assert run_gui(test_sprite_box_scaled, layer)


def test_sprite_box_loading_mechanisms(run_gui, subtests, cat_path, cat_path_relative):
    """Test the various methods of specifying which image to use for the Sprite."""
    with subtests.test("Test loading by absolute path."):
        sprite = SpriteBox(SpriteBoxDefinition(image=cat_path, width=300, height=300))
        assert run_gui(test_sprite_box_loading_mechanisms, sprite)

    with subtests.test("Test loading by relative path to executing dir."):
        sprite = SpriteBox(
            SpriteBoxDefinition(image=cat_path_relative, width=200, height=200)
        )
        assert run_gui(test_sprite_box_loading_mechanisms, sprite)

    with subtests.test("Test loading from binary IO."):
        with open(str(cat_path), "rb") as fi:
            sprite = SpriteBox(SpriteBoxDefinition(image=fi, width=400, height=400))
            assert run_gui(test_sprite_box_loading_mechanisms, sprite)

    with subtests.test("Test loading by pre-loaded pyglet image."):
        with open(str(cat_path), "rb") as fi:
            image = pyglet.image.load(filename=cat_path.name, file=fi)
        sprite = SpriteBox(SpriteBoxDefinition(image=image, width=100, height=100))
        assert run_gui(test_sprite_box_loading_mechanisms, sprite)

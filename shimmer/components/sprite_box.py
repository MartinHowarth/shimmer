"""
Module defining a Box that contains a cocos Sprite.

This allows display of static images and animated sprites.
"""

from dataclasses import dataclass
from io import IOBase
from pathlib import Path
from typing import Union, Optional

import pyglet
from pyglet.image import AbstractImage, Animation

from cocos.sprite import Sprite
from .box import Box, BoxDefinition

ANIMATION_SUFFIXES = [".gif"]


def load_image_from_path(path: Path) -> Union[AbstractImage, Animation]:
    """
    Load an image found at path into a pyglet object.

    If the image has a ".gif" extension then it will be loaded as an Animation object.

    :param path: Path to the
    :return: The pyglet object holding the loaded image or animation.
    """
    if path.suffix in ANIMATION_SUFFIXES:
        load_func = pyglet.image.load_animation
    else:
        load_func = pyglet.image.load
    with open(str(path), "rb") as fi:
        return load_func(filename=path.name, file=fi)


@dataclass(frozen=True)
class SpriteBoxDefinition(BoxDefinition):
    """
    Definition of a Box that contains a cocos Sprite.

    The texture of the Sprite is stored on this definition and therefore can be used by multiple
    instances of SpriteBox to save on resources and loading times.

    :param image: Image to display in the box. Possible types are:
        - str: name of the image resource loaded into pyglet
        - Path: path to the image file. If a relative path is given, then it is relative to the
                current working directory.
        - IOBase: Binary stream containing image data.
                  For example, from `open(image_path, "rb")`.
        - AbstractImage: An instance of a pyglet AbstractImage subclass.
        - Animation: An instance of a pyglet Animation.
    """

    image: Optional[Union[str, Path, IOBase, AbstractImage, Animation]] = None

    def __post_init__(self):
        """Handle loading the image as needed upon creation."""
        actual_image: Union[AbstractImage, Animation]

        if self.image is None:
            raise ValueError(f"`image` cannot be None for {self.__class__.__name__}.")

        if isinstance(self.image, str):
            actual_image = pyglet.resource.image(self.image)
        elif isinstance(self.image, Path):
            if self.image.is_absolute():
                actual_image = load_image_from_path(self.image)
            else:
                path = Path.cwd() / self.image
                actual_image = load_image_from_path(path)
        elif isinstance(self.image, IOBase):
            # Need a name for the image to be stored in pyglet resource as.
            # There isn't a useful name associated with a stream object, so just use its ID.
            actual_image = pyglet.image.load(str(id(self.image)), file=self.image)
        else:
            actual_image = self.image

        # Have to use __setattr__ to get around `frozen=True`.
        object.__setattr__(self, "image", actual_image)


class SpriteBox(Box):
    """A Box that contains a cocos Sprite."""

    definition_type = SpriteBoxDefinition

    def __init__(self, definition: SpriteBoxDefinition):
        """Creates a new SpriteBox."""
        super(SpriteBox, self).__init__(definition)
        self.definition: SpriteBoxDefinition = self.definition
        self.sprite = Sprite(self.definition.image, anchor=(0, 0))
        self._update_sprite_scale()
        self.add(self.sprite)

    def _update_sprite_scale(self):
        """Scale the underlying Sprite such that it fits the size of this Box."""
        if self.rect.width == 0 or self.rect.height == 0:
            self.sprite.scale_x = 1
            self.sprite.scale_y = 1
            return

        scale_x = self.rect.width / self.sprite.width
        scale_y = self.rect.height / self.sprite.height

        self.sprite.scale_x = scale_x
        self.sprite.scale_y = scale_y

    def on_size_change(self):
        """When the size of this Box changes, update the Sprite to fit the new size."""
        self._update_sprite_scale()
        super(SpriteBox, self).on_size_change()

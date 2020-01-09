"""Mock versions of the graphical dependencies of cocos."""

import cocos


class MockDirector(cocos.director.Director):
    """A Mock of the cocos Director."""

    def set_alpha_blending(self, on=True):
        """Ignore alpha blending."""

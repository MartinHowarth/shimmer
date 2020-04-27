"""A Box that only displays a rectangular portion of its children."""
from typing import Tuple, Optional

from pyglet import gl

import cocos
from .box import BoxDefinition, Box, DynamicSizeBehaviourEnum
from .mouse_box import MouseBox


class ViewPortBox(Box):
    """
    A box that provides a movable view port onto its children.

    Children of this ViewPortBox will only be visible within the bounds
    of the `self.viewport` child of this box.

    This ViewPortBox has a special child which defines the actual visual
    area that can be seen of its siblings (the other children of this ViewPortBox).

    This allows the viewable area to be moved around independently from the
    other children on this box.

    Use `add` to add children that should be made visible within the viewport.

    Use `add_to_viewport` to add children to the viewport box itself. For example
    this would be used to add a DraggableBox to the viewport so that it can be
    moved around.
    """

    def __init__(self, definition: BoxDefinition):
        """Create a new ViewPortBox."""
        super(ViewPortBox, self).__init__(
            BoxDefinition(dynamic_size_behaviour=DynamicSizeBehaviourEnum.fit_children)
        )

        # Create the actual viewport as a child.
        self.viewport = Box(definition)
        # Make the viewport be on top so it (and its children) get events before
        # the other children. For example, this enables the viewport to be
        # draggable over other children who would otherwise consume the mouse events.
        self.add(self.viewport, z=100)

        # Init variables needed for interacting with GL scissor.
        self._old_scissor_enabled: bool = False
        self._old_scissor_args: Tuple[int, int, int, int] = (gl.GLint * 4)()

    def set_size(self, width: Optional[int], height: Optional[int]) -> None:
        """Set the size of the viewport."""
        self.trace(f"Setting viewport size: {width=}, {height=}")
        self.viewport.set_size(width, height)

    def add(
        self,
        child: cocos.cocosnode.CocosNode,
        z: int = 0,
        name: Optional[str] = None,
        no_resize: bool = False,
    ) -> None:
        """
        Add a child to this box.

        The child will only be visible when within the bounds of the viewport.

        See `Box.add` for parameter details.
        """
        super(ViewPortBox, self).add(child, z, name, no_resize)

        def set_additional_coord_check_fn(node: cocos.cocosnode.CocosNode):
            # If the child (and grandchildren etc.) would handle mouse events then add an
            # additional check to ensure that the event is only handled when the mouse is
            # inside the view port.
            # This prevents the user interacting with an button that is invisible!
            if isinstance(node, MouseBox):
                node.additional_coord_check_fn = self.viewport.contains_coord

        child.walk(set_additional_coord_check_fn)

    def add_to_viewport(
        self,
        child: cocos.cocosnode.CocosNode,
        z: int = 0,
        name: Optional[str] = None,
        no_resize: bool = False,
    ) -> None:
        """
        Add a child to the actual viewport.

        See `self.add` for parameter details.
        """
        self.viewport.add(child, z, name, no_resize)

    def apply_gl_scissor(self):
        """Set the OpenGL scissor test state."""
        # Record current scissor state so we can restore to it later.
        self._old_scissor_enabled = gl.glIsEnabled(gl.GL_SCISSOR_TEST)
        # Read the current scissor state and write it into `self._old_scissor_args`
        gl.glGetIntegerv(gl.GL_SCISSOR_BOX, self._old_scissor_args)
        # Set our scissor
        if not self._old_scissor_enabled:
            gl.glEnable(gl.GL_SCISSOR_TEST)

        # Get the viewport in coordinates relative to the screen which
        # is the coordinate system that pyglet works in.
        viewport_world_rect = self.viewport.world_rect
        if cocos.director.director.autoscale:
            # Because we're working directly with pyglet here we have to handle autoscaling
            # ourselves which the director would normally handle.
            w, h = cocos.director.director.get_window_size()
            sx = cocos.director.director._usable_width / w
            sy = cocos.director.director._usable_height / h
            scissor_args = (
                int(viewport_world_rect.x * sx + cocos.director.director._offset_x),
                int(viewport_world_rect.y * sy + cocos.director.director._offset_y),
                int(viewport_world_rect.width * sx),
                int(viewport_world_rect.height * sy),
            )
        else:
            scissor_args = (
                int(viewport_world_rect.x),
                int(viewport_world_rect.y),
                int(viewport_world_rect.width),
                int(viewport_world_rect.height),
            )

        gl.glScissor(*scissor_args)

    def reset_gl_scissor(self):
        """Reset the OpenGl scissor state to the previous value."""
        gl.glScissor(*self._old_scissor_args)
        if not self._old_scissor_enabled:
            gl.glDisable(gl.GL_SCISSOR_TEST)

    def visit(self):
        """Apply the OpenGL scissor before the children are drawn, and reset it afterwards."""
        self.apply_gl_scissor()
        super().visit()
        self.reset_gl_scissor()

    def box_is_visible(self, box: Box) -> bool:
        """
        Return True if the given box is visible within the viewport area.

        Note that the Box must be a child (or grandchild, etc.) of this
        ViewPortBox to be affected by the viewport.
        """
        return box.world_rect.intersects(self.viewport.world_rect)

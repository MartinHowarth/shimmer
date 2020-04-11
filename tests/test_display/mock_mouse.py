"""A mock mouse for use in testing."""

from typing import Optional, Tuple

from pyglet.window.mouse import LEFT

from shimmer.components.box import Box


class MockMouse:
    """
    A mock of a physical mouse.

    Used to simulate mouse events in tests.
    """

    def box_center_in_world_coord(self, box: Box) -> Tuple[int, int]:
        """Get the center of the box in world coordinate space."""
        return box.point_to_world(box.rect.center)

    def press(
        self,
        box: Box,
        position: Optional[Tuple[int, int]] = None,
        buttons: int = LEFT,
        modifiers: int = 0,
    ) -> Optional[bool]:
        """
        Send an on_mouse_press event in the centre of the given Box.

        If the Box does not define an `on_mouse_press` then this has no effect.

        :param box: Box to send the event to.
        :param position: Coordinate to click the mouse at.
        :param buttons: Mouse button to simulate. Defaults to Left.
        :param modifiers: Keyboard modifiers to include.
        :return: True if the event was handled, None if it wasn't.
        """
        if position is None:
            position = self.box_center_in_world_coord(box)
        if hasattr(box, "on_mouse_press"):
            return box.on_mouse_press(*position, buttons, modifiers)
        return None

    def release(
        self,
        box: Box,
        position: Optional[Tuple[int, int]] = None,
        buttons: int = LEFT,
        modifiers: int = 0,
    ) -> Optional[bool]:
        """
        Send an on_mouse_release event in the centre of the given Box.

        If the Box does not define an `on_mouse_release` then this has no effect.

        :param box: Box to send the event to.
        :param position: Coordinate to click the mouse at.
        :param buttons: Mouse button to simulate. Defaults to Left.
        :param modifiers: Keyboard modifiers to include.
        :return: True if the event was handled, None if it wasn't.
        """
        if position is None:
            position = self.box_center_in_world_coord(box)
        if hasattr(box, "on_mouse_release"):
            return box.on_mouse_release(*position, buttons, modifiers)
        return None

    def move(
        self,
        box: Box,
        start: Optional[Tuple[int, int]] = None,
        end: Optional[Tuple[int, int]] = None,
    ) -> Optional[bool]:
        """
        Send an on_mouse_motion event in the centre of the given Box.

        If the Box does not define an `on_mouse_motion` then this has no effect.

        :param box: Box to send the event to.
        :param start: Coordinates to start the motion from. Defaults to the center of the box.
        :param end: Coordinates to end the motion at. Defaults to (1, 1) away from the start.
        :return: True if the event was handled, None if it wasn't.
        """
        if start is None:
            start = self.box_center_in_world_coord(box)
        if end is None:
            end = start[0] + 1, start[1] + 1

        dx = end[0] - start[0]
        dy = end[1] - start[1]

        if hasattr(box, "on_mouse_motion"):
            return box.on_mouse_motion(*end, dx, dy)
        return None

    def drag(
        self,
        box: Box,
        start: Optional[Tuple[int, int]] = None,
        end: Optional[Tuple[int, int]] = None,
        buttons: int = LEFT,
        modifiers: int = 0,
    ) -> Optional[bool]:
        """
        Send an on_mouse_drag event in the centre of the given Box.

        If the Box does not define an `on_mouse_drag` then this has no effect.

        :param box: Box to send the event to.
        :param start: Coordinates to start the motion from. Defaults to the center of the box.
        :param end: Coordinates to end the motion at. Defaults to (1, 1) away from the start.
        :param buttons: Mouse button to simulate. Defaults to Left.
        :param modifiers: Keyboard modifiers to include.
        :return: True if the event was handled, None if it wasn't.
        """
        if start is None:
            start = self.box_center_in_world_coord(box)
        if end is None:
            end = start[0] + 1, start[1] + 1

        dx = end[0] - start[0]
        dy = end[1] - start[1]

        if hasattr(box, "on_mouse_drag"):
            return box.on_mouse_drag(*end, dx, dy, buttons, modifiers)
        return None

    def click(self, box: Box, buttons: int = LEFT, modifiers: int = 0) -> None:
        """
        Simulate a mouse click and release in the centre of the given Box.

        :param box: Box to send the event to.
        :param buttons: Mouse button to simulate. Defaults to Left.
        :param modifiers: Keyboard modifiers to include.
        """
        self.press(box, buttons=buttons, modifiers=modifiers)
        self.release(box, buttons=buttons, modifiers=modifiers)

    def move_onto(self, box: Box) -> Optional[bool]:
        """
        Simulate a mouse motion from not on the box, to onto the box.

        :param box: Box to move the mouse onto.
        :return: True if the event was handled, None if it wasn't.
        """
        end = self.box_center_in_world_coord(box)
        start = end[0] - box.rect.width, end[1] - box.rect.height

        # Move the mouse slightly outside the box to simulate reality of moving onto something.
        self.move(box, start)
        # Then move the mouse fully onto the box.
        return self.move(box, start, end)

    def move_off(self, box: Box) -> Optional[bool]:
        """
        Simulate a mouse motion from on the box, to off the box.

        :param box: Box to move the mouse onto.
        :return: True if the event was handled, None if it wasn't.
        """
        start = self.box_center_in_world_coord(box)
        end = start[0] - box.rect.width, start[1] - box.rect.height

        # Move the mouse slightly inside the box to simulate realist of moving off something.
        self.move(box, start)
        # Then move the mouse fully off the box.
        return self.move(box, start, end)

    def drag_onto(
        self, box: Box, buttons: int = LEFT, modifiers: int = 0
    ) -> Optional[bool]:
        """
        Simulate a mouse drag from not on the box, to onto the box.

        :param box: Box to move the mouse onto.
        :param buttons: Mouse button to simulate. Defaults to Left.
        :param modifiers: Keyboard modifiers to include.
        :return: True if the event was handled, None if it wasn't.
        """
        end = self.box_center_in_world_coord(box)
        start = end[0] - box.rect.width, end[1] - box.rect.height

        # Move the mouse slightly outside the box to pretend were moving into it.
        self.drag(box, start, buttons=buttons, modifiers=modifiers)
        # Then move the mouse fully onto the box.
        return self.drag(box, start, end, buttons=buttons, modifiers=modifiers)

    def drag_off(
        self, box: Box, buttons: int = LEFT, modifiers: int = 0
    ) -> Optional[bool]:
        """
        Simulate a mouse drag from on the box, to off the box.

        :param box: Box to move the mouse onto.
        :param buttons: Mouse button to simulate. Defaults to Left.
        :param modifiers: Keyboard modifiers to include.
        :return: True if the event was handled, None if it wasn't.
        """
        start = self.box_center_in_world_coord(box)
        end = start[0] - box.rect.width, start[1] - box.rect.height

        # Drag the mouse slightly inside the box to pretend were moving into it.
        self.drag(box, start, buttons=buttons, modifiers=modifiers)
        # Then drag the mouse fully off the box.
        return self.drag(box, start, end, buttons=buttons, modifiers=modifiers)

    def click_and_drag(
        self,
        box: Box,
        start: Tuple[int, int],
        end: Tuple[int, int],
        buttons: int = LEFT,
        modifiers: int = 0,
    ) -> None:
        """
        Click the mouse, drag from start to end, then release the mouse.

        :param box: Box to send the event to.
        :param start: Coordinates to start the motion from.
        :param end: Coordinates to end the motion at.
        :param buttons: Mouse button to simulate. Defaults to Left.
        :param modifiers: Keyboard modifiers to include.
        """
        self.press(box, start, buttons=buttons, modifiers=modifiers)
        self.drag(box, start, end, buttons=buttons, modifiers=modifiers)
        self.release(box, end, buttons=buttons, modifiers=modifiers)

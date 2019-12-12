import cocos


class InputHandler(cocos.layer.Layer):
    is_event_handler = True

    def __init__(self, mouse_press_callback):
        super(InputHandler, self).__init__()
        self.mpc = mouse_press_callback

    def on_mouse_press(self, x, y, buttons, modifiers):
        """This function is called when any mouse button is pressed

        (x, y) are the physical coordinates of the mouse
        'buttons' is a bitwise or of pyglet.window.mouse constants LEFT, MIDDLE, RIGHT
        'modifiers' is a bitwise or of pyglet.window.key modifier constants
           (values like 'SHIFT', 'OPTION', 'ALT')
        """
        x, y = cocos.director.director.get_virtual_coordinates(x, y)
        self.mpc(x, y)

"""Example of a simple shooting game."""
import math
import os
import random
from pathlib import Path
from typing import Callable, List

import cocos
from cocos.actions.base_actions import Action, sequence
from cocos.actions.instant_actions import CallFunc
from cocos.actions.interval_actions import MoveTo
from cocos.euclid import Vector2
from shimmer.display.alignment import LeftTop
from shimmer.display.components.box import Box, BoxDefinition, DynamicSizeBehaviourEnum
from shimmer.display.components.mouse_box import MouseBox, MouseBoxDefinition
from shimmer.display.components.sprite_box import SpriteBoxDefinition, SpriteBox
from shimmer.display.primitives import Point2d, Color
from shimmer.display.widgets.text_box import TextBoxDefinition, TextBox

ASSETS_PATH = Path(os.path.dirname(__file__)) / "assets"


def create_cloud_definitions() -> List[SpriteBoxDefinition]:
    """Create a list of SpriteBoxDefinitions for each type of cloud asset image."""
    clouds_dir = ASSETS_PATH / "clouds"
    cloud_definitions = []
    for cloud_path in clouds_dir.iterdir():
        scale = random.uniform(0.4, 2)
        cloud_definitions.append(
            SpriteBoxDefinition(image=cloud_path, width=int(40 * scale))
        )
    return cloud_definitions


class Target(MouseBox):
    """
    A target that can be shot at.

    This is an example of a custom shimmer MouseBox, which handles determining whether
    a mouse event happens within its boundaries.
    """

    def __init__(self, on_shot: Callable):
        """
        Constructor for Target.

        :param on_shot: Function taking no arguments that is called when this target is
            clicked on.
        """
        definition = MouseBoxDefinition(width=30, height=30, on_press=self.when_shot,)
        super(Target, self).__init__(definition)
        self.on_shot = on_shot

        image_definition = SpriteBoxDefinition(
            image=ASSETS_PATH / "target.png",
            dynamic_size_behaviour=DynamicSizeBehaviourEnum.match_parent,
        )
        self.add(SpriteBox(image_definition))

    def when_shot(self, *_, **__):
        """Callback when the target is shot."""
        self.on_shot()
        self.kill()


class RandomMotionAction(Action):
    """
    Action that randomly moves the target around within the bounds of its parent Box.

    This is an example of a custom cocos Action.
    """

    def __init__(self, speed: float = 10):
        """
        Constructor for RandomMotionAction.

        :param speed: The speed, in pixels per second, of the motion.
        """
        super(RandomMotionAction, self).__init__()
        self._speed = speed or 1  # Use "or 1" to prevent speed being 0.

        self._max_x, self._max_y = (0, 0)
        self._target_location: Point2d = (0, 0)
        self._unit_vector: Point2d = (0, 0)
        self._t_arrival_s: float = 0

    def start(self):
        """
        Choose the first location to move the target to.

        This is called when this action is first applied to a cocosnode.
        """
        if isinstance(self.target.parent, Box):
            self._max_x = self.target.parent.rect.width
            self._max_y = self.target.parent.rect.height
        else:
            self._max_x, self._max_y = cocos.director.director.get_window_size()
        self.choose_next_location()

    def choose_next_location(self):
        """Choose the next location for this target to move to."""
        self._elapsed = 0.0
        x0, y0 = self.target.position
        x1 = random.randint(0, self._max_x)
        y1 = random.randint(0, self._max_y)
        dx = x1 - x0
        dy = y1 - y0
        norm = math.hypot(dx, dy)
        self._t_arrival_s = norm / self._speed
        self._unit_vector = (dx / norm, dy / norm)

    def step(self, dt: float) -> None:
        """
        Move this target based on its speed on each frame of the game.

        Called by the pyglet event loop every frame.

        :param dt: The time elapsed since the last call to `step`.
        """
        self._elapsed += dt
        if self._elapsed > self._t_arrival_s:
            # Use time elapsed to determine whether the target has arrived at the destination
            # because determining by position would be imprecise.
            self.choose_next_location()
        dx = self._unit_vector[0] * dt * self._speed
        dy = self._unit_vector[1] * dt * self._speed
        self.target.position += Vector2(dx, dy)


class RandomJumpingAction(Action):
    """
    Action which moves the target to a random position instantaneously.

    This is an example of a custom cocos Action.
    """

    def __init__(self, jump_interval_s: float):
        """
        Constructor for RandomJumpingAction.

        :param jump_interval_s: Seconds between jumps for the target.
        """
        super(RandomJumpingAction, self).__init__()
        self._jump_interval_s = jump_interval_s
        self._max_x, self._max_y = (0, 0)

    def start(self):
        """
        Set up this action when it is started.

        This is called when this action is first applied to a cocosnode.
        """
        if isinstance(self.target.parent, Box):
            self._max_x = self.target.parent.rect.width
            self._max_y = self.target.parent.rect.height
        else:
            self._max_x, self._max_y = cocos.director.director.get_window_size()

        self.do_jump()

    def do_jump(self):
        """Move the target to a random location."""
        x = random.randint(0, self._max_x)
        y = random.randint(0, self._max_y)
        self.target.position = (x, y)

    def step(self, dt: float) -> None:
        """
        Each frame, move the target if the jump interval has passed.

        Called by the pyglet event loop every frame.

        :param dt: The time elapsed since the last call to `step`.
        """
        self._elapsed: float
        self._elapsed += dt
        if self._elapsed > self._jump_interval_s:
            self._elapsed = 0
            self.do_jump()


class Scoreboard(TextBox):
    """
    Scoreboard to display the current score.

    This an example of a custom shimmer TextBox, which allows easy display and updating
    of text.
    """

    def __init__(self):
        """Constructor for Scoreboard."""
        definition = TextBoxDefinition(
            text="Score: 0", background_color=Color(50, 170, 50)
        )
        super(Scoreboard, self).__init__(definition)
        self.score: int = 0

    def increment(self):
        """Increment the current score by 1."""
        self.score += 1
        self.set_text(f"Score: {self.score}")


class BackgroundBox(Box):
    """
    A grassy background with clouds floating by.

    Matches the size of its parent Box.
    """

    def __init__(self):
        """Create a new BackgroundBox."""
        # Set the definition to match the size of its parent Box.
        definition = BoxDefinition(
            dynamic_size_behaviour=DynamicSizeBehaviourEnum.match_parent,
        )
        super(BackgroundBox, self).__init__(definition)
        self.elapsed_time: float = 0

        # Add the static terrain SpriteBox.
        terrain_definition = SpriteBoxDefinition(
            image=ASSETS_PATH / "grass_background.png",
            height=150,
            dynamic_size_behaviour=DynamicSizeBehaviourEnum.match_parent,
        )
        self.terrain = SpriteBox(terrain_definition)
        self.add(self.terrain)

        # Set the "update" function to be called every frame.
        # This will be used to create clouds at random intervals.
        self.schedule(self.update)

    def create_cloud(self):
        """Create a cloud and set it in motion across the background."""
        cloud_travel_time_s = 20

        # Choose a random cloud definition and create a sprite using that definition.
        definition = random.choice(create_cloud_definitions())
        cloud = SpriteBox(definition)
        self.add(cloud)

        # Set starting position
        cloud_starting_height = random.randint(self.rect.height // 4, self.rect.height)
        cloud.position = (-cloud.rect.width, cloud_starting_height)

        # Use cocos Actions to control the cloud movement
        # and then remove the cloud from the game.
        cloud_action = sequence(
            MoveTo((self.rect.width, cloud_starting_height), cloud_travel_time_s),
            CallFunc(cloud.kill),
        )
        cloud.do(cloud_action)

    def update(self, dt: float) -> None:
        """
        Create clouds are random intervals.

        Called on every frame.
        """
        self.elapsed_time += dt
        if self.elapsed_time > 1:
            if random.random() > 0.7:
                self.create_cloud()
            self.elapsed_time = 0


class Manager(Box):
    """
    Game manager.

    This is an example of a custom shimmer Box, which is the base class of shimmer objects.
    This provides an area for the targets to move around within, while also providing
    base cocosnode functionality.
    """

    def __init__(self, num_targets: int):
        """
        Constructor for Manager.

        :param num_targets: Number of targets to exist at once.
        """
        definition = BoxDefinition(
            width=cocos.director.director.get_window_size()[0],
            height=cocos.director.director.get_window_size()[1],
            background_color=Color(80, 80, 140),
        )
        super(Manager, self).__init__(definition)

        # Create a background for the scene.
        # Add this first so it appears behind everything we add later.
        self.background = BackgroundBox()
        self.add(self.background)

        # Create the scoreboard and put it in the top left.
        self.scoreboard = Scoreboard()
        self.add(self.scoreboard)
        self.scoreboard.align_anchor_with_other_anchor(self, LeftTop)

        # Create the initial number of targets.
        for num in range(num_targets):
            self.create_target()

    def create_target(self):
        """Create a new target and choose a random movement type for it."""
        target = Target(self.target_shot)
        self.add(target)

        # Randomise starting position of the target.
        x = random.randint(0, self.rect.width)
        y = random.randint(0, self.rect.width)
        target.position = (x, y)

        action = random.choice((RandomJumpingAction(1.5), RandomMotionAction(150)))
        target.do(action)

    def target_shot(self):
        """Callback when a target is shot."""
        self.scoreboard.increment()
        self.create_target()


def main():
    """Run the Shooter game."""
    cocos.director.director.init()
    manager = Manager(num_targets=10)
    scene = cocos.scene.Scene(manager)
    cocos.director.director.run(scene)


if __name__ == "__main__":
    main()

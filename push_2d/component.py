"""Simple physics simulator for the pushing object task."""

from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING

import pygame
import pymunk
import pymunk.pygame_util

if TYPE_CHECKING:
    from .types import CircleParameters, SpaceParameters


@dataclasses.dataclass
class Circle:
    """
    A class to represent a circle object with physics properties.

    Methods
    -------
    __post_init__()
        This method is called after the object has been initialized
        and creates a pymunk physics body and shape for the circle with a
        given position, radius, and color.
    """

    params: CircleParameters

    def __post_init__(self) -> None:
        """Create Body and Shape for the circle and set its properties."""
        self.body = pymunk.Body()
        self.body.position = self.params.position
        self.shape = pymunk.Circle(self.body, self.params.radius)
        self.shape.mass = 1.0
        self.shape.color = pygame.Color(self.params.color)
        self.shape.elasticity = 1.0


class Space(pymunk.Space):
    """
    A class that represents a 2D space simulation.

    Methods
    -------
    add_circle(circle: Circle) -> None
        Add a circular object to the simulation space along with its
        supporting pivot and gear constraints.
    clear() -> None
        Remove all objects from the simulation space.
    render() -> None
        Apply one step of the physics simulation, clearing the screen
        and rendering the updated state of the simulation.
    """

    def __init__(self, params: SpaceParameters) -> None:
        """
        Initialize Space.

        - Pygame screen
        - Physics space
        - Rendering options
        """
        super().__init__()
        self.width = params.width
        self.height = params.height
        self.fps = params.fps
        self.color = params.color
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        self.draw_options = pymunk.pygame_util.DrawOptions(self.screen)
        self.draw_options.flags = pymunk.SpaceDebugDrawOptions.DRAW_SHAPES

    def add_circle(self, circle: Circle) -> None:
        """
        Add a circular object to the simulation space.

        And Connect it to a pivot and gear joint for more realistic physics.

        Parameters
        ----------
        circle : Circle
            The circular object to add to the simulation space.
        """
        self.add(circle.body, circle.shape)

        static_body = self.static_body

        pivot = pymunk.PivotJoint(static_body, circle.body, (0, 0), (0, 0))
        self.add(pivot)
        pivot.max_bias = 0  # disable joint correction
        pivot.max_force = 1000  # emulate linear friction

        gear = pymunk.GearJoint(static_body, circle.body, 0.0, 1.0)
        self.add(gear)
        gear.max_bias = 0  # disable joint correction
        gear.max_force = 5000  # emulate angular friction

    def clear(self) -> None:
        """Remove all objects from the simulation space."""
        self.remove(*self.bodies)
        self.remove(*self.constraints)
        self.remove(*self.shapes)

    def render(self) -> None:
        """
        Apply one envornment step.

        includes:
            - One step of the physics simulation
            - Clear the screen
            - Render the updated state of the simulation
        """
        self.screen.fill(self.color)
        self.debug_draw(self.draw_options)
        pygame.display.flip()
        self.step(1 / self.fps)
        self.clock.tick(self.fps)

    def add_segments(self) -> None:
        """Create static segments around the edge to create walls."""

        def wall(a: tuple[int, int], b: tuple[int, int]) -> None:
            wall = pymunk.Segment(self.static_body, a, b, 10)
            wall.elasticity = 1.0
            wall.color = pygame.Color(self.color)
            self.add(wall)

        wall(a=(0, 1), b=(self.width, 1))
        wall(a=(1, 0), b=(1, self.height))
        wall(a=(self.width - 1, 0), b=(self.width - 1, self.height))
        wall(a=(0, self.height - 1), b=(self.width, self.height - 1))
# Copyright 2021 Casey Devet
#
# Permission is hereby granted, free of charge, to any person obtaining a 
# copy of this software and associated documentation files (the "Software"), 
# to deal in the Software without restriction, including without limitation 
# the rights to use, copy, modify, merge, publish, distribute, sublicense, 
# and/or sell copies of the Software, and to permit persons to whom the 
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included 
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS 
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL 
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING 
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
# DEALINGS IN THE SOFTWARE.

################################################################################
#                               GLOBAL VARIABLES
################################################################################

from functools import wraps
import math
import pygame

from pygameplus.painter import *
from pygameplus.screen import get_active_screen

################################################################################
#                                REDRAWMETACLASS
################################################################################

# This function adds a wrapper around a method that will make it so that when
# the method is complete, the active screen will be redraw if the sprite is 
# on that screen.

def add_redraw_to_method (method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        # Get the initial _redraw_on_completion and replace it with False to
        # suppress redraws on intermediate calls
        redraw_on_changes = getattr(self, "_redraw_on_completion", True)
        self._redraw_on_completion = False

        # Call the method.  Before and after, determine if the sprite is on the
        # active screen.
        active_screen = get_active_screen()
        on_screen_before = active_screen is not None and self in active_screen
        method(self, *args, **kwargs)
        on_screen_after = active_screen is not None and self in active_screen

        # Redraw the screen if this is not an intermediate call and if the 
        # sprite is on the screen before/after the method call.
        if redraw_on_changes and (on_screen_before or on_screen_after):
            active_screen.redraw()

        # Reset the _redraw_on_completion flag to the initial value
        self._redraw_on_completion = redraw_on_changes

    return wrapper

# This metaclass is used to create a class that wraps its methods (and/or its 
# parents' methods) using the above functions.  Include lists called
# add_redraw_methods and disable_intermediate_redraw_methods in the class
# definition of a class using this metaclass.  These lists should hold the names
# of the methods to wrapp with add_redraw and disable_intermediate_redraw,
# respectively.

class RedrawMetaClass (type):

    def __new__ (cls, name, bases, class_dict):
        new_class_dict = class_dict.copy()

        # Wrap the methods in add_redraw_methods
        for attr_name in new_class_dict.pop("add_redraw_to", []):
            # Get the attr from the current class definition or from a base class
            attr = None
            if attr_name in new_class_dict:
                attr = new_class_dict[attr_name]
            else:
                for base in bases:
                    if hasattr(base, attr_name):
                        attr = getattr(base, attr_name)
                        break

            # If the attr is callable, simply wrap it
            if callable(attr):
                new_class_dict[attr_name] = add_redraw_to_method(attr)

            # If the attr is a property, wrap the setter
            if isinstance(attr, property):
                setter = add_redraw_to_method(attr.fset)
                new_class_dict[attr_name] = property(attr.fget, setter)

            # NOTE: Any attr in the list that is not a method or property is
            # ignored
        
        return type.__new__(cls, name, bases, new_class_dict)


################################################################################
#                                 TURTLE CLASS
################################################################################

class Turtle (Painter, metaclass=RedrawMetaClass):
    '''
    A Turtle is a special sprite that can move around the screen and make 
    drawings.  The turtle's movements will be animated so that you can see it's
    movements.

    A turtle object includes all of the movement methods of a Sprite and the
    drawing methods of a Painter.
    '''

    # These methods will be changed to redraw the active screen on completion
    add_redraw_to = [
        "add",
        "go_to",
        "turn_to",
        "circle",
        "walk_path",
        "show",
        "hide",
        "end_fill",
        "dot",
        "stamp",
        "write",
        "visible",
        "position",
        "x",
        "y",
        "center_x",
        "center_y",
        "left_edge",
        "right_edge",
        "top_edge",
        "bottom_edge",
        "top_left_corner",
        "bottom_left_corner",
        "top_right_corner",
        "bottom_right_corner",
        "left_edge_midpoint",
        "right_edge_midpoint",
        "top_edge_midpoint",
        "bottom_edge_midpoint",
        "direction",
        "scale_factor",
        "width",
        "height",
        "rotates",
        "tilt",
        "smooth",
        "line_color"
        "fill_color",
        "colors",
        "fill_as_moving"
    ]

    def __init__ (self):
        '''
        Create a Turtle object.
        '''

        Painter.__init__(self, "turtle")

        # The attributes used to animate the turtle
        self.clock = pygame.time.Clock()
        self._frame_rate = 30
        self._speed = 120
        self._step_size = 4
        self._animate = True

        # Set that the turtle image should rotate when the turtle turns and
        # draw incomplete fills on the screen.
        self.rotates = True
        self.fill_as_moving = True

        # Attributes that allow the speed to be maintained over multiple changes
        # to position
        self._pixels_remaining = 4


    ### Animation properties

    @property
    def frame_rate (self):
        '''
        The number of animation frames per second.
        '''

        return self._frame_rate

    @frame_rate.setter
    def frame_rate (self, new_frame_rate):
        '''
        '''

        # Ensure that the speed is a number
        try:
            new_frame_rate = float(new_frame_rate)
        except:
            raise ValueError("The frame rate must be a number!") from None

        # Ensure that the speed is positive
        if new_frame_rate <= 0:
            raise ValueError("The frame rate must be positive!")

        # Set the speed and the step size
        self._frame_rate = new_frame_rate
        self._step_size = self._speed / new_frame_rate


    @property
    def speed (self):
        '''
        The current speed (in pixels per second) that the turtle moves on 
        the screen.
        '''

        return self._speed

    @speed.setter
    def speed (self, new_speed):

        # Ensure that the speed is a number
        try:
            new_speed = float(new_speed)
        except:
            raise ValueError("The speed must be a number!") from None

        # Ensure that the speed is positive
        if new_speed <= 0:
            raise ValueError("The speed must be positive!")

        # Set the speed and the step size
        self._speed = new_speed
        self._step_size = new_speed / self._frame_rate


    @property
    def animate (self):
        '''
        Whether or not the turtle's movements will be animated.

        If set to False, movements will happen instantaneously.
        '''

        return self._animate

    @animate.setter
    def animate (self, is_animated):

        self._animate = bool(is_animated)


    ### Overwritten properties
                
    # This will replace the position setter.  It makes it so that, if
    # animation is on, then the turtle will only move _step_size pixels each
    # frame.
    def _set_position (self, new_position):

        # Get the active screen.
        active_screen = get_active_screen()

        # If the animations are turned off, just use the parent class method.
        if not self._animate:
            Painter.position.fset(self, new_position)
            return

        # Create vectors for the start and end positions
        current = pygame.Vector2(self._pos)
        end = pygame.Vector2(new_position)

        # Calculate the distance and a vector representing each step
        distance = current.distance_to(end)
        delta_normal = (end - current).normalize()

        # Each iteration of this loop will move the turtle by at most one step
        while distance > 0:
            # If the distance fits in the current step, do the whole thing
            if distance < self._pixels_remaining:
                Painter.position.fset(self, end)
                self._pixels_remaining -= distance
                distance = 0

            # Otherwise, just do the rest of the current step and take a break
            # until the next frame
            else:
                current += self._pixels_remaining * delta_normal
                Painter.position.fset(self, current)
                distance -= self._pixels_remaining
                self._pixels_remaining = self._step_size
                if active_screen is not None and self in active_screen:
                    active_screen.redraw()
                self.clock.tick(self._frame_rate)

    # Overwrite the position property with the original getter and the new setter
    position = property(Painter.position.fget, _set_position)


    # This will replace the direction setter.  It makes it so that, if
    # animation is on, then the turtle will only turn an arc length of 
    # _step_size pixels each frame.
    def _set_direction (self, direction):

        # Get the active screen.
        active_screen = get_active_screen()

        # Get the Painter direction.setter
        parent_setter = super(Turtle, Turtle).direction.fset

        # If the animations are turned off, just use the parent class method.
        if not self._animate:
            Painter.direction.fset(self, direction)
            return

        # Calculate the arc length of the rotation of the turtle's head
        arc_length = self._scale * 5 * (direction - self._dir) / 18

        # Each iteration of this loop will turn so that it's head moves on an
        # arc that is at most one step
        while arc_length != 0:
            # If the arc_length fits in the current step, do the whole thing
            if abs(arc_length) < self._pixels_remaining:
                Painter.direction.fset(self, direction)
                self._pixels_remaining -= arc_length
                arc_length = 0

            # Otherwise, just do the rest of the current step and take a break
            # until the next frame
            else:
                turn_arc_length = 3.6 * self._pixels_remaining / self._scale
                if arc_length > 0:
                    Painter.direction.fset(self, self._dir + turn_arc_length)
                    arc_length -= self._pixels_remaining
                else:
                    Painter.direction.fset(self, self._dir - turn_arc_length)
                    arc_length += self._pixels_remaining
                self._pixels_remaining = self._step_size
                if active_screen is not None and self in active_screen:
                    active_screen.redraw()
                self.clock.tick(self._frame_rate)

    # Overwrite the direction property with the original getter and the new setter
    direction = property(Painter.direction.fget, _set_direction)


# What is included when importing *
__all__ = [
    "Turtle",
    "Color"
]
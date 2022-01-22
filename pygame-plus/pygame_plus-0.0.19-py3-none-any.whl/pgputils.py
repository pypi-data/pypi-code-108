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

import inspect
import math
import pygame

# The provided collision detection functions that are used in the "touching"
# methods.
collision_functions = {
    "rect": pygame.sprite.collide_rect,
    "circle": pygame.sprite.collide_circle,
    "mask": pygame.sprite.collide_mask
}

# A mapping of string descriptions of the mouse buttons to their associated
# number.
mouse_button_map = {
    "left": 1,
    "center": 2,
    "right": 3,
    "scrollup": 4,
    "scrolldown": 5
}
mouse_button_reverse_map = {
    1: "left",
    2: "center",
    3: "right",
    4: "scrollup",
    5: "scrolldown"
}

# Flips a polygon
def flip_polygon (polygon, x_flip, y_flip):
    def flip_point (point):
        return point.reflect(pygame.Vector2(bool(y_flip), bool(x_flip)))
    return tuple([flip_point(p) for p in polygon])

# Takes a polygon and draws it on a fitted pygame.Surface
def polygon_to_surface (polygon, line_color, fill_color=None, width=1):
    big_x = math.ceil(max([abs(p.x) for p in polygon]))
    big_y = math.ceil(max([abs(p.y) for p in polygon]))
    pygame_points = [pygame.Vector2(big_x + x, big_y - y) for x, y in polygon]
    surface = pygame.Surface((2 * big_x + 1, 2 * big_y + 1), pygame.SRCALPHA)
    if fill_color:
        pygame.draw.polygon(surface, fill_color, pygame_points)
    pygame.draw.polygon(surface, line_color, pygame_points, width)
    return surface

# The built-in polygon images that can be used for Sprites
polygon_images = {
    "turtle": ((16, 0), (14, -2), (10, -1), (7, -4), (9, -7), (8, -9), (5, -6), 
               (1, -7), (-3, -5), (-6, -8), (-8, -6), (-5, -4), (-7, 0), 
               (-5, 4), (-8, 6), (-6, 8), (-3, 5), (1, 7), (5, 6), (8, 9), 
               (9, 7), (7, 4), (10, 1), (14, 2)),
    "square": ((-10, -10), (10, -10), (10, 10), (-10, 10)),
    "circle": ((10 * math.cos(math.pi * x / 180), 10 * math.sin(math.pi * x / 180)) 
               for x in range(360)),
    "triangle": ((10.0, -5.77), (0.0, 11.55), (-10.0, -5.77)),
    "arrow": ((0.0, 0.0), (-9.0, -5.0), (-7.0, 0.0), (-9.0, 5.0)),
    "chevron": ((-7, 10), (2, 10), (7, 0), (2, -10), (-7, -10), (-2, 0))
}

# Convert the points above the pygame.Vector2 objects
for shape, points in polygon_images.items():
    polygon_images[shape] = tuple(pygame.Vector2(p) for p in points)

# Helper function that is used to call a function with the keyword arguments
# given
def call_with_args (func, **args):
    # Loop through the parameters
    signature = inspect.signature(func)
    pos_args = []
    kw_args = {}
    for name, parameter in signature.parameters.items():
        # If it's a positional argument, add it to the list
        if parameter.kind < 2:
            pos_args.append(args.get(name, None))

        # If it's a keyword argument, add it to the dictionary if given
        elif parameter.kind == 3:
            if name in args:
                kw_args[name] = args[name]

        # If a ** argument is provided, put all of the arguments given as
        # keyword arguments
        elif parameter.kind == 4:
            for arg_name, value in args.items():
                if arg_name not in signature.parameters:
                    kw_args[arg_name] = value

    # Call the function
    func(*pos_args, **kw_args)


def load_picture (picture):
    '''
    Load a picture into your program.

    This is useful if you will be changing the picture of a Sprite often.
    You can load the picture once and then change the picture to this
    object.

    This function returns a pygame Surface.
    '''
    return pygame.image.load(picture).convert_alpha()

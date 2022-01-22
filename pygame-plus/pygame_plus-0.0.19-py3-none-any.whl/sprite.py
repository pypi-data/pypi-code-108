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

import math
import pygame

from pygameplus import pgputils
from pygameplus.screen import get_active_screen, to_pygame_coordinates

################################################################################
#                               HELPER FUNCTIONS
################################################################################

def get_dimensions (obj, tilt, scale, rotation):
    if isinstance(obj, pygame.Surface):
        dims = pygame.Vector2(obj.get_size())
    else:
        dims = pygame.Vector2(obj)
    diag_1 = dims * scale
    diag_2 = diag_1.reflect(pygame.Vector2(1, 0))
    angle = tilt + rotation
    diag_1.rotate_ip(angle)
    diag_2.rotate_ip(angle)
    width = max(abs(diag_1.x), abs(diag_2.x))
    height = max(abs(diag_1.y), abs(diag_2.y))
    return pygame.Vector2(width, height)

################################################################################
#                                 SPRITE CLASS
################################################################################

class Sprite (pygame.sprite.Sprite):
    '''
    A Sprite represents an image that moves around the screen in a game.

    Sprite objects store the following information necessary for drawing these
    images on the screen:
     - The position of the sprite on the screen using coordinates
     - The direction that the sprite is pointing using an angle measured
       counterclockwise from the positive x-axis.

    Methods are provided for the following:
     - Moving and turning the sprite
     - Detecting whether or not a sprite is touching other sprites
     - Animating the sprite
     - Adding behaviour when the mouse interacts with the sprite
    '''

    def __init__ (self, image=None):
        '''
        Create a Painter object.

        An `image` may be provided:
         - The image can be the name of an image file.
         - It can also be a list of points that create a polygon.
         - If no image is provided, then the Painter will be a 1x1 pixel
           transparent sprite.
        '''

        pygame.sprite.Sprite.__init__(self)

        # Handle the image
        self._image = image
        if image is None:
            self._original = pygame.Surface((1, 1), pygame.SRCALPHA)
        elif isinstance(image, tuple) or isinstance(image, list):
            self._original = tuple([pygame.Vector2(p) for p in image])
        elif isinstance(image, pygame.Surface):
            self._original = image
        else:
            image = str(image)
            if image in pgputils.polygon_images:
                self._original = pgputils.polygon_images[image]
            else:
                self._original = pygame.image.load(image).convert_alpha()
        self._opacity = 1


        # The .image and .rect attributes are needed for drawing sprites
        # in a pygame group
        if isinstance(self._original, tuple):
            self.image = pgputils.polygon_to_surface(self._original, "black", "black")
        else:
            self.image = self._original
        self._flipped = self._original
        self._scaled = self._flipped
        self._rotated = self._scaled
        self.rect = self.image.get_rect()

        # Positional and directional attributes
        self._pos = pygame.Vector2(0, 0)
        self._anchor = ("center", "center")
        self._anchor_vec = pygame.Vector2(0, 0)
        self._dir = 0
        self._move_ratio = pygame.Vector2(1, 0)

        # Scale and rotation attributes
        self._vertical_flip = False
        self._horizontal_flip = False
        self._dirty_flip = False
        self._scale = 1
        self._dirty_scale = False
        self._smooth = False
        self._rotates = False
        self._tilt = 0
        self._dirty_rotate = False
        self._dirty_mask = True

        # Attributes for lines and fill of polygon images
        self._linecolor = "black"
        self._linecolor_obj = pygame.Color("black")
        self._linesize = 1
        self._fillcolor = "black"
        self._fillcolor_obj = pygame.Color("black")

        # Attributes that hold any event handlers associated with the sprite
        self._on_update_func = None
        self._click_funcs = [None for _ in range(5)]
        self._click_methods = [None for _ in range(5)]
        self._click_bleeds = [None for _ in range(5)]
        self._release_funcs = [None for _ in range(5)]
        self._drag_funcs = [None for _ in range(5)]


    ### Visibility Methods

    @property
    def visible (self):
        '''
        Whether or not the sprite is visible on the active screen.
        '''

        active_screen = get_active_screen()
        return active_screen is not None and self in active_screen

    @visible.setter
    def visible (self, new_visibility):

        if bool(new_visibility):
            self.show()
        else:
            self.hide()


    def show (self):
        '''
        Add the sprite to the active screen.
        '''

        active_screen = get_active_screen()
        if active_screen is not None:
            self.add(active_screen)


    def hide (self):
        '''
        Remove the sprite from the active screen.
        '''

        active_screen = get_active_screen()
        if active_screen is not None:
            self.remove(active_screen)


    ### Image property

    @property
    def picture (self):
        '''
        The sprite's current picture.

        The picture can be:
         - The name of an image file.
         - A list of points that create a polygon.
         - A pygame Surface image.
         - A predefined polygon (e.g. "circle", "square", "turtle")
         - `None`, in which case the sprite will be a 1x1 transparent pixel.
        '''

        return self._image

    @picture.setter
    def picture (self, new_image):

        # Handle the image
        self._image = new_image
        if new_image is None:
            self._original = pygame.Surface((1, 1), pygame.SRCALPHA)
        elif isinstance(new_image, tuple) or isinstance(new_image, list):
            self._original = tuple([pygame.Vector2(p) for p in new_image])
        elif isinstance(new_image, pygame.Surface):
            self._original = new_image
        else:
            new_image = str(new_image)
            if new_image in pgputils.polygon_images:
                self._original = pgputils.polygon_images[new_image]
            else:
                self._original = pygame.image.load(new_image).convert_alpha()

        # Set the dirty flags to ensure scaling and rotation
        self._dirty_scale = True
        self._dirty_rotate = True
        self._dirty_mask = True

        # Adjust the anchor if necessary
        self.anchor = self._anchor


    @property
    def opacity (self):
        '''
        The opacity of the Sprite's image.

        The opacity is on a scale from 0 to 1.  An opacity of 0 means the
        picture is fully transparent.  An opacity of 1 means the picture
        is fully opaque.
        '''

        return self._opacity

    @opacity.setter
    def opacity (self, new_opacity):

        # Ensure that the opacity is a number
        try:
            new_opacity = float(new_opacity)
        except:
            raise ValueError("The opacity must be a number!")

        # Ensure that the opacity is between 0 and 1
        if new_opacity < 0 or new_opacity > 1:
            raise ValueError("The opacity must be a value between 0 and 1!")

        self._opacity = new_opacity


    ### Position Methods

    @property
    def anchor (self):
        '''
        The point on the image that will be placed on the sprite's position
        and used as the center of gravity for scaling and rotation.

        The anchor point is a 2-tuple that can be:
         - a point relative to the center of the image (e.g. `(50, -25)`)
         - position descriptions including "center", "left", "right", "bottom"
           and "top" (e.g. `("left", "center")`)
         - a combination of the two (e.g. `("center", -25)`)

        Note that the anchor is relative to the original image and scaling
        and rotation are done after the image is placed at the anchor point.
        '''

        return tuple(self._anchor)

    @anchor.setter
    def anchor (self, new_anchor):

        # Ensure that the anchor is a 2-tuple
        try:
            anchor_x, anchor_y = new_anchor
        except:
            raise ValueError("The anchor must be a 2-tuple!")

        # Turn the x value into a number
        if anchor_x == "left":
            anchor_x = - self._original.get_width() / 2
        elif anchor_x == "right":
            anchor_x = self._original.get_width() / 2
        elif anchor_x in ["center", "middle"]:
            anchor_x = 0
        else:
            try:
                anchor_x = float(anchor_x)
            except:
                raise ValueError("Invalid anchor x value!")

        # Turn the y value into a number
        if anchor_y == "bottom":
            anchor_y = - self._original.get_height() / 2
        elif anchor_y == "top":
            anchor_y = self._original.get_height() / 2
        elif anchor_y in ["center", "middle"]:
            anchor_y = 0
        else:
            try:
                anchor_y = float(anchor_y)
            except:
                raise ValueError("Invalid anchor y value!")

        # Set the anchor vector
        self._anchor = new_anchor
        self._anchor_vec = pygame.Vector2(anchor_x, anchor_y)


    @property
    def position (self):
        '''
        The current the position of the sprite on the screen.

        The position is a pair of coordinates (x and y) which represent the
        distance that the sprite is from the center of the screen.  That is,
        the center of the screen is (0, 0) and the x-coordinate and y-coordinate
        represent respectively how far horizontally and vertically the sprite is
        from there.  Think of the screen as the traditional 2D coordinate plane
        used in mathematics.
        '''

        return tuple(self._pos)

    @position.setter
    def position (self, new_position):

        try:
            self._pos = pygame.Vector2(new_position)
        except:
            raise ValueError("Invalid position!") from None


    def go_to (self, x, y=None, turn=True):
        '''
        Turn the sprite and move the sprite to the given coordinates.

        Unlike changing the position property, this method will also turn the
        sprite in the direction of the given location.  This behaviour can be
        turned of by setting the `turn` argument to `False`.
        '''

        if turn:
            # Get the distance and direction
            delta = pygame.Vector2(x, y) - self._pos
            distance, direction = delta.as_polar()

            # Don't turn if the sprite isn't moving
            if distance > 0:
                # Adjust direction to turn in closest direction
                if direction - self._dir > 180:
                    direction -= 360
                if direction - self._dir < -180:
                    direction += 360

                # Do the turn
                self.direction = direction

        # Move the sprite
        self.position = pygame.Vector2(x, y)


    @property
    def x (self):
        '''
        The current x-coordinate of the sprite's position on the screen.
        '''

        return self._pos.x

    @x.setter
    def x (self, new_x):

        try:
            self.position = new_x, self._pos.y
        except:
            raise ValueError("Invalid x-coordinate!") from None

    @property
    def y (self):
        '''
        The current y-coordinate of the sprite's position on the screen.
        '''

        return self._pos.y

    @y.setter
    def y (self, new_y):

        try:
            self.position = self._pos.x, new_y
        except:
            raise ValueError("Invalid y-coordinate!") from None


    @property
    def center_x (self):
        '''
        The x-coordinate of the center of the sprite's image.
        '''

        return self._pos.x

    @center_x.setter
    def center_x (self, new_coordinate):

        self.x = new_coordinate


    @property
    def center_y (self):
        '''
        The y-coordinate of the center of the sprite's image.
        '''

        return self._pos.y

    @center_x.setter
    def center_y (self, new_coordinate):

        self.y = new_coordinate


    @property
    def left_edge (self):
        '''
        The x-coordinate of the left edge of the sprite's image.
        '''

        return self.center_x - self.width / 2

    @left_edge.setter
    def left_edge (self, new_coordinate):

        self.center_x = new_coordinate + self.width / 2


    @property
    def right_edge (self):
        '''
        The x-coordinate of the right edge of the sprite's image.
        '''

        return self.center_x + self.width / 2

    @right_edge.setter
    def right_edge (self, new_coordinate):

        self.center_x = new_coordinate - self.width / 2


    @property
    def top_edge (self):
        '''
        The y-coordinate of the top edge of the sprite's image.
        '''

        return self.center_y + self.height / 2

    @top_edge.setter
    def top_edge (self, new_coordinate):

        self.center_y = new_coordinate - self.height / 2


    @property
    def bottom_edge (self):
        '''
        The y-coordinate of the bottom edge of the sprite's image.
        '''

        return self.center_y - self.height / 2

    @bottom_edge.setter
    def bottom_edge (self, new_coordinate):

        self.center_y = new_coordinate + self.height / 2


    @property
    def top_left_corner (self):
        '''
        The coordinates of the top left corner of the sprite's image.
        '''

        width, height = self.size
        return self.center_x - width / 2, self.center_y + height / 2

    @top_left_corner.setter
    def top_left_corner (self, new_coordinates):

        try:
            self.left_edge, self.top_edge = new_coordinates
        except:
            raise ValueError("Invalid coordinates!")


    @property
    def bottom_left_corner (self):
        '''
        The coordinates of the bottom left corner of the sprite's image.
        '''

        width, height = self.size
        return self.center_x - width / 2, self.center_y - height / 2

    @bottom_left_corner.setter
    def bottom_left_corner (self, new_coordinates):

        try:
            self.left_edge, self.bottom_edge = new_coordinates
        except:
            raise ValueError("Invalid coordinates!")


    @property
    def top_right_corner (self):
        '''
        The coordinates of the top right corner of the sprite's image.
        '''

        width, height = self.size
        return self.center_x + width / 2, self.center_y + height / 2

    @top_right_corner.setter
    def top_right_corner (self, new_coordinates):

        try:
            self.right_edge, self.top_edge = new_coordinates
        except:
            raise ValueError("Invalid coordinates!")


    @property
    def bottom_right_corner (self):
        '''
        The coordinates of the bottom right corner of the sprite's image.
        '''

        width, height = self.size
        return self.center_x + width / 2, self.center_y - height / 2

    @bottom_right_corner.setter
    def bottom_right_corner (self, new_coordinates):

        try:
            self.right_edge, self.bottom_edge = new_coordinates
        except:
            raise ValueError("Invalid coordinates!")


    @property
    def left_edge_midpoint (self):
        '''
        The coordinates of the midpoint of the left edge of the sprite's image.
        '''

        return self.center_x - self.width / 2, self.center_y

    @left_edge_midpoint.setter
    def left_edge_midpoint (self, new_coordinates):

        try:
            self.left_edge, self.center_y = new_coordinates
        except:
            raise ValueError("Invalid coordinates!")


    @property
    def right_edge_midpoint (self):
        '''
        The coordinates of the midpoint of the right edge of the sprite's image.
        '''

        return self.center_x + self.width / 2, self.center_y

    @right_edge_midpoint.setter
    def right_edge_midpoint (self, new_coordinates):

        try:
            self.right_edge, self.center_y = new_coordinates
        except:
            raise ValueError("Invalid coordinates!")


    @property
    def top_edge_midpoint (self):
        '''
        The coordinates of the midpoint of the top edge of the sprite's image.
        '''

        return self.center_x, self.center_y + self.height / 2

    @top_edge_midpoint.setter
    def top_edge_midpoint (self, new_coordinates):

        try:
            self.center_x, self.top_edge = new_coordinates
        except:
            raise ValueError("Invalid coordinates!")


    @property
    def bottom_edge_midpoint (self):
        '''
        The coordinates of the midpoint of the bottom edge of the sprite's image.
        '''

        return self.center_x, self.center_y - self.height / 2

    @bottom_edge_midpoint.setter
    def bottom_edge_midpoint (self, new_coordinates):

        try:
            self.center_x, self.bottom_edge = new_coordinates
        except:
            raise ValueError("Invalid coordinates!")


    ### Direction Methods

    @property
    def direction (self):
        '''
        The current direction that the sprite is pointing.

        The direction is an angle (in degrees) counterclockwise from the
        positive x-axis.  Here are some important directions:
         - 0 degrees is directly to the right
         - 90 degrees is directly up
         - 180 degrees is directly to the left
         - 270 degrees is directly down
        '''

        return self._dir

    @direction.setter
    def direction (self, new_direction):

        # Ensure that the direction is a number
        try:
            self._dir = float(new_direction)
        except:
            raise ValueError("The direction must be a number!")

        # Ensure that the direction is between 0 and 360
        self._dir %= 360

        # Create a 2D vector that contains the amount that the x-coordinate
        # and y-coordinate change if the sprite moves forward 1 pixel in this
        # direction
        self._move_ratio = pygame.Vector2(1, 0).rotate(self._dir)

        # If the image rotates, then flag that we need to update the image
        if self._rotates:
            self._dirty_rotate = True


    def turn_to (self, direction):
        '''
        Change the direction.
        '''

        self.direction = direction


    def turn_left (self, angle):
        '''
        Turn the sprite left (counterclockwise) by the given `angle`.
        '''

        self.direction += angle


    def turn_right (self, angle):
        '''
        Turn the sprite right (clockwise) by the given `angle`.
        '''

        self.direction -= angle


    ### Movement Methods

    def move_forward (self, distance):
        '''
        Move the sprite by the given `distance` in the direction it is currently
        pointing.
        '''

        self.position = self._pos + distance * self._move_ratio


    def move_backward (self, distance):
        '''
        Move the sprite by the given `distance` in the opposite of the
        direction it is currently pointing.
        '''

        self.position = self._pos - distance * self._move_ratio


    ### Scaling and Rotating Image Methods

    @property
    def scale_factor (self):
        '''
        The factor by which the image's width and height are scaled.

        If the factor is greater than 1, then the image is enlarged by multiplying
        its original dimension by that number.  If factor is less than 1, then
        the image is shrunk by multiplying its original dimension by that
        number.  If factor equals 1, then the image is scaled to its original
        size.
        '''

        return self._scale

    @scale_factor.setter
    def scale_factor (self, new_factor):

        # Ensure that the factor is a number
        try:
            new_factor = float(new_factor)
        except:
            raise ValueError("The scale factor must be a number!") from None

        # Ensure that the factor is positive
        if new_factor <= 0:
            raise ValueError("The scale factor must be positive!") from None

        # Otherwise, assume just one factor
        self._scale = new_factor

        # Flag that the image may have been scaled and needs to be updated
        self._dirty_scale = True


    @property
    def width (self):
        '''
        The width of the sprite's image.
        '''

        return get_dimensions(self._original, self._tilt, self._scale,
                              self._dir if self._rotates else 0).x

    @width.setter
    def width (self, new_width):

        div = get_dimensions(self._original, self._tilt, 1,
                             self._dir if self._rotates else 0).x
        self.scale_factor = new_width / div


    @property
    def height (self):
        '''
        The height of the sprite's image.
        '''

        return get_dimensions(self._original, self._tilt, self._scale,
                              self._dir if self._rotates else 0).y

    @height.setter
    def height (self, new_height):

        div = get_dimensions(self._original, self._tilt, 1,
                             self._dir if self._rotates else 0).y
        self.scale_factor = new_height / div


    @property
    def size (self):
        '''
        The dimensions (width and height) of the sprite's image
        '''

        return tuple(get_dimensions(self._original, self._tilt, self._scale,
                                    self._dir if self._rotates else 0))


    @property
    def rotates (self):
        '''
        Whether or not the image rotates when the sprite changes direction.
        '''

        return self._rotates

    @rotates.setter
    def rotates (self, new_rotates):

        self._rotates = bool(new_rotates)

        # Flag that the image may have rotated and needs to be updated
        self._dirty_rotate = True
        self._dirty_mask = True


    @property
    def tilt (self):
        '''
        The angle that the image is tilted counterclockwise from its original
        orientation.

        If image rotation is off, then the image will stay tilted at this angle
        no matter what direction the sprite is pointing.  If image rotation is on,
        then the image will stay tilted at this angle relative to the sprite's
        direction.
        '''

        return self._tilt

    @tilt.setter
    def tilt (self, new_angle):

        # Ensure that the tilt is a number
        try:
            self._tilt = float(new_angle)
        except:
            raise ValueError("The tilt must be a number!")

        # Ensure that the angle is between 0 and 360
        self._tilt %= 360

        # Flag that the image may have rotated and needs to be updated
        self._dirty_rotate = True
        self._dirty_mask = True


    @property
    def smooth (self):
        '''
        Whether or not the image is smoothed when scaled or rotated.

        By default, a quick and simple scale and rotation is applied.  This can
        cause images to be pixelated (when enlarged), loose detail (when shrunk),
        or be distorted (when rotating).  If you set `smooth` to be `True`, then
        each new pixel will be sampled and an average color will be used.  This
        makes to scaled and rotated images be more smooth, but takes longer.  You
        may want to avoid smooth scaling if you will be scaling or rotating the
        image very frequently.
        '''

        return self._smooth

    @smooth.setter
    def smooth (self, new_smooth):

        self._smooth = bool(new_smooth)


    @property
    def flipped_horizontally (self):
        '''
        Whether or not the original picture is flipped horizontally.
        '''

        return self._horizontal_flip

    @flipped_horizontally.setter
    def flipped_horizontally (self, new_setting):

        self._horizontal_flip = bool(new_setting)

        # Flag that the image may have flipped and needs to be transformed
        self._dirty_flip = True
        self._dirty_mask = True


    @property
    def flipped_vertically (self):
        '''
        Whether or not the original picture is flipped vertically.
        '''

        return self._vertical_flip

    @flipped_vertically.setter
    def flipped_vertically (self, new_setting):

        self._vertical_flip = bool(new_setting)

        # Flag that the image may have flipped and needs to be transformed
        self._dirty_flip = True
        self._dirty_mask = True


    @property
    def flipped (self):
        '''
        Whether or not the original picture is flipped.

        This property is a 2-tuple of booleans that contains whether
        the image is flipped horizontally and vertically, respectively.
        '''

        return self._horizontal_flip, self._vertical_flip

    @flipped.setter
    def flipped (self, new_settings):

        try:
            self._horizontal_flip = bool(new_settings[0])
            self._vertical_flip = bool(new_settings[1])
        except:
            raise ValueError("This setting must be a 2-tuple of boolean values!")

        # Flag that the image may have flipped and needs to be transformed
        self._dirty_flip = True


    ### Color and Width Methods for Polygons

    @property
    def line_color (self):
        '''
        The current line color.

        The color can be one of the following values:
         - A valid color string.  See https://replit.com/@cjdevet/PygameColors
           to explore the available color strings.
         - A set of three numbers between 0 and 255 that represent the
           amount of red, green, blue to use in the color.  A fourth transparency
           value can be added.
         - An HTML color code in the form "#rrggbb" where each character
           r, g, b and a are replaced with a hexidecimal digit.  For translucent
           colors, add another pair of hex digits ("##rrggbbaa").
         - An integer that, when converted to hexidecimal, gives an HTML color
           code in the form 0xrrggbbaa.
         - A pygame Color object.
        '''

        return self._linecolor

    @line_color.setter
    def line_color (self, new_color):

        try:
            self._linecolor_obj = pygame.Color(new_color)
        except:
            raise ValueError(f"Invalid color: {new_color}") from None
        self._linecolor = new_color

        if isinstance(self._original, tuple):
            self._dirty_rotate = True


    @property
    def fill_color (self):
        '''
        The current fill color.

        The color can be one of the following values:
         - A valid color string.  See https://replit.com/@cjdevet/PygameColors
           to explore the available color strings.
         - A set of three numbers between 0 and 255 that represent the
           amount of red, green, blue to use in the color.  A fourth transparency
           value can be added.
         - An HTML color code in the form "#rrggbb" where each character
           r, g, b and a are replaced with a hexidecimal digit.  For translucent
           colors, add another pair of hex digits ("##rrggbbaa").
         - An integer that, when converted to hexidecimal, gives an HTML color
           code in the form 0xrrggbbaa.
         - A pygame Color object.
        '''

        return self._fillcolor

    @fill_color.setter
    def fill_color (self, new_color):

        try:
            self._fillcolor_obj = pygame.Color(new_color)
        except:
            raise ValueError(f"Invalid color: {new_color}") from None
        self._fillcolor = new_color

        if isinstance(self._original, tuple):
            self._dirty_rotate = True


    @property
    def colors (self):
        '''
        A tuple containing the current line color and fill color.

        You can change both the line color and fill color by setting this
        property to be a 2-tuple containing each respective color.  You
        can change both the line color and fill color to the same color by
        providing one color.
        '''

        return self._linecolor, self._fillcolor

    @colors.setter
    def colors (self, new_colors):

        # If a tuple of length 2 is given, assume two different colors
        if isinstance(new_colors, tuple) and len(new_colors) == 2:
            self.line_color, self.fill_color = new_colors

        # Otherwise, assume just one color
        else:
            self.line_color = new_colors
            self.fill_color = new_colors


    ### Update Method

    # Helper method that scales and/or rotates the image if it is dirty
    def _clean_image (self, screen=None):
        # If the image is a polygon, scale and rotate the points before drawing it
        if isinstance(self._original, tuple):
            if self._dirty_scale:
                self._scaled = tuple([self._scale * p for p in self._flipped])
                self._dirty_flip = True
                self._dirty_scale = False

            if self._dirty_flip:
                self._flipped = pgputils.flip_polygon(self._original,
                        self._horizontal_flip, self._vertical_flip)
                self._dirty_rotate = True
                self._dirty_flip = False

            if self._dirty_rotate:
                angle = self._dir + self._tilt if self._rotates else self._tilt
                self._rotated = tuple([p.rotate(angle) for p in self._scaled])
                self._dirty_rotate = False
                self.image = pgputils.polygon_to_surface(self._rotated,
                                self._linecolor, self._fillcolor, round(self._scale))

        # Otherwise, scale and rotate the surfaces
        else:
            if self._dirty_scale:
                orig_width, orig_height = self._original.get_size()
                new_width = round(self._scale * orig_width)
                new_height = round(self._scale * orig_height)
                if self._smooth:
                    self._scaled = pygame.transform.smoothscale(
                            self._original, (new_width, new_height))
                else:
                    self._scaled = pygame.transform.scale(
                            self._original, (new_width, new_height))
                self._dirty_flip = True
                self._dirty_scale = False

            if self._dirty_flip:
                self._flipped = pygame.transform.flip(self._scaled,
                        self._horizontal_flip, self._vertical_flip)
                self._dirty_rotate = True
                self._dirty_flip = False

            if self._dirty_rotate:
                angle = self._dir + self._tilt if self._rotates else self._tilt
                if self._smooth:
                    self._rotated = pygame.transform.rotozoom(
                            self._flipped, angle, 1)
                else:
                    self._rotated = pygame.transform.rotate(self._flipped, angle)
                self.image = self._rotated
                self._dirty_rotate = False

        # Update the enclosing rect
        self.rect.size = self.image.get_size()
        self.image.set_alpha(int(self._opacity * 255))
        offset_vec = self._scale * self._anchor_vec
        offset_vec.rotate_ip(self._dir + self._tilt if self._rotates else self._tilt)
        if screen is None:
            self.rect.center = to_pygame_coordinates(self._pos - offset_vec)
        else:
            self.rect.center = screen.to_pygame_coordinates(self._pos - offset_vec)

    # Helper method that determines the image's mask if it is dirty
    def _clean_mask (self, screen=None):
        if self._dirty_mask:
            self.mask = pygame.mask.from_surface(self.image)
            self._dirty_mask = False


    def update (self, screen=None):
        '''
        Update the sprite in preparation to draw the next frame.

        This method should generally not be called explicitly, but will be called
        by the event loop if the sprite is on the active screen.
        '''

        # If a custom update function has been applied, call it
        if self._on_update_func is not None:
            pgputils.call_with_args(self._on_update_func, sprite=self)

        # Update the sprite's .image and .rect attributes needed for drawing
        self._clean_image(screen)


    ### Other Sprite Methods

    def get_distance_to (self, other):
        '''
        Return the distance this sprite is away from another.
        '''

        return self._pos.distance_to(other._pos)


    def get_direction_to (self, other):
        '''
        Return the angle that this sprite must turn toward to be pointing
        directly at another.
        '''

        return pygame.Vector2(1, 0).angle_to(other._pos - self._pos)


    ### Collision Methods

    def is_touching_point (self, x, y=None, method="rect"):
        '''
        Returns whether or not the sprite is touching a given point.

        The `method` argument can be used to specify which type of collision
        detection to use:
         - The "rect" method will determine if the point is inside of the rectangle
           that the image is contained in.  This is the default.
         - The "circle" method will determine if the point is inside of a circle
           centered at the sprite's position.  To use circle collision, you need
           to specify a `.radius` attribute for the sprite or the circle will be the
           smallest circle that encloses the entire image.
         - The "mask" method will determine if the point is touching a
           non-transparent part of the image.
         - You can pass in a custom function that takes two sprites as arguments
           and returns a Boolean value indicating if they are touching.
        '''

        # If this sprite isn't visible, then it can't be in collision
        if not self.visible:
            return False

        # Get the collision detection function for the given method
        if isinstance(method, str):
            if method not in pgputils.collision_functions:
                raise ValueError(f"Invalid collision method: {method}")
            method = pgputils.collision_functions[method]

        # Create the other "sprite"
        if y is None:
            x, y = x
        other_sprite = pygame.sprite.Sprite()
        pygame_x, pygame_y = to_pygame_coordinates(x, y)
        other_sprite.rect = pygame.Rect(pygame_x, pygame_y, 1, 1)
        other_sprite.radius = 0.5
        other_sprite.mask = pygame.mask.Mask((1, 1), True)

        # Update the turtle and, if dirty, get its mask
        self._clean_image()
        if method == pygame.sprite.collide_mask:
            self._clean_mask()

        # Collision detection if given a point
        return bool(method(self, other_sprite))


    def get_touching (self, others, method="rect"):
        '''
        Takes a collection of sprites and returns the subset that the sprite is
        touching.

        See the Sprite.is_touching() method for details on the `method` parameter.
        '''

        # If this sprite isn't visible, then it can't be in collision
        if not self.visible:
            return False

        # Get the collision detection function for the given method
        if isinstance(method, str):
            if method not in pgputils.collision_functions:
                raise ValueError(f"Invalid collision method: {method}")
            method = pgputils.collision_functions[method]

        # Update the turtle and, if dirty, get its mask
        self._clean_image()
        if method == pygame.sprite.collide_mask:
            self._clean_mask()

        # If given a list, loop through it use the method from above
        if isinstance(other, list):
            hit_list = []
            for other_sprite in other:
                other_sprite._clean_image()
                if method == pygame.sprite.collide_mask:
                    other_sprite._clean_mask()
                if other_sprite in active_screen and bool(method(self, other_sprite)):
                    hit_list.append(other)
            return hit_list

        # If given a pygame sprite group, use the pygame function for
        # collision detection with a group
        elif isinstance(other, pygame.sprite.Group):
            other.update()
            hit_list = pygame.sprite.spritecollide(self, other, False, method)
            return hit_list

        # If given an invalid argument, just return False
        else:
            return ValueError("Invalid argument!")


    def is_touching (self, other, method="rect"):
        '''
        Returns whether or not the sprite is touching another sprite (or
        collection of sprites).

        The `method` argument can be used to specify which type of collision
        detection to use:
         - The "rect" method will determine if the rectangles that the images are
           contained in are overlapping.  This is the default.
         - The "circle" method will determine if circles centered at the sprites'
           positions are overlapping.  To use circle collision, you need to
           specify a `.radius` attribute for the sprites or the circle will be
           the smallest circle that encloses the entire image.
         - The "mask" method will determine if the non-transparent parts of the
           images are overlapping.
         - You can pass in a custom function that takes two sprites as arguments
           and returns a Boolean value indicating if they are touching.
        '''

        # If this sprite isn't visible, then it can't be in collision
        if not self.visible:
            return False

        active_screen = get_active_screen()

        # Get the collision detection function for the given method
        if isinstance(method, str):
            if method not in pgputils.collision_functions:
                raise ValueError(f"Invalid collision method: {method}")
            method = pgputils.collision_functions[method]

        # Update the turtle and, if dirty, get its mask
        self._clean_image()
        if method == pygame.sprite.collide_mask:
            self._clean_mask()

        # If given just a sprite, put it into a list
        if isinstance(other, pygame.sprite.Sprite):
            other._clean_image()
            if method == pygame.sprite.collide_mask:
                other._clean_mask()
            return other in active_screen and bool(method(self, other))

        # If given a list, loop through it use the method from above
        elif isinstance(other, list):
            for other_sprite in other:
                other_sprite._clean_image()
                if method == pygame.sprite.collide_mask:
                    other_sprite._clean_mask()
                if other_sprite in active_screen and bool(method(self, other_sprite)):
                    return True
            return False

        # If given a pygame sprite group, use the pygame function for
        # collision detection with a group
        elif isinstance(other, pygame.sprite.Group):
            other.update()
            hit_list = pygame.sprite.spritecollide(self, other, False, method)
            return len(hit_list) > 0

        # If given an invalid argument, just return False
        else:
            raise ValueError("Invalid argument!")


    ### Add Custom Update Function

    def on_update (self, func):
        '''
        Add a custom update function that will be called on every iteration of
        the event loop.

        You can provide the following arguments for the function `func`:
         - `sprite` - will provide the sprite object being updated
        '''

        self._on_update_func = func


    ### Click Event Methods

    def on_click (self, func, button="left", method="rect", bleeds=False):
        '''
        Add a function that will be called when the mouse is clicked on
        this sprite.

        You can provide the following arguments for the function `func`:
         - `x` - will provide x-coordinate of the mouse
         - `y` - will provide y-coordinate of the mouse
         - `pos` - will provide a tuple of the coordinates (x and y) of the mouse
         - `button` - will provide the name of the mouse button used
         - `sprite` - will provide the sprite object involved

        You can specify which mouse button needs to be used for the click using
        the `button` parameter.  It's value needs to be one of "left", "center",
        "right", "scrollup" or "scrolldown".  The left button is the default.

        The `method` can be used to specify which type of collision detection to
        use to see if the sprite was clicked on.  See `.is_touching_point()` for
        more details.

        If multiple sprites are stacked, then the event will be triggered
        for the highest sprite with a click handler.  If `bleeds` is set to
        `True`, then if this sprite is clicked, the click event will bleed
        to sprites underneath it.
        '''

        # Convert the button string to a button number
        if isinstance(button, str):
            try:
                button = pgputils.mouse_button_map[button]
            except KeyError:
                raise ValueError("Invalid button!")

        # Get the collision detection function for the given method
        if isinstance(method, str):
            if method not in pgputils.collision_functions:
                raise ValueError(f"Invalid collision method: {method}")
            method = pgputils.collision_functions[method]

        # If a button is valid, add the function to the appropriate button
        if 1 <= button <= 5:
            self._click_funcs[button - 1] = func
            self._click_methods[button - 1] = method
            self._click_bleeds[button - 1] = bool(bleeds)
        else:
            raise ValueError("Invalid button!")


    def on_release (self, func, button="left"):
        '''
        Add a function that will be called when the mouse is released after
        clicking on this sprite.

        You can provide the following arguments for the function `func`:
         - `x` - will provide x-coordinate of the mouse
         - `y` - will provide y-coordinate of the mouse
         - `pos` - will provide a tuple of the coordinates (x and y) of the mouse
         - `button` - will provide the name of the mouse button used
         - `sprite` - will provide the sprite object involved

        You can specify which mouse button needs to be used for the click using
        the `button` parameter.  It's value needs to be one of "left", "center",
        "right", "scrollup" or "scrolldown".  The left button is the default.
        '''

        # Convert the button string to a button number
        if isinstance(button, str):
            try:
                button = pgputils.mouse_button_map[button]
            except KeyError:
                raise ValueError("Invalid button!")

        # If a button is valid, add the function to the appropriate button
        if 1 <= button <= 5:
            self._release_funcs[button - 1] = func
        else:
            raise ValueError("Invalid button!")


    def on_drag (self, func, button="left"):
        '''
        Add a function that will be called when the mouse dragged while
        clicking on this sprite.

        You can provide the following arguments for the function `func`:
         - `x` - will provide x-coordinate of the mouse
         - `y` - will provide y-coordinate of the mouse
         - `pos` - will provide a tuple of the coordinates (x and y) of the mouse
         - `button` - will provide the name of the mouse button used
         - `sprite` - will provide the sprite object involved

        You can specify which mouse button needs to be used for the click using
        the `button` parameter.  It's value needs to be one of "left", "center",
        "right", "scrollup" or "scrolldown".  The left button is the default.
        '''

        # Convert the button string to a button number
        if isinstance(button, str):
            try:
                button = pgputils.mouse_button_map[button]
            except KeyError:
                raise ValueError("Invalid button!")

        # If a button is valid, add the function to the appropriate button
        if 1 <= button <= 5:
            self._drag_funcs[button - 1] = func
        else:
            raise ValueError("Invalid button!")


# What is included when importing *
__all__ = [
    "Sprite"
]

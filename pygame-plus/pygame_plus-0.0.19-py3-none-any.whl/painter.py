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

from pygameplus.screen import *
from pygameplus.sprite import Sprite

################################################################################
#                                 COLOR CLASS
################################################################################

# We will provide the Color class from pygame directly.
from pygame import Color

################################################################################
#                                PAINTER CLASS
################################################################################

class Painter (Sprite):
    '''
    A Painter is a special sub-class of a Sprite with extra methods used to 
    draw on the screen.  All methods of a Sprite object can be used on
    Painter objects.

    Some features of Painter objects include:
     - They can draw on the screen when they move.
     - They can be used to draw filled polygons.
     - They can draw dots and circles.
     - They can stamp copies of their image to the screen.
     - They can write text to the screen.
    '''

    # A cache that stores fonts previously used.
    _fonts = {}

    def __init__ (self, image=None):
        '''
        Create a Painter object.

        An `image` may be provided:
         - The image can be the name of an image file.
         - It can also be a list of points that create a polygon.
         - If no image is provided, then the Painter will be a 1x1 pixel
           transparent sprite.
        '''

        Sprite.__init__(self, image)

        # Attributes associate with lines
        self._drawing = False
        self._stepsize = 0.1

        # Attributes associates with fills
        self._filling = False
        self._fill_as_moving = None
        self._fillpoly = None
        self._fill_canvas = None
        self._drawings_over_fill = None


    ### Drawing Line Methods

    @property
    def step_size (self):
        '''
        The step size between points drawn on a line.
        '''

        return self._stepsize

    @step_size.setter
    def step_size (self, new_distance):

        # Ensure that the distance is a number.
        try:
            new_distance = float(new_distance)
        except:
            raise ValueError("The step size must be a number!")

        # Ensure that the distance is positive.
        if new_distance <= 0:
            raise ValueError("The step size must be positive!")

        self._stepsize = new_distance


    @property
    def line_width (self):
        '''
        The current width of the lines drawn.
        '''

        return self._linesize

    @line_width.setter
    def line_width (self, new_width):
        '''
        The width of the lines drawn.

        Note that any decimal widths will be rounded.
        '''

        try:
            new_width = round(new_width)
        except:
            raise ValueError("The width must be a number!")

        if new_width < 1:
            raise ValueError("The width must be positive!")

        self._linesize = new_width


    @property
    def drawing (self):
        '''
        Whether or not the painter is currently drawing a line.
        '''

        return self._drawing

    @drawing.setter
    def drawing (self, is_drawing):

        # Ensure that the argument is boolean
        is_drawing = bool(is_drawing)

        # Only start/stop drawing if the setting changed
        if is_drawing != self._drawing:
            if is_drawing:
                self.begin_line()
            else:
                self.end_line()


    def begin_line (self):
        '''
        Start drawing a line from the current position.
        '''

        self._drawing = True


    def end_line (self):
        '''
        End the line at the current position.
        '''

        self._drawing = False


    ### Drawing Methods

    # A helper method that draws a line from start to end on the given canvas.
    def _draw_line (self, start, end, canvas=None):
        if canvas is None:
            canvases = [g.canvas for g in self.groups() if isinstance(g, Screen)]
            if not canvases:
                raise RuntimeError("Can't draw!  This sprite isn't on a screen!")
        else:
            canvases = [canvas]

        # Convert to pygame coordinates
        start = to_pygame_coordinates(start)
        end = to_pygame_coordinates(end)

        # If width is 1, use the pygame function
        if self._linesize == 1:
            for canvas in canvases:
                pygame.draw.line(canvas, self._linecolor_obj, start, end)

        # Otherwise use dots instead
        else:
            # Find geometric properties of the line
            delta = end - start
            distance, direction = delta.as_polar()

            # Draw dots every 0.1 pixels along the line between the points
            radius = self._linesize / 2
            current = start
            delta = pygame.Vector2(self._stepsize, 0).rotate(direction)
            for _ in range(int(distance / self._stepsize) + 1):
                for canvas in canvases:
                    pygame.draw.circle(canvas, self._linecolor_obj, current, radius)
                current += delta
                
    
    # This will replace the position setter.  It makes it so that, if
    # drawing or filling is on, that stuff is drawn to the screen's canvas
    def _set_position (self, new_position):

        # Actually move the sprite and get the start and end points
        start = self._pos
        self._pos = pygame.Vector2(new_position)

        # If the turtle is currently creating a filled shape, add the point to the
        # list of filled polygon points and draw the line on the upper layer
        # to be drawn on top of the fill.
        if self._filling:
            self._fillpoly.append(self._pos)
            self._draw_line(start, self._pos, self._drawings_over_fill)

        # Draw the line
        if self._drawing:
            self._draw_line(start, self._pos)

    position = property(Sprite.position.fget, _set_position)


    def walk_path (self, *path, turn=True):
        '''
        Move the Sprite along a path.

        If a line is currently being drawn, then it will continue from the 
        current position and be drawn along the path.

        The path should be a list of coordinate pairs
        (e.g. `[(100, 0), (-200, 100), (200, -50)]`)

        By default, this method will also turn the turtle in the direction 
        of each of the given positions.  This behaviour can be turned of by
        setting the `turn` argument to `False`.
        '''

        # Call .go_to() on each point in the path
        for point in path:
            if isinstance(point, list):
                self.walk_path(*point)
            else:
                self.go_to(point, turn=turn)


    ### Creating Filled Shapes

    # A helper method that draws the current filled polygon on the given canvas.
    def _draw_fill (self, canvas=None):
        if canvas is None:
            canvases = [g.canvas for g in self.groups() if isinstance(g, Screen)]
            if not canvases:
                raise RuntimeError("Can't draw!  This sprite isn't on a screen!")
        else:
            canvases = [canvas]

        # Draw the points to the canvas
        points = [to_pygame_coordinates(p) for p in self._fillpoly]
        if len(points) >= 3:
            for canvas in canvases:
                pygame.draw.polygon(canvas, self._fillcolor, points)

        # Draw the lines back on top of the canvas
        for canvas in canvases:
            canvas.blit(self._drawings_over_fill, (0, 0))


    @property
    def filling (self):
        '''
        Whether or not the painter is currently creating a filled shape.
        '''

        return self._filling

    @filling.setter
    def filling (self, is_filling):

        # Ensure that the argument is boolean
        is_filling = bool(is_filling)

        # Only start/stop filling if the setting changed
        if is_filling != self._drawing:
            if is_filling:
                self.begin_fill()
            else:
                self.end_fill()


    @property
    def fill_as_moving (self):
        '''
        Whether or not a fill will be shown on the screen before it is complete.
        '''

        return self._fill_as_moving

    @fill_as_moving.setter
    def fill_as_moving (self, as_moving):

        self._fill_as_moving = bool(as_moving)


    def begin_fill (self):
        '''
        Start creating a filled shape.

        This function must be followed with a call to end_fill() which
        will draw the filled shape using all of the points visited
        from the call of this method.

        If `as_moving` is set to `True`, then the filled shape will be redrawn
        after each move of the sprite.
        '''

        # Set the fill properties
        self._filling = True
        self._fillpoly = [self._pos]

        # Create a surface to hold the lines drawn on top of the fill
        self._drawings_over_fill = pygame.Surface(screen.size, pygame.SRCALPHA)


    def end_fill (self):
        '''
        Complete drawing a filled shape.

        This function must be preceded by a call to begin_fill().  When
        this method is called, a filled shape will be drawn using all of the
        points visited since begin_fill() was called.
        '''

        # If .begin_fill() wasn't called, just do nothing.
        if not self._filling:
            return

        # Draw the filled shape on the active screen
        self._draw_fill()
        
        # Reset the filling attributes
        self._filling = False
        self._fillpoly = None


    ### Draw circles

    def dot (self, size=None, color=None):
        '''
        Draw a dot.

        The dot will be centered at the current position and have diameter
        `size`.  If no size is given a dot slightly larger than the line width
        will be drawn.

        If the `color` is not specified, the line color is used.
        '''

        canvases = [g.canvas for g in self.groups() if isinstance(g, Screen)]
        if not canvases:
            raise RuntimeError("Can't draw!  This sprite isn't on a screen!")

        # If no size is given, make the dot a bit bigger than the line size
        if size is None:
            size = max(self._linesize + 4, 2 * self._linesize)

        # If no color is given use the line color
        if color is None:
            color = self._linecolor_obj

        # Draw the dot
        point = to_pygame_coordinates(self._pos)
        for canvas in canvases:
            pygame.draw.circle(canvas, color, point, size / 2)

        # If the turtle is currently creating a filled shape, draw the dot on 
        # the upper layer to be drawn on top of the fill.
        if self._filling:
            pygame.draw.circle(self._drawings_over_fill, color, point, size / 2)


    def circle (self, radius, extent=360):
        '''
        Draw a circle counterclockwise.

        The circle will have the given `radius`.  If `radius` is negative, then
        the circle is draw clockwise.
        
        The `extent` is used to draw an arc around a portion of a circle.  If 
        `extent` is negative, draw the circle clockwise.

        The circle will actually be an approximation.  The turtle will really
        draw a regular polygon with 360 sides.
        '''

        # Because the circle is an approximation, we will calculate the
        # final position and set it after the circle is drawn.
        if extent % 360 == 0:
            end = self._pos
        else:
            delta = pygame.Vector2(0, -radius)
            delta.rotate_ip(extent if radius >= 0 else -extent)
            delta += pygame.Vector2(0, radius)
            delta.rotate_ip(self._dir)
            end = self._pos + delta

        # Sanitize extent argument
        if extent is None:
            extent = 360
        else:
            extent = int(extent)

        # Set up the number of steps and the turn angle needed between
        # steps.
        step_size = abs(radius) * 2 * math.pi / 360
        turn_size = 1 if radius >= 0 else -1

        # Repeatedly move and turn to approximate the circle
        if extent > 0:
            for _ in range(extent):
                self.move_forward(step_size)
                self.turn_left(turn_size)
        else:
            for _ in range(-extent):
                self.turn_right(turn_size)
                self.move_backward(step_size)

        # Set the position to the one calculated above
        self._pos = end


    ### Draw a stamp

    def stamp (self):
        '''
        Stamp a copy of the sprite's image to the screen at the current position.
        '''

        canvases = [g.canvas for g in self.groups() if isinstance(g, Screen)]
        if not canvases:
            raise RuntimeError("Can't draw!  This sprite isn't on a screen!")

        # Copy the image to the canvas
        self._clean_image()
        for canvas in canvases:
            canvas.blit(self.image, self.rect)

        # If the turtle is currently creating a filled shape, stamp the image on 
        # the upper layer to be drawn on top of the fill.
        if self._filling:
            self._drawings_over_fill.blit(self.image, self.rect)


    ### Write on the screen

    def write (self, text, align="middle center", font="Arial", 
            size=12, style=None, color=None):
        '''
        Write text to the screen at the turtle's current location using the pen.

        The `align` parameter sets where the turtle aligns with the text being
        written.  It is a string containing "left", "right", "center", "top",
        "bottom", "middle" or a combination separated by space (e.g. 
        "bottom center")

        The `font` parameter can be the name of a font on the system or a
        True Type Font file (.ttf) located in the directory.

        The `size` is the height of the text in pixels.
        
        The `style` argument can be "bold", "italic", "underline" or a 
        combination separated by space (e.g. "bold italic").

        If the `color` is not specified, the line color is used.
        '''

        # If font is a Font object, just use that
        if isinstance(font, pygame.font.Font):
            font_obj = font

        # If this font and size have been used before, check the _fonts cache
        elif (font, size) in Painter._fonts:
            font_obj = Painter._fonts[font, size]

        # Otherwise, the font needs to be a string
        else:
            font = str(font)

            # If the font ends in ".ttf", then load the font from the file
            if font.endswith(".ttf"):
                font_obj = pygame.font.Font(font, size)

            # Otherwise, use a system font
            else:
                font_obj = pygame.font.SysFont(font, size)

            # Add the font to the _fonts cache
            Painter._fonts[font, size] = font_obj

        # Apply the styles
        if style is not None:
            if isinstance(style, str):
                style = style.split()
            style = [s.lower() for s in style]
            font_obj.set_bold("bold" in style)
            font_obj.set_italic("italic" in style)
            font_obj.set_underline("underline" in style)

        # Get the color
        if color is None:
            color = self._linecolor

        # Render an image of the text
        image = font_obj.render(str(text), True, color)
        rect = image.get_rect()

        # Set the position of the text from the align parameter
        if isinstance(align, str):
            align = align.split()
        align = [location.lower() for location in align]
        x, y = to_pygame_coordinates(self._pos)
        rect.centerx = x
        rect.centery = y
        for location in align:
            if location == "left":
                rect.left = x
            elif location == "center":
                rect.centerx = x
            elif location == "right":
                rect.right = x
            elif location == "top":
                rect.top = y
            elif location == "middle":
                rect.centery = y
            elif location == "bottom":
                rect.bottom = y

        # Draw the text on the canvas
        canvases = [g.canvas for g in self.groups() if isinstance(g, Screen)]
        if not canvases:
            raise RuntimeError("Can't draw!  This sprite isn't on a screen!")

        for canvas in canvases:
            canvas.blit(image, rect)

        # Return a Font object that can be used for future writing
        return font_obj


    ### Override the Sprite update() method

    def update (self, screen=None):
        '''
        Update the sprite in preparation to draw the next frame.

        This method should generally not be called explicitly, but will be called
        by the event loop if the sprite is on the active screen.
        '''

        Sprite.update(self, screen)

        # If filling while moving, include the fill-so-far on the screen.
        if screen is None:
            screen = get_active_screen()
        if (screen is not None and self in screen and self._filling and
                self._fill_as_moving):
            self._draw_fill(screen._update_drawings)


# What is included when importing *
__all__ = [
    "Painter",
    "Color"
]

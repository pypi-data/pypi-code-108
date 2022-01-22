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

import pygame

from pygameplus import pgputils

################################################################################
#                                 SCREEN CLASS
################################################################################

class Screen (pygame.sprite.LayeredUpdates):
    '''
    A Screen represents a single game screen visible in the window.

    At any one time there can be only one "active" screen that is visible.
    If a screen is active and another is opened, then the active screen is 
    replaced in the window.

    Screen objects store the following information about a screen:
     - Its dimensions and title
     - The background color and/or image
     - Any images that have been drawn on the screen

    Methods are provided to do the following:
     - Open a screen and make it active
     - Change the dimensions, title or background
     - Clear any images that have been drawn on the screen
     - Add behaviour when the mouse clicks on the screen or when keyboard
       keys are used when the screen is active
    '''

    # Stores the screen that is currently visible on the screen
    _active = None

    def __init__ (self, width, height, title=""):
        '''
        Create a Screen object.

        You must specify the `width` and `height` of the screen.  Optionally, you
        can set the title of the screen.
        '''

        pygame.sprite.LayeredUpdates.__init__(self)

        # Stores the pygame surface associated with the screen
        self._surface = None

        # Attributes for the dimensions, title and background
        self._width = int(width)
        self._height = int(height)
        self._title = str(title)
        self._color = "white"
        self._color_obj = pygame.Color("white")
        self._image = None
        self._image_name = None
        self._image_rect = None

        # Attributes that hold any event handlers associated with the screen
        self._key_press_funcs = {}
        self._key_release_funcs = {}
        self._key_hold_funcs = {}
        self._click_funcs = [None for _ in range(5)]
        self._release_funcs = [None for _ in range(5)]
        self._mouse_move_func = None

        # The pygame surface that holds any drawing added to the screen
        self._canvas = pygame.Surface((width, height), pygame.SRCALPHA)
        self._update_drawings = None

        # Attribute to hold timer event handlers
        self._timers = {}


    ### Overwritten functions

    def add (self, *sprites, layer=0):
        '''
        Add the sprites to this screen.

        The arguments can be individual sprite objects or a list of sprites.
        '''

        # The add() method is overwritten so that it calls the add() method
        # of each sprite that is added.  This allows special functionality to
        # happen immediately when a sprite is added (e.g. a Turtle will appear
        # on the screen immediately)

        # Loop through the sprites and if they are pygame Sprite objects, 
        # call the sprite's add() method
        for sprite in sprites:
            if isinstance(sprite, pygame.sprite.Sprite):
                sprite._layer = layer
                sprite.add(self)

            # If the object is not a Sprite, then it's probably an iterable, so
            # recursively add it.
            else:
                self.add(*sprite)


    ### Screen Visibility Methods

    def open (self):
        '''
        Make this screen the active, visible screen in the window.
        '''

        # Call the close method for any other open screen
        if Screen._active is not None and Screen._active != self:
            self._active._close()

        # Create a new pygame screen surface in the window
        self._surface = pygame.display.set_mode((self._width, self._height))
        pygame.display.set_caption(self._title)

        # Set this as the active screen
        Screen._active = self

        # Draw the screen
        self.redraw()


    # A hidden method that is called when a screen is closed.
    def _close (self):
        # Stop all timers associated with the screen
        for event_id in self._timers:
            pygame.time.set_timer(event_id, 0)

        # Clear the timers dictionary
        self._timers.clear()


    def is_open (self):
        '''
        Return whether or not this screen is the active screen.
        '''

        return self == Screen._active


    ### Methods for the screen's properties

    @property
    def size (self):
        '''
        The size of the screen as a tuple with width and height.

        Changing this property will immediately resize the screen.
        '''

        return self._width, self._height

    @size.setter
    def size (self, new_dimensions):

        old_width = self._width
        old_height = self._height

        try:
            self._width, self._height = [int(d) for d in new_dimensions]
        except:
            raise ValueError("The size must be a tuple of two integers!") from None

        # If this screen is open, then we need to create a new pygame screen
        # width this size.
        if self.is_open():
            self._surface = pygame.display.set_mode((self._width, self._height))
            self.update()

        # Create a new canvas with the new size
        old_canvas = self._canvas
        self._canvas = pygame.Surface((self._width, self._height), pygame.SRCALPHA)
        x = (self._width - old_width) // 2
        y = (self._height - old_height) // 2
        self._canvas.blit(old_canvas, (x, y))

        # Change the rect for the background image to keep it centered.
        if self._image_rect is not None:
            self._image_rect.centerx = width / 2
            self._image_rect.centery = height / 2


    @property
    def width (self):
        '''
        The width of the screen.

        Changing this property will immediately resize the screen.
        '''

        return self._width

    @width.setter
    def width (self, new_width):

        self.size = new_width, self._height


    @property
    def height (self):
        '''
        The height of the screen.

        Changing this property will immediately resize the screen.
        '''

        return self._height

    @height.setter
    def height (self, new_height):

        self.size = self._width, new_height


    @property
    def title (self):
        '''
        The title of the screen that appears at its top.
        '''

        return self._title

    @title.setter
    def title (self, new_title):

        try:
            self._title = str(new_title)
        except:
            raise ValueError("The title must be a string!") from None
        pygame.display.set_caption(self._title)


    @property
    def background_color (self):
        '''
        The background color of the screen.

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

        If this property is changed, it won't be reflected on the screen until
        it is redrawn.
        '''

        return self._color

    @background_color.setter
    def background_color (self, new_color):

        try:
            self._color_obj = pygame.Color(new_color)
        except:
            raise ValueError("Invalid color!") from None
        self._color = new_color

    @property
    def background_image (self):
        '''
        The background image of the screen.

        This image will be placed in the center of the screen.

        The image can be:
         - The file name of an image file.
         - A Python file-like object created using open().
         - `None` to remove any background image.

        If this property is changed, it won't be reflected on the screen until
        it is redrawn.
        '''

        return self._image_name

    @background_image.setter
    def background_image (self, new_image):

        # If given None, then remove the background image
        if new_image is None:
            self._image = None
            self._image_name = None
            self._image_rect = None

        # Otherwise, add the background image provided
        else:
            self._image = pygame.image.load(new_image)
            self._image_name = new_image
            self._image_rect = self._image.get_rect()
            self._image_rect.centerx = self._width / 2
            self._image_rect.centery = self._height / 2


    ### Methods for the drawing canvas
    
    @property
    def canvas (self):
        '''
        The image of any drawings that were drawn on the screen.
        '''

        return self._canvas


    def clear_canvas (self, remove_sprites=False):
        '''
        Clear everything that was drawn on the screen.
        '''

        self._canvas.fill(0)

        # Remove any sprites that are on the screen.
        if remove_sprites:
            width = self.width
            height = self.height
            for sprite in self:
                if - width / 2 <= sprite.x <= width / 2 and - height / 2 <= sprite.y <= height / 2:
                    self.remove(sprite)


    def clear_rect (self, corner1, corner2, remove_sprites=False):
        '''
        Clear a rectangular part of the screen.
        '''

        # Ensure that the points are actually points
        try:
            corner1 = pygame.Vector2(corner1)
            corner2 = pygame.Vector2(corner2)
        except:
            raise ValueError("Invalid corner position!")

        # Determine the coordinates of the sides
        left = min(corner1.x, corner2.x)
        right = max(corner1.x, corner2.x)
        bottom = min(corner1.y, corner2.y)
        top = max(corner1.y, corner2.y)

        # Create a rect and fill that area with nothing
        top_left = self.to_pygame_coordinates(left, top)
        size = pygame.Vector2(right - left, top - bottom)
        rect = pygame.Rect(top_left, size)
        self._canvas.fill(0, rect)

        # Remove any sprites that are in the rectangle.
        if remove_sprites:
            for sprite in self:
                if left <= sprite.x <= right and bottom <= sprite.y <= top:
                    self.remove(sprite)


    def clear_circle (self, center, radius, remove_sprites=False):
        '''
        Clear a circular part of the screen.
        '''

        # Ensure that the center and radius are good
        try:
            center = pygame.Vector2(center)
            radius = float(radius)
        except:
            raise ValueError("Invalid argument!")

        # Draw a circle of nothing
        pygame_center = self.to_pygame_coordinates(center)
        pygame.draw.circle(self._canvas, 0, pygame_center, radius)

        # Remove any sprites that are in the circle
        if remove_sprites:
            for sprite in self:
                if center.distance_to(sprite._pos) <= radius:
                    self.remove(sprite)


    def clear (self):
        '''
        Clears the screen of all contents, including background images,
        drawings and sprites.
        '''

        # Clear the background
        self._color = "white"
        self._color_obj = pygame.Color("white")
        self._image = None
        self._image_name = None

        # Clear the drawings canvas
        self._canvas.fill(0)

        # Remove the sprites
        self.empty()


    def update (self, *args, **kwargs):
        '''
        Calls the update() method on all Sprites on the screen.

        This method should generally not be called explicitly, but will be called
        by the event loop if the screen is active.

        This will pass this screen to the sprites' update() methods as
        the `screen` keyword argument.
        '''

        # If no screen is provided, add such a keyword argument
        if "screen" not in kwargs:
            kwargs["screen"] = self

        # Create a surface to put any drawings that should only be present for
        # this update
        self._update_drawings = pygame.Surface((self._width, self._height), 
                                               pygame.SRCALPHA)

        # Call update() on all of the sprites
        pygame.sprite.LayeredUpdates.update(self, *args, **kwargs)


    def draw (self, surface=None):
        '''
        Draw the contents of the screen.

        This method should generally not be called explicitly, but will be called
        by the event loop if the screen is active.

        By default, this will draw the contents on the pygame Surface associated
        with this screen.  However, you can draw the screen's contents to another
        surface using this method by explicitely supplying a `surface` argument.
        '''

        # If no surface is explicitly given, draw to this screen's surface
        if surface is None:
            surface = self._surface

        # Draw the background
        surface.fill(self._color)
        if self._image is not None:
            surface.blit(self._image, self._image_rect)

        # Create a sprite to hold the drawings
        canvas_sprite = pygame.sprite.Sprite()
        canvas_sprite.image = pygame.Surface((self._width, self._height), 
                                             pygame.SRCALPHA)
        canvas_sprite.image.blit(self._canvas, (0, 0))
        canvas_sprite.image.blit(self._update_drawings, (0, 0))
        canvas_sprite.rect = pygame.Rect(0, 0, self._width, self._height)
        self.add(canvas_sprite, layer=-1)

        # Draw the sprites
        ret = pygame.sprite.LayeredUpdates.draw(self, surface)

        # Remove the drawings sprite
        self.remove(canvas_sprite)

        return ret
    
    
    def redraw (self):
        '''
        Update and draw the screen in the open window.

        This method calls update() and draw(), then flips the changes to the 
        visible screen.
        '''

        self.update()
        self.draw()
        pygame.display.flip()


    ### Methods to add event handlers

    def on_key_press (self, func, key=None):
        '''
        Add a function that will be called when a keyboard key is pressed while
        this screen is active.

        You can provide the following arguments for the function `func`:
         - `key` - will provide the name of the key

        The `key` is a string specifying which key this function applies to.  If
        no `key` is given, then this function will apply any key that does not 
        have a handler.
        '''

        if key is None:
            if func is None:
                self._key_press_funcs.pop(None, None)
            else:
                self._key_press_funcs[None] = func
        elif isinstance(key, str):
            if func is None:
                self._key_press_funcs.pop(pygame.key.key_code(key), None)
            else:
                self._key_press_funcs[pygame.key.key_code(key)] = func
        elif isinstance(key, int):
            if func is None:
                self._key_press_funcs.pop(key, None)
            else:
                self._key_press_funcs[key] = func
        else:
            try:
                for k in key:
                    self.on_key_press(func, k)
            except:
                raise ValueError("Invalid key!") from None


    def on_key_release (self, func, key=None):
        '''
        Add a function that will be called when a keyboard key is released while
        this screen is active.

        You can provide the following arguments for the function `func`:
         - `key` - will provide the name of the key

        The `key` is a string specifying which key this function applies to.  If
        no `key` is given, then this function will apply any key that does not 
        have a handler.
        '''

        if key is None:
            if func is None:
                self._key_release_funcs.pop(None, None)
            else:
                self._key_release_funcs[None] = func
        elif isinstance(key, str):
            if func is None:
                self._key_release_funcs.pop(pygame.key.key_code(key), None)
            else:
                self._key_release_funcs[pygame.key.key_code(key)] = func
        elif isinstance(key, int):
            if func is None:
                self._key_release_funcs.pop(key, None)
            else:
                self._key_release_funcs[key] = func
        else:
            try:
                for k in key:
                    self.on_key_release(func, k)
            except:
                raise ValueError("Invalid key!") from None

    
    def on_key_hold (self, func, key=None):
        '''
        Add a function that will be called when a keyboard key is held down while
        this screen is active.

        The given function will be called once for every frame of the event loop
        that passes while the key is held down.

        You can provide the following arguments for the function `func`:
         - `key` - will provide the name of the key

        The `key` is a string specifying which key this function applies to.  If
        no `key` is given, then this function will apply any key that does not 
        have a handler.
        '''

        if key is None:
            if func is None:
                self._key_hold_funcs.pop(None, None)
            else:
                self._key_hold_funcs[None] = func
        elif isinstance(key, str):
            if func is None:
                self._key_hold_funcs.pop(pygame.key.key_code(key), None)
            else:
                self._key_hold_funcs[pygame.key.key_code(key)] = func
        elif isinstance(key, int):
            if func is None:
                self._key_hold_funcs.pop(key, None)
            else:
                self._key_hold_funcs[key] = func
        else:
            try:
                for k in key:
                    self.on_key_hold(func, k)
            except:
                raise ValueError("Invalid key!") from None


    def on_click (self, func, button="left"):
        '''
        Add a function that will be called when the mouse clicks anywhere on
        this screen while it is active.

        You can provide the following arguments for the function `func`:
         - `x` - will provide x-coordinate of the click
         - `y` - will provide y-coordinate of the click
         - `pos` - will provide a tuple of the coordinates (x and y) of the click
         - `button` - will provide the name of the mouse button used to click
        '''

        # Convert the button string to a button number
        if isinstance(button, str):
            try:
                button = pgputils.mouse_button_map[button]
            except KeyError:
                raise ValueError("Invalid button!")

        # If a button is valid, add the function to the appropriate button
        if 1 <= button <= 5:
            self._click_funcs[button - 1] = func
        else:
            raise ValueError("Invalid button!")


    def on_release (self, func, button="left"):
        '''
        Add a function that will be called when the mouse releases a button
        anywhere on this screen while it is active.

        You can provide the following arguments for the function `func`:
         - `x` - will provide x-coordinate of the click
         - `y` - will provide y-coordinate of the click
         - `pos` - will provide a tuple of the coordinates (x and y) of the click
         - `button` - will provide the name of the mouse button used to click
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


    def on_mouse_move (self, func):
        '''
        Add a function that will be called when the mouse is moved anywhere on
        this screen while it is active.

        You can provide the following arguments for the function `func`:
         - `x` - will provide x-coordinate of the click
         - `y` - will provide y-coordinate of the click
         - `pos` - will provide a tuple of the coordinates (x and y) of the click
        '''

        # Add the function
        self._mouse_move_func = func


    def on_timer (self, func, delay, repeat=False):
        '''
        Call a function after a given amount of time (in milliseconds).

        The function `func` will be called after `delay` milliseconds.  `func`
        must be a function that takes no arguments.  The `delay` must be a 
        positive number.

        If `repeat` is `True`, then the timer will run repeatedly.  That is,
        the timer will restart every time that it expires.

        An event ID will be returned that can be used with the `cancel_timer()`
        method to stop the timer.

        If the screen is closed this timer will be closed.  To prevent this
        behaviour, create a global timer on the event loop.
        '''

        # Check that the arguments are valid
        if not callable(func):
            raise ValueError("The function is not callable!")
        if delay <= 0:
            raise ValueError("The delay must be positive!")

        # Get a custom pygame event type and start the timer
        event_id = pygame.event.custom_type()
        self._timers[event_id] = func
        pygame.time.set_timer(event_id, delay, not repeat)

        # Return the custom event type for cancelling
        return event_id


    def cancel_timer (self, event_id):
        '''
        Stop the timer with the given event ID.

        `event_id` must be an event ID that was returned from the `on_timer()`
        method for this EventLoop.
        '''

        # Check that the argument is a valid event type
        if event_id not in self._timers:
            raise ValueError("There is no screen timer with that event ID!")

        # Stop the timer
        pygame.time.set_timer(event_id, 0)
        self._timers.pop(event_id)


    ### Methods to convert to and from pygame coordinates

    def to_pygame_coordinates (self, x, y=None):
        '''
        Convert a point in this screen's coordinate space to the same point 
        in the pygame coordinate space.
        '''
        
        # If only one argument is given, expand it into x and y
        if y is None:
            x, y = x

        # Calcuate the pygame point and return it as a vector
        pygame_x = x + self._width / 2
        pygame_y = self._height / 2 - y
        return pygame.Vector2(pygame_x, pygame_y)

    def from_pygame_coordinates (self, pygame_x, pygame_y=None):
        '''
        Convert a point in the pygame coordinate space to the same point in 
        this screen's coordinate space.
        '''

        # If only one argument is given, expand it into x and y
        if pygame_y is None:
            pygame_x, pygame_y = pygame_x

        # Calculate the coordinates for this screen and return it as a tuple
        x = pygame_x - self._width / 2
        y = self._height / 2 - pygame_y
        return x, y


################################################################################
#                               GLOBAL FUNCTIONS
################################################################################

def get_active_screen ():
    '''
    Return the currently active screen.

    This will return None if no screen is active.
    '''

    return Screen._active


def to_pygame_coordinates (x, y=None):
    '''
    Convert a point in the active screen's coordinate space to the same point 
    in the pygame coordinate space.
    '''

    if Screen._active is None:
        raise RuntimeError("No screen is active!")
    return Screen._active.to_pygame_coordinates(x, y)


def from_pygame_coordinates (pygame_x, pygame_y=None):
    '''
    Convert a point in the pygame coordinate space to the same point in 
    the active screen's coordinate space.
    '''

    if Screen._active is None:
        raise RuntimeError("No screen is active!")
    return Screen._active.from_pygame_coordinates(pygame_x, pygame_y)
    

# What is included when importing *
__all__ = [
    "Screen", 
    "get_active_screen", 
    "to_pygame_coordinates", 
    "from_pygame_coordinates"
]

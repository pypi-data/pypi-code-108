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
from pygame.locals import *

from pygameplus import pgputils
from pygameplus.screen import get_active_screen


################################################################################
#                               EVENTLOOP CLASS
################################################################################

class EventLoopTerminated (Exception):
    '''
    Will be raised when the event loop is killed.
    '''

    pass

class EventLoop (object):
    '''
    An EventLoop represents the loop that is continuously running in the
    background of a game and handles any events that occur.

    EventLoop objects store the following information about an event loop:
     - Whether or not the event loop is running
     - The frame rate that the loop should try to maintain

    Methods are provided for the following:
     - To get or change the frame rate
     - To start and stop the loop
    '''

    def __init__ (self, frame_rate=40):
        '''
        Create an EventLoop object.

        EventLoop objects should generally not be created explicitly using the
        EventLoop() constructor.  Instead, use the start_event_loop() and
        end_event_loop() functions.
        '''

        # Attributes that store the event loops current state
        self._running = False
        self._frame_rate = frame_rate

        # Attribute to hold which sprites are currently being clicked on
        self._clicked_sprites = [None for _ in range(5)]

        # Attribute to hold timer event handlers
        self._timers = {}


    @property
    def frame_rate (self):
        '''
        The frame rate of the event loop.

        The frame rate is the number of iterations the event loop should try to
        accomplish in a second.
        '''

        return self._frame_rate

    @frame_rate.setter
    def frame_rate (self, new_frame_rate):

        # Ensure the the given frame rate is a number
        try:
            new_frame_rate = float(new_frame_rate)
        except:
            raise ValueError("The frame rate must be a number!") from None

        # Ensure that the given frame rate is positive
        if new_frame_rate <= 0:
            raise ValueError("The frame rate must be positive!")

        self._frame_rate = new_frame_rate


    @property
    def frame_delay (self):
        '''
        The frame delay of the event loop.

        The frame delay is the amount of time in milliseconds that the event loop
        should try to have between the start of each iteration of the loop.  The
        frame delay is 1000 divided by the frame rate.
        '''

        return 1000 / self._frame_rate

    @frame_delay.setter
    def frame_delay (self, new_delay):
        '''
        Change the frame delay of the event loop.

        The frame delay is the amount of time in milliseconds that the event loop
        should try to have between the start of each iteration of the loop.  The
        frame delay is 1000 divided by the frame rate.
        '''

        # Ensure the the given frame delay is a number
        try:
            new_delay = float(new_delay)
        except:
            raise ValueError("The frame delay must be a number!") from None

        # Ensure that the given frame delay is positive
        if new_delay <= 0:
            raise ValueError("The frame delay must be positive!")
        
        self._frame_rate = 1000 / new_delay


    @property
    def running (self):
        '''
        Whether or not the event loop is running.  (Read-only)

        Use `start()` and `stop()` to control the loop.
        '''

        return self._running

    @running.setter
    def running (self, new_setting):

        raise AttributeError("This property is read-only!  Use start() and stop() to control the event loop.")


    def start (self):
        '''
        Start the event loop.
        '''

        self._running = True
        clock = pygame.time.Clock()
        while self._running:
            # Force the loop to wait if the entire frame delay has not passed 
            # since the start of the last iteration
            clock.tick(self._frame_rate)

            # Get the active screen
            screen = get_active_screen()
            if screen is None:
                continue

            # Loop through the events that have occurred over the past frame
            for event in pygame.event.get():
                # If the close button is clicked, end the loop
                if event.type == QUIT:
                    self._running = False
                    pygame.display.quit()
                    return

                # If a key was pressed, call any associated handlers
                elif event.type == KEYDOWN:
                    if event.key in screen._key_press_funcs:
                        pgputils.call_with_args(screen._key_press_funcs[event.key],
                                        key=pygame.key.name(event.key))
                    elif None in screen._key_press_funcs:
                        pgputils.call_with_args(screen._key_press_funcs[None],
                                        key=pygame.key.name(event.key))

                # If a key was released, call any associated handlers
                elif event.type == KEYUP:
                    if event.key in screen._key_release_funcs:
                        pgputils.call_with_args(screen._key_release_funcs[event.key],
                                        key=pygame.key.name(event.key))
                    elif None in screen._key_release_funcs:
                        pgputils.call_with_args(screen._key_release_funcs[None],
                                        key=pygame.key.name(event.key))

                # If a mouse button is clicked down, call any associated handlers
                elif event.type == MOUSEBUTTONDOWN:
                    button = event.button
                    button_name = pgputils.mouse_button_reverse_map[button]
                    pos = screen.from_pygame_coordinates(event.pos)
                    sprites = screen.sprites()
                    sprites.reverse()
                    for sprite in sprites:
                        func = sprite._click_funcs[button - 1]
                        if func is None:
                            continue
                        method = sprite._click_methods[button - 1]
                        bleeds = sprite._click_bleeds[button - 1]
                        if sprite.is_touching_point(pos, method=method):
                            self._clicked_sprites[button - 1] = sprite
                            if sprite._click_funcs[button - 1] is not None:
                                pgputils.call_with_args(sprite._click_funcs[button - 1],
                                                pos=pos, x=pos[0], y=pos[1], 
                                                button=button, sprite=sprite)
                            if not bleeds:
                                break
                    if screen._click_funcs[button - 1] is not None:
                        pgputils.call_with_args(screen._click_funcs[button - 1],
                                        pos=pos, x=pos[0], y=pos[1], 
                                        button=button_name)

                # If a mouse button is released, call any associated handlers
                elif event.type == MOUSEBUTTONUP:
                    button = event.button
                    button_name = pgputils.mouse_button_reverse_map[button]
                    pos = screen.from_pygame_coordinates(event.pos)
                    sprite = self._clicked_sprites[button - 1]
                    if sprite and sprite._release_funcs[button - 1] is not None:
                        pgputils.call_with_args(sprite._release_funcs[button - 1],
                                        pos=pos, x=pos[0], y=pos[1], 
                                        button=button_name, sprite=sprite)
                    self._clicked_sprites[button - 1] = None
                    if screen._release_funcs[button - 1] is not None:
                        pgputils.call_with_args(screen._release_funcs[button - 1],
                                        pos=pos, x=pos[0], y=pos[1], 
                                        button=button_name)

                # If the mouse moves and a button is down, call any associated
                # drag handlers
                elif event.type == MOUSEMOTION:
                    pos = screen.from_pygame_coordinates(event.pos)
                    for button, sprite in enumerate(self._clicked_sprites, 1):
                        button_name = pgputils.mouse_button_reverse_map[button]
                        if sprite and sprite._drag_funcs[button - 1] is not None:
                            pgputils.call_with_args(sprite._drag_funcs[button - 1],
                                            pos=pos, x=pos[0], y=pos[1], 
                                            button=button_name, sprite=sprite)
                    if screen._mouse_move_func is not None:
                        pgputils.call_with_args(screen._mouse_move_func,
                                        pos=pos, x=pos[0], y=pos[1])
                    

                # If this event type matches a screen timer, call it's handler.
                elif event.type in screen._timers:
                    pgputils.call_with_args(screen._timers[event.type])

                # If this event type matches a global timer, call it's handler.
                elif event.type in self._timers:
                    pgputils.call_with_args(self._timers[event.type])

            # Get a dictionary containing the state of the keyboard keys
            keys = pygame.key.get_pressed()
            key_count = keys.count(1)

            # Loop through the keyhold handlers and call any for which the 
            # key is down
            try:
                for key_code, func in screen._key_hold_funcs.items():
                    if key_code is None and key_count > 0:
                        pgputils.call_with_args(func)
                    elif key_code is not None and keys[key_code]:
                        pgputils.call_with_args(func, key=pygame.key.name(key_code))
            except RuntimeError:
                pass

            # Update the active screen
            screen.update()
            screen.draw()
            pygame.display.flip()


    def stop (self):
        '''
        Stop the event loop.

        This does not immediately end the event loop, but will end the loop at the end of the current iteration.
        
        This will have no effect if the event loop has not started.
        '''

        self._running = False


    def kill (self):
        '''
        Terminate the event loop immediately.

        This will raise an EventLoopTerminated exception.
        '''

        raise EventLoopTerminated()


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
            raise ValueError("There is no global timer with that event ID!")

        # Stop the timer
        pygame.time.set_timer(event_id, 0)
        self._timers.pop(event_id)


################################################################################
#                               GLOBAL FUNCTIONS
################################################################################

# Creates and EventLoop instance to use with the functions below.
_event_loop = EventLoop()

def start_event_loop (frame_rate=None):
    '''
    Start the event loop to handle any interactions with the user.

    The frame rate is the number of iterations the event loop should try to
    accomplish in a second.
    '''

    if frame_rate is not None:
        _event_loop.frame_rate = frame_rate
    _event_loop.start()


def stop_event_loop ():
    '''
    End the event loop.

    This does not immediately end the event loop, but will end the loop at the 
    end of the current iteration.
        
    This will have no effect if the event loop has not started.
    '''

    _event_loop.stop()


def get_event_loop ():
    '''
    Returns the event loop object.

    This is really only necessary if you need to change the frame rate of the
    event loop while it is running or it you need to kill the event loop.
    '''

    return _event_loop


# What is included when importing *
__all__ = [
    "start_event_loop",
    "stop_event_loop",
    "get_event_loop"
]

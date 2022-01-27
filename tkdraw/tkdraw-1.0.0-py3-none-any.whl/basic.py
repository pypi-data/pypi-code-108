"""Basic interface to the tkdraw.screen module.

This module provides four elementary functions to:

- open a window
- plot a pixel at a given position in the window
- refresh the window (at any step of your program)
- wait for the user to close the window

All these functions return nothing (None).
A python exception (`AssertionError`, `InterruptedError` or `ValueError`) will
be raised if any precondition of those functions is not met, and an explicit
error message will be given.

Test this module using `python3 -m tkdraw.basic`

Example:
    ```py
    import tkdraw.basic as graph

    # size of the window (pixels)
    HEIGHT = 400
    WIDTH = 600

    # open the window
    graph.open_win(HEIGHT, WIDTH)

    # plot a horizontal line in the middle
    for j in range(WIDTH):
        graph.plot(HEIGHT//2, j)

    # wait for the user to close the window
    graph.wait()
    ```

Copyright 2018-2021, Vincent Loechner.
Distributed under the MIT license (see LICENSE)
https://github.com/vincentloechner/pytkdraw.git
"""
import tkdraw.screen as tkd


# window (global): main window of this simplified version
_WINDOW = None


def open_win(height, width, zoom=1):
    """Open a window.

    Args:
        height (int): height of the window (in pixels)
        width (int): width of the window (in pixels)
        zoom (int, optional): zoom value (default: 1). A value of 2 will
            display 2x2 screen pixels wide points when plotting.

    Raises:
        AssertionError: if the window was already opened
    """
    # pylint: disable=global-statement
    # I really want to use a global in this module, to make those functions
    # easier to use.
    global _WINDOW
    assert not _WINDOW, "ERROR: function open() was called twice!"
    _WINDOW = tkd.Screen((height, width), zoom, grid=False)


def plot(line, column, color="black"):
    """Plot a pixel at position (line, column).

    Usage notice : the effective rendering of this pixel will only be done once
    you call the refresh() or wait() function.

    Args:
        line (int): vertical position of the pixel to plot.
            (0, 0) is the top-left position.
        column (int): horizontal position of the pixel to plot
        color (str, optional): a color (default value: "black").
            This string shall contain a tkinter-compatible color string,
            for a list of predefined color names see for example:
            <https://www.wikipython.com/tkinter-ttk-tix/summary-information/\
colors/>.
            You can also specify an RGB-style color such as "#FF0000" for red.

    Raises:
        AssertionError: if the window was not opened
        InterruptedError: if the window was closed by the user
        ValueError: if not ((0 <= line < height) and (0 <= column < width))
    """
    assert _WINDOW, "ERROR: trying to plot in a non-existing window!"
    _WINDOW.draw_tile((line, column), color=color, refresh=False)


def refresh():
    """Refresh the window.

    All plots that you did before this call will be displayed for real in the
    window.

    Args:
        None

    Raises:
        AssertionError: if the window was not opened
        InterruptedError: if the window was closed by the user
    """
    assert _WINDOW, "ERROR: trying to refresh a non existing window!"
    _WINDOW.refresh()


def wait():
    """Wait for the user to close the window.

    This function is blocking, it will return once the user has (1) closed the
    window using the mouse, or (2) hit the 'escape' or 'q' key.

    Note:
        You have to call this function before the end of your program, or you
        won't be able to see the content of the window. If you don't call this
        function, the window will just disapear when the program exits.

    Args:
        None

    Raises:
        AssertionError: if the window was not opened
    """
    # pylint: disable=global-statement
    # I want to use a global in this module, to make those functions easier to
    # use
    global _WINDOW

    assert _WINDOW, "ERROR: trying to close a non existing window!"
    _WINDOW.refresh()
    while True:
        evt = _WINDOW.wait_event()
        if evt[0] == "END":
            break
        if evt[0] == "key" and (evt[1] == "Escape" or evt[1] == "q"):
            break
        # ignore all other events
    _WINDOW.close()
    _WINDOW = None


##############################################################################
# test module
##############################################################################
if __name__ == "__main__":
    HEIGHT = 300
    WIDTH = 400
    open_win(HEIGHT, WIDTH)
    for i in range(HEIGHT):
        for j in range(WIDTH):
            plot(i, j,
                 color=["black", "red", "white", "green"][((i+j)//15) % 4])
        refresh()
    wait()

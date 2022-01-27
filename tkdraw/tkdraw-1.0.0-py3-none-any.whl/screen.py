"""Simple draw graphical user interface (GUI) based on tkinter, synchroneous.

Test this module using `python3 -m tkdraw.screen`

The online documentation is available under python3:
```
$ python3
>>> import tkdraw.screen as tkd
>>> help(tkd.Screen)
or
>>> help(tkd.Screen.FUNC_NAME)
```

Copyright 2018-2021, Vincent Loechner.
Distributed under the MIT license (see LICENSE)
https://github.com/vincentloechner/pytkdraw.git
"""

import tkinter as tk
import queue


# pylint: disable=too-many-ancestors
# The tk canvas has too many already.
class Screen(tk.Canvas):
    """Main class for a window containing a board (2D grid).

    The 2D grid is pythonesque: always starts at top-left position (0, 0), in
    row-major order, ends at (height-1, width-1) included. All coordinates and
    sizes are expressed as iterable objects (a tuple or a list for example) of
    two integers.

    To open a window containing just an array of pixels, set the `pixels`
    parameter to 1 and `grid` to False.
    This class inherits from tkinter's canvas class.

    Example:
        ```
        import tkdraw.screen
        g = tkdraw.screen.Screen()
        g.message("hello")
        g.wait_event()
        g.close()
        ```
    Args:
        size ([int, int]): a couple (height, width) specifying the size of
            the grid (default: (8, 8))
        pixels (int): number of pixels of a square (default: 100)
        grid (bool): if True, prints a one-pixel grid to separate the tiles:
            horizontal and vertical lines (default: True) - the real size of
            the window is also increased by one pixel to draw the right/bottom
            lines


    Returns:
        The window object.

    Notes:
        Since this class inherits from tkinter's canvas class, more inherited
            documentation will be displayed below this paragraph. You can
            directly call the canvas methods to perform advanced drawings in
            this canvas (expert mode, be warned that a couple of coordinates
            (y, x) in tkdraw has to be transformed into two integers x+1, y+1
            in tkinter). You may refer to the documentation of tkinter
            describing the Canvas widget here:
            <https://docs.python.org/3/library/tkinter.html>
    """

    # pylint: disable=too-many-instance-attributes
    # it is reasonable here, and many are private.
    def __init__(
        self, size=(8, 8), pixels=100, grid=True
    ):
        # some private methods below, to react to asynchronous events:

        # private: the user clicked on a square
        def _click(evenement):
            # min to handle user clicking on the last pixel:
            i = min((evenement.y-1)//self.pixels, self.size[0]-1)
            j = min((evenement.x-1)//self.pixels, self.size[1]-1)
            # add the event (line, column) to the queue
            self._eventq.put(("click", (i, j)))
            # and leave the mainloop
            self.root.quit()

        # private: the user hit a key
        def _key(evenement):
            # put the event in the queue
            self._eventq.put(("key", evenement.keysym))
            # and leave the mainloop
            self.root.quit()

        # private: the user closed the window
        def _async_end():
            # put the END event in the queue
            self._eventq.put(("END", None))
            # and close
            self.close()

        # private: regularily check if some events are pending in the queue
        # and wake up
        def _checke():
            self._after_id = self.root.after(1000, _checke)
            # stop mainloop
            self.root.quit()

        #################################
        # INIT
        self.size = size
        self.pixels = pixels
        self._after_id = None
        self._gap = int(grid)  # 1 more pixel if grid is True

        self._eventq = queue.Queue()
        self._idd = None
        self._souris = (0, 0)

        self.root = tk.Tk()
        # you can create other widgets here if you want to
        # self.frame = tk.Frame(root)

        # creates THE canvas:
        tk.Canvas.__init__(
                self,
                self.root,
                height=self.size[0]*self.pixels+self._gap,
                width=self.size[1]*self.pixels+self._gap,
                background="#ddd",
                takefocus=True,
                borderwidth=0,
                highlightthickness=1)
        self.pack()
        # self.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.focus_set()

        # binds the click function to the click event
        self.bind("<Button-1>", _click)
        # binds the key function to the keypress event
        self.bind("<Any-KeyPress>", _key)

        # checke will be called once per second
        self._after_id = self.root.after(1000, _checke)
        # ensure that async_end is called if the window is killed
        self.root.protocol("WM_DELETE_WINDOW", _async_end)

        # draw the original state
        if grid:
            self.draw_grid()

    def __enter__(self):
        """Internal: With -as: statement compatibility."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Internal: With -as: statement compatibility."""
        self.close()

    def __del__(self):
        """Internal: if the object is freeed by python for some reason."""
        self.close()

    def close(self):
        """Close this window.

        Args:
            None

        Returns:
            None
        """
        if self._after_id is not None:
            self.root.after_cancel(self._after_id)
            self._after_id = None
        if self.root is not None:
            self.root.destroy()
            self.root = None

    def message(self, message):
        """Display a message in a box and wait for the user to click somewhere.

        Args:
            message (str): the string to print

        Returns:
            bool: True if the user triggered a normal event, False if the user
                closed the window abruptly.
        """
        # private: the user clicked in the box
        # pylint: disable=unused-argument
        # it's an event, don't care which one.
        def _c(event):
            self._eventq.put("ok")
            self.root.quit()

        if not self.root:
            raise InterruptedError("window killed")
        msg = tk.Message(
                self.root, text=message,
                padx=20, pady=20,
                relief=tk.RAISED, borderwidth=5,
                )
        # mouse click:
        msg.bind("<Button-1>", _c)
        # m.grid(row=0, column=0)
        msg.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        while True:
            evt = self.wait_event()
            if evt[0] == "END":
                # the window has been closed
                # put the end msg back in the queue and return False
                self._eventq.put(evt)
                return False
            # all the other events just close the message box and return True:
            msg.destroy()
            return True

    ###########################################################################
    # HIGH LEVEL INTERFACE                                                    #
    # This function can be used to print whole standard boards.               #
    # Matrices should contain integers (-> representing pieces colors/players)#
    # or the None special value (-> nothing there)                            #
    ###########################################################################

    # by default define those 10 colors:
    DEFAULT_COLOR = ["black", "white", "red", "green", "blue",
                     "yellow", "cyan", "magenta", "orange", "darkgrey"]
    """A list of ten colors used for ten players identified by numbers."""

    def draw_grid(
        self, matrix=None, grid=True
    ):
        """Draw a complete grid of pieces, using the 10 default colors.

        Args:
            matrix (list of list of int): the players pieces matrix, of the
                specified size. If matrix is None (default), just ignores it.
            grid (boolean): if True (default) draws a horizontal+vertical grid
                to separate the tiles.

        Returns:
            list of int: the graphical objects that were created for the pieces
                (grid excluded).
        """
        if not self.root:
            raise InterruptedError("window killed")
        # erase everything for a start
        self.delete(tk.ALL)
        # gap is used by draw_tile to fill the inside of a tile (including
        # borders, or not
        if grid:
            for i in range(self.size[0]+self._gap):
                self.create_line(1, i*self.pixels+1,
                                 self.size[1]*self.pixels+1, i*self.pixels+1,
                                 width=1)
            for i in range(self.size[1]+self._gap):
                self.create_line(i*self.pixels+1, 1,
                                 i*self.pixels+1,
                                 self.size[0]*self.pixels+1+self._gap,
                                 width=1)
        # draw the pieces
        lobj = []
        if matrix is not None:
            for i in range(self.size[0]):
                for j in range(self.size[1]):
                    if matrix[i][j] is not None:
                        lobj.append(self.draw_piece((i, j), matrix[i][j],
                                    refresh=False))
        # update just once at the end, for performance
        self.update()
        return lobj

    def erase(
        self
    ):
        """Erase everything from the window.

        All graphical objects that were created are deleted.

        Args:
            None

        Returns:
            None
        """
        if not self.root:
            raise InterruptedError("window killed")
        self.delete(tk.ALL)
        # redraw the grid if it was there:
        if self._gap == 1:
            self.draw_grid()

    ###########################################################################
    # INTERMEDIATE LEVEL INTERFACE                                            #
    # draw various objects on a board (2D grid)                               #
    ###########################################################################
    def draw_piece(
        self, pos, player=0,
        color=None,
        refresh=True
    ):
        """Draw a piece in position pos=(line, column), player-colored.

        Usage notice: don't use this function if your tiles are too small, you
        won't see the piece.

        Args:
            pos ([int, int]): a couple (line, column) specifying the grid
                position. (0, 0) = top-left position.
            player (int, optional): player number (default: 0)
                player is used only if color is NOT given.
            color (str, optional): fill color of the piece. If a color is
                given, player is ignored.
            refresh (bool): refresh the window after drawing (default: True)

        Returns:
            int: the ID of the graphical object (circle) that was created.
        """
        if not self.root:
            raise InterruptedError("window killed")
        if color is None:
            if isinstance(player, int):
                color = self.DEFAULT_COLOR[player % len(self.DEFAULT_COLOR)]
            else:
                color = self.DEFAULT_COLOR[0]

        bord = self.pixels//10+1
        i, j = pos
        if not (0 <= i < self.size[0] and 0 <= j < self.size[1]):
            raise ValueError("trying to draw outside the window!")

        obj = self.create_oval(j*self.pixels+bord+1,
                               i*self.pixels+bord+1,
                               (j+1)*self.pixels-bord+1,
                               (i+1)*self.pixels-bord+1,
                               width=1, fill=color)
        if refresh:
            self.update()
        return obj

    def move_piece(
        self, obj, pos, refresh=True
    ):
        """Move a piece (obj ID) in grid position pos=(line, column).

        Args:
            obj (int): a previously created piece ID
            pos ([int, int]): new grid position, a couple (line, column)
            refresh (bool, optional): refresh the window after drawing
                (default: True)

        Returns:
            None
        """
        if not self.root:
            raise InterruptedError("window killed")

        i, j = pos
        if not (0 <= i < self.size[0] and 0 <= j < self.size[1]):
            raise ValueError("trying to move a piece outside the window!")
        bord = self.pixels//10+1
        self.coords(
            obj,
            j*self.pixels+bord+1,
            i*self.pixels+bord+1,
            (j+1)*self.pixels-bord+1,
            (i+1)*self.pixels-bord+1
            )
        if refresh:
            self.update()

    def draw_tile(
        self, pos,
        color="black",
        border=0,
        refresh=True
    ):
        """Fill a tile in position pos=(line, column) with a color.

        Args:
            pos ([int, int]): grid position (line, column)
            color (str, optional): color of the tile (default: "black")
            border (int, optional): border thickness (default: 0) - borders may
                overlap over neighboring tiles
            refresh (bool): refresh the window after drawing (default: True)

        Returns:
            int: the ID of the colored tile
        """
        if not self.root:
            raise InterruptedError("window killed")

        i, j = pos
        if not (0 <= i < self.size[0] and 0 <= j < self.size[1]):
            raise ValueError("trying to fill a tile outside the window!")

        obj = self.create_rectangle(j*self.pixels+1+self._gap,
                                    i*self.pixels+1+self._gap,
                                    (j+1)*self.pixels+1,
                                    (i+1)*self.pixels+1,
                                    width=border, fill=color)
        if refresh:
            self.update()
        return obj

    def move_tile(
        self, obj, pos, refresh=True
    ):
        """Move a colored tile to another grid position.

        Args:
            obj (int): a previously created tile ID
            pos ([int, int]): new position in the grid (line, column)
            refresh (bool, optional): refresh the window after drawing
                (default: True)

        Returns:
            None
        """
        if not self.root:
            raise InterruptedError("window killed")

        i, j = pos
        if not (0 <= i < self.size[0] and 0 <= j < self.size[1]):
            raise ValueError("trying to move a tile outside the window!")
        self.coords(
            obj,
            j*self.pixels+1++self._gap,
            i*self.pixels+1++self._gap,
            (j+1)*self.pixels+1,
            (i+1)*self.pixels+1
            )
        if refresh:
            self.update()

    ###########################################################################
    # low level interface:                                                    #
    # draw pixels, lines, circles, etc.                                       #
    ###########################################################################
    # pylint: disable=too-many-arguments
    # self doesn't count, and 3 are options
    def draw_line(
        self, x_1, x_2, color="black", thickness=1, refresh=True
    ):
        """Draw a line between x_1=(l1, c1) and x_2=(l2, c2) (excluded).

        Args:
            x_1 ([int, int]): pixel-wise positions (line, column) of the first
                point. (0,0) = top-left position.
            x_2 ([int, int]): pixel-wise positions (line, column) of the second
                point, excluded.
            color (str, optional): line color (default: "black")
            thickness (int, optional): thickness of the line (default: 1)
            refresh (bool, optional): refresh the window after drawing
                (default: True)

        Returns:
            int: the ID of the graphical object that was created.
        """
        if not self.root:
            raise InterruptedError("window killed")

        obj = self.create_line(x_1[1]+1, x_1[0]+1, x_2[1], x_2[0],
                               width=thickness, fill=color)
        if refresh:
            self.update()
        return obj

    def draw_circle(
        self, x_1, x_2,
        color="black", border=1, refresh=True
    ):
        """Draw a circle in the bounding box of x_1=(l1,c1) and x_2 (excluded).

        Args:
            x_1 ([int, int]): pixel-wise positions (line, column) of the first
                point. (0,0) = top-left position.
            x_2 ([int, int]): pixel-wise positions (line, column) of the second
                point, excluded.
            color (str, optional): color of the inside (default: "black").
                If color == None, don't fill the circle.
            border (int, optional): border thickness (default: 1) - borders can
                overflow over the given pixels coordinates
            refresh (bool, optional): refresh the window after drawing
                (default: True)

        Returns:
            int: the ID of the graphical object that was created.
        """
        if not self.root:
            raise InterruptedError("window killed")

        obj = self.create_oval(x_1[1]+1, x_1[0]+1, x_2[1], x_2[0],
                               width=border, fill=color)
        if refresh:
            self.update()
        return obj

    def draw_text(
        self, position, text,
        color="black", fontname="Purisa", fontsize=11, refresh=True
    ):
        """Draw a text centered at a given position=(line, column).

        Args:
            position ([int, int]): pixel-wise position (line, column).
                (0,0) = top-left position.
            text (str): text to print
            color (str, optional): text color (default: "black")
            fontname (str, optional): font name (default: "Purisa")
            fontsize (int, optional): font size (default: 11pt)
            refresh (bool, optional): refresh the window after drawing
                (default: True)

        Returns:
            int: the ID of the graphical object that was created.
        """
        if not self.root:
            raise InterruptedError("window killed")

        obj = self.create_text(position[1]+1, position[0]+1,
                               text=text,
                               font=(fontname, fontsize),
                               fill=color)
        if refresh:
            self.update()
        return obj

    # pylint: disable=invalid-name
    # I'm too lazy to write 'background'.
    def bg(
        self, obj, before=1, refresh=True
    ):
        """Send a graphical object (ID) to the background.

        Args:
            obj (int): object ID returned by an object creation method
            before (int, optional): the object behind which to hide (default:
                1 = all)
            refresh (bool, optional): refresh the window after drawing
                (default: True)

        Returns:
            None
        """
        if not self.root:
            raise InterruptedError("window killed")
        # se met en fond, derrière l'objet 'before':
        self.tag_lower(obj, before)
        if refresh:
            self.update()

    def refresh(
        self
    ):
        """Refresh all objects previously drawn in the window.

        Note:
            You can create several successive objects without refreshing by
                passing the extra argument "refresh=False" to the drawing
                functions, and then refresh only once using this function.
                Good for speed, especially if you draw many things.

        Args:
            None

        Returns:
            None
        """
        if not self.root:
            raise InterruptedError("window killed")

        self.update()

    # pylint: disable=invalid-name
    # I'm too lazy to write 'remove'.
    def rm(
        self, obj, refresh=True
    ):
        """Delete a graphical object.

        Args:
            obj (int): an object ID (returned by an object creation method)
            refresh (bool, optional): refresh the window after drawing
                (default: True)

        Returns:
            None
        """
        if not self.root:
            raise InterruptedError("window killed")

        self.delete(obj)
        if refresh:
            self.update()

    ###########################################################################
    # Main I/O function                                                       #
    ###########################################################################
    def wait_event(self, delay=None):
        """Wait for the user to interact with the window.

        The tracked events are only keypress and mouse click (left button).

        Args:
            delay (int, optional): waiting time in ms (default: wait forever)

        Returns:
            If the delay expires (when given)

            - `None`

            Else, returns a couple, the first element being always a string:

            - `("click", (line, column))`

                if the user clicks on a tile of the board, where (line, column)
                    are the integer coordinates of the clicked tile

            - `("key", letter)`

                if the user hits a key, where letter is a string containing a
                    description of the key. If you're looking for a specific
                    key, you can give a try to the demo - running
                    `'python3 -m tkdraw'` will print all occuring events in the
                    console

            - `("END", None)`

                if the user closes the window
        """
        # private: called when the timer expires
        def delay_expire():
            self._eventq.put(None)
            self._idd = None
            self.root.quit()

        # trigger the timer
        self._idd = None
        if delay is not None:
            if not self.root:
                raise InterruptedError("window killed")
            self._idd = self.root.after(delay, delay_expire)
        # This is Tk's main loop
        # checks the events and get out if something happens
        while True:
            ####################
            try:
                # get something from the event queue
                ret = self._eventq.get(False)
                # cancels the timer if I got something
                if self._idd is not None and self.root is not None:
                    self.root.after_cancel(self._idd)
                return ret
            except queue.Empty:
                # no event in the queue, continue waiting (go to mainloop)
                pass
            ####################
            if not self.root:
                raise InterruptedError("window killed")
            # back to the mainloop, it will stop if I get an event
            self.root.mainloop()
            ####################

    def mouse_position(self):
        """Return the mouse position (pixel-wise).

        Note:
            The returned coordinates can be negative or greater than the window
                size, when the mouse is out of the window but the window still
                selected.

        Args:
            None

        Returns:
            a couple ([int, int]): pixel-wise position (line, column) relative
        to (0,0) = top-left position in the window.
        """
        # private: the mouse moved
        def _motion(event):
            self._souris = (event.y, event.x)

        if not self.root:
            raise InterruptedError("window killed")
        self.refresh()
        try:
            return self._souris
        except AttributeError:
            self.bind("<Motion>", _motion)
            return self._souris


###########################################################################
# Test program: 8x8 board, click to place/remove black/white pieces       #
###########################################################################
if __name__ == "__main__":
    SIZE = 8
    PIXEL_SIZE = 100

    def main():
        """Main function, testing the module."""
        # open the window containing a board
        # use tkdraw.screen.Screen() if you include this as a module with
        # 'import tkdraw.screen'
        win = Screen((SIZE, SIZE), PIXEL_SIZE)

        # checkered tiles:
        for i in range(SIZE):
            for j in range(i % 2, SIZE, 2):
                win.draw_tile((i, j), color="yellow", refresh=False)
        # refresh only once for performance
        win.refresh()

        # welcome message
        msg = win.draw_text((PIXEL_SIZE//2, PIXEL_SIZE+PIXEL_SIZE//2),
                          "Hello!\nclick here ->")

        # main loop: wait for user clicks and draw pieces.
        # tab = 2D grid containing the graphical object IDs
        # if you click again on a piece it will be deleted, same player plays
        tab = [[None]*SIZE for i in range(SIZE)]
        player = 1  # white player starts, black = -1.
        while True:
            evt = win.wait_event()
            # demo: print the content of the event couple
            print(evt)

            # stop when:
            if evt[0] == "END":
                break
            # or when:
            if evt[0] == "key" and evt[1] in ["q", "Q", "Escape"]:
                break

            # ignore all events other than mouse click
            if evt[0] != "click":
                continue

            lig, col = evt[1]
            if tab[lig][col] is None:
                tab[lig][col] = win.draw_piece(evt[1], player)
                # player : 1 -> -1 -> 1 -> ...
                player = -player
            else:
                # remove the piece at position (lig, col)
                win.rm(tab[lig][col])
                tab[lig][col] = None

            # remove the previous message
            win.rm(msg)
            # and put a new one
            msg = win.draw_text((PIXEL_SIZE//2, PIXEL_SIZE+PIXEL_SIZE//2),
                              [0, "white player", "black player"][player])

        # at the end, close the window properly
        win.close()

    main()

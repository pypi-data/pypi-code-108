"""Testing the tkdraw screen module, board version."""
import tkdraw.screen


def test_screen():
    """Test the main functions from the screen module.

    Will open a tkinter window and ask for interactions with the user.
    """
    HEIGHT = 6
    WIDTH = 8
    TILE_SIZE = 100

    grid = [
        [0, 1, 2, 3, 4, 5, 6, 7],
        [None]*8,
        [None, 8, 9, None, None, None, None, None],
        [None]*8,
        [0]*8,
        [2]*8,
    ]
    # open a window containing a HEIGHTxWIDTH board,
    # each tile is TILE_SIZE pixels wide,
    g = tkdraw.screen.Screen((HEIGHT, WIDTH), TILE_SIZE)

    # draw checkered tiles in it
    for i in range(HEIGHT):
        for j in range(WIDTH):
            if (i+j) % 2 == 0:
                g.draw_tile((i, j), "grey")

    g.message("""This is a message box.
    You should see a checkered board in the window.
    Just click anywhere to continue.
    """)

    for i in range(HEIGHT):
        for j in range(WIDTH):
            if grid[i][j] is not None:
                g.draw_piece((i, j), grid[i][j])

    g.message("""You should see a board containing colored pieces in the window.
    <click>
    """)

    g_objects = g.draw_grid(grid)

    g.message("""And now the same one, without the checkered tiles in background.
    <click>
    """)

    t_object = g.draw_text((TILE_SIZE*(HEIGHT+1)//2, TILE_SIZE*WIDTH//2),
        "this is a text inside the window.\n<click to remove>")
    g.wait_event()
    g.rm(t_object)

    t_object = g.draw_text((TILE_SIZE*(HEIGHT+1)//2, TILE_SIZE*WIDTH//2),
        "<click to remove the pieces>")
    g.wait_event()
    for o in g_objects:
        g.rm(o)
    g.rm(t_object)


    t_object = g.draw_text((TILE_SIZE*(HEIGHT+1)//2, TILE_SIZE*WIDTH//2),
        "please hit the space key\n<waiting>")
    while g.wait_event() != ("key", "space"):
        pass
    g.rm(t_object)

    g.draw_text((TILE_SIZE*(HEIGHT+1)//2, TILE_SIZE*WIDTH//2),
        """Thank you for running this test!
Close the window or hit <escape> to quit.

If something went wrong and you want
   to report it hit the 'E' key now.""")

    # wait for the user to close the window
    while True:
        e = g.wait_event()
        if e in [("END", None), ("key", "Escape")]:
            break
        if e == ("key", "E"):
            assert False, "something went wrong."

    g.close()

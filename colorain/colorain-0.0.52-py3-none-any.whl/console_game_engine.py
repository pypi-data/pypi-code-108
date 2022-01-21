##################################################
##################################################
# Submodule for turning the console into a canvas #
# CGE = Console Game Engine #
##################################################
##################################################

##################################################
# Imports #
##################################################
import sys
from .colorain import *
Stx = StyledText


##################################################
# Block Elements #
##################################################
BLOCK_FULL = chr(9608)
BLOCK_THREEQTR = chr(9619)
BLOCK_HALF = chr(9618)
BLOCK_QTR = chr(9817)

BLOCKS = [BLOCK_FULL, BLOCK_THREEQTR, BLOCK_HALF, BLOCK_QTR]

##################################################
# Move the cursor relative to current position #
##################################################
def move_cursor(line, col):
    base = "\033["

    linedir = "A" if line < 0 else "B"
    coldir = "C" if col > 0 else "D"
    
    linecode = f"{base}{abs(line)}{linedir}"
    colcode = f"{base}{abs(col)}{coldir}"
    sys.stdout.write(linecode)
    sys.stdout.write(colcode) 


##################################################
# Get a one-character input w/o echoing #
##################################################
def getChar():
    try:
        # for Windows-based systems
        import msvcrt # If successful, we are on Windows
        return msvcrt.getch()

    except ImportError:
        # for POSIX-based systems (with termios & tty support)
        import tty, termios  # raises ImportError if unsupported

        fd = sys.stdin.fileno()
        oldSettings = termios.tcgetattr(fd)

        try:
            tty.setcbreak(fd)
            answer = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, oldSettings)

        return answer


##################################################
# 2D coordinate #
##################################################
class Coord2D:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __repr__(self):
        return f"{(self.x, self.y)}"
    
    def __add__(self, coord):
        return Coord2D(self.x + coord.x, self.y + coord.y)
    
    def __sub__(self, coord):
        return Coord2D(self.x - coord.x, self.y - coord.y)
    
    def __eq__(self, coord):
        return self.x == coord.x and self.y == coord.y


##################################################
# 2D scene (i.e., 2D canvas) #
##################################################
class Scene2D:
    def __init__(self, width, height, colour = None):
        self.width = width
        self.height = height
        self.scene = [[BLOCKS[0]][:]*2*self.width for i in range(self.height)]
    
    def render(self, reset=True):
        sys.stdout.write('\n'.join([''.join(ln) for ln in self.scene]))
        if reset:
            move_cursor(-self.height+1, -2*self.width)
        else: print()

    def edit_pixel(self, pixel_loc, newval):
        if isinstance(pixel_loc, Coord2D):
            x, y = pixel_loc.x, pixel_loc.y
        elif isinstance(pixel_loc, tuple):
            x, y = pixel_loc[0], pixel_loc[1]
        self.scene[y][2*x] = newval
        self.scene[y][2*x+1] = newval
    
    def reset_pixel(self, pixel_loc):
        if isinstance(pixel_loc, tuple):
            pixel_loc = Coord2D(pixel_loc[0], pixel_loc[1])
        self.edit_pixel(pixel_loc, BLOCKS[0])

    def paint_pixel(self, pixel_loc, colour):
        if isinstance(pixel_loc, tuple):
            pixel_loc = Coord2D(pixel_loc[0], pixel_loc[1])
        self.edit_pixel(pixel_loc, Stx(f"<{fgtokens[colour]}>{BLOCKS[0]}</>").parsed)


class Sprite:
    def __init__(self, scene, positions):
        self.scene = scene
        self.positions = positions
        self.draw()

    def draw(self):
        self.scene.edit_pixel(self.positions[0], Stx(f"<f=lg;b=b>{BLOCKS[2]}</>").parsed)
        for pos in self.positions[1:]:
            self.scene.edit_pixel(pos, Stx(f"<f=lr;b=y>{BLOCKS[2]}</>").parsed)
    
    def erase(self):
        for pos in self.positions:
            self.scene.reset_pixel(pos)

    def translate(self, x, y):
        self.erase()
        for pos in self.positions:
            pos.x += x
            pos.y += y
        self.draw()
##################################################
##################################################
# Submodule for turning the console into a canvas #
# / Console Game Engine #
##################################################
##################################################

##################################################
# Imports #
##################################################
import sys
import math
import threading
from .colorain import *

##################################################
# Block Elements #
##################################################
BLOCK_FULL = chr(9608)
BLOCK_THREEQTR = chr(9619)
BLOCK_HALF = chr(9618)
BLOCK_QTR = chr(9617)

BLOCKS = [BLOCK_FULL, BLOCK_THREEQTR, BLOCK_HALF, BLOCK_QTR]

##################################################
# Move the cursor relative to current position #
##################################################
def move_cursor(line, col):
    base = "\033["

    linedir = "A" if line < 0 else "B"
    coldir = "C" if col > 0 else "D"
    
    linecode = f"{base}{abs(line)}{linedir}" if line!=0 else ""
    colcode = f"{base}{abs(col)}{coldir}" if col!=0 else ""
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

def run_input_thread(handle_input, args):
    inp_thread = threading.Thread(target = handle_input, args = args)
    inp_thread.start()

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
    
    def dot(self, coord):
        return self.x*coord.x + self.y*coord.y

    def rotate(self, angle, reference):
        rotn_mat = [Coord2D(math.cos(angle), -math.sin(angle)), \
            Coord2D(math.sin(angle), math.cos(angle))]
        newpt = Coord2D(rotn_mat[0].dot(self - reference), rotn_mat[1].dot(self - reference))
        self.x = newpt.x + reference.x
        self.y = newpt.y + reference.y

class Vector2D:
    def __init__(self, start, end):
        if isinstance(start, tuple):
            start = Coord2D(*start)
        if isinstance(end, tuple):
            end = Coord2D(*end)
        self.start = start
        self.end = end
        self.x = self.end.x - self.start.x
        self.y = self.end.y - self.start.y

    def __repr__(self):
        return f"{self.x}i + {self.y}j"
    
    def __add__(self, vector):
        sum_start = self.start
        sum_end = self.end + Coord2D(vector.x, vector.y)
        return Vector2D(sum_start, sum_end)

    def dot(self, vector):
        return self.x*vector.x + self.y*vector.y

    def length(self):
        sqr_len = self.dot(self)
        print(f"{chr(int('221a',16))}{sqr_len}")
        return   math.sqrt(sqr_len)

    def rotate(self, angle):
        return Vector2D(self.start.rotate(angle), self.end.rotate(angle))

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

    def draw(self, color):
        for pos in self.positions:
            self.scene.paint_pixel(pos, color)
    
    def erase(self):
        for pos in self.positions:
            self.scene.reset_pixel(pos)

    def translate(self, x, y):
        self.erase()
        for pos in self.positions:
            pos.x += x
            pos.y += y
        self.draw()
    
    def rotate(self, angle, reference):
        self.erase()
        for pos in self.positions:
            pos.rotate(angle, reference)
            pos.x = math.floor(pos.x)
            pos.y = math.floor(pos.y)
        self.draw()


class VLine(Sprite):
    def draw(self, color='red'):
        for pos in self.positions:
            self.scene.paint_pixel(pos, color)
    def rotate(self, angle):
        super().rotate(angle, self.positions[0])

class Rect(Sprite):
    def __init__(self, scene, topleft, width, height):
        positions = []
        for i in range(width):
            for j in range(height):
                positions.append(topleft + Coord2D(i,j))
        super().__init__(scene, positions)
    
    def rotate(self, angle):
        super().rotate(angle, self.positions[0])
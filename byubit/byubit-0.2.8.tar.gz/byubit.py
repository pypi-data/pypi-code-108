# Inspired by Stanford: http://web.stanford.edu/class/cs106a/handouts_w2021/reference-bit.html
from dataclasses import dataclass
from typing import Literal, Protocol, Optional
from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

import numpy as np
import matplotlib
import matplotlib.pyplot as plt


class MoveOutOfBoundsException(Exception):
    """Raised when Bit tries to move out of bounds"""


class MoveBlockedByBlackException(Exception):
    """Raised when Bit tries to move out of bounds"""


class BitComparisonException(Exception):
    def __init__(self, message, annotations):
        self.message = message
        self.annotations = annotations

    def __str__(self):
        return self.message


# 0,0  1,0  2,0
# 0,1  1,1, 2,1
# 0,2  1,2, 2,2
# dx and dy
_orientations = [
    np.array((1, 0)),  # Right
    np.array((0, 1)),  # Up
    np.array((-1, 0)),  # Left
    np.array((0, -1))  # Down
]

EMPTY = 0
BLACK = 1
RED = 2
GREEN = 3
BLUE = 4

_names_to_colors = {
    None: EMPTY,
    'black': BLACK,
    'red': RED,
    'green': GREEN,
    'blue': BLUE
}

_colors_to_names = {v: k for k, v in _names_to_colors.items()}

_codes_to_colors = {
    "-": EMPTY,
    "k": BLACK,
    "r": RED,
    "g": GREEN,
    "b": BLUE
}

_colors_to_codes = {v: k for k, v in _codes_to_colors.items()}

MAX_STEP_COUNT = 10_000


@dataclass
class BitHistoryRecord:
    name: str  # What event produced the associated state?
    error_message: Optional[str]  # Error info
    world: np.array  # 2D list indexed with [x,y]
    pos: np.array  # [x, y]
    orientation: int
    annotations: np.array  # 2D list of expected colors


class BitHistoryRenderer(Protocol):
    def render(self, history: list[BitHistoryRecord]) -> bool:
        """Present the history.
        Return True if there were no errors
        Return False if there were errors
        """


class TextRenderer(BitHistoryRenderer):
    def render(self, history: list[BitHistoryRecord]):
        print()
        for num, record in enumerate(history):
            print(f"{num}: {record.name}")

        return history[-1].error_message is None


def draw_record(ax, record: BitHistoryRecord):
    dims = record.world.shape

    # Draw squares
    for y in range(dims[1]):
        for x in range(dims[0]):
            ax.add_patch(plt.Rectangle(
                (x, y),
                1, 1,
                color=_colors_to_names[record.world[x, y]] or "white")
            )

    # Draw the "bit"
    ax.scatter(
        record.pos[0] + 0.5,
        record.pos[1] + 0.5,
        c='cyan',
        s=500,
        marker=(3, 0, 90 * (-1 + record.orientation))
    )

    if record.annotations is not None:
        for x in range(record.world.shape[0]):
            for y in range(record.world.shape[1]):
                if record.world[x, y] != record.annotations[x, y]:
                    ax.text(x + 0.6, y + 0.6, "!",
                            fontsize=16, weight='bold',
                            bbox={'facecolor': _colors_to_names[record.annotations[x, y]] or "white"})

    ax.set_title(record.name)
    if record.error_message is not None:
        ax.set_xlabel("⚠️" + record.error_message)

    ax.set_xlim([0, dims[0]])
    ax.set_ylim([0, dims[1]])
    ax.set_xticks(range(0, dims[0]))
    ax.set_yticks(range(0, dims[1]))
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.grid(True)


class LastFrameRenderer(BitHistoryRenderer):
    """Displays the last frame
    Similar to the <=0.1.6 functionality
    """
    def render(self, history: list[BitHistoryRecord]):
        print()
        for num, record in enumerate(history):
            print(f"{num}: {record.name}")

        last_record = history[-1]

        fig, axs = plt.subplots(1, 1, figsize=(6, 6))
        ax = fig.gca()

        draw_record(ax, last_record)

        plt.show()

        return history[-1].error_message is None


class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class MainWindow(QtWidgets.QMainWindow):
    history: list[BitHistoryRecord]
    cur_pos: int

    def __init__(self, history, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        matplotlib.use('Qt5Agg')

        self.history = history
        self.cur_pos = 0

        # Create the maptlotlib FigureCanvas object,
        # which defines a single set of axes as self.axes.
        self.canvas = MplCanvas(parent=self, width=5, height=4, dpi=100)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.canvas)

        button_widget = QtWidgets.QWidget()
        button_layout = QtWidgets.QHBoxLayout()

        # Start
        start_button = QtWidgets.QPushButton()
        start_button.setText("⬅️⬅️ First Step")
        button_layout.addWidget(start_button)

        def start_click():
            self.cur_pos = 0
            self._display_current_record()

        start_button.clicked.connect(start_click)

        # Back
        back_button = QtWidgets.QPushButton()
        back_button.setText("⬅️ Prev Step")
        button_layout.addWidget(back_button)

        def back_click():
            if self.cur_pos > 0:
                self.cur_pos -= 1
            self._display_current_record()

        back_button.clicked.connect(back_click)

        # Next
        next_button = QtWidgets.QPushButton()
        next_button.setText("Next Step ➡️")
        button_layout.addWidget(next_button)

        def next_click():
            if self.cur_pos < len(self.history) - 1:
                self.cur_pos += 1
            self._display_current_record()

        next_button.clicked.connect(next_click)

        # Last
        last_button = QtWidgets.QPushButton()
        last_button.setText("Last Step ➡️➡️")
        button_layout.addWidget(last_button)

        def last_click():
            self.cur_pos = len(self.history) - 1
            self._display_current_record()

        last_button.clicked.connect(last_click)

        button_widget.setLayout(button_layout)

        layout.addWidget(button_widget)  # will become the controls

        master_widget = QtWidgets.QWidget()
        master_widget.setLayout(layout)
        self.setCentralWidget(master_widget)
        self._display_current_record()
        self.show()

    def _display_current_record(self):
        self._display_record(self.cur_pos, self.history[self.cur_pos])

    def _display_record(self, index: int, record: BitHistoryRecord):
        print(f"{index}: {record.name}")
        self.canvas.axes.clear()  # Clear the canvas.
        draw_record(self.canvas.axes, record)
        self.canvas.axes.set_title(f"{index}: {record.name}")
        self.canvas.axes.set_xlabel(record.error_message)

        # Trigger the canvas to update and redraw.
        self.canvas.draw()


class AnimatedRenderer(BitHistoryRenderer):
    """Displays the world, step-by-step
    The User can pause the animation, or step forward or backward manually
    """
    def render(self, history: list[BitHistoryRecord]):
        """
        Run QT application
        """
        qtapp = QtWidgets.QApplication([])
        w = MainWindow(history)
        qtapp.exec_()

        return history[-1].error_message is None


# RENDERER = TextRenderer
# RENDERER = LastFrameRenderer
RENDERER = AnimatedRenderer


# Convention:
# We'll have 0,0 be the origin
# The position defines the X,Y coordinates
class Bit:
    world: np.array
    pos: np.array  # x and y
    orientation: int  # _orientations[orientation] => dx and dy

    history: list[BitHistoryRecord]

    @staticmethod
    def run_all(args: list, renderer: BitHistoryRenderer = None):
        def decorator(bit_func):
            for bit1, bit2 in args:
                Bit.evaluate(bit_func, bit1, bit2, renderer or RENDERER())
            return bit_func

        return decorator

    @staticmethod
    def run(bit1, bit2=None, renderer: BitHistoryRenderer = None):
        def decorator(bit_func):
            Bit.evaluate(bit_func, bit1, bit2, renderer or RENDERER())
            return bit_func

        return decorator

    @staticmethod
    def evaluate(bit_function, bit1, bit2=None, renderer: BitHistoryRenderer = None) -> bool:
        """Return value communicates whether the run succeeded or not"""

        renderer = renderer or RENDERER()

        if isinstance(bit1, str):
            bit1 = Bit.load(bit1)

        if isinstance(bit2, str):
            bit2 = Bit.load(bit2)
        try:
            bit_function(bit1)

            if bit2 is not None:
                bit1._compare(bit2)

        except BitComparisonException as ex:
            bit1._register("comparison error", str(ex), ex.annotations)

        except Exception as ex:
            print(ex)
            bit1._register("error", str(ex))

        finally:
            return renderer.render(bit1.history)

    @staticmethod
    def new_world(size_x, size_y):
        return Bit(np.zeros((size_x, size_y)), (0, 0), 0)

    @staticmethod
    def load(filename: str):
        """Parse the file into a new Bit"""
        with open(filename, 'rt') as f:
            return Bit.parse(f.read())

    @staticmethod
    def parse(content: str):
        """Parse the bitmap from a string representation"""
        # Empty lines are ignored
        lines = [line for line in content.split('\n') if line]

        # There must be at least three lines
        assert len(lines) >= 3

        # Position is the second-to-last line
        pos = np.fromstring(lines[-2], sep=" ", dtype=int)

        # Orientation is the last line: 0, 1, 2, 3
        orientation = int(lines[-1].strip())

        # World lines are all lines up to the second-to-last
        # We transpose because numpy stores our lines as columns
        #  and we want them represented as rows in memory
        world = np.array([[_codes_to_colors[code] for code in line] for line in lines[-3::-1]]).transpose()

        return Bit(world, pos, orientation)

    def __init__(self, world: np.array, pos: np.array, orientation: int):
        self.world = world
        self.pos = np.array(pos)
        self.orientation = orientation
        self.history = []
        self._register("initial state")

    def __repr__(self) -> str:
        """Present the bit information as a string"""
        # We print out each row in reverse order so 0,0 is at the bottom of the text, not the top
        world_str = "\n".join(
            "".join(_colors_to_codes[self.world[x, self.world.shape[1] - 1 - y]] for x in range(self.world.shape[0]))
            for y in range(self.world.shape[1])
        )
        pos_str = f"{self.pos[0]} {self.pos[1]}"
        orientation = self.orientation
        return f"{world_str}\n{pos_str}\n{orientation}\n"

    def render(self) -> bool:
        return self.renderer.render()

    def _record(self, name, message=None, annotations=None):
        return BitHistoryRecord(
            name, message, self.world.copy(), self.pos, self.orientation,
            annotations.copy() if annotations is not None else self.world.copy()
        )

    def _register(self, name, message=None, annotations=None):
        self.history.append(self._record(name, message, annotations))
        if len(self.history) > MAX_STEP_COUNT:
            message = "Bit has done too many things. Is he stuck in an infinite loop?"
            raise Exception(message)

    def save(self, filename: str):
        """Save your bit world to a text file"""
        with open(filename, 'wt') as f:
            f.write(repr(self))
        print(f"Bit saved to {filename}")

    def draw(self, filename=None, message=None, annotations=None):
        """Display the current state of the world"""
        fig = plt.figure()
        ax = fig.gca()
        draw_record(ax, self._record("", annotations=annotations))

        if message:
            ax.set_title(message)
        if filename:
            print("Saving bit world to " + filename)
            fig.savefig(filename)
        else:
            plt.show()

    def _next_orientation(self, direction: Literal[1, 0, -1]) -> np.array:
        return (len(_orientations) + self.orientation + direction) % len(_orientations)

    def _get_next_pos(self, turn: Literal[1, 0, -1] = 0) -> np.array:
        return self.pos + _orientations[self._next_orientation(turn)]

    def _pos_in_bounds(self, pos) -> bool:
        return np.logical_and(pos >= 0, pos < self.world.shape).all()

    def move(self):
        """If the direction is clear, move that way"""
        next_pos = self._get_next_pos()
        if not self._pos_in_bounds(next_pos):
            message = f"Bit tried to move to {next_pos}, but that is out of bounds"
            raise MoveOutOfBoundsException(message)

        elif self._get_color_at(next_pos) == BLACK:
            message = f"Bit tried to move to {next_pos}, but that space is blocked"
            raise MoveBlockedByBlackException(message)

        else:
            self.pos = next_pos
            self._register("move")

    def left(self):
        """Turn the bit to the left"""
        self.orientation = self._next_orientation(1)
        self._register("left")

    def right(self):
        """Turn the bit to the right"""
        self.orientation = self._next_orientation(-1)
        self._register("right")

    def _get_color_at(self, pos):
        return self.world[pos[0], pos[1]]

    def _space_is_clear(self, pos):
        return self._pos_in_bounds(pos) and self._get_color_at(pos) != BLACK

    def front_clear(self) -> bool:
        """Can a move to the front succeed?

        The edge of the world is not clear.

        Black squares are not clear.
        """
        ret = self._space_is_clear(self._get_next_pos())
        self._register(f"front_clear: {ret}")
        return ret

    def left_clear(self) -> bool:
        ret = self._space_is_clear(self._get_next_pos(1))
        self._register(f"left_clear: {ret}")
        return ret

    def right_clear(self) -> bool:
        ret = self._space_is_clear(self._get_next_pos(-1))
        self._register(f"right_clear: {ret}")
        return ret

    def _paint(self, color: int):
        self.world[self.pos[0], self.pos[1]] = color

    def erase(self):
        """Clear the current position"""
        self._paint(EMPTY)
        self._register("erase")

    def paint(self, color):
        """Color the current position with the specified color"""
        if color not in _names_to_colors:
            message = f"Unrecognized color: {color}. Known colors are: {list(_names_to_colors.keys())}"
            raise Exception(message)
        self._paint(_names_to_colors[color])
        self._register(f"paint {color}")

    def get_color(self) -> str:
        """Return the color at the current position"""
        ret = _colors_to_names[self._get_color_at(self.pos)]
        self._register(f"get_color: {ret}")
        return ret

    def _compare(self, other: 'Bit'):
        """Compare this bit to another"""
        if not self.world.shape == other.world.shape:
            raise Exception(
                f"Cannot compare Bit worlds of different dimensions: {tuple(self.pos)} vs {tuple(other.pos)}")

        if not np.array_equal(self.world, other.world):
            raise BitComparisonException(f"Bit world does not match expected world", other.world)

        if self.pos[0] != other.pos[0] or self.pos[1] != other.pos[1]:
            raise Exception(f"Location of Bit does not match: {tuple(self.pos)} vs {tuple(other.pos)}")

        self._register("compare correct!", annotations=other.world)

    def compare(self, other: 'Bit'):
        try:
            self._compare(other)
            return True
        except BitComparisonException as ex:
            self.draw(message=str(ex), annotations=ex.annotations)

        finally:
            self.draw()

        return False

import copy
from typing import Tuple

import chess
import matplotlib.pyplot as plt
import numpy as np

import matplotlib.patches as patches

SYMBOLS = {
    "K": "♔",
    "Q": "♕",
    "R": "♖",
    "B": "♗",
    "N": "♘",
    "P": "♙",
    "k": "♚",
    "q": "♛",
    "r": "♜",
    "b": "♝",
    "n": "♞",
    "p": "♟︎",
}


def plot_board(ax: plt.Axes, board: chess.Board, checkers: bool = True):
    r"""
    Creates a board image on the specified axis.

    Parameters
    ----------
    ax: plt.Axes
        Axes to apply the board to.
    board: chess.Board
        Board object to plot.
    checkers: bool, default=True
        Whether or not to apply a checker pattern to the background.

    Examples
    --------
    >>> import chess
    >>> from chessplotlib import plot_board
    >>> import matplotlib.pyplot as plt
    >>> board = chess.Board()
    >>> ax = plt.gca()
    >>> plot_board(ax, board)
    >>> plt.show()

    .. image:: ../../examples/starting_board.png
    """
    ax.set_xlim([-0.5, 7.5])
    ax.set_ylim([7.5, -0.5])
    for i in range(8):
        ax.axhline(i - 0.5, 0, 8, color="black")
        ax.axvline(i - 0.5, 0, 8, color="black")

    ax.tick_params(labeltop=True, labelright=True, length=0)

    ax.set_yticks(list(reversed(list(range(8)))))
    ax.set_xticks(list(range(8)))

    ax.set_yticklabels(("1", "2", "3", "4", "5", "6", "7", "8"))
    ax.set_xticklabels(("a", "b", "c", "d", "e", "f", "g", "h"))

    if checkers:
        make_checkers(ax)

    X, Y = np.meshgrid(np.arange(8), np.arange(8))
    locs = np.stack([X.flatten(), Y.flatten()], axis=1)

    for square in chess.SQUARES_180:
        piece = board.piece_at(square)
        if piece:
            add_piece(ax, chess.SQUARE_NAMES[square], piece.symbol())


def plot_move(
    ax: plt.Axes,
    board: chess.Board,
    move: chess.Move,
    alpha: float = 1.0,
    color: str = "red",
    piece_alpha: float = 1.0,
    piece_color: str = "black",
):
    r"""
    Visualizes a move on top of a plotted board.

    Parameters
    ----------
    ax: plt.Axes
        Axes containing the state of the board in which the move with take place
    move: chess.Move
        Potential move represented with a chess.Move object
    alpha: float, default=1.0
        Alpha value for move visual
    color: str, default=black
        Color for move visual

    Examples
    --------
    >>> import chess
    >>> from chessplotlib import plot_board, plot_move
    >>> import matplotlib.pyplot as plt
    >>> board = chess.Board()
    >>> ax = plt.gca()
    >>> plot_board(ax, board)
    >>> plot_move(ax, board, "e2e4")
    >>> plt.show()

    .. image:: ../../examples/opening_move.png
    """
    from_square = _from_square(move)
    to_square, promotion = _to_square(move)

    square = chess.SQUARE_NAMES.index(from_square)
    from_piece = board.piece_at(square)

    if promotion == "":
        to_piece = from_piece
    else:
        to_piece = chess.Piece.from_symbol(promotion)

    add_arrow(ax, from_square, to_square, alpha=alpha, color=color)
    add_piece(ax, to_square, to_piece.symbol(), alpha=piece_alpha, color=piece_color)


def mark_square(ax: plt.Axes, square: str):
    r"""
    Highlights a square in red.

    Parameters
    ----------
    ax: plt.Axes
        Axes containing the state of the board
    square: str
        String name for square, (i.e. e1)

    Examples
    --------
    >>> import chess
    >>> from chessplotlib import plot_board, mark_square
    >>> import matplotlib.pyplot as plt
    >>> board = chess.Board()
    >>> ax = plt.gca()
    >>> plot_board(ax, board)
    >>> mark_square(ax, "e2")
    >>> plt.show()

    .. image:: ../../examples/starting_board_marked.png
    """
    row, col = _square_to_grid(square)

    rect = patches.Rectangle(
        (row - 0.5, col - 0.5),
        1.0,
        1.0,
        linewidth=2,
        edgecolor="r",
        facecolor="none",
        zorder=3,
    )

    # Add the patch to the Axes
    ax.add_patch(rect)


def mark_move(ax: plt.Axes, move: chess.Move):
    """
    Marks the two squares used in a move

    Parameters
    ----------
    ax: plt.Axes
        Axes containing the state of the board
    move: chess.Move
        String name for square, (i.e. e1)
    """
    from_square = _from_square(move)
    to_square, _ = _to_square(move)

    mark_square(ax, from_square)
    mark_square(ax, to_square)


def make_checkers(ax: plt.Axes):
    """
    Adds checkers to the board to make it look more natural

    Parameters
    ----------
    ax: plt.Axes
        Axes to add checkers to
    """
    X, Y = np.meshgrid(np.arange(8), np.arange(8))
    checker = (((X + Y) % 2) + 0.3) / 2
    ax.imshow(checker, cmap="Greys", vmax=1.0, vmin=0.0)


def add_piece(
    ax: plt.Axes, square: str, piece: str, alpha: float = 1.0, color: str = "black"
):
    """
    Adds a pieces to the board.

    Adds the piece, `piece`, at location square on axes ax.

    Parameters
    ----------
    ax: plt.Axes
        Axes containing board
    square: str
        String representing the square (i.e. "e1")
    piece: str
        String symbol for the piece (i.e. "P")
    alpha: float
        Alpha for the piece, controls piece visibility
    color: str
        black or white, controls the color of the piece
    """
    x, y = _square_to_grid(square)
    ax.text(
        x,
        y + 0.05,
        SYMBOLS[piece],
        fontsize=32,
        ha="center",
        va="center",
        alpha=alpha,
        color=color,
    )


def add_arrow(
    ax: plt.Axes,
    from_square: str,
    to_square: str,
    alpha=1.0,
    color="black",
):
    """
    Adds an arrow from one square to the next

    Draws an arrow connecting two squares together. Can be used to represent
    moves.

    Parameters
    ----------
    ax: plt.Axes
        Axes containing board.
    from_square: str
        String representing the square to start the arrow (i.e. "e1").
    to_square: str
        String representing the square to finish the arrow (i.e. "e4").
    alpha: float
        Alpha for the piece, controls piece visibility.
    color: str
        Controls the color of the piece, typically black or white.
    """
    from_x, from_y = _square_to_grid(from_square)
    to_x, to_y = _square_to_grid(to_square)

    ax.arrow(
        from_x,
        from_y,
        to_x - from_x,
        to_y - from_y,
        alpha=alpha,
        color=color,
        zorder=4,
        head_width=0.15,
        length_includes_head=True,
    )


def _from_square(move: chess.Move) -> str:
    """
    Converts a move into the from location
    """
    return chess.SQUARE_NAMES[move.from_square]


def _to_square(move: chess.Move) -> Tuple[str, str]:
    """
    Converts a move into the to location and promotion
    """

    promotion = ""
    if move.promotion is not None:
        promotion = chess.PIECE_SYMBOLS[move.promotion]

    return (chess.SQUARE_NAMES[move.to_square], promotion)


def _square_to_grid(square: str) -> Tuple[int, int]:
    """
    Converts the string name of the square into the grid location
    """
    row_val = square[0]
    col_val = square[1]
    col = ["8", "7", "6", "5", "4", "3", "2", "1"].index(col_val)
    row = ["a", "b", "c", "d", "e", "f", "g", "h"].index(row_val)
    return row, col

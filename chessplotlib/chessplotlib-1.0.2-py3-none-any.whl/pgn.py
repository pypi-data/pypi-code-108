import copy

import numpy as np
import chess.pgn

from chessplotlib import plot_board, plot_move


class PGNViewer:
    r"""
    Class used to create interactive PGN Viewers.

    This class wraps a figure with key bindings to move between the moves in
    the game. Left and right arrows will increment the current move number, q
    will exit. This class can easily be inherited to create new visualizers by
    overloading the render function.

    Attributes
    ----------
    boards : List[chess.Board]
        List of all the boards in the game.
    moves : List[chess.Move]
        List of all the moves in the game.
    move_num : int
        Current Move number
    ax : plt.Axes
        Axes being plotted on
    fig : plt.Figure
        Figure being plotted on

    Examples
    ---------
    >>> from chessplotlib import PGNViewer
    >>> import chess.pgn
    >>> import matplotlib.pyplot as plt
    >>> game = chess.pgn.read_game(open("example.pgn", "r"))
    >>> fig, ax = plt.subplots(1, 1)
    >>> viewer = PGNViewer(fig, ax, game)
    >>> plt.show()
    """

    def __init__(self, fig, ax, game):
        """
        Parameters
        ----------
        fig : plt.Figure
            Current figure
        ax : plt.Axes
            Current axis
        game : chess.pgn.Game
            A loaded PGN game file
        """

        board = game.board()
        boards = [copy.copy(board)]
        self.moves = list(game.mainline_moves())
        for move in self.moves:
            board.push(move)
            boards.append(copy.copy(board))

        self.fig = fig
        self.ax = ax
        self.boards = boards
        self.move_num = 0

        self.render(self.ax, self.move_num, self.boards, self.moves)
        self.fig.canvas.mpl_connect("key_press_event", self._press)

    def render(self, ax, move_num, boards, moves):
        """
        Updates the plot for the next move.

        This is the function that controls how each move is visualized. If you
        would like to use a different visualization method, this is the
        function to overload.

        Parameters
        ----------
        ax : plt.Axes
            Axis to plot on
        move_num : int
            Current move number
        boards : List[chess.Board]
            List of game boads
        moves : List[chess.Moves]
            List of total moves
        """
        plot_board(ax, boards[move_num], checkers=True)
        plot_move(ax, boards[move_num], moves[move_num], piece_alpha=0.5)

    def _press(self, event):
        if event.key == "left":
            self.move_num -= 1

        elif event.key == "right":
            self.move_num += 1

        elif event.key == "q":
            exit()

        # Don't go out of the list range
        self.move_num = np.clip(self.move_num, 0, len(self.moves) - 1)

        self.ax.clear()
        self.render(self.ax, self.move_num, self.boards, self.moves)
        self.fig.canvas.flush_events()
        self.fig.canvas.draw()

import chess
import pytest
import numpy as np
from matplotlib import image
import matplotlib.pyplot as plt
from chessplotlib import plot_board, plot_move, mark_move

with open("test/boards.txt", "r") as bf:
    BOARD_FENS = [l.rstrip() for l in bf.readlines()]

with open("test/moves.txt", "r") as mf:
    MOVE_UCIS = [l.rstrip() for l in mf.readlines()]


@pytest.mark.parametrize("i,board_fen", list(enumerate(BOARD_FENS)))
def test_board_plot(i, board_fen):
    plt.cla()
    board = chess.Board(board_fen)
    ax = plt.gca()
    plot_board(ax, board)
    plt.savefig(f"./test/temp.png")

    new = image.imread(f"./test/temp.png")
    baseline = image.imread(f"./test/baseline/board_{i}.png")

    assert (new == baseline).all()


move_options = [(i, BOARD_FENS[i], MOVE_UCIS[i]) for i in range(len(BOARD_FENS))]


@pytest.mark.parametrize("i,board_fen,move_uci", move_options)
def test_move_plot(i, board_fen, move_uci):
    plt.cla()
    board = chess.Board(board_fen)
    move = chess.Move.from_uci(move_uci)
    ax = plt.gca()
    plot_board(ax, board)
    plot_move(ax, board, move)
    plt.savefig(f"./test/temp.png")

    new = image.imread(f"./test/temp.png")
    baseline = image.imread(f"./test/baseline/move_{i}.png")

    assert (new == baseline).all()


@pytest.mark.parametrize("i,board_fen,move_uci", move_options)
def test_mark_move_plot(i, board_fen, move_uci):
    plt.cla()
    board = chess.Board(board_fen)
    move = chess.Move.from_uci(move_uci)
    ax = plt.gca()
    plot_board(ax, board)
    plot_move(ax, board, move)
    mark_move(ax, move)
    plt.savefig(f"./test/temp.png")

    new = image.imread(f"./test/temp.png")
    baseline = image.imread(f"./test/baseline/marked_move_{i}.png")

    assert (new == baseline).all()

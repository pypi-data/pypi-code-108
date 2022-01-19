"""
API for rich sequence comparisons
"""
from typing import Iterable

from pypey import pype, px

from pyaliner.align import align, COMPACT, CLASSIC, tp1p2_align, itp_align
from pyaliner.display import rich_paired_in_true_pred, rich_paired_true_pred, in_terminal, rich_inlined_true_pred, \
    rich_paired_true_pred1_pred2

compact_align = px(align, kind=COMPACT)

PAIRED = 'paired'
INLINED = 'inlined'


def compare_in_true_pred_from_file(path: str, alignment: str = COMPACT):
    """
    Visually compares triplets of inputs, ground-truths and predictions in the given file.

    :param path: path to file with a collection of three lines, each an input followed by a ground-truth
        followed by a prediction
    :param alignment: the type of alignment to apply to the triplet
    :return: nothing, but displays comparison in terminal
    """
    compare_in_true_pred(pype.file(path).map(str.strip).select(bool).map(str.split), alignment)


def compare_in_true_pred_from_files(in_path: str, true_path: str, pred_path: str, alignment: str = COMPACT):
    """
    Visually compares triplets of inputs, ground-truths and predictions in the given files.

    :param in_path: path to file with with a line per input sequence
    :param true_path: path to file with with a line per ground-truth sequence
    :param pred_path: path to file with with a line per predicted sequence
    :param alignment: the type of alignment to apply to the triplet
    :return: nothing, but displays comparison in terminal
    """
    in_lines, true_lines, pred_lines = \
        (pype.file(path).map(str.strip).select(bool) for path in [in_path, true_path, pred_path])

    compare_in_true_pred(in_lines.interleave(true_lines).interleave(pred_lines, n=2).map(str.split), alignment)


def compare_true_pred_from_file(path: str, alignment: str, view: str = PAIRED):
    """
    Visually compares pairs of ground-truths and predictions in the given file.

    :param path: path to file with an even number of lines, each being a ground-truth or a prediction, in that order
    :param alignment: the type of alignment to apply to the triplet
    :param view: the view to display in the terminal
    :return: nothing, but displays comparison in terminal
    """
    compare_true_pred(pype.file(path).map(str.strip).select(bool).map(str.split), alignment, view)


def compare_true_pred_from_files(true_path: str, pred_path: str, alignment: str, view: str = PAIRED):
    """
    Visually compares pairs of ground-truths and predictions in the given files.

    :param true_path: path to file with with a line per ground-truth sequence
    :param pred_path: path to file with with a line per predicted sequence
    :param alignment: the type of alignment to apply to the triplet
    :param view: the view to display in the terminal
    :return: nothing, but displays comparison in terminal
    """
    true_lines, pred_lines = (pype.file(path).map(str.strip).select(bool) for path in [true_path, pred_path])

    compare_true_pred(true_lines.interleave(pred_lines).map(str.split), alignment, view)


def compare_true_pred1_pred2_from_file(path: str):
    """
    Visually compares triplets of ground-truths, 1st predictions and 2nd predictions in the given file.

    :param path: path to file with a collection of three lines, each a ground-truth, followed by a prediction,
        followed by another prediction
    :return: nothing, but displays comparison in terminal
    """
    compare_true_pred1_pred2(pype.file(path).map(str.strip).select(bool).map(str.split))


def compare_true_pred1_pred2_from_files(true_path: str, pred1_path: str, pred2_path: str):
    """
    Visually compares triplets of ground-truths, 1st predictions and 2nd predictions in the given file.

    :param true_path: path to file with with a line per ground-truth sequence
    :param pred1_path: path to file with with a line per predicted sequence
    :param pred2_path: path to file with with a line per predicted sequence
    :return: nothing, but displays comparison in terminal
    """
    true_lines, pred1_lines, pred2_lines = \
        (pype.file(path).map(str.strip).select(bool) for path in [true_path, pred1_path, pred2_path])

    compare_true_pred1_pred2(true_lines.interleave(pred1_lines).interleave(pred2_lines, n=2).map(str.split))


def compare_in_true_pred(triplets: Iterable[Iterable[str]], alignment: str = COMPACT):
    """
    Visually compares triplets of inputs, ground-truths and predictions in the collection.

    :param triplets: collection of three strings, each being an input, a ground-truth or a prediction, in that order
    :param alignment: the type of alignment to apply to the triplet
    :return: nothing, but displays comparison in terminal
    """
    align_fn = align if alignment == CLASSIC else compact_align

    alignments = pype(triplets).chunk(size=3).map(lambda in_seq, true, pred: itp_align(in_seq, true, pred, align_fn))

    in_terminal(rich_paired_in_true_pred(alignments))


def compare_true_pred(pairs: Iterable[Iterable[str]], alignment: str, view: str = PAIRED):
    """
    Visually compares pairs of ground-truths and predictions in the given file.

    :param pairs: collection of even number of strings, each ground-truth followed by a prediction
    :param alignment: the type of alignment to apply to the triplet
    :param view: the view to display in the terminal
    :return: nothing, but displays comparison in terminal
    """

    alignments = pype(pairs).chunk(size=2).map(compact_align if alignment == COMPACT else align)

    in_terminal(rich_inlined_true_pred(alignments) if view == INLINED else rich_paired_true_pred(alignments))


def compare_true_pred1_pred2(triplets: Iterable[Iterable[str]]):
    """
    Visually compares triplets of ground-truths, 1st predictions and 2nd predictions in the collection.

    :param triplets: collection of three strings, each a ground-truth, a prediction, and another prediction
    :return: nothing, but displays comparison in terminal
    """

    alignments = pype(triplets).chunk(size=3).map(lambda true, pred1, pred2: tp1p2_align(true, pred1, pred2))

    in_terminal(rich_paired_true_pred1_pred2(alignments))

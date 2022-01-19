"""
Functions to display visually rich comparisons between sequential data
"""
import os
from shutil import get_terminal_size
from typing import Tuple, Iterable, Sequence

from itertools import zip_longest
from pypey import pype
from rich.console import Console

from pyaliner.align import align, COMPACT, JOIN, GAP, SKIP, Seq

ELLIPSIS = '[orange3]...[/orange3]'
WHITE = 'grey93'
BOLD_BLUE = 'b #0EADF1'
BOLD_RED = 'b #F1520E'
DIM_MAGENTA = 'dim bright_magenta'
MAGENTA = 'bright_magenta'
GREY = 'grey70'

SCREEN_WIDTH = 100
SPACE_N = 1
ELLIPSIS_N = 3
MARGIN_N = 3

DEFAULT_CONSOLE = Console(highlight=False)


def in_terminal(comparisons: Iterable[str], console: Console = DEFAULT_CONSOLE):
    """
    Displays comparisons with a pager in the terminal

    :param comparisons: collection of comparison lines
    :param console: console to print to terminal with
    :return: nothing, but displays comparison in terminal
    """

    # return tuple(comparisons)
    if not os.environ.get('PAGER'):
        os.environ['PAGER'] = 'less -r'

    with console.pager(styles=True):
        for line in comparisons:
            console.print(line)


def rich_paired_in_true_pred(alignments: Iterable[Tuple[Seq, Seq, Seq]]) -> Iterable[str]:
    """
    Creates rich visual comparison strings for a collection of triples of input, true and predicted sequences, aligned
    against each other

    :param alignments: Triples of tuples of strings representing inputs, ground-truths and predictions
    :return: a collection of rich strings for terminal display
    """
    screen_width, _ = get_terminal_size()

    return (pype(alignments)
            .map(lambda in_seq, true, pred: seq_in_true_pred_paired(in_seq, true, pred, screen_width))
            .map(''.join))


def rich_paired_true_pred(alignments: Iterable[Tuple[Seq, Seq]]) -> Iterable[str]:
    """
    Creates rich visual comparison strings for a collection of pairs of true and predicted sequences, aligned
    against each other

    :param alignments: Pairs of tuples of strings representing ground-truths and predictions
    :return: a collection of rich strings for terminal display
    """
    screen_width, _ = get_terminal_size()

    return pype(alignments).map(lambda true, pred: seq_true_pred_paired(true, pred, screen_width)).map(''.join)


def rich_inlined_true_pred(alignments: Iterable[Tuple[Seq, Seq]]) -> Iterable[str]:
    """
    Creates rich visual comparison strings for a collection of pairs of true and predicted sequences, embedded in the
    same line

    :param alignments: Pairs of tuples of strings representing ground-truths and predictions
    :return: a collection of rich strings for terminal display
    """
    for ref, rec in alignments:
        ui = []

        for ref_token, rec_token in zip(ref, rec):

            if ref_token == rec_token:

                ui.append(_in_white(ref_token))

            elif rec_token == GAP:

                ui.append(f'{_in_dim_magenta("[")}{_in_strike_red(ref_token)}{_in_dim_magenta("]")}')

            elif ref_token == GAP:

                ui.append(f'{_in_dim_magenta("[")}{_in_magenta("↗ ")}{_in_red(rec_token)}{_in_dim_magenta("]")}')

            else:

                ui.append(f'{_in_dim_magenta("[")}{_in_blue(ref_token)} {_in_red(rec_token)}{_in_dim_magenta("]")}')

        yield f' {" ".join(ui)}\n'.replace(JOIN, _in_white(JOIN))


def rich_paired_true_pred1_pred2(alignments: Iterable[Tuple[Seq, Seq, Seq]]) -> Iterable[str]:
    """
    Creates rich visual comparison strings for a collection of triples of input, true and predicted sequences, aligned
    against each other

    :param alignments: Triples of tuples of strings representing inputs, ground-truths and predictions
    :return: a collection of rich strings for terminal display
    """
    screen_width, _ = get_terminal_size()

    return (pype(alignments)
            .map(lambda in_seq, true, pred: seq_true_pred1_pred2(in_seq, true, pred, screen_width))
            .map(''.join))


def seq_in_true_pred_paired(in_seq: Sequence[str], true: Sequence[str], pred: Sequence[str], screen_width: int)\
        -> Iterable[str]:
    """
    Creates rich visual comparison strings for at triplet of input, true and predicted sequences, one for each chunk
    that fits the screen width

    :param in_seq: input sequence
    :param true: true sequence
    :param pred: predicted sequence
    :param screen_width: max terminal screen width
    :return: an `Iterable` of  rich strings
    """
    in_ui, true_ui, pred_ui = [], [], []

    length = 0

    for in_token, true_token, pred_token in zip_longest(in_seq, true, pred, fillvalue=SKIP):

        true_token, pred_token = _realign_true_pred(true_token, pred_token)

        pad = max(len(in_token), len(JOIN.join(true_token)), len(JOIN.join(pred_token)))

        if (length + pad + SPACE_N + ELLIPSIS_N + SPACE_N + MARGIN_N) >= screen_width:
            in_ui.append(f'{ELLIPSIS}')
            true_ui.append(f'{ELLIPSIS}')
            pred_ui.append(f'{ELLIPSIS}')

            yield f" {' '.join(in_ui)}\n {' '.join(true_ui)}\n {' '.join(pred_ui)}\n\n".replace(JOIN, _in_grey(JOIN))

            in_ui = [ELLIPSIS]
            true_ui = [ELLIPSIS]
            pred_ui = [ELLIPSIS]

            length = ELLIPSIS_N + SPACE_N

        in_colour_fn = _in_white if in_token == JOIN.join(true_token) and in_token == JOIN.join(
            pred_token) else _in_blue

        coloured_true_token, coloured_pred_token = _recolour(in_token, true_token, pred_token)

        in_ui.append(in_colour_fn(f'{in_token:^{pad}}'))
        true_ui.append(f'{coloured_true_token + " " * (max(0, len(in_token) - len(JOIN.join(true_token))))}')
        pred_ui.append(f'{coloured_pred_token + " " * (max(0, len(in_token) - len(JOIN.join(true_token))))}')

        length += pad + SPACE_N

    yield f" {' '.join(in_ui)}\n {' '.join(true_ui)}\n {' '.join(pred_ui)}\n".replace(JOIN, _in_grey(JOIN))


def seq_true_pred_paired(true: Sequence[str], pred: Sequence[str], screen_width: int) -> Iterable[str]:
    """
    Creates rich visual comparison strings for a pair of true and predicted sequences, one for each chunk that fits
    the screen width

    :param true: true sequence
    :param pred: predicted sequence
    :param screen_width: max terminal screen width
    :return: an `Iterable` of  rich strings
    """
    true_ui, pred_ui = [], []

    length = 0

    for true_token, pred_token in zip_longest(true, pred):

        pad = max(len(true_token), len(pred_token))

        if (length + pad + SPACE_N + ELLIPSIS_N + SPACE_N + MARGIN_N) >= screen_width:
            true_ui.append(f'{ELLIPSIS}')
            pred_ui.append(f'{ELLIPSIS}')

            yield f" {' '.join(true_ui)}\n {' '.join(pred_ui)}\n\n".replace(JOIN, _in_grey(JOIN))

            true_ui = [ELLIPSIS]
            pred_ui = [ELLIPSIS]

            length = ELLIPSIS_N + SPACE_N

        true_colour_fn = _in_white if true_token == pred_token else _in_blue
        pred_colour_fn = _in_white if true_token == pred_token else _in_red

        true_ui.append(true_colour_fn(f'{true_token:^{pad}}'))
        pred_ui.append(pred_colour_fn(f'{pred_token:^{pad}}'))

        length += pad + SPACE_N

    yield f" {' '.join(true_ui)}\n {' '.join(pred_ui)}\n".replace(JOIN, _in_grey(JOIN))


def seq_true_pred1_pred2(true: Sequence[str], pred1: Sequence[str], pred2: Sequence[str], screen_width: int)\
        -> Iterable[str]:
    """
    Creates rich visual comparison strings for at triplet of true, 1st and 2nd predicted sequences, one for each chunk
    that fits the screen width

    :param true: true sequence
    :param pred1: first predicted sequence
    :param pred2: second predicted sequence
    :param screen_width: max terminal screen width
    :return: an `Iterable` of  rich strings
    """
    true_ui, pred1_ui, pred2_ui = [], [], []

    length = 0

    for true_token, pred1_token, pred2_token in zip_longest(true, pred1, pred2, fillvalue=SKIP):

        pad = max(len(true_token), len(pred1_token), len(pred2_token))

        if (length + pad + SPACE_N + ELLIPSIS_N + SPACE_N + MARGIN_N) >= screen_width:
            true_ui.append(f'{ELLIPSIS}')
            pred1_ui.append(f'{ELLIPSIS}')
            pred2_ui.append(f'{ELLIPSIS}')

            yield f" {' '.join(true_ui)}\n {' '.join(pred1_ui)}\n {' '.join(pred2_ui)}\n\n"

            true_ui = [ELLIPSIS]
            pred1_ui = [ELLIPSIS]
            pred2_ui = [ELLIPSIS]

            length = ELLIPSIS_N + SPACE_N

        true_colour_fn = _in_white if true_token == pred1_token and true_token == pred2_token else _in_blue
        pred1_colour_fn = _in_white if true_token == pred1_token else _in_grey if pred1_token == SKIP else _in_red
        pred2_colour_fn = _in_white if true_token == pred2_token else _in_grey if pred2_token == SKIP else _in_red

        true_ui.append(true_colour_fn(f'{true_token:^{pad}}'))
        pred1_ui.append(pred1_colour_fn(f'{pred1_token:^{pad}}'))
        pred2_ui.append(pred2_colour_fn(f'{pred2_token:^{pad}}'))

        length += pad + SPACE_N

    yield f" {' '.join(true_ui)}\n {' '.join(pred1_ui)}\n {' '.join(pred2_ui)}\n"


def _realign_true_pred(true: str, pred: str) -> Tuple[Seq, Seq]:
    unjoined_true, unjoined_pred = tuple(true.split(JOIN)), tuple(pred.split(JOIN))

    new_true, new_pred = [], []

    for true_bit, pred_bit in zip(*align(unjoined_true, unjoined_pred, kind=COMPACT)):
        pad = max(len(true_bit), len(pred_bit))

        new_true.append(f'{true_bit:^{pad}}')
        new_pred.append(f'{pred_bit:^{pad}}')

    return tuple(new_true[::-1]), tuple(new_pred[::-1])


def _recolour(in_seq: str, true: Seq, pred: Seq) -> Tuple[str, str]:
    if JOIN.join(true) == in_seq and JOIN.join(pred) == in_seq:
        return _in_white(' '.join(true)), _in_white(' '.join(pred))

    colored_true, coloured_pred = [], []

    for true_token, pred_token in zip(true, pred):
        colored_true.append(_in_blue(true_token))
        coloured_pred.append(_in_blue(pred_token) if true_token == pred_token else _in_red(pred_token))

    return ' '.join(colored_true[::-1]), ' '.join(coloured_pred[::-1])


def _in_white(token: str) -> str:
    return f'[{WHITE}]{token}[/{WHITE}]'


def _in_grey(token: str) -> str:
    return f'[{GREY}]{token}[/{GREY}]'


def _in_blue(token: str) -> str:
    return f'[{BOLD_BLUE}]{token}[/{BOLD_BLUE}]'


def _in_red(token: str) -> str:
    return f'[{BOLD_RED}]{token}[/{BOLD_RED}]'


def _in_dim_magenta(token: str) -> str:
    return f'[{DIM_MAGENTA}]{token}[/{DIM_MAGENTA}]'


def _in_magenta(token: str) -> str:
    return f'[{MAGENTA}]{token}[/{MAGENTA}]'


def _in_strike_red(token: str) -> str:
    return f'[s {BOLD_RED}]{token}[/s {BOLD_RED}]'


def _in_strong_red(token: str) -> str:
    return f'[u {BOLD_RED}]{token}[/u {BOLD_RED}]'

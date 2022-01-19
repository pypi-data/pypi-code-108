"""
Functions to align sequential data
"""

import re
from collections import deque
from typing import Tuple, Sequence, List

from edlib import align as edalign
from pypey import pype, Fn

Seq = Tuple[str, ...]

CLASSIC = 'classic'
COMPACT = 'compact'
NGRAM = 'ngram'

GAP = '⎵'
JOIN = '∙'
SKIP = '∷'

LEV = lambda left, right: float(left != right)

CIGAR_RE = re.compile(r'([=DIX])')

DELTA = 1e-6


def align(left: Sequence[str], right: Sequence[str], cost_fn: Fn[[str, str], float] = LEV, kind: str = CLASSIC) \
        -> Tuple[Seq, Seq]:
    """
    Aligns left and right sequences using the edit distance computation. Passing in a cost function allows
    varying the substitution, deletion and insertion costs. The type of alignment can be varied with the `kind`
    parameter, which can be `CLASSIC` OR `COMPACT`. `COMPACT` alignment merges adjacent mismatches into a single one,
    joined up with the `JOIN` symbol, which can show differences more clearly.

    In the current implementation, when a cost function other than `LEV` is passed in, or when the number of unique
    tokens in the left and right sequences is greater than 256, alignments slows down.
    
    :param left: left sequence of strings
    :param right: right sequence of strings
    :param cost_fn: function taking a left and a right token and returning a cost
    :param kind: the kind of of alignment, default is `CLASSIC`
    :return: a `tuple` of `str`s  with the left and right alignments
    """
    if cost_fn == LEV:
        return _fast_align(left, right) if kind == CLASSIC else _compact_align(left, right)

    return _flexible_align(left, right, cost_fn)[:-1]


def as_cigar(left: Sequence[str], right: Sequence[str]) -> str:
    """
    Returns a CIGAR-encoded version of the given alignment

    :param left: right alignment
    :param right: left alignment
    :return: CIGAR-encoded alignment
    """
    cigar = ''

    for left_token, right_token in zip(left, right):
        if left_token == right_token:

            if cigar and cigar[-1] == '=':
                *head, num, op = CIGAR_RE.split(cigar)[:-1]
                cigar = f'{"".join(head)}{int(num) + 1}{op}'
            else:
                cigar += '1='

        elif left_token == GAP:

            if cigar and cigar[-1] == 'D':
                *head, num, op = CIGAR_RE.split(cigar)[:-1]
                cigar = f'{"".join(head)}{int(num) + 1}{op}'
            else:
                cigar += '1D'

        elif right_token == GAP:

            if cigar and cigar[-1] == 'I':
                *head, num, op = CIGAR_RE.split(cigar)[:-1]
                cigar = f'{"".join(head)}{int(num) + 1}{op}'
            else:
                cigar += '1I'
        else:

            if cigar and cigar[-1] == 'X':
                *head, num, op = CIGAR_RE.split(cigar)[:-1]
                cigar = f'{"".join(head)}{int(num) + 1}{op}'
            else:
                cigar += '1X'

    return cigar


def compact(left_ali: Sequence[str], right_ali: Sequence[str]) -> Tuple[Seq, Seq]:
    """
    Takes a classic alignment and turns it into a compact one

    :param left_ali: left classic alignment
    :param right_ali: right classic alignment
    :return: compact alignment
    """
    new_left_ali, new_right_ali = [], []

    for left_token, right_token in zip(left_ali, right_ali):

        if (not new_left_ali and not new_right_ali) or left_token == right_token:
            new_left_ali.append(left_token)
            new_right_ali.append(right_token)

            continue

        last_left, last_right = new_left_ali[-1], new_right_ali[-1]

        if right_token == GAP:

            if last_left == GAP:

                new_left_ali.pop()
                new_left_ali.append(left_token)

            elif last_left != last_right:

                new_left_ali.append(_join(new_left_ali.pop(), left_token))

            else:

                new_left_ali.append(left_token)
                new_right_ali.append(right_token)

        elif left_token == GAP:

            if last_right == GAP:

                new_right_ali.pop()
                new_right_ali.append(right_token)

            elif last_left != last_right:

                new_right_ali.append(_join(new_right_ali.pop(), right_token))

            else:

                new_left_ali.append(left_token)
                new_right_ali.append(right_token)
        else:

            if last_left == GAP:

                new_left_ali.pop()
                new_left_ali.append(left_token)
                new_right_ali.append(_join(new_right_ali.pop(), right_token))

            elif last_right == GAP:

                new_right_ali.pop()
                new_right_ali.append(right_token)

                new_left_ali.append(_join(new_left_ali.pop(), left_token))

            else:

                new_left_ali.append(left_token)
                new_right_ali.append(right_token)

    return tuple(new_left_ali), tuple(new_right_ali)


def itp_align(in_seq: Sequence[str], true: Sequence[str], pred: Sequence[str], align_fn: Fn) -> Tuple[Seq, Seq, Seq]:
    """
    Aligns input, true and predicted sequences

    :param in_seq: input sequence
    :param true: true sequence
    :param pred: predicted sequence
    :param align_fn: alignment function
    :return: a triplet with the passed-in sequences aligned
    """
    # TODO THIS IS A SLOW HEURISTIC METHOD, NEEDS REPLACING WITH MORE PERFORMANT BETTER THOUGHT-THROUGH ALGORITHM

    true_ali, pred_ali = align_fn(true, pred)

    input_ali, true_ali = align_fn(in_seq, true_ali)
    input_ali, pred_ali = align_fn(input_ali, pred_ali)

    if len(input_ali) != len(true_ali) or len(true_ali) != len(pred_ali):
        true_ali, pred_ali = align_fn(true_ali, pred_ali)

        input_ali, true_ali = align_fn(input_ali, true_ali)
        input_ali, pred_ali = align_fn(input_ali, pred_ali)

    if len(input_ali) != len(true_ali) or len(true_ali) != len(pred_ali):
        true_ali, pred_ali = align_fn(true_ali, pred_ali)

        input_ali, true_ali = align_fn(input_ali, true_ali)
        input_ali, pred_ali = align_fn(input_ali, pred_ali)

    return (pype([input_ali, true_ali, pred_ali])
            .zip(trunc=False, pad=SKIP)
            .reject(lambda _in, true, pred: _in == GAP and true == GAP and pred == GAP)
            .map(lambda _in, true, pred: (_in.strip(GAP + JOIN) if len(_in) > 2 else _in, true, pred))
            .unzip()
            .map(tuple)
            .to(tuple))


def tp1p2_align(true: Sequence[str], pred1: Sequence[str], pred2: Sequence[str]) -> Tuple[Seq, Seq, Seq]:
    """
    Aligns true, 1st and 2nd predicted sequences

    :param true: true sequence
    :param pred1: input sequence
    :param pred2: predicted sequence
    :return: a triplet with the passed-in sequences aligned
    """
    true1_ali, pred1_ali = (deque(seq) for seq in align(true, pred1))

    true2_ali, pred2_ali = (deque(seq) for seq in align(true, pred2))

    return three_way_realign(true1_ali, pred1_ali, true2_ali, pred2_ali)


def three_way_realign(true1_ali: Sequence[str],
                      pred1_ali: Sequence[str],
                      true2_ali: Sequence[str],
                      pred2_ali: Sequence[str]) -> Tuple[Seq, Seq, Seq]:
    """

    Combines the 4 aligned sequences into a single true sequence and adjusted 1st and 2nd predicted sequences. This
    function assumes that the only difference between 1st and 2nd true alignments is in the number and placement of
    gaps.

    :param true1_ali: first true alignment
    :param pred1_ali: first predicted alignment
    :param true2_ali: second true alignment
    :param pred2_ali: second predicted algnment
    :return: a triplet with the combined alignments of the passed-in sequences
    """
    combo_true_ali, combo_pred1_ali, combo_pred2_ali = [], [], []

    while true1_ali or true2_ali:
        true1 = true1_ali.popleft() if true1_ali else None
        pred1 = pred1_ali.popleft() if pred1_ali else None
        true2 = true2_ali.popleft() if true2_ali else None
        pred2 = pred2_ali.popleft() if pred2_ali else None

        if true1 == GAP and true2 != GAP:
            combo_true_ali.append(true1)
            combo_pred1_ali.append(pred1)
            combo_pred2_ali.append(SKIP)
            true2_ali.appendleft(true2)
            pred2_ali.appendleft(pred2)

        elif true1 != GAP and true2 == GAP:
            combo_true_ali.append(true2)
            combo_pred1_ali.append(SKIP)
            combo_pred2_ali.append(pred2)
            true1_ali.appendleft(true1)
            pred1_ali.appendleft(pred1)

        else:
            combo_true_ali.append(true1)
            combo_pred1_ali.append(pred1)
            combo_pred2_ali.append(pred2)

    return pype([combo_true_ali, combo_pred1_ali, combo_pred2_ali]).map(tuple).to(tuple)


def _fast_align(left: Sequence[str], right: Sequence[str]) -> Tuple[Seq, Seq]:
    """
    A fast implementation of the classic edit distances alignment, using `edlib`

    :param left: left sequence of strings
    :param right:  right sequence of strings
    :return: a `tuple` of `str`s  with the left and right alignments
    """
    cigar = None
    try:

        cigar = edalign(left, right, task='path')['cigar']

    except ValueError:

        cigar = as_cigar(*_flexible_align(left, right, LEV)[:-1])

    cigar = pype(CIGAR_RE.split(cigar)[:-1]).chunk(2)

    left_start, right_start = 0, 0
    left_ali, right_ali = [], []

    for num, op in cigar:
        num = int(num)

        if op == 'X' or op == '=':

            left_ali.extend(left[left_start: left_start + num])
            right_ali.extend(right[right_start: right_start + num])

            left_start, right_start = left_start + num, right_start + num

        elif op == 'I':

            left_ali.extend(left[left_start: left_start + num])
            right_ali.extend([GAP] * num)

            left_start += num

        else:
            left_ali.extend([GAP] * num)
            right_ali.extend(right[right_start: right_start + num])

            right_start += num

    return tuple(left_ali), tuple(right_ali)


def _compact_align(left: Sequence[str], right: Sequence[str]) -> Tuple[Seq, Seq]:
    """
    Aligns sequences by finding the classic edit distance alignment and then merging adjacent substitutions, insertions
    and deletions, joined up with the `JOIN` symbol

    :param left: left sequence of strings
    :param right:  right sequence of strings
    :return: a `tuple` of `str`s  with the left and right alignments
    """
    cigar = None

    try:

        cigar = edalign(left, right, task='path')['cigar']

    except ValueError:

        cigar = as_cigar(*_flexible_align(left, right, LEV)[:-1])

    cigar = pype(CIGAR_RE.split(cigar)[:-1]).chunk(2).eager()

    left_start, right_start = 0, 0
    left_ali, right_ali = [], []

    for num, op in cigar:
        num = int(num)

        if op == '=':

            left_ali.extend(left[left_start: left_start + num])
            right_ali.extend(right[right_start: right_start + num])

            left_start, right_start = left_start + num, right_start + num

        elif op == 'X':

            left_ali.append(JOIN.join(left[left_start: left_start + num]))
            right_ali.append(JOIN.join(right[right_start: right_start + num]))

            left_start, right_start = left_start + num, right_start + num

        elif op == 'I':

            left_ali.extend(left[left_start: left_start + num])
            right_ali.extend([GAP] * num)

            left_start += num

        else:
            left_ali.extend([GAP] * num)
            right_ali.extend(right[right_start: right_start + num])

            right_start += num

    return compact(left_ali, right_ali)


def _flexible_align(left: Sequence[str], right: Sequence[str], cost_fn: Fn[[str, str], float]) \
        -> Tuple[Seq, Seq, float]:
    """
    Slow version of the classic edit distance alignment supporting parametrisation of the cost matrix

    :param left: left sequence of strings
    :param right:  right sequence of strings
    :param cost_fn: function taking a left and a right token and returning a cost
    :return: a `tuple` of `str`s  with the left and right alignments
    """
    if not left or not right:
        raise Exception(f'{left} or {right} or both are empty')

    return _grid_align(left, right, cost_fn, _grid(left, right, cost_fn))


def _grid_align(left: Sequence[str], right: Sequence[str], cost_of: Fn[[str, str], float], grid: List[List[float]]) \
        -> Tuple[Seq, Seq, float]:
    """
    computes minimum cost alignment of left and right sequences for the given cost grid and cost function

    :param left: left sequence
    :param right: right sequence
    :param cost_of: left - right symbol substitution/indel cost function
    :param grid: partial edit distance costs grid
    :return: left sequence alignment, right sequence alignment and edit distance
    """
    L_align, R_align = deque(), deque()
    row, col = len(left), len(right)

    # order of conditionals is important as it will determine which alignment (middle[=implemented], left, right)
    # will be preferred when they have the same cost
    while row + col > 0:

        cost = grid[row][col]

        if row > 0 and col > 0 and abs(cost - grid[row - 1][col - 1] - cost_of(left[row - 1], right[col - 1])) < DELTA:

            L_align.appendleft(left[row - 1])
            R_align.appendleft(right[col - 1])
            row -= 1
            col -= 1

        elif row > 0 and abs(cost - grid[row - 1][col] - cost_of(left[row - 1], GAP)) < DELTA:

            L_align.appendleft(left[row - 1])
            R_align.appendleft(GAP)
            row -= 1

        elif col > 0 and abs(cost - grid[row][col - 1] - cost_of(GAP, right[col - 1])) < DELTA:

            L_align.appendleft(GAP)
            R_align.appendleft(right[col - 1])
            col -= 1

        else:
            raise Exception(f'No cell cost match for '
                            f'alignments {L_align} {R_align} of {left} {right} at r=[{row}] c=[{col}]')

    return tuple(L_align), tuple(R_align), grid[-1][-1]


def _grid(left: Sequence[str], right: Sequence[str], cost_of: Fn[[str, str], float]) -> List[List[float]]:
    """
    Builds a 2D-array where each cell contains the cost of the partial paths ending in the
    corresponding positions of the left and right strings. The last cell contains the minimum
    edit distance, aka, alignment cost.

    It follows the convention that the left string is indexed by rows and the right one by columns; also,
    the left-GAP cost is associated with the row above and the GAP-right cost with the column to the left; filling
    of the grid advances by column, top to bottom

    :param left: the left sequence
    :param right: the right sequence
    :param cost_of: the edit operation cost function
    :return: a 2D array filled with the partial alignment costs

    """

    V, H = len(left) + 1, len(right) + 1

    grid = [[0. for c in range(H)] for r in range(V)]

    for r in range(1, V):
        grid[r][0] = grid[r - 1][0] + cost_of(left[r - 1], GAP)  # first column

    for c in range(1, H):

        grid[0][c] = grid[0][c - 1] + cost_of(GAP, right[c - 1])  # first row

        for r in range(1, V):
            grid[r][c] = min(
                grid[r - 1][c - 1] + cost_of(left[r - 1], right[c - 1]),  # diagonal / substitution
                grid[r - 1][c] + cost_of(left[r - 1], GAP),  # vertical / gap in right
                grid[r][c - 1] + cost_of(GAP, right[c - 1]))  # horizontal / gap in left

    return grid


def _join(left: str, right: str) -> str:
    return f'{left}{JOIN}{right}'

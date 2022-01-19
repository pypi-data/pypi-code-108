from collections import defaultdict
from dataclasses import dataclass
from functools import partial
from statistics import mean
from typing import Tuple, Callable as Fn, Iterable, Dict, Sequence

from math import inf, sqrt, log
from more_itertools import interleave_evenly
from pypey import Pype, pype

from pyaliner import Seq, GAP
from pyaliner.align import _flexible_align as cost_align

Pair = Tuple[Seq, Seq]


@dataclass
class Stats:
    bigrams: Dict[Tuple[str, str], int]
    leftgrams: Dict[str, int]
    rightgrams: Dict[str, int]
    N: int


def left_align_all(pairs: Iterable[Tuple[Seq, Seq]]) -> Iterable[Tuple[Seq, Seq]]:
    """

    :param pairs:
    :return:
    """

    for left, right in pairs:
        longest = max(len(left), len(right))
        left += (GAP,) * (longest - len(left))
        right += (GAP,) * (longest - len(right))

        yield left, right, 0


def left_align(left: Sequence[str], right: Sequence[str]) -> Tuple[Seq, Seq, float]:
    """

    :param pairs:
    :return:
    """

    longest = max(len(left), len(right))
    left += (GAP,) * (longest - len(left))
    right += (GAP,) * (longest - len(right))

    return left, right, 0


def flat_align(left: Sequence[str], right: Sequence[str]):
    if len(left) == len(right):

        return left, right, 0

    elif len(left) > len(right):

        gaps = (GAP,) * (len(left) - len(right))

        return left, tuple(interleave_evenly([right, gaps])), 0

    else:

        gaps = (GAP,) * (len(right) - len(left))

        return tuple(interleave_evenly([left, gaps])), right, 0


def estimate_cost_align_fn_from(alignments: Pype[Tuple[Pair, Pair, float]]):
    nmpis = npmi_scores_from(counts_from(alignments.map(lambda left, right, cost: (left, right))))

    cost_fn = lambda left, right: 1 - .5 * (nmpis.get((left, right), .5) + 1)

    return partial(cost_align, cost_fn=cost_fn)


def autoalign(pairs: Iterable[Tuple[Pair]],
              align_fn: Fn[[Sequence[str], Sequence[str]], Tuple] = left_align,
              estimate_align_fn: Fn[[Iterable[Tuple]], Fn[[Sequence, Sequence], Tuple]] = estimate_cost_align_fn_from,
              min_avg_loss: float = inf,
              max_cycles: int = 10_000) -> Tuple[Tuple[Seq, Seq, float], ...]:
    """"""
    print('cycle', max_cycles)
    alignments = pype(align_fn(left, right) for left, right in pairs).eager()

    if max_cycles <= 0:
        return alignments

    avg_loss = mean(loss for left, right, loss in alignments)
    print('loss', avg_loss)
    if avg_loss >= min_avg_loss:
        return alignments

    return autoalign(pairs, estimate_align_fn(alignments), estimate_align_fn, avg_loss, max_cycles - 1)


def counts_from(alignments: Iterable[Pair]) -> Stats:
    """

    :param alignments:
    :return:
    """
    bicounts = defaultdict(int)
    for L_align, R_align in alignments:

        for left_sym, right_sym in zip(L_align, R_align):
            bicounts[left_sym, right_sym] += 1

    N = 0
    left_counts, right_counts = defaultdict(int), defaultdict(int)
    for (left_sym, right_sym), freq in bicounts.items():
        left_counts[left_sym] += freq
        right_counts[right_sym] += freq
        N += freq

    return Stats(bicounts, left_counts, right_counts, N)


def npmi_scores_from(stats: Stats) -> Dict[Tuple[str, str], float]:
    npmis = {}

    for (left, right), bigram in stats.bigrams.items():
        bi_prob, left_prob, right_prob, N = bigram / stats.N, stats.leftgrams[left] / stats.N, stats.rightgrams[
            right] / stats.N, stats.N

        npmi = (log(bi_prob) - log(left_prob) - log(right_prob)) / - log(bi_prob)

        npmis[left, right] = corrected_pmi(npmi, stats.leftgrams[left], stats.rightgrams[right])

    return npmis


def corrected_pmi(pmi: float, left_freq: int, right_freq: int) -> float:
    return pmi * (1 - 1 / sqrt(min(left_freq, right_freq)))

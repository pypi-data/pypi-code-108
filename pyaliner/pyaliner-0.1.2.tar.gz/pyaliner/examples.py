from typing import Tuple, Sequence

from pypey import pype, Pype

from pyaliner.autoalign import autoalign, Pair, estimate_cost_align_fn_from, flat_align


def g2p_data_from(path: str) -> Pype[Tuple[Pair, Pair]]:
    return (pype
            .file(path)
            .map(lambda line: line.split(','))
            .map(lambda word, pron: (tuple(word.split('(')[0]), tuple(pron.replace('ˈ', '').replace('ˌ', '').split())))
            .uniq()
            .eager())


def aligned_print(left: Sequence[str], right: Sequence[str]):
    ali_left, ali_right = [], []

    for left_token, right_token in zip(left, right):
        pad = max(len(left_token), len(right_token))

        ali_left.append(f'{left_token:{pad}}')
        ali_right.append(f'{right_token:{pad}}')

    return ali_left, ali_right


if __name__ == '__main__':
    path = '/home/jose/Documents/projects/speech2vec/data/britfone.main.3.0.1.extra.csv'


    (autoalign(g2p_data_from(path), align_fn = flat_align, max_cycles=100)
     .sort(lambda _1, _2, cost: -cost/len(_1))
     .map(lambda left, right, cost: tuple(aligned_print(left, right)) + (cost,))
     .print(lambda left, right, cost: f'{" ".join(left)}\t[{cost/len(left):5.3f}]\n{" ".join(right)}\n'))

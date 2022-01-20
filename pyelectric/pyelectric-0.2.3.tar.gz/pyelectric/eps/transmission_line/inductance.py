import math
from typing import Any, Iterable, List

from .conductor import Conductor


def list_of_lists_to_list(list_of_list: Iterable[List[Any]]) -> List[Any]:
    return [item for sublist in list_of_list for item in sublist]


def geometric_mean_distance(conductors_bundles: List[List[Conductor]]) -> float:
    distance: float = 1
    n: int = 0
    for i, conductors_bundle in enumerate(conductors_bundles):
        compare_conductors_bundles = conductors_bundles[i+1:]
        compare_conductors = list_of_lists_to_list(compare_conductors_bundles)
        for conductor1 in conductors_bundle:
            for conductor2 in compare_conductors:
                d = conductor1.distance(conductor2.position)
                distance *= d if d > 0 else conductor1.gmr
                n += 1
    distance = distance**(1/n)
    return distance


def calc_inductance(conductors_bundles: List[List[Conductor]]) -> float:
    Dm = geometric_mean_distance(conductors_bundles)
    Ds_list = [geometric_mean_distance([c, c]) for c in conductors_bundles]

    L_list = [2e-7*math.log(Dm/Ds) for Ds in Ds_list]
    L = sum(L_list)
    return L

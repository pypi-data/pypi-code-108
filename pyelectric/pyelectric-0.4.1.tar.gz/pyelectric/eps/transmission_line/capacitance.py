import math
from copy import deepcopy
from functools import reduce
from typing import Any, List

from .conductor import Conductor


def list_of_lists_to_list(list_of_list: List[List[Any]]) -> List[Any]:
    return [item for sublist in list_of_list for item in sublist]


def geometric_mean(list_of_numbers: List[float]) -> float:
    return reduce(lambda x, y: x*y, list_of_numbers)**(1/len(list_of_numbers))


def geometric_mean_distance(conductors_bundles: List[List[Conductor]]) -> float:
    distance: float = 1
    n: int = 0
    for i, conductors_bundle in enumerate(conductors_bundles):
        compare_conductors_bundles = conductors_bundles[i+1:]
        compare_conductors = list_of_lists_to_list(compare_conductors_bundles)
        for conductor1 in conductors_bundle:
            for conductor2 in compare_conductors:
                d = conductor1.distance(conductor2.position)
                distance *= d if d > 0 else conductor1.radius
                n += 1
    distance = distance**(1/n)
    return distance


def get_discounted_arrow_conductors(conductors_bundles: List[List[Conductor]], arrow: float) -> List[List[Conductor]]:
    conductors_bundles = deepcopy(conductors_bundles)
    for conductors_bundle in conductors_bundles:
        for conductor in conductors_bundle:
            conductor.position.y -= (2/3)*arrow
    return conductors_bundles


def get_ground_conductors(conductors_bundles: List[List[Conductor]]) -> List[List[Conductor]]:
    conductors_bundles = deepcopy(conductors_bundles)
    for conductors_bundle in conductors_bundles:
        for conductor in conductors_bundle:
            conductor.position.y *= -1
    return conductors_bundles


def calc_alpha(conductors_bundles: List[List[Conductor]], arrow: float) -> float:
    up_conductors_bundles = get_discounted_arrow_conductors(
        conductors_bundles, arrow)
    down_conductors_bundles = get_ground_conductors(up_conductors_bundles)

    Hs_list = [geometric_mean_distance([up, down]) for up, down in zip(
        up_conductors_bundles, down_conductors_bundles)]
    Hs = geometric_mean(Hs_list)

    Hm = geometric_mean_distance([
        list_of_lists_to_list(up_conductors_bundles),
        list_of_lists_to_list(down_conductors_bundles)
    ])

    alpha = math.log(Hm/Hs)

    return alpha


def calc_capacitance(conductors_bundles: List[List[Conductor]], arrow: float = None) -> float:
    Dm = geometric_mean_distance(conductors_bundles)
    Ds_list = [geometric_mean_distance([c, c]) for c in conductors_bundles]

    alpha: float = 0 if arrow is None else calc_alpha(
        conductors_bundles, arrow)
    e0 = 8.85e-12
    C_list = [2*math.pi*e0/(math.log(Dm/Ds) - alpha) for Ds in Ds_list]
    C = sum(C_list)/len(conductors_bundles)
    return C

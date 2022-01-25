import math
from typing import Dict, Callable, Set, Iterable

from sm.evaluation.sm_metrics import ScoringFn

ItemParents = Dict[str, Iterable[str]]


class HierarchyScoringFn(ScoringFn):
    def __init__(self, item_parents: ItemParents, get_item_uri: Callable[[str], str]):
        # mapping from the item to its parents
        self.i2i: Dict[str, Dict[str, int]] = {p: {} for p in item_parents}
        for p in item_parents:
            self.build_i2i(p, p, 1, item_parents, set())
        self.i2i = {
            get_item_uri(p): {get_item_uri(pp): d for pp, d in ppd.items()}
            for p, ppd in self.i2i.items()
        }

    def build_i2i(
        self,
        origin_item: str,
        current_item: str,
        distance: int,
        item_parents: ItemParents,
        visited: Set[str],
    ):
        if current_item in visited or current_item not in item_parents:
            return

        visited.add(current_item)
        for pp in item_parents[current_item]:
            if pp in self.i2i[origin_item]:
                self.i2i[origin_item][pp] = min(self.i2i[origin_item][pp], distance)
            else:
                self.i2i[origin_item][pp] = distance
            self.build_i2i(origin_item, pp, distance + 1, item_parents, visited)

    def get_match_score(self, pred_item: str, target_item: str):
        if pred_item == target_item:
            return 1.0
        if pred_item in self.i2i[target_item]:
            # pred_predicate is the parent of the target
            distance = self.i2i[target_item][pred_item]
            if distance > 5:
                return 0.0
            return math.pow(0.8, distance)
        if target_item in self.i2i[pred_item]:
            distance = self.i2i[pred_item][target_item]
            if distance > 3:
                return 0.0
            return math.pow(0.7, distance)
        return 0.0

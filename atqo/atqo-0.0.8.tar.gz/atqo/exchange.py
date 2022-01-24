from collections import defaultdict
from enum import Enum
from functools import cached_property, reduce
from itertools import product
from math import gcd
from typing import Dict, Iterable, List, Tuple, Union

from .exceptions import NotEnoughResources
from .resource_handling import CapabilitySet, NumStore


class CapsetExchange:
    def __init__(
        self,
        actor_capsets: Iterable[CapabilitySet],
        resources: Union[Dict[Enum, int], Iterable[Tuple[Enum, int]]],
    ) -> None:
        """trade resources for running actors with capsets

        - find possible trades
        - when prompted, filter these to possible ones
        - select best valued one
        - execute trade, refresh possible ones, repeat
        """

        self._sources = (
            [*resources.items()] if isinstance(resources, dict) else resources
        )  # can be limited what can be used together, later
        self._actor_capsets = sorted(actor_capsets)
        self.actors_running = {cs: 0 for cs in self._actor_capsets}
        self.tasks_queued = NumStore()
        self.idle_sources = [l // self._grans[eid] for eid, l in self._sources]

    def __repr__(self) -> str:
        bases = [
            ("actors used", self.actors_running),
            ("tasks queued", self.tasks_queued),
            (
                "using resources",
                self._utilized_resources,
            ),
            ("available resources", self.idle_sources),
        ]
        descr = "\n".join(f"{k}:\t{v}" for k, v in bases)
        return f"Capset Exchange: \n{descr}\n"

    def set_values(self, new_values: Union[NumStore, Dict[Enum, int]]):
        self.tasks_queued = NumStore(new_values)
        self._execute_positive_trades()
        return self.actors_running

    @property
    def idle(self):
        return not sum(self.actors_running.values())

    def _execute_positive_trades(self):
        while True:
            state = ExchangeState(self.tasks_queued, self.actors_running)
            max_value = 0
            best_trade = None
            for trade in self._possible_trades:
                if not self._is_possible(trade):
                    continue
                trade_value = state.valuation(trade)
                if trade_value > max_value:
                    best_trade = trade
                    max_value = trade_value
            if max_value <= 0:
                break
            self._execute_trade(best_trade)

    def _is_possible(self, trade: NumStore):
        for rid, num in trade:
            if isinstance(rid, int):
                rem = self.idle_sources[rid]
            else:
                rem = self.actors_running[rid]
            if (num + rem) < 0:
                return False
        return True

    def _get_source_prices(self, capset: CapabilitySet):

        by_source = self._source_combs(capset.total_resource_use)
        if not by_source:
            msg = f"can't ever start {capset}: \n{capset.total_resource_use}"
            raise NotEnoughResources(msg)

        return [NumStore({capset: 1}) - p for p in by_source]

    def _get_barter_prices(self, capset: CapabilitySet):

        bf = BarterFinder(capset, self._actor_capsets)

        barters = []
        for resources, barter_capsets in bf.barter_pairs:
            if resources.min_value > 0:
                source_combs = self._source_combs(resources.pos_part)
                barters += [barter_capsets + sc for sc in source_combs]
            else:
                barters.append(barter_capsets)
        return barters

    def _execute_trade(self, trade: NumStore):
        for rid, num in trade:
            if isinstance(rid, int):
                self.idle_sources[rid] += num
            else:
                self.actors_running[rid] += num

    def _source_combs(self, resource_use):
        combs = []
        for res_id, res_need in resource_use:
            gran_need = res_need // self._grans[res_id]
            poss_sources = [
                NumStore({sid: gran_need})
                for sid, limit in self._sources_by_res[res_id]
                if limit >= gran_need
            ]
            combs.append(poss_sources)
        if not combs:
            return []
        return [sum(poss, NumStore({})) for poss in product(*combs)]

    @property
    def _utilized_resources(self):
        return sum(
            [
                cs.total_resource_use * n
                for cs, n in self.actors_running.items()
            ],
            start=NumStore(),
        )

    @cached_property
    def _grans(self):
        # granularities

        res_int_lists = defaultdict(list)
        for res_id, res_int in self._sources + [
            items
            for capset in self._actor_capsets
            for items in capset.total_resource_use
        ]:
            res_int_lists[res_id].append(res_int)

        return {
            res_id: reduce(gcd, res_ints)
            for res_id, res_ints in res_int_lists.items()
        }

    @cached_property
    def _possible_trades(self) -> Iterable[NumStore]:
        """find all (so far most/useful) possible trades

        1. find all 1 actor -> idle resource trades
          - if one is not possible, raise/warn something
        2. find some between actor trades
        """
        all_trades = []
        for capset in self._actor_capsets:
            all_trades += self._get_source_prices(
                capset
            ) + self._get_barter_prices(capset)

        return all_trades + [t * -1 for t in all_trades]

    @cached_property
    def _sources_by_res(self) -> Dict[Enum, List[Tuple[int, int]]]:
        out = defaultdict(list)
        for sid, (res_id, limit) in enumerate(self._sources):
            out[res_id].append((sid, limit))
        return out


class BarterFinder:
    def __init__(
        self, capset: CapabilitySet, capsets: List[CapabilitySet]
    ) -> None:
        self._capset = capset
        self._possible_barters = [cs for cs in capsets if cs != capset]
        self.barter_pairs: List[Tuple[NumStore, NumStore]] = []
        self._get_all_barter_pairs(capset.total_resource_use)

    def _get_all_barter_pairs(self, available: NumStore, in_so_far=NumStore()):
        for capset in self._possible_barters:
            rest = available - capset.total_resource_use
            if rest.min_value >= 0:
                new_far = in_so_far + NumStore({capset: 1})
                self.barter_pairs.append(
                    (rest, new_far + NumStore({self._capset: -1}))
                )
                self._get_all_barter_pairs(rest, new_far)


class ExchangeState:
    def __init__(self, task_dic: NumStore, actor_dic: dict):
        self.rem_acts = actor_dic.copy()
        self.holes = defaultdict(lambda: 0)
        rem_tasks = 0
        for tcs, tcount in task_dic:
            task_stack = tcount
            for acs, acount in self.rem_acts.items():
                if not (acs >= tcs):
                    continue
                if acount > task_stack:
                    self.rem_acts[acs] -= task_stack
                    task_stack = 0
                    break
                task_stack -= acount
                self.rem_acts[acs] = 0
                self.holes[acs] -= task_stack
            rem_tasks += task_stack

    def valuation(self, trade: NumStore):
        value = 0
        for id_, c in trade:
            if isinstance(id_, int):
                value += c * 1e-5
                continue
            if c > 0:
                if -self.holes.get(id_, 0) < c:
                    return 0
                value += c
            if self.rem_acts[id_] < -c:
                value += c + self.rem_acts[id_]
        return value

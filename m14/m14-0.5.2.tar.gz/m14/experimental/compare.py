#!/usr/bin/env python3
# coding: utf-8

import dataclasses
from functools import cached_property

from pymongo.collection import Collection


@dataclasses.dataclass
class Comparison:
    c1_values: list
    c2_values: list

    @classmethod
    def from_collections(cls, c1: Collection, c2: Collection, field: str):
        args = (
            [r[field] for r in c1.find(projection=[field])],
            [r[field] for r in c2.find(projection=[field])]
        )
        return cls(*args)

    @cached_property
    def values(self):
        return self.c1_values + self.c2_values

    @cached_property
    def uniq_values(self):
        return self.uniq_c1_values | self.uniq_c2_values

    @cached_property
    def uniq_c1_values(self):
        return set(self.c1_values)

    @cached_property
    def uniq_c2_values(self):
        return set(self.c2_values)

    @cached_property
    def common_values(self):
        vals = [v for v in self.c1_values if v in self.uniq_c2_values]
        return [v for v in self.c2_values if v in self.uniq_c1_values] + vals

    @cached_property
    def uniq_common_values(self):
        return self.uniq_c1_values & self.uniq_c2_values

    def find_diff(self):
        return (
            self.uniq_c1_values - self.uniq_c2_values,
            self.uniq_c2_values - self.uniq_c1_values,
        )

    @property
    def counts(self):
        return (
            len(self.values),
            len(self.c1_values),
            len(self.c2_values),
            len(self.common_values),
            len([v for v in self.c1_values if v not in self.uniq_c2_values]),
            len([v for v in self.c2_values if v not in self.uniq_c1_values]),
        )

    @property
    def uniq_counts(self):
        return (
            len(self.uniq_values),
            len(self.uniq_c1_values),
            len(self.uniq_c2_values),
            len(self.uniq_common_values),
            len(self.uniq_c1_values - self.uniq_c2_values),
            len(self.uniq_c2_values - self.uniq_c1_values),
        )

    @property
    def duplication_ratio(self):
        return [t / u for t, u in zip(self.counts, self.uniq_counts)]

    def get_stats(self):
        attrnames = ['counts', 'uniq_counts', 'duplication_ratio']
        return {k: getattr(self, k) for k in attrnames}

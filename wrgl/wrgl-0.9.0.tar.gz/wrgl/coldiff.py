# SPDX-License-Identifier: Apache-2.0
# Copyright © 2021 Wrangle Ltd

import attr
import typing
import math

from wrgl.commit import Table
from wrgl.serialize import none_field_transformer


def longest_increasing_list(values: typing.List[int]) -> typing.List[int]:
    """Returns indices of longest increasing values

    :param list[int] values: arbitrary integers

    :rtype: list[int]
    """
    @attr.s(auto_attribs=True)
    class Node(object):
        ind: int
        len: int
        prev: "Node"

    nodes: typing.Dict[int, Node] = dict()
    root: Node = None
    for i, v in enumerate(values):
        prev: Node = None
        for j in range(v-1, -1, -1):
            if j in nodes and (prev is None or prev.len < nodes[j].len):
                prev = nodes[j]
            if prev is not None and j < prev.len:
                break
        nodes[v] = Node(ind=i, len=1, prev=prev)
        if prev is not None:
            nodes[v].len = prev.len + 1
        if root is None or root.len < nodes[v].len or (root.len == nodes[v].len and v == i):
            root = nodes[v]
    results = []
    while root is not None:
        results.insert(0, root.ind)
        root = root.prev
    return results


@attr.s(auto_attribs=True)
class MoveOp(object):
    old_ind: int
    new_ind: int


def moveOps(sl: typing.List[int]) -> typing.List[MoveOp]:
    """moveOps returns move operations that changed order of array indices
    """
    anchor_indices = longest_increasing_list(sl)
    for i in anchor_indices:
        sl[i] = -1
    ops: typing.List[MoveOp] = []
    for i, v in enumerate(sl):
        if v == -1:
            continue
        ops.append(MoveOp(old_ind=v, new_ind=i))
    return ops


@attr.s(auto_attribs=True, field_transformer=none_field_transformer)
class Move(object):
    after: int
    before: int


@attr.s(auto_attribs=True, field_transformer=none_field_transformer)
class Column(object):
    name: str = attr.ib()
    base_idx: int = attr.ib()
    base_pk: bool = attr.ib()
    added: typing.Set[int] = attr.ib(factory=set)
    removed: typing.Set[int] = attr.ib(factory=set)
    moved: typing.Dict[int, Move] = attr.ib(factory=dict)
    layer_idx: typing.Dict[int, int] = attr.ib(factory=dict)
    layer_pk: typing.Set[int] = attr.ib(factory=set)

    @property
    def is_added(self) -> bool:
        return len(self.added) > 0

    @property
    def is_removed(self) -> bool:
        return len(self.removed) > 0

    @property
    def is_moved(self) -> bool:
        return len(self.moved) > 0


class ColDiff(object):
    """Keeps track of how column composition and order change between a base version and one or more versions
    """

    columns: typing.List[Column]
    name_map: typing.Dict

    def __init__(self, base: Table, *layers: Table) -> None:
        self.columns = []
        self.name_map = dict()
        for layer in layers:
            self.insert_columns(layer.columns)
        self.insert_columns(base.columns)
        for i, layer in enumerate(layers):
            self.assign_column_attrs(base.columns, i, layer.columns)
        self.hoist_pk_to_start({
            v: i for i, v in enumerate(layers[0].primary_key)
        })
        self.assign_index(base, *layers)

    def hoist_pk_to_start(self, pk: typing.Dict[str, int]) -> None:
        self.columns = sorted(
            self.columns, key=lambda col: pk.get(col.name, math.inf))
        self.name_map = {
            s: i for i, s in enumerate([
                col.name for col in self.columns
            ])
        }

    def assign_index(self, base: Table, *layers: Table) -> None:
        for i, name in enumerate(base.columns):
            self.columns[self.name_map[name]].base_idx = i
        for name in base.primary_key:
            self.columns[self.name_map[name]].base_pk = True
        for i, layer in enumerate(layers):
            for j, name in enumerate(layer.columns):
                self.columns[self.name_map[name]].layer_idx[i] = j
            for name in layer.primary_key:
                self.columns[self.name_map[name]].layer_pk.add(i)

    def insert_columns(self, column_names: typing.List[str]) -> None:
        offset = -1
        insert_map: typing.Dict[int, typing.List[Column]] = dict()
        for name in column_names:
            if name in self.name_map:
                offset = self.name_map[name]
                continue
            insert_map.setdefault(offset, []).append(Column(name=name))
        if len(insert_map) == 0:
            return
        inserts = sorted(
            list(insert_map.items()),
            key=lambda pair: -pair[0]
        )
        for insert_off, cols in inserts:
            self.columns[insert_off+1:insert_off+1] = cols
        self.name_map = {
            s: i for i, s in enumerate([
                col.name for col in self.columns
            ])
        }

    def assign_column_attrs(self, base_cols: typing.List[str], layer_idx: int, layer_cols: typing.List[str]) -> None:
        base_set = set(base_cols)
        layer_set = set(layer_cols)
        for name in layer_cols:
            if name not in base_set:
                self.columns[self.name_map[name]].added.add(layer_idx)
        for name in base_cols:
            if name not in layer_set:
                self.columns[self.name_map[name]].removed.add(layer_idx)
        self.assign_column_moved(base_cols, layer_idx, layer_set)

    def assign_column_moved(self, base_cols: typing.List[str], layer_idx: int, layer_set: typing.Set[str]) -> None:
        common_cols = [
            name for name in base_cols
            if name in layer_set
        ]
        common_map = {
            name: i for i, name in enumerate(common_cols)
        }
        old_indices = []
        new_indices = []
        for i, col in enumerate(self.columns):
            if col.name in common_map:
                new_indices.append(i)
                old_indices.append(common_map[col.name])
        ops = moveOps(old_indices)
        non_anchor = set([v.old_ind for v in ops])
        for op in ops:
            new_ind = new_indices[op.new_ind]
            after = None
            for i in range(op.old_ind-1, -1, -1):
                if i in non_anchor:
                    continue
                after = common_cols[i]
                if after in self.name_map:
                    break
            if after is not None:
                self.columns[new_ind].moved[layer_idx] = Move(
                    after=self.name_map[after]
                )
                continue

            before = None
            for i in range(op.old_ind, len(common_cols)):
                if i in non_anchor:
                    continue
                before = common_cols[i]
                if before in self.name_map:
                    break
            if before is not None:
                self.columns[new_ind].moved[layer_idx] = Move(
                    before=self.name_map[before]
                )

    def rearrange_row(self, layer: int, row: typing.List[str]) -> typing.List[str]:
        return [
            None if col.layer_idx is None or layer not in col.layer_idx
            else row[col.layer_idx[layer]]
            for col in self.columns
        ]

    def rearrange_base_row(self, row: typing.List[str]) -> typing.List[str]:
        return [
            None if col.base_idx is None else row[col.base_idx]
            for col in self.columns
        ]

    def combine_rows(self, layer: int, new_row: typing.List[str], old_row: typing.List[str]) -> typing.List[typing.Tuple[str or None, str or None]]:
        return [
            (
                None if layer in col.removed else new_row[col.layer_idx[layer]],
                None if layer in col.added else old_row[col.base_idx]
            )
            for col in self.columns
        ]

    def no_column_changes(self) -> bool:
        for col in self.columns:
            if len(col.added) > 0 or len(col.removed) > 0 or len(col.moved) > 0:
                return False
        return True

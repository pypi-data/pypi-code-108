import pandas as pd
from typing import List
from collections import defaultdict
from dataclasses import dataclass, field
from .models import StratumItemModel

# --- FACTORY HELPERS ---------------------------------------------------------


@dataclass
class StrataFactory:
    df: pd.DataFrame
    cols: List[str] = field(default_factory=list)
    default_strata: str = None
    reverse: bool = False
    """
    Builds up hirearchy ``StratumItemModel`` items from a dataframe.
    Use ``self.stratas`` to get the generated strata list.

    Args:
        df: dataframe containing hierarchy columns
        cols: list of column names for the hierarchy; if all columns used, leave as default.
        default_strata: optional, usually the first strata in the list, such as 'All'
        reverse: set to True if upper level begins at the end columns and next levels move to the left.

    """

    def __post_init__(self):
        self.stratas = []
        _parent = None
        if self.default_strata:
            _parent = 0
            self.stratas.append(StratumItemModel(id=_parent, name=self.default_strata))
        self.df_ = self.df[self.cols] if self.cols else self.df
        self.root = self.ctree()
        self.map_to_root()
        self.populate(self.root, parent=_parent)

    @classmethod
    def ctree(cls):
        return defaultdict(cls.ctree)

    def map_to_root(self):
        for row in self.df_.itertuples(index=False):
            last = None
            for link in (reversed(row) if self.reverse else row):
                root_ = last if last is not None else self.root
                last = root_[link]

    def populate(self, subroot: dict, start: int = 1, parent: int = None):
        parents_temp_map = {}
        for n, key in enumerate(subroot.keys(), start=start):
            parents_temp_map[key] = n
            strata = StratumItemModel(id=n, name=key, parent_id=parent)
            self.stratas.append(strata)
        for key, values in subroot.items():
            if values:
                self.populate(values, len(self.stratas) + 1, parent=parents_temp_map[key])


@dataclass
class Leaf:
    parent: str
    value: float
    children: List[str] = field(default_factory=list)


def validate_sunburst_total_values(labels: list, parents: list, values: list) -> None:
    """
    Validates the total values are correct for Sunburst charts.

    Raises:
        ValueError: describes which parent does not have enough value for their children.

    """
    tree = {}
    for n, label in enumerate(labels):
        tree[label] = Leaf(parents[n], values[n])
    for n, parent in enumerate(parents):
        if parent in tree:
            tree[parent].children.append(labels[n])
    for parent, leaf in tree.items():
        children_sum = sum(tree[c].value for c in leaf.children)
        if leaf.value < children_sum:
            raise ValueError(f'Parent `{parent}` does not enough value ({leaf.value}) for its children values ({children_sum}).')

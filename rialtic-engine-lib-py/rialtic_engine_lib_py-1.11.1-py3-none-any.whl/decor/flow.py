import enum
from copy import copy
from typing import Dict, Any, List, Iterable, Callable

from enginelib.decor.node import Label
from enginelib.decor.predicate import Predicate
from enginelib.decor.tree import Tree
from enginelib.errors import Error


class DFS(enum.Enum):
    UNSEEN = 0
    DISCOVERED = 1
    EXPLORED = 2


class Connection:
    def __init__(self, label: Label, flow: 'Flow', ignore_insight: bool):
        self.label = str(label)
        self.flow = flow
        self.ignore_insight = ignore_insight


class Flow:
    _count: int = 0

    def __init__(self, tree: Tree):
        self.tree = copy(tree)
        if self.tree.root:
            raise Error(f'Flow cannot be created if the given tree has already been assembled.')
        self.connections: Dict[str, Connection] = dict()
        self.__class__._count += 1
        self.number = self.__class__._count
        self._has_on_start = False

    def connect(self, labels: Any, flow: 'Flow', ignore_insight: bool = False):
        labels = self._validate_and_normalize(labels)

        for label in labels:
            if label in self.connections:
                raise Error(f'There is already a connection at [{self.tree.name}]@{label} '
                            f'for flow #{self.number}.')

            if label not in self.tree.ResultClass.insight_type:
                raise Error(f'Not possible to create a connection at [{self.tree.name}]@{label} '
                            f'for flow #{self.number}, as the label "{label}" does not exist in the tree.')

            conn = Connection(label, flow, ignore_insight)
            if flow._has_cycle(status={self.number: DFS.DISCOVERED}):
                self._log(f'Flow #{self.number}  [{self.tree.name}]@{label}')
                raise Error(f'Circular flow detected. Please, make sure flow connections are acyclic.')

            self.connections[label] = conn

    def _has_cycle(self, status: Dict[int, DFS]) -> bool:
        """Depth first search."""
        if status.setdefault(self.number, DFS.UNSEEN) == DFS.DISCOVERED:
            self._log('Cycle detected (printed backwards): ')
            self._log(f'Flow #{self.number}  [{self.tree.name}]')
            return True

        status[self.number] = DFS.DISCOVERED
        for label, conn in self.connections.items():
            number = conn.flow.number
            if status.setdefault(number, DFS.UNSEEN) == DFS.EXPLORED:
                continue
            if conn.flow._has_cycle(status):
                self._log(f'Flow #{self.number}  [{self.tree.name}]@{label}')
                return True

        status[self.number] = DFS.EXPLORED
        return False

    def _validate_and_normalize(self, labels: Any) -> List[str]:
        valid_labels = self.tree.ResultClass.insight_type
        if labels == any or labels == all:
            labels = list(valid_labels)
        elif isinstance(labels, str) or isinstance(labels, int):
            labels = [labels]
        elif not isinstance(labels, Iterable):
            raise TypeError(f'Parameter `labels` should be a list of labels or a single label.')

        normalized_labels: List[str] = list()
        for label in labels:
            if label not in valid_labels:
                raise ValueError(f'Invalid label "{label}" given in the `labels` parameter.')
            normalized_labels.append(str(label))
        return normalized_labels

    def on_start(self, func: Callable[..., Any]):
        if self._has_on_start:
            raise Error('Only one function may be decorated with `@on_start` for each flow.')

        self._has_on_start = True
        predicate = Predicate(func, require_return_bool=False)
        root_label = self.tree.root_label
        self.tree.execute_before.setdefault(root_label, list()).insert(0, predicate)
        return func

    @staticmethod
    def _log(*args, **kwargs):
        print(*args, **kwargs)

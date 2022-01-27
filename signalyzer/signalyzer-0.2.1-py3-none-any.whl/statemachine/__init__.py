# -*- coding: utf-8 -*-
"""
statemachine
~~~~~~~~~~~~
Module contains a statemachine to evaluate and visualize statemachine
transitions.

:copyright: (c) 2022 by Jochen Gerhaeusser.
:license: BSD, see LICENSE for details
"""
from __future__ import annotations

from dataclasses import (
    dataclass, field, fields)
from itertools import (
    chain, permutations, repeat)

import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go

from .. import Trace
from ..types import *

# module exports
__all__ = [
    'State2D',
    'State3D',
    'Statemachine',
]


@dataclass(eq=False)
class Statemachine(MutableMapping):
    """ statemachine data class to :attr:`evaluate` the state transitions
    between :attr:`states` of a statemachine.

    A *state* of the statemachine is defined by a tuple pair, consisting of
    a unique integer *number* of the state, and the *label* of the state.

    The :attr:`states` of a statemachine must define a consecutive, ascending
    interval of integer :attr:`numbers`.
    """
    #: States of the statemachine
    states: Union[Dict[int, Union[str, State2D, State3D]]]
    #: Signal trace with the state numbers
    signal: Trace = field(default_factory=Trace)
    #: List with the state labels of the statemachine
    labels: List = field(default_factory=list)
    #: Matrix with the counted transitions between the states
    matrix: List[List[int]] = field(default_factory=list)

    @classmethod
    def create(cls,
               states: Union[int, Iterable[str, State2D, State3D]],
               start: Optional[int] = 0,
               **kwargs) -> Statemachine:
        """ Creates either a statemachine with the number of *states* without
        labeling them, or a statemachine with states from an iterable containing
        the labels or representations of the *states* to create.

        :param states: number of states or a list with the labels or
            representations for the :attr:`states` to create
        :param int start: start number for the :attr:`states` to create
            Default is ``0``.
        """
        if isinstance(states, int):
            nodes = dict(enumerate(range(states), start))
        elif isinstance(states, (list, tuple)):
            nodes = dict(enumerate(states, start))
        else:
            nodes = dict()
        return cls(states=nodes, **kwargs)

    def __post_init__(self):
        if not self.labels:
            for key, value in self.items():
                if isinstance(value, (State2D, State3D)):
                    self.labels.append(value.name)
                elif value is None:
                    self.labels.append(str(key))
                else:
                    self.labels.append(str(value))
        if self.signal:
            # computes the transition matrix
            self.evaluate()
        elif not self.matrix:
            # initialize zeroed transition matrix
            self.matrix = self.zeroed_matrix()

    @property
    def numbers(self):
        """ List with the state numbers of the statemachine."""
        return list(self.states.keys())

    def __setitem__(self, key: int, value: Union[str, State2D, State3D]):
        self.states[key] = value

    def __getitem__(self, key: int) -> Union[str, State2D, State3D]:
        return self.states[key]

    def __delitem__(self, key):
        raise NotImplemented()

    def __iter__(self):
        return iter(self.states)

    def __len__(self) -> int:
        return len(self.states)

    def fields(self) -> Tuple[Any, ...]:
        """ Returns a tuple describing the fields of the data class."""
        return fields(self)

    def zeroed_matrix(self) -> List[List[int, ...]]:
        """ Returns the zeroed transition matrix of the statemachine.
        """
        return [[0] * len(self) for _ in range(len(self))]

    def zeroed_counters(self) -> Dict[tuple[int, ...], int]:
        """ Returns the dictionary with the zeroed state transition counters
        of the statemachine."""
        return dict((transition, 0) for transition in permutations(self.states, 2))

    def evaluate(self, signal: Optional[Trace] = None) -> Statemachine:
        """ Counts the state transitions between the :attr:`states` of the
        statemachine in the :attr:`signal`.

        The :attr:`~Trace.samples` of the :attr:`signal` must contain only
        integer :attr:`numbers` defined by the :attr:`states` of the state
        machine.

        :param signal: optional a new :attr:`signal` to evaluate
        """
        # assign new signal to evaluate
        if isinstance(signal, Trace):
            self.signal = signal

        # compute transition deltas from state signal
        deltas = self.signal.delta()

        # create state transition counters for the states
        counters = self.zeroed_counters()

        # count transitions between states
        for state, delta in zip(self.signal, deltas):
            if delta:
                counters[(state - delta, state)] += 1

        # reset transition matrix
        self.matrix = self.zeroed_matrix()

        # offset correction of the states
        offset = min(self.states)

        # fill transition matrix with counted transitions
        for key, value in counters.items():
            i, j = key
            self.matrix[i - offset][j - offset] = value
        return self

    def flatten(self) -> Iterator:
        """ Returns an iterator to flatten the state transition :attr:`matrix`
        into a list.
        """
        return chain.from_iterable(self.matrix)

    def data(self) -> List[List[str, int, ...]]:
        """ Returns the data table with the counted state transitions
        between the :attr:`states` of the statemachine.
        """
        # table data
        data = list()
        # add column labels
        data.append([''] + self.labels)
        # add rows
        for name, values in zip(self.labels, self.matrix):
            data.append([name] + values)
        return data

    def table(self, **kwargs) -> go.Figure:
        """ Returns a table figure for the state transition :attr:`matrix`
        of the statemachine. """
        return ff.create_table(self.data(), index=True, **kwargs)

    def plot(self, **kwargs) -> go.Heatmap:
        """ Returns a heatmap plot for the state transition :attr:`matrix`
        of the statemachine."""
        settings = dict(
            z=self.matrix,
            x=self.labels,
            y=self.labels
        )
        plot = go.Heatmap(**settings)
        return plot.update(**kwargs)

    def heatmap(self, **kwargs) -> go.Figure:
        """ Returns a heatmap figure for the state transition :attr:`matrix`
        of the statemachine."""
        # default settings
        settings = dict(
            x=self.labels,
            y=self.labels,
            text_auto=True,
            color_continuous_scale='Blues'
        )
        settings.update(kwargs)
        return px.imshow(self.matrix, **settings)

    def flowchart(self, **kwargs) -> go.Sankey:
        """ Returns a sankey flow-chart plot for the state transition
        :attr:`matrix` of the statemachine."""
        # number of states
        count = len(self)

        settings = dict(
            node=dict(label=self.labels),
            link=dict(
                source=list(
                    chain.from_iterable([repeat(i, count) for i in range(count)])),
                target=list(range(count)) * count,
                value=list(self.flatten())
            )
        )
        plot = go.Sankey(**settings)
        return plot.update(**kwargs)


@dataclass(unsafe_hash=True)
class State2D:
    """ State represented by a 2-dimensional node."""
    #: Name of the state
    name: str
    #: X-coordinate of the node
    x: int
    #: Y-coordinate of the node
    y: int
    #: Color of the node
    color: str = 'Black'


@dataclass(unsafe_hash=True)
class State3D:
    """ State represented by a 3-dimensional node."""
    #: Name of the state
    name: str
    #: X-coordinate of the state node
    x: int
    #: Y-coordinate of the state node
    y: int
    #: Z-coordinate of the state node
    z: int
    #: Color of the node
    color: str = 'Black'

from ctypes import Union
import typing as t
from collections import OrderedDict
from dataclasses import dataclass

import numpy as np
import torch

TensorSequence = t.Union[torch.tensor, t.Sequence[torch.Tensor]]


@dataclass
class Variable:
    """
    Represents objects that can be stored, e.g. state or reward
    """

    name: str  # variable name, for instance 'state'
    dtype: torch.dtype = torch.float32  # data type, should be a torch data type
    shape: t.Sequence[t.Sequence[int]] = (
        (1,),
    )  # Nesting is possible, iseful if a state representation consists of two tensors with different shapes

    def duplicate(self, duplicate_name: str) -> "Variable":
        return Variable(duplicate_name, self.dtype, self.shape)


class Batch(OrderedDict):
    def unpack(self):
        return tuple(self.values())

    def __getattr__(self, key: str) -> t.Any:
        try:
            return super().__getitem__(key)
        except AttributeError:
            return self[key]


class Buffer:
    """
    Implements a Buffer for exactly one type of variable
    The variable may however consists of multiple components with different shapes.
    """

    def __init__(self, size: int, variable: Variable, device: torch.device):
        self.variable = variable
        self.buffers = [
            np.zeros((size,) + tuple(shape)) for shape in self.variable.shape
        ]
        self.device = device

    def __setitem__(
        self, idx: t.Union[int, np.ndarray, t.List[int]], variable_instance: t.Any
    ) -> None:
        if len(self.variable.shape) > 1:  # more than one component
            for i, component_instance in enumerate(variable_instance):
                self.buffers[i][idx] = component_instance
        else:  # only one component
            self.buffers[0][idx] = variable_instance

    def __getitem__(self, idx: t.Union[int, np.ndarray, t.List[int]]) -> TensorSequence:
        if len(self.variable.shape) > 1:  # more than one component
            return [
                torch.from_numpy(self.buffers[i][idx])
                .to(self.variable.dtype)
                .to(self.device)
                for i in range(len(self.variable.shape))
            ]
        else:  # only one component
            return (
                torch.from_numpy(self.buffers[0][idx])
                .to(self.variable.dtype)
                .to(self.device)
            )


class ReplayBuffer:
    """
    A more flexible replay buffer implementation for use with pytorch

    Can be useful when implementing e.g. n-step returns, when storing continuous actions that have some
    fixed shape, when there is more than one reward signal, [...].
    """

    def __init__(
        self,
        size: int,
        batch_size: int,
        variables: t.List[Variable],
        seed: t.Any = 0,
        device=None,
    ):
        """

        :param size: Buffer size, i.e. maxmimal number of entries
        :type size: int

        :param batch_size: size of sampled batches
        :type batch_size: int

        :param variables:
        :type variables: List[Variable]

        :param seed:
        :type seed: Any

        :param device:
        """
        self.device = device
        self.size = size
        self.batch_size = batch_size
        self.variables = variables
        self.seed = seed
        self.rng = np.random.default_rng(seed)

        self.buffers = {
            variable.name: Buffer(size, variable, self.device) for variable in variables
        }
        self.counter = 0
        self.num_stored = 0

    def add(self, **variable_instances) -> None:
        for variable_name, variable_instance in variable_instances.items():
            self.buffers[variable_name][self.counter] = variable_instance

        self.counter = (self.counter + 1) % self.size
        self.num_stored = min(self.size, self.num_stored + 1)

    def __len__(self) -> int:
        return self.num_stored

    def sample(self) -> Batch:
        sample_ids = self.rng.integers(0, len(self), self.batch_size)
        return Batch(
            **{var.name: self.buffers[var.name][sample_ids] for var in self.variables}
        )


# Based on https://github.com/openai/baselines/blob/ea25b9e8b234e6ee1bca43083f8f3cf974143998/baselines/common/segment_tree.py#L93
class SumTree:
    def __init__(self, capacity: int):
        self._capacity = capacity  # total capacity is number of leafs
        self._value = np.zeros(
            self._capacity * 2
        )  # so we need to store capacity times two many node values

    @property
    def root_sum(self) -> int:
        return self._value[1]

    def __setitem__(self, idx: int, value: float):
        if idx >= self._capacity:
            raise IndexError(
                f"Index {idx} is out of range for SumTree with capacity {self._capacity}"
            )
        idx += self._capacity
        delta = value - self._value[idx]
        self._value[idx] = value
        idx = idx >> 1
        while idx >= 1:
            self._value[idx] += delta
            idx = idx >> 1

    def __getitem__(self, idx: int):
        if idx >= self._capacity:
            raise IndexError(
                f"Index {idx} is out of range for SumTree with capacity {self._capacity}"
            )
        return self._value[idx + self._capacity]

    def retrieve_idx(self, priority_mass: float) -> int:
        """
        Args:
            priority_mass (float): A cumulative priority in `[0, p_total]` where `p_total` corresponds
            to the current `SumTree.root_sum`

        Returns:
            int: The largest index `i` s.t. `sum(self._values[0], ..., self._values[i-1]) < priority_mass`
        """
        # start at root
        idx = 1
        while idx < self._capacity:
            left_idx = idx << 1
            left_value = self._value[left_idx]
            if left_value > priority_mass:
                idx = left_idx  # descend to left child
            else:
                priority_mass -= left_value
                idx = left_idx + 1  # descend to right child
        return idx - self._capacity


class PrioritisedReplayBuffer(ReplayBuffer):
    def __init__(
        self,
        size: int,
        batch_size: int,
        variables: t.List[Variable],
        seed: t.Any = 0,
        alpha: float = 1.0,
        device="cpu",
    ):
        super().__init__(size, batch_size, variables, seed, device)
        self._alpha = alpha
        self._max_priority = 1.0

        capacity = 1
        while capacity < size:
            capacity = capacity << 1
        self._capacity = capacity
        self._sum_tree = SumTree(capacity)
        self._interval_offsets = np.arange(self.batch_size)

    def add(self, **variable_instances) -> None:
        self._sum_tree[self.counter] = self._max_priority ** self._alpha
        super().add(**variable_instances)

    def sample(self, beta: float) -> t.Tuple[Batch, torch.Tensor, t.List]:
        """Sample a batch using proportional prioritisation

        Args:
            beta (float): Importance sampling influence weight in [0,1].
            1 means full importance reweighting, while 0 means no reweighting (all weights will equal 1).

        Returns:
            Tuple[Batch, torch.Tensor, List]: The experience batch, a tensor of importance weights and the indice list of the sampled transitions
        """
        # samples from intervals [0, P/B], [P/B, 2P/b], ..., [(B-1)P/B, P]
        # for batch size B
        interval_size = self._sum_tree.root_sum / self.batch_size
        samples = self.rng.random(size=self.batch_size)
        samples = (samples + self._interval_offsets) * interval_size

        # retrieve corresponding indices from sum tree
        sample_ids = [self._sum_tree.retrieve_idx(sample) for sample in samples]

        # calculate IS weights
        # make sure they are always <= 1 for stability
        weights = torch.tensor(
            [
                min(
                    (self._sum_tree.root_sum / (self._sum_tree[idx] * len(self)))
                    ** beta,
                    1,
                )
                for idx in sample_ids
            ],
            dtype=torch.float32,
        )

        batch = Batch(
            **{var.name: self.buffers[var.name][sample_ids] for var in self.variables}
        )

        return batch, weights, sample_ids

    def update_priorities(self, idxs: t.Iterable[int], priorities: t.Iterable[float]):
        """Updates the internal priorities for the given indices.

        Args:
            idxs (Iterable[int]): The indices of items whose priorities need to be updated
            priorities (Iterable[float]): The new priorities
        """
        for idx, priority in zip(idxs, priorities):
            self._sum_tree[idx] = priority
            if priority > self._max_priority:
                self._max_priority = priority


class StandardPrioritisedReplayBuffer(PrioritisedReplayBuffer):
    def __init__(
        self,
        buffer_size,
        num_state_variables,
        state_variable_sizes,
        batch_size,
        seed=0,
        device=None,
        alpha: float = 1.0,
    ):
        S = Variable("states", shape=state_variable_sizes)
        A = Variable("actions", dtype=torch.long)
        R = Variable("rewards")
        T = S.duplicate("next_states")
        D = Variable("dones")
        super().__init__(
            size=buffer_size,
            batch_size=batch_size,
            variables=[S, A, R, T, D],
            seed=seed,
            device=device,
            alpha=alpha,
        )

    def add(self, state, action, reward, next_state, done):
        super().add(
            states=state,
            actions=action,
            rewards=reward,
            next_states=next_state,
            dones=done,
        )

from __future__ import annotations
from enum import Enum


class State(Enum):
    """Task-state enum.

    The following 9 states are defined:

    >>> for state in State:
    ...     state
    <State.undefined: 'u'>
    <State.queued: 'q'>
    <State.hold: 'h'>
    <State.running: 'r'>
    <State.done: 'd'>
    <State.FAILED: 'F'>
    <State.TIMEOUT: 'T'>
    <State.MEMORY: 'M'>
    <State.CANCELED: 'C'>

    >>> State.queued == State.queued
    True
    >>> State.queued == 'queued'
    True
    >>> State.queued == 'queue'
    Traceback (most recent call last):
      ...
    TypeError: Unknown state: queue
    >>> State.queued == 117
    False
    >>> State.done in {'queued', 'running'}
    False
    """

    undefined = 'u'
    queued = 'q'
    hold = 'h'
    running = 'r'
    done = 'd'
    FAILED = 'F'
    TIMEOUT = 'T'
    MEMORY = 'M'
    CANCELED = 'C'

    def __eq__(self, other: object) -> bool:
        if isinstance(other, State):
            return self.name == other.name
        if isinstance(other, str):
            if other in State.__members__:
                return self.name == other
            raise TypeError(f'Unknown state: {other}')
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.name)

    def __str__(self) -> str:
        return self.name

    def is_bad(self) -> bool:
        """Return true for FAILED, TIMEOUT, MEMORY and CANCELED.

        >>> State.running.is_bad()
        False
        """
        return self.name.isupper()

    @staticmethod
    def str2states(s: str) -> set['State']:
        """Convert single character state string to set of State objects.

        >>> names = [state.name for state in State.str2states('rdA')]
        >>> sorted(names)
        ['CANCELED', 'FAILED', 'MEMORY', 'TIMEOUT', 'done', 'running']
        >>> State.str2states('x')
        Traceback (most recent call last):
          ...
        ValueError: Unknown state: x.  Must be one of q, ..., a or A.
        """
        states: set[State] = set()
        for c in s:
            if c == 'a':
                states.update([State.queued,
                               State.hold,
                               State.running,
                               State.done])
            elif c == 'A':
                states.update([State.FAILED,
                               State.CANCELED,
                               State.TIMEOUT,
                               State.MEMORY])
            else:
                try:
                    states.add(State(c))
                except ValueError:
                    raise ValueError(
                        'Unknown state: ' + s +
                        '.  Must be one of q, h, r, d, F, C, T, M, a or A.')
        return states

""" Methods to handle task id's
"""

import operator
import re
from collections import deque

import itertools
import typing
from dataclasses import dataclass

from momotor.bundles import InvalidDependencies
from momotor.options.types import StepTasksType, StepTaskNumberType

TASK_OPERATORS = {
    '+': operator.add,
    '-': operator.sub,
    '*': operator.mul,
    '/': operator.floordiv,
    '%': operator.mod,
}
TASK_OPER_RE_STR = "|".join(re.escape(oper) for oper in TASK_OPERATORS.keys())
TASK_OPER_RE = re.compile(rf'({TASK_OPER_RE_STR})')

ID_RE_STR = rf'(?:[\w.$@]|{TASK_OPER_RE_STR})+'


def task_id_from_number(task_number: typing.Optional[typing.Iterable[int]]) -> str:
    """ Convert a task number (tuple of ints) into a task id (dotted string)

    >>> task_id_from_number(None)
    ''

    >>> task_id_from_number((1,))
    '1'

    >>> task_id_from_number((1, 2,))
    '1.2'

    >>> task_id_from_number((1, 2, 3,))
    '1.2.3'

    """
    return '.'.join(str(t) for t in task_number) if task_number else ''


def task_number_from_id(task_id: typing.Optional[str]) -> StepTaskNumberType:
    """ Convert a task_id string into a task number

    >>> task_number_from_id('') is None
    True

    >>> task_number_from_id('1')
    (1,)

    >>> task_number_from_id('1.2')
    (1, 2)

    >>> task_number_from_id('1.2.3')
    (1, 2, 3)
    """
    return tuple(int(p) for p in task_id.split('.')) if task_id else None


@dataclass(frozen=True)
class StepTaskId:
    """ A step-id and task-number pair
    """
    step_id: str
    task_number: StepTaskNumberType

    def __str__(self):
        if self.task_number:
            return self.step_id + '.' + task_id_from_number(self.task_number)
        else:
            return self.step_id


def iter_task_numbers(sub_tasks: StepTasksType) -> typing.Generator[StepTaskNumberType, None, None]:
    """ Generate all the task-numbers for the subtasks.

    >>> list(iter_task_numbers(tuple()))
    [None]

    >>> list(iter_task_numbers((1,)))
    [(0,)]

    >>> list(iter_task_numbers((3,)))
    [(0,), (1,), (2,)]

    >>> list(iter_task_numbers((2, 2)))
    [(0, 0), (0, 1), (1, 0), (1, 1)]

    >>> list(iter_task_numbers((2, 3)))
    [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)]

    :param sub_tasks: sequence of integers with the number of sub-tasks for each level
    :return: the task numbers
    """
    if sub_tasks:
        yield from itertools.product(*(range(st) for st in sub_tasks))
    else:
        yield None


def iter_task_ids(step_id: str, sub_tasks: StepTasksType) -> typing.Generator[StepTaskId, None, None]:
    """ Generate all the task-ids for the subtasks.

    >>> list(str(t) for t in iter_task_ids('step', tuple()))
    ['step']

    >>> list(str(t) for t in iter_task_ids('step', (2,)))
    ['step.0', 'step.1']

    >>> list(str(t) for t in iter_task_ids('step', (2, 2)))
    ['step.0.0', 'step.0.1', 'step.1.0', 'step.1.1']

    :param step_id: the id of the step
    :param sub_tasks: sequence of integers with the number of sub-tasks for each level
    :return: the task numbers
    """
    for task_number in iter_task_numbers(sub_tasks):
        yield StepTaskId(step_id, task_number)


def get_task_id_lookup(task_ids: typing.Iterable[StepTaskId]) -> typing.Dict[str, StepTaskId]:
    """ Convert an iterable of :py:const:`StepTaskId` objects into a lookup table to convert a string representation of
    a task-id to the :py:const:`StepTaskId`

    >>> get_task_id_lookup({StepTaskId('step', (0, 0))})
    {'step.0.0': StepTaskId(step_id='step', task_number=(0, 0))}

    :param task_ids: the task ids to convert
    :return: the lookup table
    """
    return {
        str(task_id): task_id
        for task_id in task_ids
    }


def apply_task_number(depend_id: str, task_id: StepTaskId) -> str:
    """ Replace ``$`` references in dependency strings with their value from the `task_id` parameter,
    e.g. ``$0`` in `depend_id` will be replaced with ``task_id.task_number[0]``

    Simple arithmetic on the values can be done, available operators are ``+``, ``-``, ``*``, ``/`` and ``%``, for
    the usual operations `add`, `subtract`, `multiply`, `integer division` and `modulo`.
    Arithmetic operations are evaluated from left to right, there is no operator precedence.

    When subtraction results in a negative value or division in infinity, this will not directly throw an exception,
    but instead will generate an invalid task-id containing ``#NEG`` or ``#INF``.

    Special value ``$@`` will be replaced with the full task number.

    Raises :py:exc:`~momotor.bundles.exception.InvalidDependencies` if `depend_id` contains invalid
    references or is syntactically incorrect.

    Examples:

    >>> tid = StepTaskId('step', (0, 1, 2))
    >>> apply_task_number('test', tid)
    'test'

    >>> apply_task_number('test.$0', tid)
    'test.0'

    >>> apply_task_number('test.$0.$1', tid)
    'test.0.1'

    >>> apply_task_number('test.$1.$2', tid)
    'test.1.2'

    >>> apply_task_number('test.$0-1.$1-1.$2-1', tid)
    'test.#NEG.0.1'

    >>> apply_task_number('test.$0+1.$1+1.$2+1', tid)
    'test.1.2.3'

    >>> apply_task_number('test.$0*2.$1*2.$2*2', tid)
    'test.0.2.4'

    >>> apply_task_number('test.$0/2.$1/2.$2/2', tid)
    'test.0.0.1'

    >>> apply_task_number('test.$0%2.$1%2.$2%2', tid)
    'test.0.1.0'

    >>> apply_task_number('test.$0*2+1.$1*2+1.$2*2+1', tid)
    'test.1.3.5'

    >>> apply_task_number('test.$0+1*2.$1+1*2.$2+1*2', tid)
    'test.2.4.6'

    >>> apply_task_number('test.$0+$1+$2', tid)
    'test.3'

    >>> apply_task_number('test.$1/0', tid)
    'test.#INF'

    >>> apply_task_number('test.$@', tid)
    'test.0.1.2'

    >>> apply_task_number('test.$X', tid)
    Traceback (most recent call last):
    ...
    momotor.bundles.exception.InvalidDependencies: Task 'step.0.1.2' has invalid dependency 'test.$X'

    >>> apply_task_number('test.$1$2', tid)
    Traceback (most recent call last):
    ...
    momotor.bundles.exception.InvalidDependencies: Task 'step.0.1.2' has invalid dependency 'test.$1$2'

    >>> apply_task_number('test.$1^4', tid)
    Traceback (most recent call last):
    ...
    momotor.bundles.exception.InvalidDependencies: Task 'step.0.1.2' has invalid dependency 'test.$1^4'

    >>> apply_task_number('test.$9', tid)
    Traceback (most recent call last):
    ...
    momotor.bundles.exception.InvalidDependencies: Task 'step.0.1.2' has invalid dependency 'test.$9'

    """
    if '.$' in depend_id:
        task_number = task_id.task_number
        if task_number:
            task_lookup = {
                f'${idx}': value
                for idx, value in enumerate(task_number)
            }
        else:
            task_lookup = {}

        def _replace(section):
            if section == '$@':
                # expand `$@` into the full task number string
                return task_id_from_number(task_number)
            elif section in {'*', '?'}:
                # ignore wildcards
                return section

            parts = deque(TASK_OPER_RE.split(section))

            result, oper = None, None
            try:
                while parts:
                    value = parts.popleft()
                    try:
                        value = task_lookup[value]
                    except KeyError:
                        value = int(value)

                    result = TASK_OPERATORS[oper](result, value) if oper else value

                    if parts:
                        oper = parts.popleft()

            except ZeroDivisionError:
                return '#INF'

            if result is None:
                raise ValueError

            elif result < 0:
                return '#NEG'

            return str(result)

        try:
            return '.'.join(
                _replace(part) if idx else part
                for idx, part in enumerate(depend_id.split('.'))
            )
        except (ValueError, IndexError, TypeError) as e:
            raise InvalidDependencies(
                f"Task '{task_id!s}' has invalid dependency '{depend_id!s}'"
            )

    return depend_id

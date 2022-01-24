""" Methods for querying and filtering results
"""

import re
import typing
from collections import deque

from momotor.bundles.elements.result import Result
from momotor.options.task_id import StepTaskId, apply_task_number


def make_result_id_re(query: str) -> "typing.re.Pattern":
    """ Make a regex that matches a :ref:`result query <result query>` to the query.

    Uses a glob-like pattern matching on the dot-separated elements of the selector.
    For the first element (the step-id part), a ``*`` will match zero or more characters except ``.``
    For all the other elements (the task number parts), a ``*`` matches one or more elements starting at that position
    and a ``?`` matches a single element in that position.

    Special query ``**`` matches all step-ids and task-numbers, i.e. it produces a regex that matches anything.

    This method does *not* apply any task numbers, apply
    :py:meth:`~momotor.options.task_id.apply_task_number` to the selector before calling this function for
    that if needed.

    Examples:

    >>> make_result_id_re('test').match('test') is not None
    True

    >>> make_result_id_re('test').match('test.1') is not None
    False

    >>> make_result_id_re('test').match('testing') is not None
    False

    >>> make_result_id_re('test.1').match('test.2') is not None
    False

    >>> make_result_id_re('test.2').match('test.2.3') is not None
    False

    >>> make_result_id_re('test.2.3').match('test.2.3') is not None
    True

    >>> make_result_id_re('test.?').match('test.2.3') is not None
    False

    >>> make_result_id_re('test.?.?').match('test.2.3') is not None
    True

    >>> make_result_id_re('test.?.?.?').match('test.2.3') is not None
    False

    >>> make_result_id_re('test.*').match('test.2.3') is not None
    True

    >>> make_result_id_re('test.?.*').match('test.2.3') is not None
    True

    >>> make_result_id_re('test.?.?.*').match('test.2.3') is not None
    False

    >>> make_result_id_re('*').match('test') is not None
    True

    >>> make_result_id_re('*').match('test.2.3') is not None
    False

    >>> make_result_id_re('*.*').match('test.2.3') is not None
    True

    >>> make_result_id_re('test*').match('testing') is not None
    True

    >>> make_result_id_re('*sti*').match('testing') is not None
    True

    >>> make_result_id_re('*sting').match('testing') is not None
    True

    >>> make_result_id_re('te*ng').match('testing') is not None
    True

    >>> make_result_id_re('test*').match('tasting') is not None
    False

    >>> make_result_id_re('test*').match('testing.1') is not None
    False

    >>> make_result_id_re('test**').match('testing.1') is not None
    True

    >>> make_result_id_re('t*t**').match('testing.1') is not None
    True

    >>> make_result_id_re('t*x**').match('testing.1') is not None
    False

    >>> make_result_id_re('test*.*').match('testing.1') is not None
    True

    >>> make_result_id_re('**').match('testing') is not None
    True

    >>> make_result_id_re('**').match('testing.1') is not None
    True

    :param query: the result-id query to convert
    :return: a compiled regular expression (a :py:func:`re.compile` object) for the query
    """
    if query == '**':
        regex = r'^.*$'

    else:
        regex_parts = deque()

        first = True
        for selector_part in query.split('.'):
            if first and '*' in selector_part:
                double_star = selector_part.endswith('**')
                if double_star:
                    selector_part = selector_part[:-1]
                regex_part = r'[^.]*'.join(re.escape(step_id_part) for step_id_part in selector_part.split('*'))
                if double_star:
                    regex_part += r'(?:\.(\d+))*'

            elif selector_part == '*':
                regex_part = r'\d+(?:\.(\d+))*'
            elif selector_part == '?':
                regex_part = r'\d+'
            else:
                regex_part = re.escape(selector_part)

            regex_parts.append(regex_part)
            first = False

        regex = r'^' + r'\.'.join(regex_parts) + r'$'

    return re.compile(regex)


def result_query_fn(query: str, task_id: StepTaskId = None) -> typing.Callable[[Result], bool]:
    """ Make a function to match a result with a :ref:`result query <result query>`.

    The query is either a literal id (e.g. ``step``, ``step.1`` etc), or a glob-like query to select
    multiple id's, (e.g. ``*``, ``step.*``, ``step.?``). Also applies task numbers if `task_id` is provided.

    Multiple queries are possible, separated with a comma.

    :param query: the query to convert
    :param task_id: a task id to resolve id references in the query
    :return: a callable that takes a :py:class:`~momotor.bundles.elements.result.Result` and returns a boolean
             indicating if that result matches the query
    """

    if not query:
        # Optimization for querying none
        def _none(result: Result) -> bool:
            return False

        return _none

    elif query == '**':
        # Optimization for querying all
        def _all(result: Result) -> bool:
            return True

        return _all

    if ',' in query:
        queries = query.split(',')
    else:
        queries = [query]

    if task_id:
        fns = [
            make_result_id_re(
                apply_task_number(query.strip(), task_id)
            ).match
            for query in queries
        ]
    else:
        fns = [
            make_result_id_re(query.strip()).match
            for query in queries
        ]

    def _match(result: Result) -> bool:
        return any(fn(result.step_id) for fn in fns)

    return _match


def filter_result_query(results: typing.Iterable[Result], query: str, task_id: StepTaskId = None) \
        -> typing.Iterator[Result]:
    """ Filter an iterable of :py:class:`~momotor.bundles.elements.result.Result` objects on a
    :ref:`result query <result query>`

    Returns an iterator that iterates all the :py:class:`~momotor.bundles.elements.result.Result` objects
    from `results` that match the `query`

    :param results: an iterable with the results to query
    :param query: the query to filter the results on
    :param task_id: a task id to resolve id references in the query
    :return: `results` filtered on the `query`
    """

    query_matcher = result_query_fn(query, task_id)
    return filter(query_matcher, results)

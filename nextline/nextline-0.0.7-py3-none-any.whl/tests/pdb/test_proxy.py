import sys
import asyncio
from itertools import count

import pytest
from unittest.mock import Mock

from nextline.trace import Trace
from nextline.utils import Registry
from nextline.pdb.proxy import PdbProxy
from nextline.trace import UniqThreadTaskIdComposer

from . import subject


##__________________________________________________________________||
@pytest.fixture()
def mock_trace():
    y = Mock(spec=Trace)
    yield y


@pytest.fixture()
def mock_registry():
    y = Mock(spec=Registry)
    yield y


@pytest.fixture()
def proxy(mock_trace, mock_registry):
    thread_asynctask_id = UniqThreadTaskIdComposer().compose()

    modules_to_trace = {"tests.pdb.subject"}

    prompting_counter = count().__next__
    prompting_counter()  # consume 0

    y = PdbProxy(
        thread_asynctask_id=thread_asynctask_id,
        trace=mock_trace,
        modules_to_trace=modules_to_trace,
        registry=mock_registry,
        ci_registry=Mock(),
        prompting_counter=prompting_counter,
    )

    y.pdb.trace_dispatch = Mock()

    yield y


##__________________________________________________________________||
def unpack_trace_dispatch_call(trace_dispatch):
    trace_results = []
    while trace_dispatch.call_count:
        trace_results.append(
            [
                (
                    c.args[0].f_code.co_name,
                    c.args[1],
                    asyncio.isfuture(c.args[2]),
                )
                for c in trace_dispatch.call_args_list
            ]
        )
        trace_dispatch = trace_dispatch.return_value

    # e.g.,
    # trace_results = [
    #     [('run_a', 'call', False), ('<lambda>', 'call', False), ('a', 'call', False), ('a', 'call', False)],
    #     [('run_a', 'line', False), ('<lambda>', 'line', False), ('a', 'line', False), ('a', 'exception', False)],
    #     [('<lambda>', 'return', False), ('a', 'return', True), ('a', 'line', False), ('run_a', 'return', False)],
    #     [('a', 'return', False)]
    # ]

    return trace_results


##__________________________________________________________________||
params = [
    pytest.param(subject.f, id="simple"),
    pytest.param(subject.subject, id="nested-func"),
    pytest.param(
        subject.call_gen,
        id="yield",
        marks=pytest.mark.skipif(
            sys.version_info >= (3, 10), reason="StopIteration won't be raised"
        ),
    ),
    pytest.param(subject.run_a, id="asyncio"),
    pytest.param(subject.call_lambda, id="lambda"),
]


@pytest.mark.skipif(
    sys.version_info < (3, 9), reason="co_name <lambda> is different "
)
@pytest.mark.parametrize("subject", params)
def test_proxy(proxy, mock_trace, mock_registry, snapshot, subject):
    """test PdbProxy"""
    # TODO: the test needs to be restructured so that, for example, a
    # coroutine or a generator can be the outermost scope.

    trace_org = sys.gettrace()
    sys.settrace(proxy.trace_func)
    subject()
    sys.settrace(trace_org)

    assert 1 == mock_registry.open_register.call_count
    assert 1 == mock_registry.register_list_item.call_count
    assert 1 == mock_registry.close_register.call_count

    assert 1 == mock_trace.returning.call_count

    trace_results = unpack_trace_dispatch_call(proxy.pdb.trace_dispatch)
    snapshot.assert_match(trace_results)


##__________________________________________________________________||

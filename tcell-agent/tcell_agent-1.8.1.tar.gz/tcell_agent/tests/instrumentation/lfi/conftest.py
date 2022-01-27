import pytest
from mock import patch


class Context(object):
    remote_address = None
    uri = None
    method = None
    route_id = None
    user_id = None
    session_id = None


@pytest.fixture(scope='function')
def tcell_agent(request):
    config = {'get_policy.return_value.block_command.return_value': True}
    patcher = patch('tcell_agent.instrumentation.lfi.utils.TCellAgent', **config)
    agent = patcher.start()
    request.instance.agent = agent
    yield
    patcher.stop()


@pytest.fixture(scope='function')
def tcell_context(request):
    patcher = patch('tcell_agent.instrumentation.lfi.utils.get_tcell_context', return_value=Context)
    context = patcher.start()
    request.instance.context = context
    yield
    patcher.stop()


@pytest.fixture(scope='function')
def disable_block(request):
    patcher = patch(
        'tcell_agent.instrumentation.lfi.wrappers.utils.should_block_file_open', return_value=False
    )
    block = patcher.start()
    request.instance.block = block
    yield
    patcher.stop()

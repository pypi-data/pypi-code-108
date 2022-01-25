import functools
import io
import os
import sys
from contextlib import redirect_stdout
from unittest.mock import patch, Mock

import pytest
from IPython.core.interactiveshell import InteractiveShell
from ipykernel.zmqshell import ZMQInteractiveShell
from urllib3.response import HTTPResponse

from seeq.sdk.rest import ApiException
from seeq.spy import _errors
from seeq.spy._errors import *


@pytest.mark.unit
def test_ipython_vs_jupyter():
    with patch('seeq.spy._errors.get_ipython') as mock:
        mock.return_value = None
        assert _errors.is_ipython() is False
        assert _errors.is_jupyter() is False

        mock.return_value = InteractiveShell()
        assert _errors.is_ipython() is True
        assert _errors.is_jupyter() is False

        mock.return_value = ZMQInteractiveShell()
        assert _errors.is_ipython() is True
        assert _errors.is_jupyter() is True


@pytest.mark.unit
def test_is_datalab():
    os.environ['SEEQ_SDL_CONTAINER_IS_DATALAB'] = ''
    assert _errors.is_datalab() is False

    os.environ['SEEQ_SDL_CONTAINER_IS_DATALAB'] = 'true'
    assert _errors.is_datalab() is True


@pytest.mark.unit
def test_get_ipython_cell_no():
    # Test old filename structure for ipython cell frames
    f_code = Mock()
    f_code.co_filename = '<ipython-input-42-a2cd98761df60>'
    frame = Mock()
    frame.f_code = f_code
    assert _errors.get_ipython_cell_no(frame) == '42'

    # Test a frame pointing to a file that isn't an ipython cell
    f_code.co_filename = '/seeq/spy/_common.py'
    assert _errors.get_ipython_cell_no(frame) is None

    # Test the current filename structure with a real IPython shell
    f_code.co_filename = '/tmp/ipykernel_619/113536796.py'
    shell = InteractiveShell()
    code1 = "print([1,2,3])"
    code2 = "from seeq import spy\nprint('hello world')"
    code3 = "spy"
    for code in (code1, code2, code3):
        shell.run_cell(code, store_history=True)
    frame.f_globals = shell.user_ns

    with patch('inspect.getsource') as mock_getsource:
        mock_getsource.side_effect = lambda arg: code2 + '\n' if arg == frame else ''
        assert _errors.get_ipython_cell_no(frame) == 2


@pytest.mark.unit
def test_get_exception_message():
    assert _errors.get_exception_message(SPyRuntimeError(IndexError('My Message'))) == 'My Message'
    try:
        raise_api_error()
    except ApiException as e:
        message = '(401) Unauthorized - Header contains an invalid authentication token. Please login again.'
        assert _errors.get_exception_message(e) == message
        assert _errors.get_exception_message(SchedulePostingError(e)) == message


@pytest.mark.unit
def test_get_exception_name():
    assert _errors.get_exception_name(ApiException()) == 'Seeq API Error'
    assert _errors.get_exception_name(SchedulePostingError()) == 'Scheduling Error'
    assert _errors.get_exception_name(SPyRuntimeError()) == 'SPy Error'
    assert _errors.get_exception_name(IndexError()) == 'IndexError'


@pytest.mark.unit
def test_format_tb_header():
    colors = Mock()
    colors.excName = '__EXC_NAME__'
    colors.em = '__EM__'
    colors.Normal = '__NORMAL__'
    colors.filenameEm = '__FILENAME_EM__'

    e = SPyRuntimeError('Error message')
    lineno = 4
    ipy_inputno = 12
    warning = 'Warning message'
    expected_header = '__EXC_NAME__SPy Error: __NORMAL__Error message'
    expected_location = 'Error found at __EM__line 4__NORMAL__ in __FILENAME_EM__cell 12__NORMAL__.'
    expected = '\n%s\n\n%s\n\n%s' % (expected_header, expected_location, warning)
    assert _errors.format_tb_header(colors, e, lineno, ipy_inputno=ipy_inputno, warning=warning) == expected

    filename = 'file.py'
    expected_location = 'Error found at __EM__line 4__NORMAL__ in __FILENAME_EM__file file.py__NORMAL__.'
    expected = '\n%s\n\n%s\n\n%s' % (expected_header, expected_location, warning)
    assert _errors.format_tb_header(colors, e, lineno, filename=filename, warning=warning) == expected


@pytest.mark.unit
def test_show_stacktrace_button():
    def raise_index_error(i):
        x = range(i)
        return x[i]

    try:
        raise_index_error(5)
        exc_tuple = None
    except IndexError:
        exc_tuple = sys.exc_info()

    shell = InteractiveShell()
    shell.InteractiveTB.set_colors('NoColor')

    button = _errors.show_stacktrace_button(shell, exc_tuple)
    button.close = Mock()
    assert button.description == 'Click to show stack trace'

    with redirect_stdout(io.StringIO()) as stdout:
        button.click()
        output = stdout.getvalue()

    button.close.assert_called_once()
    assert 'Traceback (most recent call last)' in output
    assert 'test_errors.py in raise_index_error' in output
    assert 'return x[i]' in output
    assert 'To show stack trace by default, set spy.options.friendly_exceptions to False' in output


@pytest.mark.unit
def test_add_and_remove_exception_handler():
    shell = InteractiveShell()
    with patch('seeq.spy._errors.spy_exception_handler') as mock_exc_handler:
        with patch('seeq.spy._errors.get_ipython') as mock_get_ipython:
            mock_get_ipython.return_value = shell
            _errors.add_spy_exception_handler()

            shell.run_cell('[][0]')
            mock_exc_handler.assert_called_once()
            _errors.remove_spy_exception_handler()

    shell.showtraceback = Mock()
    shell.run_cell('[][0]')
    shell.showtraceback.assert_called_once()


def raise_spy_error():
    raise SPyRuntimeError('My message')


def raise_api_error():
    r = HTTPResponse(
        status=401,
        reason='Unauthorized',
        body=b'{"statusMessage":"Header contains an invalid authentication token. Please login again."}'
    )
    raise ApiException(http_resp=r)


def raise_fatal_spy_error():
    raise IndexError('My message')


def raise_scheduling_spy_error():
    raise SchedulePostingError(SPyRuntimeError('My message'))


def raise_scheduling_api_error():
    try:
        raise_api_error()
    except ApiException as e:
        raise SchedulePostingError(e)


@pytest.mark.unit
def test_exception_handler():
    shell = InteractiveShell()
    shell.InteractiveTB.set_colors('NoColor')
    shell.showtraceback = Mock()
    shell.run_cell = functools.partial(shell.run_cell, store_history=True)
    shell.run_cell('from seeq.spy.tests import test_errors')

    with patch('seeq.spy._errors.get_ipython') as mock_get_ipython:
        mock_get_ipython.return_value = shell
        _errors.add_spy_exception_handler()

    with patch('seeq.spy._errors.is_jupyter') as mock_is_jupyter, \
            patch('seeq.spy._errors.show_stacktrace_button') as mock_show_stacktrace_button:
        mock_is_jupyter.return_value = True
        button = Mock()
        mock_show_stacktrace_button.return_value = button

        def test_func_wrapper(func):
            return f'def {func}_wrapper():\n    test_errors.{func}()'

        def get_last_tb(from_button=True):
            if from_button:
                return mock_show_stacktrace_button.call_args[0][1][2]
            else:
                # noinspection PyUnresolvedReferences
                return shell.showtraceback.call_args[0][0][2]

        def get_tb_len(tb):
            if tb is None:
                return 0
            return get_tb_len(tb.tb_next) + 1

        with redirect_stdout(io.StringIO()) as stdout:
            shell.run_cell(test_func_wrapper('raise_spy_error'))
            shell.run_cell('raise_spy_error_wrapper()')
        output = stdout.getvalue()
        assert 'SPy Error: My message' in output
        assert 'Error found at line 2 in cell 2' in output
        assert mock_show_stacktrace_button.call_count == 1
        assert shell.showtraceback.call_count == 0
        assert get_tb_len(get_last_tb()) == 3

        with redirect_stdout(io.StringIO()) as stdout:
            shell.run_cell(test_func_wrapper('raise_api_error'))
            shell.run_cell('raise_api_error_wrapper()')
        output = stdout.getvalue()
        assert 'Seeq API Error: (401) Unauthorized - Header contains' in output
        assert 'Error found at line 2 in cell 4' in output
        assert mock_show_stacktrace_button.call_count == 2
        assert shell.showtraceback.call_count == 0
        assert get_tb_len(get_last_tb()) == 4

        with redirect_stdout(io.StringIO()) as stdout:
            shell.run_cell(test_func_wrapper('raise_fatal_spy_error'))
            shell.run_cell('raise_fatal_spy_error_wrapper()')
        output = stdout.getvalue()
        assert 'IndexError: My message' in output
        assert 'Error found at line 2 in cell 6' in output
        assert mock_show_stacktrace_button.call_count == 2
        assert shell.showtraceback.call_count == 1
        assert get_tb_len(get_last_tb(from_button=False)) == 4

        with redirect_stdout(io.StringIO()) as stdout:
            shell.run_cell(test_func_wrapper('raise_scheduling_spy_error'))
            shell.run_cell('raise_scheduling_spy_error_wrapper()')
        output = stdout.getvalue()
        assert 'Scheduling Error: My message' in output
        assert 'Error found at line 2 in cell 8' in output
        assert mock_show_stacktrace_button.call_count == 3
        assert shell.showtraceback.call_count == 1
        assert get_tb_len(get_last_tb()) == 3

        with redirect_stdout(io.StringIO()) as stdout:
            shell.run_cell(test_func_wrapper('raise_scheduling_api_error'))
            shell.run_cell('raise_scheduling_api_error_wrapper()')
        output = stdout.getvalue()
        assert 'Scheduling Error: (401) Unauthorized' in output
        assert 'Error found at line 2 in cell 10' in output
        assert mock_show_stacktrace_button.call_count == 4
        assert shell.showtraceback.call_count == 1
        assert get_tb_len(get_last_tb()) == 3

        with redirect_stdout(io.StringIO()) as stdout:
            shell.run_cell('import pandas as pd')
            shell.run_cell('def raise_user_error():\n    pd.Series([0])[1]')
            shell.run_cell('raise_user_error()')
        output = stdout.getvalue()
        assert 'KeyError: 1' in output
        assert 'Error found at line 2 in cell 13'
        assert mock_show_stacktrace_button.call_count == 5
        assert shell.showtraceback.call_count == 1
        assert get_tb_len(get_last_tb()) > 3

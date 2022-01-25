import inspect
import json
import os
import re
import sys

import ipywidgets as widgets
from IPython.core.getipython import get_ipython
from IPython.display import display

from seeq.sdk.rest import ApiException

__all__ = ['SPyDependencyNotFound', 'SPyException', 'SPyRuntimeError', 'SPyValueError', 'SPyTypeError',
           'SchedulePostingError', 'get_api_exception_message']


class SPyDependencyNotFound(Exception):
    pass


class SPyException(Exception):
    pass


class SPyRuntimeError(SPyException, RuntimeError):
    pass


class SPyValueError(SPyException, ValueError):
    pass


class SPyTypeError(SPyException, TypeError):
    pass


class SchedulePostingError(SPyRuntimeError):
    pass


def is_ipython():
    # noinspection PyBroadException
    try:
        return get_ipython() is not None
    except BaseException:
        return False


def is_jupyter():
    # noinspection PyBroadException
    try:
        return get_ipython().__class__.__name__ == 'ZMQInteractiveShell'
    except BaseException:
        return False


def is_datalab():
    return os.environ.get('SEEQ_SDL_CONTAINER_IS_DATALAB') == 'true'


def get_ipython_cell_no(frame):
    matched = re.match(r'^<ipython-input-(\d+)-[a-z\d]+>$', frame.f_code.co_filename)
    if matched:
        return matched[1]
    # ipykernel now creates cell filenames that don't include their input number.
    # The following workaround searches the internal ipython cell input variables for the frame's sourcecode
    if 'ipykernel' not in frame.f_code.co_filename:
        return None
    # noinspection PyBroadException
    try:
        # Sometimes there is an extra newline character at end of source string versus the ipython saved input
        sourcecode = inspect.getsource(frame).strip()
        cell_inputs = frame.f_globals.get('_ih')
        if cell_inputs is None or not isinstance(cell_inputs, list):
            return None
        for input_no in reversed(range(len(cell_inputs))):
            if sourcecode in cell_inputs[input_no]:
                return input_no
        return None
    except Exception:
        return None


def get_api_exception_message(e):
    if not isinstance(e, ApiException):
        raise ValueError('Exception is not an ApiException.')
    content = e.reason if e.reason and e.reason.strip() else ''
    if e.body:
        # noinspection PyBroadException
        try:
            body = json.loads(e.body)
            if len(content) > 0:
                content += ' - '
            content += body['statusMessage']
        except Exception:
            pass

    return '(%d) %s' % (e.status, content)


def get_exception_message(e):
    if isinstance(e, ApiException):
        return get_api_exception_message(e)
    if isinstance(e.args, tuple) and len(e.args) == 1 and isinstance(e.args[0], Exception):
        return get_exception_message(e.args[0])
    return str(e)


def get_exception_name(e):
    if isinstance(e, ApiException):
        return 'Seeq API Error'
    if isinstance(e, SchedulePostingError):
        return 'Scheduling Error'
    if isinstance(e, SPyException):
        return 'SPy Error'
    return type(e).__name__


def format_tb_header(colors, exception, lineno, ipy_inputno=None, filename=None, warning=None, pretty_name=True):
    exc_name = get_exception_name(exception) if pretty_name else type(exception).__name__
    exc_msg = get_exception_message(exception)

    header = f'{colors.excName}{exc_name}: {colors.Normal}{exc_msg}'
    location = None
    if ipy_inputno is not None:
        location = f'Error found at {colors.em}line {lineno}{colors.Normal} in ' \
                   f'{colors.filenameEm}cell {ipy_inputno}{colors.Normal}.'
    elif filename is not None:
        location = f'Error found at {colors.em}line {lineno}{colors.Normal} in ' \
                   f'{colors.filenameEm}file {filename}{colors.Normal}.'
    return '\n' + '\n\n'.join([s for s in [header, location, warning] if s is not None])


def show_stacktrace_button(self, exc_tuple):
    layout_kwargs = dict()
    layout_kwargs['width'] = 'auto'
    layout_kwargs['height'] = 'auto'
    if not is_datalab():
        # Data Lab has nice widget layouts preconfigured. If not in Data Lab, just adding border can help prettify
        layout_kwargs['border'] = 'solid 1px black'
    button = widgets.Button(description='Click to show stack trace',
                            layout=widgets.Layout(**layout_kwargs))

    colors = self.InteractiveTB.Colors
    exc_options_msg = '(To show stack trace by default, set %sspy.options.friendly_exceptions%s to %sFalse%s)' % (
        colors.valEm, colors.Normal, colors.name, colors.Normal
    )

    def click_func(b):
        b.close()
        self.showtraceback(exc_tuple=exc_tuple, running_compiled_code=True)
        print(exc_options_msg)

    button.on_click(click_func)
    return button


def spy_exception_handler(self, etype, value, tb, tb_offset=None):
    # Surround the whole exception handler with try/catch, so if anything goes
    # wrong, the user will see the normal stack trace with hopefully no side effects
    try:
        # Disable exception chaining. It's confusing and displays messages we don't want to display
        value.__suppress_context__ = True
        # The following loop traverses through the traceback and identifies
        # the traceback head that calls SPy, if it exists
        spy_call_head = None
        runner = tb
        while runner:
            try:
                if 'seeq.spy' in inspect.getmodule(runner.tb_next.tb_frame.f_code).__name__:
                    spy_call_head = runner
                    break
            except AttributeError:
                # If the module can't be determined, this catches the None.__name__ call
                pass
            runner = runner.tb_next

        if spy_call_head is not None:
            warning = None
            if issubclass(etype, ApiException):
                # ApiException
                # We don't truncate the stacktrace because seeing the code that calls the API could be useful for
                # both the user as well as Seeq support
                button = True

            elif issubclass(etype, SPyException):
                # Handled SPy error that user can fix
                # Truncate stacktrace so that no internal SPy code is unnecessarily displayed
                spy_call_head.tb_next = None
                button = True

            else:
                # Fatal SPy error
                warning = 'This error was not handled by SPy. Please contact Seeq support if this problem persists.'
                button = False

            spy_call_cell_no = get_ipython_cell_no(spy_call_head.tb_frame)
            spy_call_lineno = spy_call_head.tb_lineno
            spy_call_filename = spy_call_head.tb_frame.f_code.co_filename
            header = format_tb_header(self.InteractiveTB.Colors, value, spy_call_lineno, spy_call_cell_no,
                                      spy_call_filename, warning)

        else:
            # User error outside of SPy

            # get last ipython cell in stacktrace
            last_cell = tb
            while last_cell.tb_next is not None and get_ipython_cell_no(last_cell.tb_next.tb_frame) is not None:
                last_cell = last_cell.tb_next

            # If the previous loop iterated zero times, then there has been a break in compatibility (likely
            # "ipykernel" is no longer in the ipython cell filename). Fast-forward to the last frame in this case,
            # so we don't display the run_cell frame in interactiveshell.py
            if last_cell == tb:
                while last_cell.tb_next:
                    last_cell = last_cell.tb_next

            cell_no = get_ipython_cell_no(last_cell.tb_frame)
            line_no = last_cell.tb_lineno
            filename = last_cell.tb_frame.f_code.co_filename
            header = format_tb_header(self.InteractiveTB.Colors, value, line_no, cell_no, filename, pretty_name=False)
            button = True

        print(header)
        if button and is_jupyter():
            # Display a button, which will show the (possibly truncated) traceback when clicked
            display(show_stacktrace_button(self, (etype, value, tb)))
        else:
            # If not running in Jupyter, or when handling a fatal SPy error, show traceback automatically
            self.showtraceback((etype, value, tb), running_compiled_code=True)

    except KeyboardInterrupt:
        print('\n' + self.get_exception_only(), file=sys.stderr)

    except BaseException:
        self.showtraceback((etype, value, tb), running_compiled_code=True)


def add_spy_exception_handler():
    if not is_ipython():
        raise SPyRuntimeError('Friendly SPy exception handling is unavailable when not using IPython.')

    # Set IPython to use this exception handler for all exceptions of type SPyException
    get_ipython().set_custom_exc((Exception,), spy_exception_handler)


def remove_spy_exception_handler():
    if is_ipython():
        get_ipython().set_custom_exc((), None)

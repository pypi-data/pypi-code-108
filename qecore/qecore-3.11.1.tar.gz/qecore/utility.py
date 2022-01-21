#!/usr/bin/env python3
import os
import sys
import traceback
import shlex
from functools import partial
from subprocess import STDOUT, CalledProcessError, check_output
from time import sleep, time
from types import FunctionType

QE_DEVELOPMENT = not os.path.isdir("/mnt/tests/")


def get_application(context, application):
    """
    Get Application class instance of an application, based upon given name.

    :type context: <behave.runner.Context>
    :param context: Context object that is passed from common_steps.

    :type application: str
    :param application: String of application identification: name.

    :rtype: <qecore.application.Application>
    :return: Application class instance

    .. note::

        Do **NOT** call this by yourself. This function is called by :mod:`common_steps`.
    """

    app_class_to_return = None
    try:
        # Get app from environment file.
        app_class_to_return = getattr(context, application)
    except AttributeError:
        # Get app from sandbox application list.
        for app in context.sandbox.applications:
            if app.component == application:
                app_class_to_return = app
                break
    except TypeError:
        app_class_to_return = context.sandbox.default_application
        assert context.sandbox.default_application is not None, "\n".join((
            "Default application was not found. Check your environment file!"
            "This is indication that no application was defined in environment.py file."
        ))

    assert app_class_to_return is not None, "\n".join((
        f"Application '{application}' was not found.",
        "Possibly wrongly defined application in environment.py file or incorrect use of decorator in .feature file.",
    ))

    assert not isinstance(app_class_to_return, str), \
        "Application class was not found. Usually indication of not installed application."

    return app_class_to_return


def get_application_root(context, application):
    """
    Get Accessibility object of an application, based upon given name.

    :type context: <behave.runner.Context>
    :param context: Context object that is passed from common steps.

    :type application: str
    :param application: String of application identification: name.

    :rtype: <dogtail.tree.root.application>
    :return: Return root object of application.

    .. note::

        Do **NOT** call this by yourself. This function is called by :mod:`common_steps`.
    """
    from dogtail.tree import root

    try:
        root_to_return = root.application(application)
    except Exception:
        traceback.print_exc(file=sys.stdout)
        assert False, "".join((
            "Application was not found in accessibility. Check your environment or feature file!",
        ))

    return root_to_return


def run(command, verbose=False):
    """
    Execute a command and get output.

    :type command: str
    :param command: Command to be executed.

    :type verbose: bool
    :param verbose: Boolean value for verbose option.

    :rtype: str
    :return: Return string value of command output.

    :rtype: list
    :return: Return list with following format (output, return code, exception).
    """

    try:
        output = check_output(command, shell=True, stderr=STDOUT, encoding="utf-8")
        return output if not verbose else (output, 0, None)
    except CalledProcessError as error:
        return error.output if not verbose else (error.output, error.returncode, error)


def run_embed(context, command, *a, **kw):
    """
    Execute a command and get output.
    This version of command run will also embed results to the html log.

    :type context: <behave.runner.Context>
    :param context: Context object that will be used embedding.

    :type command: str
    :param command: Command to be executed.

    :rtype: list
    :return: Return list with following format (output, return code, exception).
    """

    try:
        output = check_output(command, shell=True, stderr=STDOUT, *a, **kw, encoding="utf-8")
        return_code = 0
        error = None
    except CalledProcessError as error:
        output = error.output
        return_code = error.returncode
        error = error

    context.embed("text/plain", f"$?={return_code}", caption=f"{command} result")
    context.embed("text/plain", output, caption=f"{command} output")

    return (error.output, error.returncode, error)


# behave-common-steps leftover.
def wait_until(tested, element=None, timeout=30, period=0.25, params_in_list=False):
    """
    This function keeps running lambda with specified params until the
    result is True or timeout is reached. Instead of lambda, Boolean variable
    can be used instead.

    Sample usages::

        >>> wait_until(lambda x: x.name != 'Loading...', context.app.instance)
        Pause until window title is not 'Loading...'.
        Return False if window title is still 'Loading...'
        Throw an exception if window doesn't exist after default timeout

        >>> wait_until(lambda element, expected: x.text == expected,
            (element, 'Expected text'), params_in_list=True)
        Wait until element text becomes the expected (passed to the lambda)

        >>> wait_until(dialog.dead)
        Wait until the dialog is dead

    """

    if isinstance(tested, bool):
        curried_func = lambda: tested
    # Or if callable(tested) and element is a list or a tuple.
    elif isinstance(tested, FunctionType) and \
            isinstance(element, (tuple, list)) and params_in_list:
        curried_func = partial(tested, *element)
    # Or if callable(tested) and element is not None?
    elif isinstance(tested, FunctionType) and element is not None:
        curried_func = partial(tested, element)
    else:
        curried_func = tested

    exception_thrown = None
    mustend = int(time()) + timeout
    while int(time()) < mustend:
        try:
            if curried_func():
                return True
        except Exception as error:  # pylint: disable=broad-except
            # If lambda has thrown the exception we'll re-raise it later
            # and forget about if lambda passes.
            exception_thrown = error
        sleep(period)
    if exception_thrown is not None:
        raise exception_thrown  # pylint: disable=raising-bad-type
    else:
        return False


KEY_VALUE = {
    "Alt" : 64, "Alt_L" : 64, "Alt_R" : 108,
    "Shift" : 50, "Shift_L" : 50, "Shift_R" : 62,
    "Ctrl" : 37, "Tab" : 23, "Super" : 133,
}

class HoldKey:
    """
    Simple utility to press a key and do some other actions.

    This is a context manager so the usage is as follows::

        >>> with HoldKey("Alt"):
        >>>     do_some_stuff()

    """

    def __init__(self, key_name):
        from dogtail.rawinput import holdKey
        self.key_name = key_name
        holdKey(self.key_name)
    def __enter__(self):
        return self
    def __exit__(self, my_type, value, trace):
        from dogtail.rawinput import releaseKey
        releaseKey(self.key_name)


class Tuple(tuple):
    """
    Simple tuple class with some defined arithmetic operations.

    :type command: tuple
    :param command: Tuple.
    """

    def __add__(self, other):
        return Tuple(x + y for x, y in zip(self, other))
    def __rmul__(self, other):
        return Tuple(other * x for x in self)
    def __eq__(self, other):
        return all(x == y for x, y in zip(self, other))
    def __lt__(self, other):
        return self[0] < other[0] or self[1] < other[1]
    def __gt__(self, other):
        return self[0] > other[0] or self[1] > other[1]


def validate_command(command):
    """
    Simple utility to try and escape any character that is not alpha character.

    :type command: str
    :param command: Command to be executed.

    :rtype: str
    :return: Validated command.
    """

    parsed_command = shlex.split(command)
    valid_command = ""
    for command_part in parsed_command:
        for character in command_part:
            valid_command += f"\\{character}" if not character.isalpha() else character
        valid_command += " "
    return valid_command


def verify_path(template_path):
    """
    Simple utility to verify if the file exists.

    :type template_path: str
    :param template_path: File location.

    :rtype: str or None
    :return: File path if found, None if not found.
    """

    try:
        assert os.path.isfile(template_path)
    except Exception as error:
        assert False, f"Desired file was not found: {error}"
    return template_path


SPACER = ' '
def plain_dump(node):
    """
    Simple attempt to get more information from a11y tree.

    :type node: <dogtail.tree.root.application>
    :param node: Accessibility node.
    """

    def crawl(node, depth):
        dump(node, depth)
        for child in node.children:
            crawl(child, depth + 1)

    def dump_std_out(item, depth):
        print(SPACER * depth + str(item) + \
            f"     [p:{item.position}, s:{item.size}, vis:{item.visible}, show:{item.showing}]")

    dump = dump_std_out
    crawl(node, 0)

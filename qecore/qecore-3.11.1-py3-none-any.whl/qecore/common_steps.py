#!/usr/bin/env python3
from time import sleep
import subprocess
from behave import step
from dogtail.rawinput import typeText, pressKey, keyCombo, absoluteMotion, click
from qecore.utility import get_application, get_application_root, run
from qecore.get_node import GetNode, get_center
from qecore.step_matcher import use_step_matcher

__author__ = """
Filip Pokryvka <fpokryvk@redhat.com>,
Michal Odehnal <modehnal@redhat.com>,
Bohdan Milar <bmilar@redhat.com>
"""

# To stop using "qecore" matcher use matcher "parse".
use_step_matcher("qecore")

"""
This allows multiple decorator definitions on one line separated by ' | '
EXAMPLE:
This decorator:
    @step('Item "{name}" "{role_name}" | with description "{description}" | that is "{attr}"')

matches for example the following steps:
    * Item "foo" "push button"
    * Item "foo" "push button" with description "something useful"
    * Item "foo" "push button" with description "something useful" that is "visible"
    * Item "foo" "push button" that is "visible"

And also any permutation of decorator parts except the first part, so this is also valid step:
    * Item "foo" "push button" that is "visible" with description "something useful"

WARNING:
"qecore" matcher does not work well with unquoted decorator arguments, use "parse" instead
"""

SIZE_DEC = "".join([' | has size at least "{size_low}"',
                    ' | has size at most "{size_high}"'])
POS_DEC = "".join([' | that is at least "{position_low}" from topleft',
                   ' | that is at most "{position_high}" from topleft'])
SIZE_POS_DEC = SIZE_DEC + POS_DEC


@step('{m_btn} click "{name}" "{role_name}" | with description "{description}" | that is "{attr}" | in "{a11y_root_name}"' + SIZE_POS_DEC)
def mouse_click(context, retry=True, expect_positive=True, **kwargs):
    with GetNode(context, **kwargs, retry=retry, expect_positive=expect_positive) as (data, node):
        node.click(data.m_btn)


@step('Mouse over "{name}" "{role_name}" | with description "{description}" | that is "{attr}" | in "{a11y_root_name}"' + SIZE_POS_DEC)
def mouse_over(context, retry=True, expect_positive=True, **kwargs):
    with GetNode(context, **kwargs, retry=retry, expect_positive=expect_positive) as (_, node):
        absoluteMotion(*(get_center(node)))


@step('Make an action "{action}" for "{name}" "{role_name}" | with description "{description}" | that is "{attr}" | in "{a11y_root_name}"' + SIZE_POS_DEC)
def make_action(context, action, retry=True, expect_positive=True, **kwargs):
    with GetNode(context, **kwargs, retry=retry, expect_positive=expect_positive) as (_, node):
        node.doActionNamed(action)


@step('Item "{name}" "{role_name}" | found | with description "{description}" | is "{attr}" | in "{a11y_root_name}"' + SIZE_POS_DEC)
def node_attribute(context, retry=True, expect_positive=True, **kwargs):
    with GetNode(context, **kwargs, retry=retry, expect_positive=expect_positive) as (_, node):
        assert node is not None, "Node was not found, it should be!"


@step('Item "{name}" "{role_name}" | was not found | with description "{description}" | is not "{attr}" | in "{a11y_root_name}"' + SIZE_POS_DEC)
def node_not_attribute(context, retry=True, expect_positive=False, **kwargs):
    with GetNode(context, **kwargs, retry=retry, expect_positive=expect_positive) as (_, node):
        assert node is None, "Node was found, it should not be!"


@step('Item "{name}" "{role_name}" | with description "{description}" | has text "{text}" | in "{a11y_root_name}"' + SIZE_POS_DEC)
def node_with_text(context, text, retry=True, expect_positive=True, **kwargs):
    with GetNode(context, **kwargs, retry=retry, expect_positive=expect_positive) as (_, node):
        assert text in node.text, "".join((
            f"Found node should have text: {text}\n",
            f"Instead the node has text: {node.text}"
        ))


@step('Item "{name}" "{role_name}" | with description "{description}" | does not have text "{text}" | in "{a11y_root_name}"' + SIZE_POS_DEC)
def node_without_text(context, text, retry=True, expect_positive=True, **kwargs):
    with GetNode(context, **kwargs, retry=retry, expect_positive=expect_positive) as (_, node):
        assert not text in node.text, "".join((
            f"Found node should have text: {text}\n",
            f"Node was found with text: {node.text}"
        ))


@step('Item "{name}" "{role_name}" | does not have description "{description}" | that is "{attr}" | in "{a11y_root_name}"' + SIZE_POS_DEC)
def node_without_description(context, description, retry=True, expect_positive=True, **kwargs):
    with GetNode(context, **kwargs, retry=retry, expect_positive=expect_positive) as (_, node):
        assert not description in node.description, "".join((
            f"Found node should not have description: {description}\n",
            f"Instead the node has description: {node.description}"
        ))


@step('Wait until "{name}" "{role_name}" | with description "{description}" | is "{attr}" | in "{a11y_root_name}"' + SIZE_POS_DEC)
def wait_until_attr(context, retry=True, expect_positive=True, **kwargs):
    with GetNode(context, **kwargs, retry=retry, expect_positive=expect_positive) as (_, node):
        for _ in range(30):
            if not node.sensitive:
                sleep(0.2)
            else:
                return


@step('Wait until "{name}" "{role_name}" | appears | with description "{description}" | in "{root}"')
def wait_until_in_root(context, name=None, role_name=None, description=None, m_btn=None, attr=None, root=None, retry=True, expect_positive=True):
    try:
        application_a11y_instance = get_application(context, root).instance # from sandbox/application
    except AssertionError:
        application_a11y_instance = get_application_root(context, root) # from a11y tree

    for _ in range(30):
        if application_a11y_instance.findChildren(lambda x: \
            ((name is None) or name in repr(x.name)) and \
            ((role_name is None) or role_name == x.roleName) and \
            ((description is None) or description in x.description)) == []:
            sleep(0.2)
        else:
            return


@step('Start another instance of "{application}" | via "{start_via}" | via command "{command}" | via command | in "{session}"')
def start_another_instance_of_application(context, application=None, start_via="command", command=None, session=None, kill=False):
    start_application(context, application, start_via, command, session, kill)


@step('Start application "{application}" | via "{start_via}" | via command "{command}" | via command | in "{session}"')
def start_application(context, application=None, start_via="command", command=None, session=None, kill=True):
    application = get_application(context, application)
    if start_via == "menu":
        try:
            application.start_via_menu(kill=kill)
        except Exception:
            application.start_via_menu(kill=kill)
    elif start_via == "command":
        try:
            application.start_via_command(command=command, in_session=session, kill=kill)
        except RuntimeError as error:
            assert False, error
        except Exception:
            application.start_via_command(command=command, in_session=session, kill=kill)
    else:
        raise AssertionError("Only defined options are 'command' and 'menu'.")


# Stop using qecore matcher.
use_step_matcher("parse")


@step('Close application "{application}" via "{close_via}"')
def application_in_not_running(context, application=None, close_via="gnome panel"):
    application = get_application(context, application)

    if close_via == "gnome panel":
        gnome_panel = context.sandbox.shell.child(application.name, "menu")
        for _ in range(10):
            gnome_panel.click()
            sleep(0.5)
            gnome_menu = context.sandbox.shell.findChildren(
                lambda x: x.name == "Quit" and x.roleName == "label"
            )
            if gnome_menu != []:
                gnome_menu[0].click()
                break
            pressKey("Esc")


    elif close_via == "gnome panel with workaround":
        gnome_panel = context.sandbox.shell.child(application.name, "menu")
        for _ in range(10):
            gnome_panel.click()
            sleep(0.5)
            gnome_menu = context.sandbox.shell.findChildren(
                lambda x: x.name == "Quit" and x.roleName == "label"
            )
            if gnome_menu != []:
                gnome_menu[0].point()
                sleep(0.5)
                pressKey("Enter")
                break
            pressKey("Esc")


    elif (close_via == "application panel menu") or\
        (close_via == "application menu" and context.sandbox.distribution == "Fedora"):
        application_panel = application.instance.children[0][0]
        for _ in range(10):
            application_panel.click(3)
            sleep(0.5)
            application_panel_menu = context.sandbox.shell.findChildren(
                lambda x: x.name == "Close" and x.roleName == "label"
            )
            if application_panel_menu != []:
                application_panel_menu[0].click()
                break
            pressKey("Esc")


    elif close_via in ("application file menu", "application menu"):
        for _ in range(10):
            context.execute_steps(f'* Left click "File" "menu" in "{application.component}"')
            sleep(0.5)
            application_file_menu = application.instance.findChildren(
                lambda x: ("Close" in x.name or "Quit" in x.name) and x.roleName == "menu item" and x.sensitive
            )
            if application_file_menu != []:
                application_file_menu[0].click()
                break
            pressKey("Esc")


    elif close_via == "application toggle menu":
        for _ in range(10):
            context.execute_steps(f'* Left click "Application menu" "toggle button" in "{application.component}"')
            sleep(0.5)
            try:
                context.execute_steps(f'* Left click "Quit" "push button" in "{application.component}"')
                break
            except Exception:
                pressKey("Esc")


    elif "menu:" in close_via:
        menu_name = None
        menu_item_name = None
        try:
            _, menu_name, menu_item_name = close_via.split(":")
        except Exception as error:
            raise Exception(f"Expected format of specific close via menu is 'menu:<menu>:<menu_item>\n{error}")

        for _ in range(10):
            application.instance.child(menu_name, "menu").click()
            sleep(0.5)
            try:
                application.instance.child(menu_item_name, "menu item").click()
                break
            except Exception:
                pressKey("Esc")


    elif close_via == "shortcut":
        application.close_via_shortcut()


    elif close_via == "kill command":
        application.kill_application()


    else:
        raise AssertionError("".join((
            "Only defined options are:\n",
            "'gnome panel', 'application menu', 'shortcut', 'kill command', \n",
            "'application file menu', 'application toggle menu' and 'application panel menu'"
        )))


@step('Application "{application}" is no longer running')
def application_is_not_running(context, application):
    application = get_application(context, application)
    if application.is_running():
        application.wait_before_app_closes(15)


@step('Application "{application}" is running')
def application_is_running(context, application):
    application = get_application(context, application)
    application.already_running()
    if not application.is_running():
        application.wait_before_app_starts(15)


@step('Run and save command output: "{command}"')
def run_and_save(context, command):
    """
    Run a shell command and store its returncode, stdour and stderr to context.

    :type command: str
    :param command: Command line to be executed and result stored.
    """

    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, encoding="utf-8")
    try:
        stdout, stderr = process.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        process.terminate()
        stdout, stderr = process.communicate()

    context.command = command
    context.command_stdout = stdout
    context.command_stderr = stderr
    context.command_return_code = process.returncode


@step('Last command output "{operand}" "{expected_output}"')
def verify_content_in_output(context, operand, expected_output):
    """
    Verify that the result of last command has a certain data as a result.

    :type operand: str
    :param operand: String specifying what operation to do.

    :type expected_output: str
    :param expected_output: Expected data to be compared to the command output.
    """

    assert hasattr(context, "command_stdout"), "".join((
        "\nYou have not saved a command output to be checked.",
        "\nTo do that use '* Run and save command output: \"<command>\"'"
    ))

    valid_operands = ("is", "is not", "contains", "does not contain", "begins with",
                      "does not begin with", "ends with", "does not end with")
    assert operand in valid_operands, "".join((
        f"You have attempted to use operand: '{operand}'",
        f"But only defined operands are:\n'{valid_operands}'"
    ))

    command_output = context.command_stdout
    if operand == "is":
        assert expected_output == command_output, "".join((
            f"\nWanted output: '{expected_output}'",
            f"\nActual output: '{command_output}'"
        ))

    if operand == "is not":
        assert expected_output != command_output, "".join((
            f"\nNot Wanted output: '{expected_output}'",
            f"\nActual output: '{command_output}'"
        ))

    if operand == "contains":
        assert expected_output in command_output, "".join((
            f"\nOutput should contain: '{expected_output}'",
            f"\nBut it does not: '{command_output}'"
        ))

    if operand == "does not contain":
        assert not expected_output in command_output, "".join((
            f"\nOutput should not contain: '{expected_output}'",
            f"\nBut it does: '{command_output}'"
        ))

    if operand == "begins with":
        assert command_output.startswith(expected_output), "".join((
            f"\nOutput should begin with: '{expected_output}'",
            f"\nBut it does not: '{command_output}'"
        ))

    if operand == "does not begin with":
        assert not command_output.startswith(expected_output), "".join((
            f"\nOutput should not begin with: '{expected_output}'",
            f"\nBut it does: '{command_output}'"
        ))

    if operand == "ends with":
        assert command_output.endswith(expected_output), "".join((
            f"\nOutput should end with: '{expected_output}'",
            f"\nBut it does not: '{command_output}'"
        ))

    if operand == "does not end with":
        assert not command_output.endswith(expected_output), "".join((
            f"\nOutput should not end with: '{expected_output}'",
            f"\nBut it does: '{command_output}'"
        ))


@step('Return code of last command output "{operand}" "{expected_return_code}"')
def verify_return_code_of_command(context, operand, expected_return_code):
    """
    Verify the return code of last command.

    :type operand: str
    :param operand: String specifying what operation to do.

    :type expected_return_code: str
    :param expected_return_code: Expected data to be compared to the command output.
    """

    assert hasattr(context, "command_stdout"), "".join((
        "\nYou have not saved a command output to be checked.",
        "\nTo do that use '* Run and save command output: \"<command>\"'"
    ))

    valid_operands = ("is", "is not")
    assert operand in valid_operands, "".join((
        f"You have attempted to use operand: '{operand}'",
        f"But only defined operands are:\n'{valid_operands}'"
    ))

    return_code = context.command_return_code
    if operand == "is":
        assert int(expected_return_code) == int(return_code), "".join((
            f"\nWanted return code: '{expected_return_code}'",
            f"\nActual return code: '{return_code}'"
        ))

    if operand == "is not":
        assert int(expected_return_code) != int(return_code), "".join((
            f"\nNot Wanted return code: '{expected_return_code}'",
            f"\nActual return code: '{return_code}'"
        ))


@step('Type text: "{text}"')
def type_text(context, text):
    typeText(text)


@step('Press key: "{key_name}"')
def press_key(context, key_name):
    pressKey(key_name)


@step('Key combo: "{combo_name}"')
def key_combo(context, combo_name):
    keyCombo(combo_name)


@step('Wait {number} second before action')
@step('Wait {number} seconds before action')
def wait_up(context, number):
    sleep(int(number))


@step('Move mouse to: x: "{position_x}", y: "{position_y}"')
def absolutie_motion(context, position_x, position_y):
    absoluteMotion(int(position_x), int(position_y))


@step('{button} click on: x: "{position_x}", y: "{position_y}"')
def click_on_position(context, button, position_x, position_y):
    buttons = dict(Left=1, Middle=2, Right=3)
    click(int(position_x), int(position_y), buttons[button])

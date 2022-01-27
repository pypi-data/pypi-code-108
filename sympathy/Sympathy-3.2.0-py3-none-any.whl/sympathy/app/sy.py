# This file is part of Sympathy for Data.
# Copyright (c) 2013 Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
import os
import sys

import sympathy.app.application.start
import sympathy.app.settings
from sympathy.utils.log import setup_log_levels


def excepthook(exit_after_exception):
    org_excepthook = sys.excepthook
    in_excepthook = [False]

    def inner(exctype, value, traceback):
        if in_excepthook[0]:
            return
        try:
            in_excepthook[0] = True
            if org_excepthook:
                org_excepthook(exctype, value, traceback)
            sys.stdout.flush()
            sys.stderr.flush()
        finally:
            in_excepthook[0] = False
            if exit_after_exception:
                sys.exit(1)

    return inner


def setting_to_unicoded_path(key, settings):
    value = settings.get(key, [])
    if isinstance(value, list):
        return os.pathsep.join([x for x in value])
    else:
        return value


def append_to_path(env_path, new_path):
    # Don't append if new_path is an empty string.
    if not new_path:
        return env_path
    elif not env_path:
        return new_path
    else:
        return u'{0}{1}{2}'.format(env_path, os.pathsep, new_path)


def setup_win32(env_path):
    """
    Windows specific settings. Paths to the bundled Python is setup
    properly.
    """
    python_base_dir = os.path.dirname(sys.executable)
    paths = [
        python_base_dir,
        os.path.join(python_base_dir, 'Scripts'),
        os.path.join(python_base_dir, 'Lib', 'site-packages', 'PySide2'),
        os.path.join(python_base_dir, 'Lib', 'site-packages',
                     'pywin32_system32'),
        os.path.join(python_base_dir, 'Lib', 'site-packages', 'numpy', 'core'),
        env_path]
    return os.pathsep.join(path for path in paths if path != '')


def use_platform_setting(win32, other):
    return win32 if sys.platform == 'win32' else other


def setup_environment(parsed=None):
    """Setup environment needed for Sympathy to execute. Paths and
    other environment variables are loaded depending on the system
    and the settings available.
    """
    env_path = os.environ['PATH']
    try:
        del os.environ['PATH']
    except KeyError:
        pass
    # Add application directory to PATH.
    if sys.platform == 'win32':
        env_path = setup_win32(env_path)

    sy_environment = {
        'SY_VALID_STARTUP': '1',
        'PYTHONPATH': '',
        'PATH': env_path
    }

    os.environ.update(sy_environment)


def execute_sympathy(parsed):
    """A utility function to execute Sympathy and read the return value
    independently of the host system.
    """
    cmd = parsed.launch_command
    setup_log_levels(parsed.loglevel)
    if cmd == 'gui':
        return sympathy.app.application.start.start_gui_application(
            parsed, sys.argv)
    elif cmd == 'cli':
        return sympathy.app.application.start.start_cli_application(
            parsed, sys.argv)


def run_binary(parsed):
    if parsed.filename:
        # Make absolute.
        parsed.filename = os.path.abspath(parsed.filename)

    sys.excepthook = excepthook(parsed.exit_after_exception)
    setup_environment(parsed)
    returncode = execute_sympathy(parsed)
    sys.exit(returncode)


def run(app):
    run_binary(app)


def run_function(function):
    setup_environment()
    return function()


if __name__ == '__main__':
    run_binary()

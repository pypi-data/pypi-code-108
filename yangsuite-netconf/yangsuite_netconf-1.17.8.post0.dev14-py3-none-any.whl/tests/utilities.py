# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.
"""Utility helper functions for tests."""

import json
import shutil
import os.path
from yangsuite.paths import set_base_path
from mock import MagicMock

canned_input_dir = os.path.join(os.path.dirname(__file__), 'canned_input')
canned_output_dir = os.path.join(os.path.dirname(__file__), 'canned_output')


def canned_input_str(filename, dir=''):
    """Get the text contents of the specified canned_input file."""
    with open(os.path.join(canned_input_dir, dir, filename), 'r') as fd:
        return fd.read()


def canned_input_data(filename, dir=''):
    """Get the specified canned_input file as a JSON object."""
    return json.loads(canned_input_str(filename, dir))


def canned_output_str(filename, dir=''):
    """Get the text contents of the specified canned_output file."""
    with open(os.path.join(canned_output_dir, dir, filename), 'r') as fd:
        return fd.read()


def canned_output_data(filename, dir=''):
    """Get the specified canned_output file as a JSON object."""
    return json.loads(canned_output_str(filename, dir))


def clone_test_data(new_location):
    if os.path.exists(new_location):
        shutil.rmtree(new_location)
    shutil.copytree(os.path.join(os.path.dirname(__file__), 'data'),
                    new_location)
    set_base_path(new_location)


def mock_manager(mock_connect):
    """Given a mock of manager.connect, set up the appropriate MagicMock.

    Returns:
      MagicMock: of 'manager' object returned/yielded by connect() method.
    """
    # We used to use MagicMock(spec=ncclient.manager.Manager) here, but as of
    # ncclient 0.6.3, the Manager class uses some trickery with __getattr__
    # (https://github.com/ncclient/ncclient/pull/200)
    # that MagicMock isn't smart enough to detect and mock out.
    # Hence, we now just use a generic MagicMock object instead.
    manager = MagicMock()
    mock_connect.return_value = manager
    mock_connect.return_value.__enter__.return_value = manager
    manager.connected = True
    manager.take_notification.return_value = None
    return manager

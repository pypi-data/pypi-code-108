"""A module responsible for Masterful code deployment."""

import atexit
import json
import os
import sys
import types
import uuid

import memory_tempfile
import requests
from requests import auth

from masterful import constants
from masterful import version

try:
  memory_tempfile = memory_tempfile.MemoryTempfile(fallback=True)
  _DOWNLOAD_FOLDER = memory_tempfile.gettempdir()
except AttributeError:
  import tempfile
  _DOWNLOAD_FOLDER = tempfile.gettempdir()
except RuntimeError:
  import tempfile
  _DOWNLOAD_FOLDER = tempfile.gettempdir()


def _pretty_error_message(response, account_id) -> str:
  status_code = response.status_code
  account_status = response.json().get('context', {}).get('account_status', '')
  pretty_messages = {
      400:
          f"The Masterful account id '{account_id}' or authorization key is in a bad format. Please register for a new account at https://www.masterfulai.com/try-free.",
      401:
          f"The authorization key for Masterful account id '{account_id}' is incorrect. Please check your key and try again.",
      403:
          f"The Masterful account id '{account_id}' has hit its free usage limits ({account_status}). Please contact your Masterful representative to get a new key.",
      404:
          f"The Masterful account id '{account_id}' does not exist. Please check your key and try again.",
  }
  if status_code in pretty_messages:
    print(ValueError(pretty_messages[status_code]))
  else:
    print(
        f'Failed to register Masterful package. (Internal Server Error: {response.status_code}){os.linesep}'
        f'{json.dumps(response.json(), indent=2)}')



def _print_success_message(version: str) -> None:
  """Prints a user friendly message to confirm the success of register.

  Args:
    version: The package version to include in the message.
  """
  print(
    "MASTERFUL: Your account has been successfully registered."
    f" Masterful v{version} is loaded."
  )


def register(account_id: str = '',
             authorization_key: str = '') -> types.ModuleType:
  """Authorizes the Masterful library and prepares the system for its use.

  This function authorizes usage of the Masterful library, and loads it into
  memory for use. This function *must* be called before using or importing
  any other Masterful packages.

  Note this function returns a new Masterful module instance, so you must
  replace the existing instance like so::

    import masterful
    masterful = masterful.register(...)

  If you need credentials for using Masterful, please request them
  `here <https://www.masterfulai.com/try-free>`_

  Args:
    account_id: The account credentials that were assigned by Masterful.
    authorization_key: The authorization key assigned by Masterful for the provided account.

  Returns:
    Module containing the latest implementation of the Masterful API.
  """

  def remove_file(file_path: str):
    if os.path.exists(file_path):
      os.remove(file_path)

  # Download zip file of Masterful package
  if not account_id:
    account_id = account_id if account_id else constants.MASTERFUL_ACCOUNT_ID

  if not authorization_key:
    authorization_key = (authorization_key if authorization_key else
                         constants.MASTERFUL_AUTHORIZATION_KEY)

  zip_path = f'{_DOWNLOAD_FOLDER}/masterful-{version.__version__}.zip'
  if not f'{zip_path}/masterful-{version.__version__}/' in sys.path:
    response = requests.get(
        constants.MASTERFUL_LOAD + f'?version={version.__version__}',
        auth=auth.HTTPBasicAuth(account_id, authorization_key),
        stream=True)

    if response.status_code != 200:
      _pretty_error_message(response, account_id)
      sys.exit()

    with open(zip_path, 'wb') as zip_file:
      zip_file.write(response.raw.read())
    atexit.register(lambda: remove_file(zip_path))

    # Prepend zip file to system path
    if zip_path not in sys.path:
      sys.path.insert(0, f'{zip_path}/masterful-{version.__version__}/')

    # Remove masterful from the global modules list
    masterful_module_names = []
    for module_name in sys.modules:
      if 'masterful' in module_name:
        masterful_module_names.append(module_name)

    for module_name in masterful_module_names:
      del sys.modules[module_name]

    # Re-import the new masterful
    globals()['masterful'] = __import__('masterful')

  import masterful

  # Update the constants so the rest of the package
  # can use them
  import masterful.constants
  masterful.constants.MASTERFUL_ACCOUNT_ID = account_id
  masterful.constants.MASTERFUL_AUTHORIZATION_KEY = authorization_key
  masterful.constants.MASTERFUL_SESSION_ID = str(uuid.uuid4())
  _print_success_message(version.__version__)

  return masterful

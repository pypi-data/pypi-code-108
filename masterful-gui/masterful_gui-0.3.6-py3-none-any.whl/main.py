"""Masterful GUI app main module.

This module is the main entry point for the app. Should be kept as simple
as possible, it defines the global flags for the app and runs it.
"""

import sys

from absl import app
from absl import flags

import masterful_gui.program as program

# The default port the app runs on.
_DEFAULT_PORT = 7007

# The name assigned to the server instance.
_SERVER_NAME = "Masterful GUI"

# TODO(ray): If the user picks a different port, CORS problems might be
# introduced. Add a dynamic solution to whitelist the user selected port
# to prevent CORS breakages.
flags.DEFINE_integer('port', _DEFAULT_PORT, 'The port for running the server')


def run_main():
  """The main function that runs the app."""
  visualize = program.Visualize(_SERVER_NAME)

  try:
    app.run(visualize.main)
  except Exception as e:
    print(f'Running Masterful GUI failed: {str(e)}')
    sys.exit(1)


if __name__ == '__main__':
  run_main()
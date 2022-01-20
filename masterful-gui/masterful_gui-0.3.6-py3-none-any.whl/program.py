"""The Masterful GUI central program module. 

This module defines the Masterful GUI program. The program constructs all the
various pieces that each handles part of the experience and combines them
together to create the full Masterful GUI experience.
"""
from pathlib import Path

from absl import flags

from masterful_gui import server
from masterful_gui import application
from masterful_gui import version

FLAGS = flags.FLAGS

# The host to bind the web server to.
_HOSTNAME = 'localhost'

# Directory where static files are collected.
_STATIC_DIR = f"{Path(__file__).parent}/static"


class Visualize(object):
  """The Masterful GUI program class, internally called Visualize."""

  def __init__(self, name: str):
    """Initializes the instance.
    
    Args:
      name: An assigned name for the 
    """
    self._name = name

  def main(self, ignored_argv=("",)):
    """Blocking main function for Masterful GUI.
        
    This method is called by `visualize.backend.main.run_main`, which is
    the standard entrypoint for the Masterful GUI command line program.        
    
    Args:
      ignored_argv: Do not pass. Required for Abseil compatibility.
    """
    application.init_settings_env_variable()
    app = application.create_wsgi_app()
    application.make_migrations()
    application.migrate()

    web_server = server.VisualizeServer(_HOSTNAME, FLAGS.port, app, _STATIC_DIR)
    web_server.print_serving_messsage(version.__version__)

    try:
      web_server.serve_forever()
    except KeyboardInterrupt:
      pass

    print(f"\n{self._name} stopped.")
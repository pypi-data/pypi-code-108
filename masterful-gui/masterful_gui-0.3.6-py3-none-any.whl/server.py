"""The Masterful GUI web server module."""

import sys

from werkzeug.serving import run_simple

# TODO(MAS-1169): Set the args based on dev vs. prod mode.
# The current configuration optimizes for prod mode.


class VisualizeServer(object):
  """Handles the creation of the web server that runs the WSGI application.
  
  This class is a wrapper class around the Werkzeug web server functionality.  
  It currently plays the role of abstracting the web serving responsiblity
  to an object, but internally only passes configuration args to the Werkzeug
  API that creates the default web server. As development continues we will
  need to customize ceratin behaviors of the web server, such customiztations
  are going to live here.
  """

  def __init__(self,
               hostname: str,
               port: int,
               app,
               static_files: str,
               use_reloader: bool = False,
               use_debugger: bool = False):
    """Initializes the instance.
    
    Args:
      hostname: The host to bind to. i.e. 'localhost'.
      port: The port the server should use.
      app: The WSGI app the server will execute.
      static_files: The absolute path to the static files dir.
      use_reloader: Whether the server should automatically restart the python
        process if the modules were changed while it's running. Only set True
        for dev, in production this should always be False.
      use_debugger: Enables/disables the werkzeug debugging system.
    """
    self._hostname = hostname
    self._port = port
    self._app = app
    self._static_files = static_files
    self._use_reloader = use_reloader
    self._use_debugger = use_debugger

  def print_serving_messsage(self, version: str):
    """Prints a user-friendly message prior to server start.
    
    This will (should) be called just before `serve_forever`.

    Args:
      version: The current version of the GUI to be displayed in the console
        output.
    
    TODO(ray): Update this after adding a version module or an alternative
    solution.
    
    TODO(ray): Make it pretty add some style to make this standout on the
    terminal.
    """
    sys.stderr.write(
        f"Masterful GUI {version} at http://{self._hostname}:{self._port}/ "
        "(Press CTRL+C to quit)\n\n")
    sys.stderr.flush()

  def serve_forever(self):
    """Runs the server indefinitly."""

    run_simple(
        self._hostname,
        self._port,
        self._app,
        use_reloader=self._use_reloader,
        use_debugger=self._use_debugger,
        static_files={'/static': self._static_files},
    )

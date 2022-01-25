"""
potluck_server
Includes `potluck_server.sync` and `potluck_server.app` modules, the
first providing rather crude file-system-backed synchronous state, and
the second being a WSGI Flask app for collecting student submissions and
evaluating them via `potluck_eval` (see the `potluck` module).

Main server documentation is in `potluck_server.app`.
"""

"""
Package for defining and evaluating Python programming tasks.

potluck/__init__.py

For a high-level interface, import `potluck.compare`. To define a task
specification, import `potluck.specifications`. To define tests for a
specification, import `potluck.meta`.


## Compatibility

Overall `potluck` requires Python 3.6 or later, but the following modules
are compatible with Python 2.7:

- `potluck.render`
- `potluck.html_tools`
- `potluck.phrasing`
- `potluck.file_utils`
- `potluck.time_utils`
- `potluck.logging`


## Dependencies:

Core (these should be installed automatically when installing via `pip`)

- `jinja2` for report rendering via HTML templates.
- `pygments` for code highlighting in reports.
- `importlib_resources` for resource loading.
- `markdown` and `beautifulsoup4` for creating instructions. If
    `pymdown-extensions` is available, its 'extra' collection will be
    used instead of standard markdown 'extra', which allows for things
    like code fences inside itemized lists.
- `python_dateutil` for time zone management.

Optional (installing via [option] should fetch these when using `pip`)

- `[test]` installs `pytest` for running the tests.
- `[expectations]` installs `optimism` for capturing student tests using
    that module.
- `[turtle_capture]` installs `Pillow` (>=6.0.0) for capturing turtle
    drawings, but you will need to manually install Ghostscript (which is
    not available directly from PyPI).
- `[server]` installs `flask` and `flask_cas` for supporting the
    `potluck_server` module.
- `[security]` installs `flask_talisman` and `flask_seasurf` for
    baseline server security.
- `[https_debug]` installs `pyopenssl` for using HTTPS with a
    self-signed certificate when doing local debugging.


## Getting Started

Unless you want to get into the guts of things, `potluck.specifications`
is the place to get started, while `potluck.rubrics` and
`potluck.contexts` deal with more advanced concepts without getting too
far into the weeds. `potluck.meta` and `potluck.snippets` are also useful
high-level interfaces for building tasks.


## Flask App

For automatically collecting and evaluating submissions using `potluck`,
a Flask WSGI app is available in the separate `potluck_server` module.
"""

# Import version variable
from ._version import __version__ # noqa F401

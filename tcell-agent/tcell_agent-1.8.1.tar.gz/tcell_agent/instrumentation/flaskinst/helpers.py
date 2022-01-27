from __future__ import unicode_literals

try:
    from flask import __version__
    FLASK_VERSION = tuple([int("".join(i for i in x if i.isnumeric())) for x in __version__.split(".")])
except Exception:
    FLASK_VERSION = (0, 0, 0)

"""Generators generate the final Dockerfile based on the settings.

The following generators are currently supported:

* :mod:`~ou_container_builder.generators.jupyter_notebook`
* :mod:`~ou_container_builder.generators.web_app`
"""
from . import jupyter_notebook  # noqa
from . import web_app  # noqa

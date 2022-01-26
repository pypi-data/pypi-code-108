# Copyright 2011-2018 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
"""
This is the :mod:`atelier` package.

.. autosummary::
   :toctree:

   invlib
   invlib.utils
   invlib.tasks
   jarbuilder
   projects
   test
   utils
   sphinxconf
   sheller

"""

import setuptools  # try to avoid "Distutils was imported before Setuptools"

from .setup_info import SETUP_INFO

__version__ = SETUP_INFO['version']

intersphinx_urls = dict(docs="https://lino-framework.gitlab.io/atelier")
srcref_url = 'https://gitlab.com/lino-framework/atelier/blob/master/%s'
# doc_trees = ['docs']

current_project = None
"""
The currently loaded project.  An instance of
:class:`atelier.Project`.  This is set by :func:`atelier.invlib.setup_from_tasks`.
"""

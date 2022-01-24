# -*- coding: UTF-8 -*-
# Copyright 2002-2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

"""Some extensions for Sphinx.

.. autosummary::
   :toctree:

   base
   logo
   actordoc
   help_texts_extractor

"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

from atelier import sphinxconf
from atelier.sphinxconf import interproject
from sphinx.ext import autosummary
from sphinx.ext.autodoc.importer import import_module
from sphinx.util import logging ; logger = logging.getLogger(__name__)

if False:
    # temporary patch reports failed imports
    def _import_by_name(name: str) -> Tuple[Any, Any, str]:
        """Import a Python object given its full name."""

        try:
            name_parts = name.split('.')

            # # 20200429 first try whether it is a full module name
            # try:
            #     mod = import_module(name)
            #     parent_name = '.'.join(name_parts[:-1])
            #     if parent_name:
            #         parent = import_module(parent_name)
            #     else:
            #         parent = None
            #     return parent, mod, name
            # except ImportError:
            #     pass

            # try first interpret `name` as MODNAME.OBJ
            modname = '.'.join(name_parts[:-1])
            if modname:
                try:
                    mod = import_module(modname)
                    return getattr(mod, name_parts[-1]), mod, modname
                except (ImportError, IndexError, AttributeError):
                    pass

            # ... then as MODNAME, MODNAME.OBJ1, MODNAME.OBJ1.OBJ2, ...
            last_j = 0
            modname = None
            for j in reversed(range(1, len(name_parts) + 1)):
                last_j = j
                modname = '.'.join(name_parts[:j])
                try:
                    import_module(modname)
                except ImportError as e:
                    logger.info("Failed to import %s : %s", modname, e)
                    continue

                if modname in sys.modules:
                    break

            if last_j < len(name_parts):
                parent = None
                obj = sys.modules[modname]
                for obj_name in name_parts[last_j:]:
                    parent = obj
                    obj = getattr(obj, obj_name)
                return obj, parent, modname
            else:
                return sys.modules[modname], None, modname
        except (ValueError, ImportError, AttributeError, KeyError) as e:
            raise ImportError(*e.args)

    # autosummary.import_by_name = my_import_by_name
    autosummary._import_by_name = _import_by_name


def configure(globals_dict, django_settings_module=None, project=None):
    """
    Adds to your :xfile:`conf.py` an arbitrary series of things that all
    Lino docs configuration files have in common.

    To be called from inside the Sphinx :xfile:`conf.py` file as follows::

      from lino.sphinxcontrib import configure
      configure(globals())

    This will also call :func:`atelier.sphinxconf.configure`, and then
    adds more things specific to the Lino framework.

    This adds the main Lino doctrees to your `intersphinx_mapping
    <https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html#confval-intersphinx_mapping>`__.

    You can specify an additional positional argument `django_settings_module`
    (the name of a Django settings module).  If this argument is specified, call
    :meth:`lino.startup` with it.

    """
    if django_settings_module is not None:
        from lino import startup
        startup(django_settings_module)
        print("Django started with DJANGO_SETTINGS_MODULE={}.".format(django_settings_module))
        from django.conf import settings
        print(settings.SITE.welcome_text())

    sphinxconf.configure(globals_dict, project)

    im = {}
    im['lf'] = ('https://www.lino-framework.org/', None)
    im['cg'] = ('https://community.lino-framework.org/', None)
    im['ug'] = ('https://using.lino-framework.org/', None)
    im['hg'] = ('https://hosting.lino-framework.org/', None)
    im['book'] = ('https://dev.lino-framework.org/', None)
    # im['www'] = ('https://www.saffre-rumma.net/', None)

    interproject.configure(globals_dict, **im)

    extlinks = globals_dict['extlinks']
    extlinks['ticket'] = ('https://jane.mylino.net/#/api/tickets/PublicTickets/%s', '#')

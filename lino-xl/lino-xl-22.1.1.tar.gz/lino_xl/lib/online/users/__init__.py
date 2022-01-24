# Copyright 2015-2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
"""

Deprecated. :term:`online registration` this is now implemented in the standard
:mod:`lino.modlib.users`.

An extension of :mod:`lino.modlib.users` that makes User inherit from Person
(Multi-table inheritance).

The main purpose was to automatically have a :term:`partner` for every
:term:`site user`.



.. autosummary::
   :toctree:

    choicelists
    desktop

"""

from lino.modlib.users import Plugin


class Plugin(Plugin):
    needs_plugins = ['lino_xl.lib.countries']
    extends_models = ['User']
    # online_registration = True

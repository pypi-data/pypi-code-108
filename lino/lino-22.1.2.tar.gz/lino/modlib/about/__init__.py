# Copyright 2008-2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

"""
See :doc:`/plugins/about`.

"""

from lino.api import ad


class Plugin(ad.Plugin):
    "See :doc:`/dev/plugins`."

    def setup_site_menu(self, site, user_type, m):
        m.add_action(site.models.about.About)

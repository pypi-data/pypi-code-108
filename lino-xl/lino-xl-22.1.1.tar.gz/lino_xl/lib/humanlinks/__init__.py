# Copyright 2014-2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

"""Adds functionality to manage "parency links" between two "persons".


"""

from lino.api import ad, _


class Plugin(ad.Plugin):
    "Extends :class:`lino.core.plugin.Plugin`."
    verbose_name = _("Parency links")

    ## settings
    person_model = 'contacts.Person'
    """
    A string referring to the model which represents a human in your
    application.  Default value is ``'contacts.Person'`` (referring to
    :class:`lino_xl.lib.contacts.Person`).
    """

    def on_site_startup(self, site):
        self.person_model = site.models.resolve(self.person_model)
        super(Plugin, self).on_site_startup(site)


    def setup_explorer_menu(self, site, user_type, m):
        # mg = site.plugins.contacts
        mg = site.plugins[self.person_model._meta.app_label]
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('humanlinks.Links')
        m.add_action('humanlinks.LinkTypes')

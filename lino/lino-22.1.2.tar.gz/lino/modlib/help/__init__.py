# -*- coding: UTF-8 -*-
# Copyright 2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
"""
Lino's help framework.  See :doc:`/plugins/help`.

"""

from lino.api import ad

class Plugin(ad.Plugin):

    make_help_pages = False
    """Whether to activate the help button.

    Setting this to `True` will cause Lino to automatically run
    :manage:`makehelp` during :manage:`collectstatic`.

    """

    def before_actors_discover(self):
        from lino.core.utils import get_models
        from lino.modlib.help.utils import HelpTextsLoader
        self.htl = HelpTextsLoader(self.site)
        # Install help texts to all database fields:
        # models_list = get_models(include_auto_created=True)
        models_list = get_models()
        for model in models_list:
            self.htl.install_help_text(model)  # needed only for makedocs
            for f in model._meta.get_fields(include_parents=False):
            # for f in model._meta.get_fields():
                self.htl.install_help_text(f, model, f.name)
            # for f in model._meta.private_fields:
            #     site.install_help_text(f, model, f.name)
            # if model.__name__ == "Client":
            #     print(' '.join([f.name for f in model._meta.private_fields]))

    def on_ui_init(self, kernel):
        from lino.core import actors

        for a in actors.actors_list:
            self.htl.install_help_text(a)
            if a.parameters is not None:
                for name, fld in a.parameters.items():
                    self.htl.install_help_text(fld, a, name)

            for ba in a.get_actions():
                # site.install_help_text(
                #     ba.action.__class__, ba.action.action_name)
                # site.install_help_text(ba.action, a, ba.action.action_name)
                # site.install_help_text(ba.action, ba.action.__class__)
                if a.model is not None:
                    self.htl.install_help_text(
                        ba.action, a.model, ba.action.action_name)
                self.htl.install_help_text(
                    ba.action, a, ba.action.action_name)
                self.htl.install_help_text(ba.action.__class__)
                # htl.install_help_text(
                #     ba.action, ba.action.__class__,
                #     attrname=ba.action.action_name)

                if ba.action.parameters is not None:
                    for name, fld in ba.action.parameters.items():
                        self.htl.install_help_text(
                            fld, ba.action.__class__, name)

        self.htl = None  # free the resources

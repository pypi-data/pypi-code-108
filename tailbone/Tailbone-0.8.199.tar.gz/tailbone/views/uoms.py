# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2021 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
UOM Views
"""

from __future__ import unicode_literals, absolute_import

from rattail.db import model

from tailbone.views import MasterView


class UnitOfMeasureView(MasterView):
    """
    Master view for the UOM mappings.
    """
    model_class = model.UnitOfMeasure
    route_prefix = 'uoms'
    url_prefix = '/units-of-measure'
    bulk_deletable = True
    has_versions = True

    labels = {
        'sil_code': "SIL Code",
    }

    grid_columns = [
        'abbreviation',
        'sil_code',
        'description',
        'notes',
    ]

    form_fields = [
        'abbreviation',
        'sil_code',
        'description',
        'notes',
    ]

    def configure_grid(self, g):
        super(UnitOfMeasureView, self).configure_grid(g)

        g.set_renderer('description', self.render_description)

        g.set_sort_defaults('abbreviation')

        g.set_link('abbreviation')
        g.set_link('description')

    def configure_form(self, f):
        super(UnitOfMeasureView, self).configure_form(f)

        f.set_renderer('description', self.render_description)
        f.set_type('notes', 'text')

        if not self.creating:
            f.set_readonly('abbreviation')

        if self.creating or self.editing:
            f.remove('description')
            f.set_enum('sil_code', self.enum.UNIT_OF_MEASURE)

    def redirect_after_create(self, uom, **kwargs):
        return self.redirect(self.get_index_url())

    def redirect_after_edit(self, uom, **kwargs):
        return self.redirect(self.get_index_url())

    def render_description(self, uom, field):
        code = uom.sil_code
        if code:
            if code in self.enum.UNIT_OF_MEASURE:
                return self.enum.UNIT_OF_MEASURE[code]
            return "(unknown code)"

    def collect_wild_uoms(self):
        app = self.get_rattail_app()
        handler = app.get_products_handler()
        uoms = handler.collect_wild_uoms()
        self.request.session.flash("All abbreviations from the wild have been added.  Now please map each to a SIL code.")
        return self.redirect(self.get_index_url())

    @classmethod
    def defaults(cls, config):
        cls._uom_defaults(config)
        cls._defaults(config)

    @classmethod
    def _uom_defaults(cls, config):
        route_prefix = cls.get_route_prefix()
        url_prefix = cls.get_url_prefix()
        permission_prefix = cls.get_permission_prefix()
        model_title_plural = cls.get_model_title_plural()

        # fix perm group name
        config.add_tailbone_permission_group(permission_prefix, model_title_plural, overwrite=False)

        # collect wild uoms
        config.add_tailbone_permission(permission_prefix, '{}.collect_wild_uoms'.format(permission_prefix),
                                       "Collect UoM abbreviations from the wild")
        config.add_route('{}.collect_wild_uoms'.format(route_prefix), '{}/collect-wild-uoms'.format(url_prefix),
                         request_method='POST')
        config.add_view(cls, attr='collect_wild_uoms', route_name='{}.collect_wild_uoms'.format(route_prefix),
                        permission='{}.collect_wild_uoms'.format(permission_prefix))


def includeme(config):
    UnitOfMeasureView.defaults(config)

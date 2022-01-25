# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2020 Lance Edgar
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
Project views
"""

from __future__ import unicode_literals, absolute_import

import os
import zipfile
# from collections import OrderedDict

import colander

from tailbone import forms
from tailbone.views import View


class GenerateProject(colander.MappingSchema):
    """
    Base schema for the "generate project" form
    """
    name = colander.SchemaNode(colander.String())

    slug = colander.SchemaNode(colander.String())

    organization = colander.SchemaNode(colander.String())

    python_project_name = colander.SchemaNode(colander.String())

    python_name = colander.SchemaNode(colander.String())

    has_db = colander.SchemaNode(colander.Boolean())

    extends_db = colander.SchemaNode(colander.Boolean())

    has_batch_schema = colander.SchemaNode(colander.Boolean())

    has_web = colander.SchemaNode(colander.Boolean())

    has_web_api = colander.SchemaNode(colander.Boolean())

    has_datasync = colander.SchemaNode(colander.Boolean())

    # has_filemon = colander.SchemaNode(colander.Boolean())

    # has_tempmon = colander.SchemaNode(colander.Boolean())

    # has_bouncer = colander.SchemaNode(colander.Boolean())

    integrates_catapult = colander.SchemaNode(colander.Boolean())

    integrates_corepos = colander.SchemaNode(colander.Boolean())

    # integrates_instacart = colander.SchemaNode(colander.Boolean())

    integrates_locsms = colander.SchemaNode(colander.Boolean())

    # integrates_mailchimp = colander.SchemaNode(colander.Boolean())

    uses_fabric = colander.SchemaNode(colander.Boolean())


class GenerateByjoveProject(colander.MappingSchema):
    """
    Schema for generating a new 'byjove' project
    """
    name = colander.SchemaNode(colander.String())

    slug = colander.SchemaNode(colander.String())


class GenerateFabricProject(colander.MappingSchema):
    """
    Schema for generating a new 'fabric' project
    """
    name = colander.SchemaNode(colander.String())

    slug = colander.SchemaNode(colander.String())

    organization = colander.SchemaNode(colander.String())

    python_project_name = colander.SchemaNode(colander.String())

    python_name = colander.SchemaNode(colander.String())

    integrates_with = colander.SchemaNode(colander.String(),
                                          missing=colander.null)


class GenerateProjectView(View):
    """
    View for generating new project source code
    """

    def __init__(self, request):
        super(GenerateProjectView, self).__init__(request)
        self.handler = self.get_handler()

    def get_handler(self):
        from rattail.projects.handler import RattailProjectHandler
        return RattailProjectHandler(self.rattail_config)

    def __call__(self):
        use_buefy = self.get_use_buefy()

        # choices = OrderedDict([
        #     ('has_db', {'prompt': "Does project need its own Rattail DB?",
        #                 'type': 'bool'}),
        # ])

        project_type = 'rattail'
        if self.request.method == 'POST':
            project_type = self.request.POST.get('project_type', 'rattail')
        if project_type not in ('rattail', 'byjove', 'fabric'):
            raise ValueError("Unknown project type: {}".format(project_type))

        if project_type == 'byjove':
            schema = GenerateByjoveProject
        elif project_type == 'fabric':
            schema = GenerateFabricProject
        else:
            schema = GenerateProject
        form = forms.Form(schema=schema(), request=self.request,
                          use_buefy=use_buefy)
        if form.validate(newstyle=True):
            zipped = self.generate_project(project_type, form)
            return self.file_response(zipped)
            # self.request.session.flash("New project was generated: {}".format(form.validated['name']))
            # return self.redirect(self.request.current_route_url())

        return {
            'index_title': "Generate Project",
            'handler': self.handler,
            # 'choices': choices,
            'use_buefy': use_buefy,
        }

    def generate_project(self, project_type, form):
        options = form.validated
        slug = options['slug']
        path = self.handler.generate_project(project_type, slug, options)

        zipped = '{}.zip'.format(path)
        with zipfile.ZipFile(zipped, 'w', zipfile.ZIP_DEFLATED) as z:
            self.zipdir(z, path, slug)
        return zipped

    def zipdir(self, zipf, path, slug):
        for root, dirs, files in os.walk(path):
            relative_root = os.path.join(slug, root[len(path)+1:])
            for fname in files:
                zipf.write(os.path.join(root, fname),
                           arcname=os.path.join(relative_root, fname))

    @classmethod
    def defaults(cls, config):
        config.add_tailbone_permission('common', 'common.generate_project',
                                       "Generate new project source code")
        config.add_route('generate_project', '/generate-project')
        config.add_view(cls, route_name='generate_project',
                        permission='common.generate_project',
                        renderer='/generate_project.mako')


def includeme(config):
    GenerateProjectView.defaults(config)

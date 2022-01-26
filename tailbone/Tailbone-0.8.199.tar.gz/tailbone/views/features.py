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
Feature views
"""

from __future__ import unicode_literals, absolute_import

import six
import colander
import markdown

from tailbone import forms
from tailbone.views import View


class GenerateFeatureView(View):
    """
    View for generating new feature source code
    """

    def __init__(self, request):
        super(GenerateFeatureView, self).__init__(request)
        self.handler = self.get_handler()

    def get_handler(self):
        app = self.get_rattail_app()
        handler = app.get_feature_handler()
        return handler

    def __call__(self):
        use_buefy = self.get_use_buefy()

        schema = self.handler.make_schema()
        app_form = forms.Form(schema=schema, request=self.request,
                              use_buefy=use_buefy)
        for key, value in six.iteritems(self.handler.get_defaults()):
            app_form.set_default(key, value)

        feature_forms = {}
        for feature in self.handler.iter_features():
            schema = feature.make_schema()
            form = forms.Form(schema=schema, request=self.request,
                              use_buefy=use_buefy)
            for key, value in six.iteritems(feature.get_defaults()):
                form.set_default(key, value)
            feature_forms[feature.feature_key] = form

        result = rendered_result = None
        feature_type = 'new-report'
        if self.request.method == 'POST':
            if app_form.validate(newstyle=True):

                feature_type = self.request.POST['feature_type']
                feature = self.handler.get_feature(feature_type)
                if not feature:
                    raise ValueError("Unknown feature type: {}".format(feature_type))

                feature_form = feature_forms[feature.feature_key]
                if feature_form.validate(newstyle=True):
                    context = dict(app_form.validated)
                    context.update(feature_form.validated)
                    result = self.handler.do_generate(feature, **context)
                    rendered_result = self.render_result(result)

        context = {
            'index_title': "Generate Feature",
            'handler': self.handler,
            'use_buefy': use_buefy,
            'app_form': app_form,
            'feature_type': feature_type,
            'feature_forms': feature_forms,
            'result': result,
            'rendered_result': rendered_result,
        }

        return context

    def render_result(self, result):
        return  markdown.markdown(result, extensions=['fenced_code',
                                                      'codehilite'])

    @classmethod
    def defaults(cls, config):

        # generate feature
        config.add_tailbone_permission('common', 'common.generate_feature',
                                       "Generate new feature source code")
        config.add_route('generate_feature', '/generate-feature')
        config.add_view(cls, route_name='generate_feature',
                        permission='common.generate_feature',
                        renderer='/generate_feature.mako')


def includeme(config):
    GenerateFeatureView.defaults(config)

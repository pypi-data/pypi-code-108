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
Tailbone Web API - "Common" Views
"""

from __future__ import unicode_literals, absolute_import

import rattail
from rattail.db import model
from rattail.mail import send_email
from rattail.util import OrderedDict

from cornice import Service

import tailbone
from tailbone import forms
from tailbone.forms.common import Feedback
from tailbone.api import APIView, api
from tailbone.db import Session


class CommonView(APIView):
    """
    Misc. "common" views for the API.

    .. attribute:: feedback_email_key

       This is the email key which will be used when sending "user feedback"
       email.  Default value is ``'user_feedback'``.
    """
    feedback_email_key = 'user_feedback'

    @api
    def about(self):
        """
        Generic view to show "about project" info page.
        """
        packages = self.get_packages()
        return {
            'project_title': self.get_project_title(),
            'project_version': self.get_project_version(),
            'packages': packages,
            'package_names': list(packages),
        }

    def get_project_title(self):
        return self.rattail_config.app_title(default="Tailbone")

    def get_project_version(self):
        import tailbone
        return tailbone.__version__

    def get_packages(self):
        """
        Should return the full set of packages which should be displayed on the
        'about' page.
        """
        return OrderedDict([
            ('rattail', rattail.__version__),
            ('Tailbone', tailbone.__version__),
        ])

    @api
    def feedback(self):
        """
        View to handle user feedback form submits.
        """
        # TODO: this logic was copied from tailbone.views.common and is largely
        # identical; perhaps should merge somehow?
        schema = Feedback().bind(session=Session())
        form = forms.Form(schema=schema, request=self.request)
        if form.validate(newstyle=True):
            data = dict(form.validated)

            # figure out who the sending user is, if any
            if self.request.user:
                data['user'] = self.request.user
            elif data['user']:
                data['user'] = Session.query(model.User).get(data['user'])

            # TODO: should provide URL to view user
            if data['user']:
                data['user_url'] = '#' # TODO: could get from config?

            data['client_ip'] = self.request.client_addr
            email_key = data['email_key'] or self.feedback_email_key
            send_email(self.rattail_config, email_key, data=data)
            return {'ok': True}

        return {'error': "Form did not validate!"}

    @classmethod
    def defaults(cls, config):
        cls._common_defaults(config)

    @classmethod
    def _common_defaults(cls, config):

        # about
        about = Service(name='about', path='/about')
        about.add_view('GET', 'about', klass=cls)
        config.add_cornice_service(about)

        # feedback
        feedback = Service(name='feedback', path='/feedback')
        feedback.add_view('POST', 'feedback', klass=cls,
                          permission='common.feedback')
        config.add_cornice_service(feedback)


def includeme(config):
    CommonView.defaults(config)

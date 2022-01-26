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
Base View Class
"""

from __future__ import unicode_literals, absolute_import

import os

import six

from rattail.db import model
from rattail.core import Object
from rattail.util import progress_loop

from pyramid import httpexceptions
from pyramid.renderers import render_to_response
from pyramid.response import FileResponse

from tailbone.db import Session
from tailbone.auth import logout_user
from tailbone.progress import SessionProgress
from tailbone.util import should_use_buefy
from tailbone.config import protected_usernames


class View(object):
    """
    Base class for all class-based views.
    """
    # quickie (search)
    expose_quickie_search = False

    def __init__(self, request, context=None):
        self.request = request

        # if user becomes inactive while logged in, log them out
        if getattr(request, 'user', None):
            # TODO: why is the user sometimes not attached to session?
            # (this has only been seen on mobile, when creating a new ordering batch)
            if request.user not in Session():
                request.user = Session.merge(request.user)
            if not request.user.active:
                headers = logout_user(request)
                raise self.redirect(request.route_url('home'))

        config = self.rattail_config
        if config:
            self.enum = config.get_enum()
            self.model = config.get_model()

    @property
    def rattail_config(self):
        """
        Reference to the effective Rattail config object.
        """
        return getattr(self.request, 'rattail_config', None)

    def get_rattail_app(self):
        """
        Returns the  Rattail ``AppHandler`` instance, creating it if necessary.
        """
        if not hasattr(self, 'rattail_app'):
            self.rattail_app = self.rattail_config.get_app()
        return self.rattail_app

    def forbidden(self):
        """
        Convenience method, to raise a HTTP 403 Forbidden exception.
        """
        return httpexceptions.HTTPForbidden()

    def notfound(self):
        return httpexceptions.HTTPNotFound()
    
    def get_use_buefy(self):
        """
        Returns a flag indicating whether or not the current theme supports
        (and therefore should use) the Buefy JS library.
        """
        return should_use_buefy(self.request)

    def late_login_user(self):
        """
        Returns the :class:`rattail:rattail.db.model.User` instance
        corresponding to the "late login" form data (if any), or ``None``.
        """
        if self.request.method == 'POST':
            uuid = self.request.POST.get('late-login-user')
            if uuid:
                return Session.query(model.User).get(uuid)

    def user_is_protected(self, user):
        """
        This logic will consult the settings for a list of "protected"
        usernames, which should require root privileges to edit.  If the given
        ``user`` object is represented in this list, it is considered to be
        protected and this method will return ``True``; otherwise it returns
        ``False``.
        """
        if not hasattr(self, 'protected_usernames'):
            self.protected_usernames = protected_usernames(self.rattail_config)
        if self.protected_usernames and user.username in self.protected_usernames:
            return True
        return False

    def redirect(self, url, **kwargs):
        """
        Convenience method to return a HTTP 302 response.
        """
        return httpexceptions.HTTPFound(location=url, **kwargs)

    def progress_loop(self, func, items, factory, *args, **kwargs):
        return progress_loop(func, items, factory, *args, **kwargs)

    def make_progress(self, key):
        """
        Create and return a :class:`tailbone.progress.SessionProgress`
        instance, with the given key.
        """
        return SessionProgress(self.request, key)

    # TODO: this signature seems wonky
    def render_progress(self, progress, kwargs, template=None):
        """
        Render the progress page, with given kwargs as context.
        """
        if not template:
            template = '/progress.mako'
        kwargs['progress'] = progress
        kwargs.setdefault('can_cancel', True)
        return render_to_response(template, kwargs, request=self.request)

    def json_response(self, data):
        """
        Convenience method to return a JSON response.
        """
        return render_to_response('json', data,
                                  request=self.request)

    def file_response(self, path, filename=None, attachment=True):
        """
        Returns a generic FileResponse from the given path
        """
        if not os.path.exists(path):
            return self.notfound()
        response = FileResponse(path, request=self.request)
        response.content_length = os.path.getsize(path)
        if attachment:
            if not filename:
                filename = os.path.basename(path)
                if six.PY2:
                    filename = filename.encode('ascii', 'replace')
            response.content_disposition = str('attachment; filename="{}"'.format(filename))
        return response

    def get_quickie_context(self):
        return Object(
            url=self.get_quickie_url(),
            perm=self.get_quickie_perm(),
            placeholder=self.get_quickie_placeholder())

    def get_quickie_url(self):
        raise NotImplementedError

    def get_quickie_perm(self):
        raise NotImplementedError

    def get_quickie_placeholder(self):
        pass

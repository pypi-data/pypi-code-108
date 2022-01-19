# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2022 Lance Edgar
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
Tailbone Web API - Auth Views
"""

from __future__ import unicode_literals, absolute_import

from rattail.db.auth import set_user_password

from cornice import Service

from tailbone.api import APIView, api
from tailbone.db import Session
from tailbone.auth import login_user, logout_user


class AuthenticationView(APIView):

    @api
    def check_session(self):
        """
        View to serve as "no-op" / ping action to check current user's session.
        This will establish a server-side web session for the user if none
        exists.  Note that this also resets the user's session timer.
        """
        data = {'ok': True}
        if self.request.user:
            data['user'] = self.get_user_info(self.request.user)

        data['permissions'] = list(self.request.tailbone_cached_permissions)

        # background color may be set per-request, by some apps
        if hasattr(self.request, 'background_color') and self.request.background_color:
            data['background_color'] = self.request.background_color
        else: # otherwise we use the one from config
            data['background_color'] = self.rattail_config.get(
                'tailbone', 'background_color')

        return data

    @api
    def login(self):
        """
        API login view.
        """
        if self.request.method == 'OPTIONS':
            return self.request.response

        username = self.request.json.get('username')
        password = self.request.json.get('password')
        if not (username and password):
            return {'error': "Invalid username or password"}

        # make sure credentials are valid
        user = self.authenticate_user(username, password)
        if not user:
            return {'error': "Invalid username or password"}

        # is there some reason this user should not login?
        error = self.why_cant_user_login(user)
        if error:
            return {'error': error}

        app = self.get_rattail_app()
        auth = app.get_auth_handler()

        login_user(self.request, user)
        return {
            'ok': True,
            'user': self.get_user_info(user),
            'permissions': list(auth.get_permissions(Session(), user)),
        }

    def authenticate_user(self, username, password):
        app = self.get_rattail_app()
        auth = app.get_auth_handler()
        return auth.authenticate_user(Session(), username, password)

    def why_cant_user_login(self, user):
        """
        This method is given a ``User`` instance, which represents someone who
        is just now trying to login, and has already cleared the basic hurdle
        of providing the correct credentials for a user on file.  This method
        is responsible then, for further verification that this user *should*
        in fact be allowed to login to this app node.  If the method determines
        a reason the user should *not* be allowed to login, then it should
        return that reason as a simple string.
        """

    @api
    def logout(self):
        """
        API logout view.
        """
        if self.request.method == 'OPTIONS':
            return self.request.response

        logout_user(self.request)
        return {'ok': True}

    @api
    def become_root(self):
        """
        Elevate the current request to 'root' for full system access.
        """
        if not self.request.is_admin:
            raise self.forbidden()
        self.request.user.record_event(self.enum.USER_EVENT_BECOME_ROOT)
        self.request.session['is_root'] = True
        return {
            'ok': True,
            'user': self.get_user_info(self.request.user),
        }

    @api
    def stop_root(self):
        """
        Lower the current request from 'root' back to normal access.
        """
        if not self.request.is_admin:
            raise self.forbidden()
        self.request.user.record_event(self.enum.USER_EVENT_STOP_ROOT)
        self.request.session['is_root'] = False
        return {
            'ok': True,
            'user': self.get_user_info(self.request.user),
        }

    @api
    def change_password(self):
        """
        View which allows a user to change their password.
        """
        if self.request.method == 'OPTIONS':
            return self.request.response

        if not self.request.user:
            raise self.forbidden()

        data = self.request.json_body

        # first make sure "current" password is accurate
        if not self.authenticate_user(self.request.user, data['current_password']):
            return {'error': "The current/old password you provided is incorrect"}

        # okay then, set new password
        set_user_password(self.request.user, data['new_password'])
        return {
            'ok': True,
            'user': self.get_user_info(self.request.user),
        }

    @classmethod
    def defaults(cls, config):
        cls._auth_defaults(config)

    @classmethod
    def _auth_defaults(cls, config):

        # session
        check_session = Service(name='check_session', path='/session')
        check_session.add_view('GET', 'check_session', klass=cls)
        config.add_cornice_service(check_session)

        # login
        login = Service(name='login', path='/login')
        login.add_view('POST', 'login', klass=cls)
        config.add_cornice_service(login)

        # logout
        logout = Service(name='logout', path='/logout')
        logout.add_view('POST', 'logout', klass=cls)
        config.add_cornice_service(logout)

        # become root
        become_root = Service(name='become_root', path='/become-root')
        become_root.add_view('POST', 'become_root', klass=cls)
        config.add_cornice_service(become_root)

        # stop root
        stop_root = Service(name='stop_root', path='/stop-root')
        stop_root.add_view('POST', 'stop_root', klass=cls)
        config.add_cornice_service(stop_root)

        # change password
        change_password = Service(name='change_password', path='/change-password')
        change_password.add_view('POST', 'change_password', klass=cls)
        config.add_cornice_service(change_password)


def includeme(config):
    AuthenticationView.defaults(config)

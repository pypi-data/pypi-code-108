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
Tailbone Web API - Core Views
"""

from __future__ import unicode_literals, absolute_import

from rattail.util import load_object

from tailbone.views import View


def api(view_meth):
    """
    Common decorator for all API views.  Ideally this would not be needed..but
    for now, alas, it is.
    """
    def wrapped(view, *args, **kwargs):

        # TODO: why doesn't this work here...? (instead we have to repeat this
        # code in lots of other places)
        # if view.request.method == 'OPTIONS':
        #     return view.request.response

        # invoke the view logic first, since presumably it may involve a
        # redirect in which case we don't really need to add the CSRF token.
        # main known use case for this is the /logout endpoint - if that gets
        # hit then the "current" (old) session will be destroyed, in which case
        # we can't use the token from that, but instead must generate a new one.
        result = view_meth(view, *args, **kwargs)

        # explicitly set CSRF token cookie, unless OPTIONS request 
        # TODO: why doesn't pyramid do this for us again?
        if view.request.method != 'OPTIONS':
            view.request.response.set_cookie(name='XSRF-TOKEN',
                                             value=view.request.session.get_csrf_token())

        return result

    return wrapped


class APIView(View):
    """
    Base class for all API views.
    """

    def pretty_datetime(self, dt):
        if not dt:
            return ""
        return dt.strftime('%Y-%m-%d @ %I:%M %p')

    def get_user_info(self, user):
        """
        This method is present on *all* API views, and is meant to provide a
        single means of obtaining "common" user info, for return to the caller.
        Such info may be returned in several places, e.g. upon login but also
        in the "check session" call, or e.g. as part of a broader return value
        from any other call.

        :returns: Dictionary of user info data, ready for JSON serialization. 

        Note that you should *not* (usually) override this method in any view,
        but instead configure a "supplemental" function which can then add or
        replace info entries.  Config for that looks like e.g.:

        .. code-block:: ini

           [tailbone.api]
           extra_user_info = poser.web.api.util:extra_user_info

        Note that the above config assumes a simple *function* defined in your
        ``util`` module; such a function would look like e.g.::

           def extra_user_info(request, user, **info):
               # add favorite color
               info['favorite_color'] = 'green'
               # override display name
               info['display_name'] = "TODO"
               # remove short_name
               info.pop('short_name', None)
               return info
        """
        # basic / default info
        is_admin = user.is_admin()
        employee = user.employee
        info = {
            'uuid': user.uuid,
            'username': user.username,
            'display_name': user.display_name,
            'short_name': user.get_short_name(),
            'is_admin': is_admin,
            'is_root': is_admin and self.request.session.get('is_root', False),
            'employee_uuid': employee.uuid if employee else None,
        }

        # maybe get/use "extra" info
        extra = self.rattail_config.get('tailbone.api', 'extra_user_info',
                                        usedb=False)
        if extra:
            extra = load_object(extra)
            info = extra(self.request, user, **info)

        return info

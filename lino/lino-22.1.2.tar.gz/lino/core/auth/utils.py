# Copyright 2011-2020 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

"""Utilities for authentication. Adapted from `django.contrib.auth`.

"""

from django.conf import settings
from django.utils.crypto import constant_time_compare
from django.utils.module_loading import import_string

from lino.utils import SimpleSingleton

class AnonymousUser(SimpleSingleton):
    """A singleton class whose instance will be assigned to the
    :attr:`user` attribute of anonymous incoming requests, similar to
    Django's approach.

    See also :attr:`lino.core.site.Site.anonymous_user_type`.

    """
    # authenticated = False

    is_authenticated = False
    """This is always `False`.
    See also :attr:`lino.modlib.users.User.is_authenticated`.
    """

    is_active = False

    email = None
    username = 'anonymous'
    modified = None
    partner = None
    language = None
    readonly = True
    pk = None
    id = None
    time_zone =  None
    notify_myself = False
    user_type = None
    is_anonymous = True

    def __init__(self):
        settings.SITE.startup()
        from lino.modlib.users.choicelists import UserTypes
        self.user_type = UserTypes.get_by_name(self.username, None)

    def __str__(self):
        return self.username

    def get_typed_instance(self, model):
        # 20131022 AttributeError at /api/outbox/MyOutbox : 'AnonymousUser'
        # object has no attribute 'get_typed_instance'
        return self

    def get_username(self):
        return self.username

    def get_preferences(self):
        """Return the preferences of this user. The returned object is a
        :class:`lino.core.userprefs.UserPrefs` object.

        """
        from lino.core import userprefs
        return userprefs.reg.get(self)

    def has_perm(self, perm, obj=None):
        return False

    def has_perms(self, perm_list, obj=None):
        for perm in perm_list:
            if not self.has_perm(perm, obj):
                return False
        return True

    def get_choices_text(self, request, actor, field):
        return str(self)


def activate_social_auth_testing(globals_dict, has_google=False):
    """
    Used for testing a development server.
    See for example the :xfile:`settings.py` of :mod:`lino_book.projects.noi1e`.

    """
    Site = globals_dict['Site']

    Site.social_auth_backends = [
        'social_core.backends.github.GithubOAuth2',
        # 'social_core.backends.google.GoogleOAuth2',
        # 'social_core.backends.google.GoogleOAuth',
        'social_core.backends.facebook.FacebookOAuth2',
        'social_core.backends.mediawiki.MediaWiki'
    ]
    if not has_google:
        Site.social_auth_backends.append('social_core.backends.google.GooglePlusAuth')

    globals_dict.update(
        # https://github.com/organizations/lino-framework/settings/applications/632218
        SOCIAL_AUTH_GITHUB_KEY = '355f66b1557f0cbf4d1d',
        SOCIAL_AUTH_GITHUB_SECRET = '4dbeea1701bf03316c1759bdb422d9f88969b782',

        SOCIAL_AUTH_FACEBOOK_KEY = '1837593149865295',
        SOCIAL_AUTH_FACEBOOK_SECRET = '1973f9e9d9420c4c6502aa40cb8cb7db',
        SOCIAL_AUTH_FACEBOOK_SCOPE = ['email', 'public_profile', 'user_friends'],

        SOCIAL_AUTH_MEDIAWIKI_KEY = '7dbd2e1529e45108f798349811c7a2b7',
        SOCIAL_AUTH_MEDIAWIKI_SECRET = '8041055fcd16333fa242b346e0ae52133fd2ee14',
        SOCIAL_AUTH_MEDIAWIKI_URL = 'https://meta.wikimedia.org/w/index.php',
        SOCIAL_AUTH_MEDIAWIKI_CALLBACK = 'oob'
        )

    if not has_google:
        globals_dict.update(
            SOCIAL_AUTH_GOOGLE_PLUS_KEY = '451271712409-9qtm9bvjndaeep2olk3useu61j6qu2kp.apps.googleusercontent.com',
            SOCIAL_AUTH_GOOGLE_PLUS_SECRET = 'NHyaqV2HY8lV5ULG6k51OMwo',
            SOCIAL_AUTH_GOOGLE_PLUS_SCOPE = [
                'profile',
                'https://www.googleapis.com/auth/plus.login',
                'https://www.googleapis.com/auth/contacts.readonly', # To have just READ permission
                'https://www.googleapis.com/auth/contacts ', # To have WRITE/READ permissions
            ]
        )

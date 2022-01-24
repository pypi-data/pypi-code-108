# Copyright 2008-2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

import json
from pathlib import Path

from lino.api import ad, _
# from lino_xl.lib.contacts import Plugin
# from lino.modlib.users import Plugin


class Plugin(ad.Plugin):
    "See :class:`lino.core.plugin.Plugin`."

    verbose_name = _("Google API")
    # partner_model = 'google.Person'
    # extends_models = ['Person']

    needs_plugins = ['lino.modlib.users']

    ## settings

    backend = 'lino_xl.lib.google.backend.LinoGoogleOAuth2'

    client_secret_file = str(Path.home()) + '/lino/client_secret.json'
    """The `path` to the GoogleAPI secret file client_secret.json."""
    scopes = [
        'https://www.googleapis.com/auth/userinfo.profile',
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/contacts',
        'https://www.googleapis.com/auth/user.addresses.read',
        'https://www.googleapis.com/auth/user.birthday.read',
        'https://www.googleapis.com/auth/user.gender.read',
        'https://www.googleapis.com/auth/user.phonenumbers.read',
        'https://www.googleapis.com/auth/calendar',
        'https://www.googleapis.com/auth/calendar.events'
    ]
    """ GoogleAPi Scopes

    After modifying these scopes, delete all database entry for this provider
    and reauthenticate.

    """
    application_name = "LinoOAuthClient"
    """ The Application's name defined in the google API Console"""

    @classmethod
    def setup_site_features(self, feats):
        feats.activate('third_party_authentication', priority=1000)

    def on_init(self):
        super().on_init()
        if not self.has_feature('third_party_authentication'):
            return
        from lino.core.site import has_socialauth
        if has_socialauth:
            self.needs_plugins.append('social_django')
            try:
                with open(self.client_secret_file) as f:
                    client_secret = json.load(f)
                self.site.update_settings(
                    SOCIAL_AUTH_GOOGLE_KEY=client_secret['web']['client_id'],
                    SOCIAL_AUTH_GOOGLE_SECRET=client_secret['web']['client_secret'],
                    SOCIAL_AUTH_GOOGLE_SCOPE=self.scopes,
                    SOCIAL_AUTH_GOOGLE_USE_UNIQUE_USER_ID = True,
                    SOCIAL_AUTH_GOOGLE_AUTH_EXTRA_ARGUMENTS = {
                        'access_type': 'offline',
                        'include_granted_scopes':'true',
                        'prompt': 'select_account'
                    },
                    SOCIAL_AUTH_GOOGLE_PIPELINE = (
                        'social_core.pipeline.social_auth.social_details',
                        'social_core.pipeline.social_auth.social_uid',
                        'social_core.pipeline.social_auth.auth_allowed',
                        'social_core.pipeline.social_auth.social_user',
                        'social_core.pipeline.user.get_username',
                        # 'social_core.pipeline.mail.mail_validation',
                        # 'social_core.pipeline.social_auth.associate_by_email',
                        'social_core.pipeline.user.create_user',
                        'social_core.pipeline.social_auth.associate_user',
                        'lino_xl.lib.google.pipeline.intercept_extra_data',
                        'social_core.pipeline.social_auth.load_extra_data',
                        'social_core.pipeline.user.user_details'
                    )
                )
                self.site.social_auth_backends.append(self.backend)
            except FileNotFoundError:
                # print("Please make sure to provide OAuth client credentials",
                #     "accessable from google. Look at the following link for help:",
                #     "https://support.google.com/cloud/answer/6158849?hl=en")
                pass

    def get_requirements(self, site):
        yield "social-auth-app-django"
        yield "google-api-python-client"
        yield "google-auth"
        yield "google-auth-httplib2"
        yield "google-auth-oauthlib"

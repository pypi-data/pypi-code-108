# Copyright 2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from social_core.backends.google import GoogleOAuth2

class LinoGoogleOAuth2(GoogleOAuth2):
    name = "google"
    EXTRA_DATA = [
        ('id_token', 'id_token'),
        ('expires_in', 'expires_in'),
        ('expiry', 'expiry'),
        ('token_type', 'token_type'),
        ('access_token', 'access_token'),
        ('refresh_token', 'refresh_token'),
        ('rapt_token', 'rapt_token'),
        ('scope', 'scopes')
    ]

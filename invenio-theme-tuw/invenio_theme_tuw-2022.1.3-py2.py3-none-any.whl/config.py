# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 - 2021 TU Wien.
#
# Invenio-Theme-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""TU Wien theme for Invenio (RDM)."""

THEME_TUW_MATOMO_ENABLED = True
"""Controls whether or not to include the JS snippet for Matomo in the base template."""

THEME_TUW_MATOMO_URL = "https://s191.dl.hpc.tuwien.ac.at/"
"""The URL under which Matomo is reachable."""

THEME_TUW_DISPLAY_STAGING_WARNING = False
"""Whether or not to display a warning that it's the staging system."""

APP_THEME = ["semantic-ui"]


# Invenio-Theme
# =============
# See https://invenio-theme.readthedocs.io/en/latest/configuration.html

# Name displayed in tab
THEME_SITENAME = "TU Wien Research Data"

# Frontpage
THEME_FRONTPAGE = True

# Templates
BASE_TEMPLATE = "invenio_theme_tuw/page.html"
THEME_FRONTPAGE_TEMPLATE = "invenio_theme_tuw/frontpage.html"
THEME_HEADER_TEMPLATE = "invenio_theme_tuw/header.html"
THEME_FOOTER_TEMPLATE = "invenio_theme_tuw/footer.html"
THEME_JAVASCRIPT_TEMPLATE = "invenio_theme_tuw/javascript.html"
THEME_ERROR_TEMPLATE = "invenio_theme_tuw/page_error.html"

# Header logo
THEME_LOGO = "images/TU_Signet_white.png"
INSTANCE_THEME_FILE = "less/invenio_theme_tuw/theme.less"

# Override the Invenio-OAuthClient login form
OAUTHCLIENT_SIGNUP_TEMPLATE = "invenio_theme_tuw/login/signup.html"
OAUTHCLIENT_LOGIN_USER_TEMPLATE = "invenio_theme_tuw/login/login_user.html"
ACCOUNTS_COVER_TEMPLATE = "invenio_theme_tuw/login/page_cover.html"

# User profile page
USERPROFILES_PROFILE_TEMPLATE = "invenio_theme_tuw/settings/profile.html"


# Flask-WebpackExt
# ================
# See https://flask-webpackext.readthedocs.io/en/latest/configuration.html

WEBPACKEXT_PROJECT = "invenio_theme_tuw.webpack:project"

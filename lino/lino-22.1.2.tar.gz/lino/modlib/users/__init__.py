# Copyright 2011-2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

"""
Implements functionality for managing users.  See
:doc:`/specs/users` and :doc:`/dev/users`

Submodules:

.. autosummary::
   :toctree:

    utils
"""


from lino.api import ad, _


class Plugin(ad.Plugin):
    verbose_name = _("Users")
    needs_plugins = ['lino.modlib.system']
    # online_registration = False
    active_sessions_limit = -1

    allow_online_registration = False
    """Whether to allow users to register online."""
    verification_code_expires = 5
    """
    This value is in minutes. Used to invalidate a user verification code after
    the elapsed minutes.
    """
    user_type_new = 'user'
    """The default user_type for an unverified user."""
    user_type_verified = 'user'
    """The default user_type for a verified user."""

    my_setting_text = _("My settings")

    # partner_model = 'contacts.Person'
    partner_model = 'contacts.Partner'

    @classmethod
    def setup_site_features(self, feats):
        feats.define_feature(
            'third_party_authentication',
            _("Whether to allow login using credentials from third party"))

    def on_site_startup(self, site):
        super(Plugin, self).on_site_startup(site)
        # if isinstance(self.partner_model, str):
        #     if not site.is_installed_model_spec(self.partner_model):
        #         self.partner_model = None
        #         return
        self.partner_model = site.models.resolve(self.partner_model)

    def unused_on_plugins_loaded(self, site):
        if self.allow_online_registration:
            # If you use gmail smtp to send email.
            # See: https://support.google.com/mail/answer/7126229?visit_id=1-636656345878819046-1400238651&rd=1#cantsignin&zippy=%2Ci-cant-sign-in-to-my-email-client
            # For this setup you will have to allow less secure app access from
            # your google accounts settings: https://myaccount.google.com/lesssecureapps
            site.update_settings(
                EMAIL_HOST='smtp.gmail.com',
                EMAIL_PORT=587, # For TLS | use 465 for SSL
                EMAIL_HOST_USER='username@gmail.com',
                EMAIL_HOST_PASSWORD='*********',
                EMAIL_USE_TLS=True
            )

    def on_init(self):
        super(Plugin, self).on_init()
        self.site.set_user_model('users.User')
        from lino.core.site import has_socialauth
        if self.has_feature('third_party_authentication') and has_socialauth:
            self.needs_plugins.append('social_django')

    def setup_config_menu(self, site, user_type, m):
        g = site.plugins.system
        m = m.add_menu(g.app_label, g.verbose_name)
        m.add_action('users.AllUsers')

    def setup_explorer_menu(self, site, user_type, m):
        g = site.plugins.system
        m = m.add_menu(g.app_label, g.verbose_name)
        m.add_action('users.Authorities')
        m.add_action('users.UserTypes')
        m.add_action('users.UserRoles')
        if site.has_feature('third_party_authentication'):
            m.add_action('users.SocialAuths')

    def setup_site_menu(self, site, user_type, m):
        m.add_action('users.Sessions')

    def get_quicklinks(self):
        # yield "users.Me"
        yield "users.Me.my_settings"
        # yield dict(instance=user,
        #     action='users.MySettings',
        #     label=_("My settings"))

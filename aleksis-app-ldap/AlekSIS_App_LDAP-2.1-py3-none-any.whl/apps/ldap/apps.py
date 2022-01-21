from allauth.account.signals import password_changed, password_reset, password_set, user_signed_up

from aleksis.core.util.apps import AppConfig

from .util.ldap_password import ldap_change_password
from .util.ldap_sync import ldap_create_user, ldap_sync_user_on_login, update_dynamic_preferences


class LDAPConfig(AppConfig):
    name = "aleksis.apps.ldap"
    verbose_name = "AlekSIS — LDAP (General LDAP import/export)"

    urls = {
        "Repository": "https://edugit.org/AlekSIS/official/AlekSIS-App-LDAP/",
    }
    licence = "EUPL-1.2+"
    copyright_info = (
        ([2020, 2021, 2022], "Dominik George", "dominik.george@teckids.org"),
        ([2020], "Tom Teichler", "tom.teichler@teckids.org"),
    )

    def ready(self) -> None:
        super().ready()

        update_dynamic_preferences()

        password_changed.connect(ldap_change_password)
        password_reset.connect(ldap_change_password)
        password_set.connect(ldap_change_password)

        user_signed_up.connect(ldap_create_user)

        from django_auth_ldap.backend import populate_user  # noqa

        populate_user.connect(ldap_sync_user_on_login)

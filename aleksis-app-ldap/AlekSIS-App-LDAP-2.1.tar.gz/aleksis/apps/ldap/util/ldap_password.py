from aleksis.core.util.core_helpers import get_site_preferences

from .ldap import TemporaryBind


def ldap_change_password(request, user, **kwargs):
    enable_password_change = get_site_preferences()["ldap__enable_password_change"]
    admin_password_change = get_site_preferences()["ldap__admin_password_change"]
    admin_dn = get_site_preferences()["ldap__admin_dn"]
    admin_password = get_site_preferences()["ldap__admin_password"]

    if not enable_password_change:
        # Do nothing if password change in LDAP is disabled
        return

    if not hasattr(user, "ldap_user"):
        # Add ldap_user relation to user if not available yet
        # This can happen on password reset, when the user is acted upon
        # but was never logged-in
        from django_auth_ldap.backend import LDAPBackend, _LDAPUser  # noqa

        user.ldap_user = _LDAPUser(LDAPBackend(), user=user)

    if not user.ldap_user.dn:
        # The user is not linked to an LDAP user, so we do not handle the password change
        return

    # Get old and new password from submitted form
    # We rely on allauth already having validated the form before emitting the signal
    old = request.POST.get("oldpassword", None)
    new = request.POST["password1"]

    # Determine as which user to make the password change
    if old and not admin_password_change:
        # If we are changing a password as user, use their credentials
        # except if the preference mandates always using admin credentials
        bind_dn, password = user.ldap_user.dn, old
    elif admin_dn:
        # In all other cases, use admin credentials if available
        bind_dn, password = admin_dn, admin_password
    else:
        # If not available, try using the regular LDAP auth credentials
        bind_dn, password = None, None

    with TemporaryBind(user.ldap_user, bind_dn, password) as conn:
        conn.passwd_s(user.ldap_user.dn, old, new)

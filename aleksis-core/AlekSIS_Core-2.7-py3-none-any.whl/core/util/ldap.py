"""Utilities and extensions for django_auth_ldap."""

from django.core.exceptions import PermissionDenied

from django_auth_ldap.backend import LDAPBackend as _LDAPBackend

from ..models import UserAdditionalAttributes


class LDAPBackend(_LDAPBackend):
    default_settings = {"SET_USABLE_PASSWORD": False}

    def authenticate_ldap_user(self, ldap_user, password):
        """Authenticate user against LDAP and set local password if successful.

        Having a local password is needed to make changing passwords easier. In
        order to catch password changes in a universal way and forward them to
        backends (like LDAP, in this case), getting the old password first is
        necessary to authenticate as that user to LDAP.

        We buy the small insecurity of having a hash of the password in the
        Django database in order to not require it to have global admin permissions
        on the LDAP directory.
        """
        user = super().authenticate_ldap_user(ldap_user, password)

        if self.settings.SET_USABLE_PASSWORD:
            if not user:
                # The user could not be authenticated against LDAP.
                # We need to make sure to let other backends handle it, but also that
                # we do not let actually deleted/locked LDAP users fall through to a
                # backend that cached a valid password
                if UserAdditionalAttributes.get_user_attribute(
                    ldap_user._username, "ldap_authenticated", False
                ):
                    # User was LDAP-authenticated in the past, so we fail authentication now
                    # to not let other backends override a legitimate deletion
                    raise PermissionDenied("LDAP failed to authenticate user")
                else:
                    # No note about LDAP authentication in the past
                    # The user can continue authentication like before if they exist
                    return user

            # Set a usable password so users can change their LDAP password
            user.set_password(password)
            user.save()

            # Not that we LDAP-autenticated the user so we can check this in the future
            UserAdditionalAttributes.set_user_attribute(
                ldap_user._username, "ldap_authenticated", True
            )

        return user

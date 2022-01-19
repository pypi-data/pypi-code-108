from django.conf import settings
from psu_base.classes.User import User
from psu_base.classes.Log import Log
from psu_base.services import utility_service, message_service

log = Log()


class Auth:
    sso_user = None
    impersonated_user = None
    proxied_user = None

    def is_logged_in(self):
        logged_in = self.sso_user is not None and self.sso_user.is_valid()
        return logged_in

    def is_impersonating(self):
        return self.impersonated_user is not None and self.impersonated_user.is_valid()

    def is_proxying(self):
        return self.proxied_user is not None and self.proxied_user.is_valid()

    def get_user(self):
        """
        Get the appropriate user identity.
            Use impersonated identity when impersonating
            Use SSO identity when not impersonating
        """
        if self.is_impersonating():
            return self.impersonated_user
        else:
            return self.sso_user

    def has_authority(self, authority_code, sso_user_only=False, require_global=False):
        """
        Determine if the current user has an authority.
        In non-production, a user may impersonate a user with elevated permissions (for testing)
        In production, impersonate feature may be needed to debug an issue, but should not grant elevated permissions
        In all environments, access will be lowered to the impersonated user's access level

        Note: Global authorities are included in app authorities, and do not need to be checked unless
              specifically looking for GLOBAL access
        """
        # If not logged in, the user has no authorities
        if not self.is_logged_in():
            return False

        allowed = False

        # SSO and Impersonated users must be evaluated
        sso_has_it = self.sso_user.has_authority(authority_code, require_global)
        if self.is_impersonating() and not sso_user_only:
            impersonated_has_it = self.impersonated_user.has_authority(
                authority_code, require_global
            )
        else:
            impersonated_has_it = False

        # Being a developer can have an impact on access
        sso_is_developer = self.sso_user.has_authority("developer")

        # If not impersonating, or if sso_user_only=True, only look at the sso_user
        if sso_user_only or not self.is_impersonating():
            allowed = sso_has_it

            # In non-prod, developers get full access
            if (
                (not allowed)
                and sso_is_developer
                and utility_service.is_non_production()
            ):
                # Just in case it is someday desired, allow a way to disable the elevated access for developers
                if (
                    hasattr(settings, "ELEVATE_DEVELOPER_ACCESS")
                    and not settings.ELEVATE_DEVELOPER_ACCESS
                ):
                    log.debug(f"Elevated developer access DISABLED")
                else:
                    allowed = True

        # In non-prod, allow elevated permissions via impersonation (for testing)
        elif utility_service.is_non_production():
            allowed = impersonated_has_it

        # In production, only allow if SSO user also has it
        else:
            allowed = sso_has_it and impersonated_has_it

        # log.summary(
        #     allowed,
        #     [
        #         authority_code,
        #         self.sso_user if sso_user_only else self.get_user(),
        #         'GLOBAL' if require_global else utility_service.get_app_code()
        #     ]
        # )
        return allowed

    def can_impersonate(self):
        """
        The impersonate feature is slightly different than other authorities because it is
        environment-specific (prod/non-prod).
        Also, the SSO user retains the authority when impersonating someone who does not
        have it, which allows the SSO user to terminate the impersonation, or choose another.
        """
        return self.has_authority("~impersonate", True)

    def start_impersonating(self, user_info):
        log.trace([user_info])
        failure = False

        # Clear any existing impersonation
        self.stop_impersonating()

        if user_info and str(user_info) not in ["", "0", "None"]:
            # Look up the given user
            self.impersonated_user = User(user_info, as_proxy=True, allow_gravatar=True)
            # If SSO user requested to self-impersonate, just remove the impersonation
            if self.impersonated_user.equals(self.sso_user):
                log.info("Removing self-impersonation request")
                self.stop_impersonating()
            # If lookup failed, remove impersonation
            elif (
                self.impersonated_user is None or not self.impersonated_user.is_valid()
            ):
                message_service.post_error("Unable to locate the specified person")
                self.impersonated_user = None
                failure = True

        # Save changes to auth object
        self.save()

        # Indicate success or failure
        return not failure

    def stop_impersonating(self):
        self.impersonated_user = None
        self.save()
        # ToDo: Should probably invalidate the session

    def set_proxy(self, user_info):
        # Clear any existing proxy
        self.remove_proxy()
        # Look up the given user
        self.proxied_user = User(user_info, as_proxy=True)
        # If lookup failed, remove proxy
        if self.proxied_user is None or not self.proxied_user.is_valid():
            message_service.post_error("Unable to locate the specified person")
            self.proxied_user = None
            return False
        self.save()
        return True

    def remove_proxy(self):
        self.proxied_user = None
        self.save()

    def save(self):
        utility_service.set_session_var(
            self.session_var(), self.to_dict() if self.is_logged_in() else None
        )

    #
    # @staticmethod
    # def reset_session(**kwargs):
    #     session = utility_service.get_session()
    #     # Back-up the session values not to be removed
    #     holder = {}
    #     for kk in [
    #         'next', 'next_impersonate', 'next_proxy'
    #     ]:
    #         holder[kk] = session.get(kk)
    #
    #     # Clear the session
    #     session.clear()
    #
    #     # Restore the backed-up values
    #     for kk, vv in holder.items():
    #         session[kk] = vv
    #     del holder

    @staticmethod
    def session_var():
        return "psu_base_auth_object"

    def __init__(self, from_sso=None, auto_resume=False, app_change=False):
        # Resume from session
        if auto_resume or app_change:
            saved = utility_service.get_session_var(self.session_var())
            if saved and not app_change:
                self.sso_user = User(saved["sso_user"])
                self.impersonated_user = User(saved["impersonated_user"])
                self.proxied_user = User(saved["proxied_user"], as_proxy=True)
            elif saved:
                sso_username = (
                    saved["sso_user"].get("username") if saved["sso_user"] else None
                )
                imp_username = (
                    saved["impersonated_user"].get("username")
                    if saved["impersonated_user"]
                    else None
                )
                prx_username = (
                    saved["proxied_user"].get("username")
                    if saved["proxied_user"]
                    else None
                )
                self.sso_user = User(sso_username)
                self.impersonated_user = User(imp_username)
                self.proxied_user = User(prx_username, as_proxy=True)

        # New from SSO
        elif from_sso:
            log.trace([from_sso, auto_resume])

            # New from SSO (no proxies selected yet)
            self.sso_user = User(from_sso, allow_gravatar=True)
            # If identity lookup failed
            if not self.sso_user.is_valid():
                self.sso_user = None
                log.error(f"Unable to locate identity for '{from_sso}'")
                self.sso_user = User(None)
                self.sso_user.display_name = "Anonymous"
                if str(from_sso).endswith("-high"):
                    message_service.post_error(
                        "You must log in with your Odin account, not your High account."
                    )

        # Empty auth object (i.e. not logged in)
        else:
            pass

        # Having an sso_user == None is annoying ('NoneType' object has no attribute <whatever>)
        if not self.is_logged_in():
            self.sso_user = User(None)
            self.sso_user.display_name = "Anonymous"

    def __repr__(self):
        if self.is_impersonating():
            return f"{self.sso_user} as {self.impersonated_user.username}"
        elif self.is_logged_in():
            return str(self.sso_user)
        else:
            return "<Anonymous User>"

    def to_dict(self):
        return {
            "sso_user": self.sso_user.to_dict() if self.sso_user else None,
            "impersonated_user": self.impersonated_user.to_dict()
            if self.impersonated_user
            else None,
            "proxied_user": self.proxied_user.to_dict() if self.proxied_user else None,
        }

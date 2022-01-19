from psu_base.classes.Finti import Finti
from psu_base.classes.Log import Log
from psu_base.services import utility_service
from psu_base.classes.DynamicRole import DynamicRole

log = Log()


class User:
    first_name = None
    last_name = None
    display_name = None
    username = None
    psu_id = None
    uuid = None
    email_address = None
    primary_role = None
    roles = None
    pidm = None
    authorities = None
    global_authorities = None
    id_photo = None
    proxy = None

    # Preferred name added in Sep 2021, and does not exist in SSO attributes - only in Finti response
    pref_first_name = None
    pref_last_name = None
    override_name = None
    legal_first_name = None
    legal_last_name = None

    def is_valid(self):
        return self.email_address is not None

    def is_provisional(self):
        return self.username.contains("@")

    def has_authority(self, authority_code, require_global=False):
        has_it = False
        if authority_code:
            if require_global:
                authorities = self.global_authorities
            else:
                authorities = self.authorities

            # If a single code was given, put it in a list
            if type(authority_code) is not list:
                authority_code = [authority_code] if authority_code else []

            # If a dynamic role was given, expand it out to the full role list
            role_list = []
            for code in authority_code:
                code = str(code)
                if code.startswith("~") or code.upper().startswith("DYNAMIC"):
                    role_list.extend(DynamicRole().decode(code))
                else:
                    role_list.append(code)

            for code in list(set(role_list)):
                if authorities and code in authorities:
                    has_it = True
        return has_it

    @property
    def preferred_first_name(self):
        # if self.override_name:
        #     return self.override_name
        if self.pref_first_name:
            return self.pref_first_name
        elif self.legal_first_name:
            return self.legal_first_name
        else:
            return self.first_name

    @property
    def preferred_last_name(self):
        if self.pref_last_name:
            return self.pref_last_name
        elif self.legal_last_name:
            return self.legal_last_name
        else:
            return self.last_name

    def __init__(self, src, as_proxy=False, allow_gravatar=False, get_authorities=True):
        # If given a dict (created from a User object)
        if type(src) is dict and "first_name" in src:
            self.first_name = src["first_name"]
            self.last_name = src["last_name"]
            self.display_name = src["display_name"]
            self.username = src["username"]
            self.psu_id = src["psu_id"]
            self.uuid = src["uuid"]
            self.email_address = src["email_address"]
            self.primary_role = src["primary_role"]
            self.roles = src["roles"]
            self.pidm = src["pidm"]
            self.authorities = src.get("authorities")
            self.global_authorities = src.get("global_authorities")
            self.id_photo = src.get("id_photo")
            self.proxy = as_proxy
            # Preferred names:
            self.pref_first_name = src.get("pref_first_name")
            self.pref_last_name = src.get("pref_last_name")
            self.override_name = src.get("override_name")
            self.legal_first_name = src.get("legal_first_name", self.first_name)
            self.legal_last_name = src.get("legal_last_name", self.last_name)

        # If given dict of SSO data (via Finti)
        # Example usage: Bulk processing of identity search results
        elif type(src) is dict and "given_name" in src:
            self.first_name = src["given_name"]
            self.last_name = src["sn"]
            self.display_name = f"{self.first_name} {self.last_name}".strip()
            self.uuid = src["psuuuid"]
            self.pidm = src["pidm"]
            if "employeeNumber" in src:
                self.psu_id = src["employeeNumber"]
            self.username = src["uid"]
            self.email_address = src["mail"]

            self.primary_role = src["eduPersonPrimaryAffiliation"]
            self.roles = []
            role_string = src.get("eduPersonScopedAffiliation")
            if role_string:
                if "," in role_string:
                    role_list = role_string.split(",")
                    self.roles = [rr.replace("@pdx.edu", "") for rr in role_list]
                elif ":" in role_string:
                    role_list = role_string.split(":")
                    self.roles = [rr.lower() for rr in role_list]
                else:
                    self.roles = [role_string.lower()]

            # Authorities
            if get_authorities:
                self.authorities = Finti(reduce_logging=True).get(
                    "wdt/v1/sso_proxy/auth/permissions/",
                    {"username": self.username, "app": utility_service.get_app_code()},
                )
            # Initialize an empty list when no authorities were found
            if not self.authorities:
                self.authorities = []

            # GLOBAL Authorities
            if get_authorities:
                self.global_authorities = Finti(reduce_logging=True).get(
                    "wdt/v1/sso_proxy/auth/permissions/",
                    {"username": self.username, "app": "GLOBAL"},
                )
            # Initialize an empty list when no global_authorities were found
            if not self.global_authorities:
                self.global_authorities = []

            # Photo
            if "photo" in src:
                self.id_photo = src.get("photo")
            else:
                # ToDo: Get ID photo from Finti?
                pass

            # Preferred names:
            self.pref_first_name = src.get("pref_first_name")
            self.pref_last_name = src.get("pref_last_name")
            self.override_name = src.get("override_name")
            self.legal_first_name = src.get("legal_first_name", self.first_name)
            self.legal_last_name = src.get("legal_last_name", self.last_name)

        # If given a User object
        elif type(src) is User:
            self.first_name = src.first_name
            self.last_name = src.last_name
            self.display_name = src.display_name
            self.username = src.username
            self.psu_id = src.psu_id
            self.uuid = src.uuid
            self.email_address = src.email_address
            self.primary_role = src.primary_role
            self.roles = src.roles
            self.pidm = src.pidm
            self.authorities = src.authorities
            self.global_authorities = src.global_authorities
            self.id_photo = src.id_photo
            self.proxy = src.proxy
            # Preferred names:
            self.pref_first_name = src.pref_first_name
            self.pref_last_name = src.pref_last_name
            self.override_name = src.override_name
            self.legal_first_name = src.legal_first_name or self.first_name
            self.legal_last_name = src.legal_last_name or self.last_name

        # If given an identifier (username, pidm, psu_id, uuid)
        elif src:
            log.trace([src])
            user_data = str(src)
            sso_dict = Finti(reduce_logging=True).get(
                "wdt/v1/sso_proxy/auth/identity/" + user_data
            )

            if type(sso_dict) is dict and (sso_dict.get("uid") or sso_dict.get("psuuuid")):
                # Email address
                self.email_address = sso_dict["mail"] if "mail" in sso_dict else None
                self.clean_address()

                # Name
                self.first_name = (
                    sso_dict["given_name"] if "given_name" in sso_dict else None
                )
                self.last_name = sso_dict["sn"] if "sn" in sso_dict else None
                if "display_name" in sso_dict and sso_dict["display_name"]:
                    self.display_name = sso_dict["display_name"]
                else:
                    self.display_name = f"{self.first_name} {self.last_name}".strip()

                # Preferred names:
                self.pref_first_name = sso_dict.get("pref_first_name")
                self.pref_last_name = sso_dict.get("pref_last_name")
                self.override_name = sso_dict.get("override_name")
                self.legal_first_name = sso_dict.get("legal_first_name", self.first_name)
                self.legal_last_name = sso_dict.get("legal_last_name", self.last_name)

                # Identifiers
                self.uuid = sso_dict["psuuuid"] if "psuuuid" in sso_dict else None
                self.psu_id = (
                    sso_dict["employeeNumber"] if "employeeNumber" in sso_dict else None
                )
                self.username = sso_dict["uid"] if "uid" in sso_dict else None
                self.pidm = sso_dict["pidm"] if "pidm" in sso_dict else None

                # Role(s)
                self.primary_role = sso_dict.get("eduPersonPrimaryAffiliation")
                self.roles = []
                role_string = sso_dict.get("eduPersonScopedAffiliation")
                if role_string:
                    if "," in role_string:
                        role_list = role_string.split(",")
                        self.roles = [rr.replace("@pdx.edu", "") for rr in role_list]
                    elif ":" in role_string:
                        role_list = role_string.split(":")
                        self.roles = [rr.lower() for rr in role_list]
                    else:
                        self.roles = [role_string.lower()]

                # Authorities
                if get_authorities:
                    self.authorities = Finti(reduce_logging=True).get(
                        "wdt/v1/sso_proxy/auth/permissions/",
                        {
                            "username": self.username,
                            "app": utility_service.get_app_code(),
                        },
                    )
                # Initialize an empty list when no authorities were found
                if not self.authorities:
                    self.authorities = []

                # GLOBAL Authorities
                if get_authorities:
                    self.global_authorities = Finti(reduce_logging=True).get(
                        "wdt/v1/sso_proxy/auth/permissions/",
                        {"username": self.username, "app": "GLOBAL"},
                    )
                # Initialize an empty list when no global_authorities were found
                if not self.global_authorities:
                    self.global_authorities = []

                # ID Photo (not always available)
                if "photo" in sso_dict:
                    self.id_photo = sso_dict.get("photo")

                # If Gravatar image is available, use that instead of ID photo
                if allow_gravatar:
                    gravatar = utility_service.get_gravatar_image_src(
                        self.email_address
                    )
                    if gravatar:
                        self.id_photo = gravatar

        # Recently started seeing a bunch of new students in this state
        # (Has valid pdx.edu address in zgbidmp, but not in goremal)
        if self.username and not self.email_address:
            if "@" not in self.username and "-high" not in self.username:
                self.email_address = f"{self.username}@pdx.edu"

        # Use preferred names or legal names by default?
        use_preferred = utility_service.get_setting('USE_PREFERRED_NAMES', False)
        if use_preferred:
            self.display_name = f"{self.preferred_first_name} {self.preferred_last_name}".strip()

    def clean_address(self):
        if self.email_address and "@gdev.pdx.edu" in self.email_address:
            self.email_address = self.email_address.replace("@gdev.", "@")
        if self.email_address and "@gtest.pdx.edu" in self.email_address:
            self.email_address = self.email_address.replace("@gtest.", "@")
        if self.email_address:
            self.email_address = self.email_address.strip()

    def equals(self, identifier):
        """Does the given identifier match this identity"""
        # If nothing provided, cannot be the same
        if identifier is None:
            return False
        # If this user is invalid, cannot be equal
        if not self.is_valid():
            return False
        # If a dict representation of this class was provided
        elif type(identifier) is dict and "username" in identifier:
            return self.equals(identifier["username"])
        # Otherwise, check each possible identifier
        elif self.username and self.username.lower() == str(identifier).lower():
            return True
        elif self.psu_id == str(identifier):
            return True
        elif self.uuid == str(identifier):
            return True
        elif self.email_address.lower() == str(identifier).lower():
            return True
        elif self.pidm == str(identifier):
            return True
        else:
            return False

    def __repr__(self):
        return f"<{self.username}: {self.display_name}>"

    def to_dict(self):
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "display_name": self.display_name,
            "username": self.username,
            "psu_id": self.psu_id,
            "uuid": self.uuid,
            "email_address": self.email_address,
            "primary_role": self.primary_role,
            "roles": self.roles,
            "pidm": self.pidm,
            "authorities": self.authorities,
            "global_authorities": self.global_authorities,
            "id_photo": self.id_photo,
            # Preferred names:
            "pref_first_name": self.pref_first_name,
            "pref_last_name": self.pref_last_name,
            "override_name": self.override_name,
            "legal_first_name": self.legal_first_name,
            "legal_last_name": self.legal_last_name,
        }

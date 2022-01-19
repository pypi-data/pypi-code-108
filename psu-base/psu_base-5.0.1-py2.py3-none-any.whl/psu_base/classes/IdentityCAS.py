from django.core.handlers.wsgi import WSGIRequest
from psu_base.services import utility_service


class IdentityCAS:
    """
    Hold basic identity info expected to be returned from CAS/Shibboleth
    """

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

    def __init__(self, request):
        # Get user from http request
        if type(request) is WSGIRequest and request.user.is_authenticated:
            sso_dict = request.session["attributes"]

        # A dict may be given in Unit Tests
        elif type(request) is dict and utility_service.is_non_production():
            sso_dict = request

        # Otherwise, return an empty object
        else:
            # Initialize an empty object
            return

        # Email address
        self.email_address = sso_dict["mail"] if "mail" in sso_dict else None
        self.clean_address()

        # Name
        self.first_name = sso_dict["given_name"] if "given_name" in sso_dict else None
        self.last_name = sso_dict["sn"] if "sn" in sso_dict else None
        if "display_name" in sso_dict and sso_dict["display_name"]:
            self.display_name = sso_dict["display_name"]
        else:
            self.display_name = f"{self.first_name} {self.last_name}".strip()

        # Identifiers
        self.uuid = sso_dict["psuuuid"] if "psuuuid" in sso_dict else None
        self.psu_id = (
            sso_dict["employeeNumber"] if "employeeNumber" in sso_dict else None
        )
        self.username = sso_dict["uid"] if "uid" in sso_dict else None
        self.pidm = sso_dict["pidm"] if "pidm" in sso_dict else None

        # Role(s)
        self.primary_role = sso_dict.get("eduPersonPrimaryAffiliation")
        psa = sso_dict.get("eduPersonScopedAffiliation")
        self.roles = [rr.replace("@pdx.edu", "") for rr in psa] if psa else []

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
        # If a dict representation of this class was provided
        elif type(identifier) is dict and "username" in identifier:
            return self.equals(identifier["username"])
        # Otherwise, check each possible identifier
        elif self.username.lower() == str(identifier).lower():
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

    def to_dict(self):
        return {
            "email_address": self.email_address,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "display_name": self.display_name,
            "uuid": self.uuid,
            "psu_id": self.psu_id,
            "username": self.username,
            "pidm": self.pidm,
            "primary_role": self.primary_role,
            "roles": self.roles,
        }

    def __repr__(self):
        return f"<CAS:{self.username} {self.display_name}>"

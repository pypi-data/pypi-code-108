from django.conf import settings
from psu_base.services import utility_service
from psu_base.classes.Log import Log

log = Log()


class DynamicRole:
    prod = None
    non_prod = None

    def __init__(self):
        self.prod = utility_service.is_production()
        self.non_prod = not self.prod

    def decode(self, string):
        string = str(string)
        base_roles = []
        plus_roles = []
        if "power" in string.lower():
            base_roles = self.power_user()
        elif "super" in string.lower():
            base_roles = self.super_user()
        elif "security" in string.lower():
            base_roles = self.security_officer()
        elif "impersonat" in string.lower():
            base_roles = self.impersonator()
        elif string.lower().endswith("ro"):
            base_roles = self.ro()

        if "+" in string:
            plus_string = string.split("+")[1:]
            plus_roles = utility_service.csv_to_list(plus_string)

        return base_roles + plus_roles

    @staticmethod
    def plus(additional):
        if type(additional) is str:
            ll = utility_service.csv_to_list(additional)
        elif type(additional) is list:
            ll = additional
        else:
            ll = []

        return ll if ll else []

    def power_user(self, plus=None):
        """
        The lowest-level of increased authority on a site.
        Gets access to base features like viewing audit logs or editing infotext
        """
        # This will be the same for prod and non-prod (at least for now)
        if self.prod:
            pass

        return ["admin", "developer", "oit-es-manager"] + self.plus(plus)

    def super_user(self, plus=None):
        """
        An increased level of authority.
        Perhaps features not suitable for non-technical users, or features that affect site functions.
        """
        if self.prod:
            return ["oit-es-manager"] + self.plus(plus)
        else:
            return ["developer", "oit-es-manager"] + self.plus(plus)

    def security_officer(self, plus=None):
        """
        Allows access to monitor security features (i.e. review XSS attempts), and to modify user permissions
        """
        if self.prod:
            return ["authorize", "oit-es-manager"] + self.plus(plus)
        else:
            return ["authorize", "developer", "oit-es-manager"] + self.plus(plus)

    def impersonator(self, plus=None):
        """
        Allows impersonation
        """
        if self.prod:
            return ["oit-es-manager"] + self.plus(plus)
        else:
            return ["admin", "impersonate", "developer", "oit-es-manager"] + self.plus(
                plus
            )

    def ro(self, plus=None):
        """
        Someone in the RO office (any known RO role)
        """
        return ["ro", "ro_admin", "ro_psr", "ro_tech", "ro_office"] + self.plus(plus)

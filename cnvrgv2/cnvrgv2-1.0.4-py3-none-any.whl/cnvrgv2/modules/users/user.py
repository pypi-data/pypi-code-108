from cnvrgv2.errors import CnvrgArgumentsError
from cnvrgv2.config import routes, error_messages
from cnvrgv2.modules.base.dynamic_attributes import DynamicAttributes
from cnvrgv2.proxy import Proxy, HTTP
import os

from cnvrgv2.utils.url_utils import encode_base64


class ROLES:
    ADMIN = 'admin'
    MANAGER = 'manager'
    MEMBER = 'member'
    REVIEWER = 'reviewer'
    ALL_ROLES = [ADMIN, MANAGER, MEMBER, REVIEWER]


class User(DynamicAttributes):
    available_attributes = {
        "icon": str,
        "username": str,
        "name": str,
        "bio": str,
        "company": str,
        "time_zone": str,
        "git_access_token": str,
        "default_homepage": str,
        "vscode_settings": str,
        "roles": list,
        "organizations": list
    }

    def __init__(self, domain, token, attributes=None):
        self._proxy = Proxy(domain=domain, token=token)
        if attributes:
            self._email = attributes["email"]
            attributes["icon"] = None
            attributes["vscode_settings"] = None

        self._token = token
        self._route = routes.USER_CURRENT
        self._attributes = attributes or {}

    @property
    def email(self):
        return self._email

    def save(self):
        """
        In case of any attribute change, saves the changes
        """
        self.update(**self._attributes)

    def update(self, **kwargs):
        """
        Update the users profile
        @param kwargs: icon, username, name, password, bio, company, time_zone,
        git_access_token, default homepage, vscode_settings
        """
        if kwargs.get("icon") and not os.path.exists(kwargs.get("icon")):
            raise CnvrgArgumentsError(error_messages.NO_FILE)

        if kwargs.get("vscode_settings") and not os.path.exists(kwargs.get("vscode_settings")):
            raise CnvrgArgumentsError(error_messages.NO_FILE)

        kwargs["icon"] = encode_base64(kwargs.get("icon"))
        kwargs["vscode_settings"] = encode_base64(kwargs.get("vscode_settings"))

        response = self._proxy.call_api(route=routes.USER_CURRENT, http_method=HTTP.PUT, payload=kwargs)
        self._attributes = response.attributes

    def leave_org(self, slug):
        """
        leave organization - remove it from list of organizations and update database
        @param slug: organization slug
        """
        if not any(org.get("slug") == slug for org in self._attributes["organizations"]):
            raise CnvrgArgumentsError(error_messages.ORGANIZATION_NOT_FOUND)

        self._proxy.call_api(route=routes.USER_MEMBERSHIPS + slug, http_method=HTTP.DELETE)
        self._attributes["organizations"] = list(
            filter(lambda org: org.get("slug") != slug, self._attributes["organizations"])
        )

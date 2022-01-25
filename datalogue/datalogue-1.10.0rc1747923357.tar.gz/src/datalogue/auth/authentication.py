from abc import ABC, abstractmethod
from datetime import datetime
from typing import Union, Optional, List
from uuid import UUID

from datalogue.dtl_utils import SerializableStringEnum
from datalogue.errors import _enum_parse_error, DtlError


class AuthenticationType(SerializableStringEnum):
    LDAP = "LDAP"
    OpenId = "OpenId"

    @staticmethod
    def authentication_type_from_str(string: str,) -> Union[DtlError, "AuthenticationType"]:
        return SerializableStringEnum.from_str(AuthenticationType)(string)

    @staticmethod
    def parse_error(s: str) -> DtlError:
        return DtlError(_enum_parse_error("authentication type", s))


class Authentications(ABC):
    def __init__(self, name: str, authentication_type: AuthenticationType, activated: bool = True):
        """
        Builds an Authentication

        :param name: Name of the Authentication
        :param authentication_type: Type of Authentication. Ex: LDAP, OpenId
        :param activated: Is the authentication activated
        """
        self.name = name
        self.provider_type = authentication_type
        self.activated = activated

    def __eq__(self, other: "Authentications"):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(name: {self.name}, provider_type: {self.provider_type}, "
            f"activated: {self.activated!r})"
        )

    def _base_payload(self) -> dict:
        base = {
            "name": self.name,
            "providerType": self.provider_type.value,
            "activated": self.activated,
        }

        return base

    @abstractmethod
    def _as_payload(self):
        pass


class AuthenticationsReference:
    def __init__(
        self,
        ref_id: UUID,
        org_id: UUID,
        name: str,
        activated: bool,
        provider_type: AuthenticationType,
        config: Authentications,
        created_at: datetime,
        created_by: UUID,
        updated_at: datetime,
        updated_by: UUID,
        owner: UUID,
    ):
        """
        Represents a reference to an Authentication

        :param ref_id: UUID of the authentication
        :param org_id: UUID of the organization to which this authentication belongs to
        :param name: Name of the Authentication
        :param activated: Activation status of the authentication
        :param provider_type: Type of authentication provider Ex: LDAP, OpenId
        :param config: Provider specific configuration
        :param created_at: Creation timestamp
        :param created_by: UUID of the user who created this authentication
        :param updated_at: Last updated timestamp
        :param updated_by: UUID if the user who last updated this authentication
        :param owner: UUID of the owner of this authentication
        """
        self.id = ref_id
        self.org_id = org_id
        self.name = name
        self.activated = activated
        self.type = provider_type
        self.config = config
        self.created_at = created_at
        self.created_by = created_by
        self.updated_at = updated_at
        self.updated_by = updated_by
        self.owner = owner

    def __eq__(self, other: "AuthenticationType"):
        if isinstance(self, other.__class__):
            return (
                self.id == other.id
                and self.name == other.name
                and self.type == other.type
                and self.config._as_payload() == other.config._as_payload()
                and self.owner == other.owner
            )
        return False

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(id: {self.id}, org_id: {self.org_id}, name: {self.name}, "
            f"activated: {self.activated}, type: {self.type}, config: {self.config}, "
            f"created_at: {self.created_at}, created_by: {self.created_by}, updated_at: {self.updated_at}, "
            f"updated_by: {self.updated_by}, owner: {self.owner})"
        )


# todo - below method is used for listing auth types, but misses out standard fields
def _authentication_ref_from_payload(json: dict,) -> Union[DtlError, AuthenticationsReference]:
    ref_id = json.get("id")
    if not isinstance(ref_id, str):
        return DtlError("An AuthenticationsReference needs a 'id' field")
    else:
        ref_id = UUID(ref_id)

    org_id = json.get("organizationId")
    if isinstance(org_id, str):
        org_id = UUID(org_id)

    name = json.get("name")
    if name is None:
        return DtlError("An AuthenticationsReference needs a 'name' field")

    activated = json.get("activated")

    auth_type = json.get("providerType")
    if not isinstance(auth_type, str):
        return DtlError("An AuthenticationsReference needs a 'providerType' field")
    else:
        auth_type = AuthenticationType.from_str(AuthenticationType)(auth_type).value

    config = json.get("config")
    if isinstance(config, dict):
        if auth_type == AuthenticationType.LDAP.value:
            config = LdapAuthenticationDef.from_payload(config)

    return AuthenticationsReference(ref_id, org_id, name, activated, auth_type, config, None, None, None, None, None)


class LdapAuthenticationDef(Authentications):
    type_str = AuthenticationType.LDAP

    def __init__(
        self,
        name: str,
        host: str,
        port: int,
        bind_cn: str,
        bind_password: str,
        sub_directory: str,
        group_dn: List[str],
        login_attribute: str = "cn",
        group_member_attribute: str = "memberOf",
        mail_attribute: str = "mail",
        first_name_attribute: Optional[str] = None,
        last_name_attribute: Optional[str] = None,
        display_name_attribute: Optional[str] = "displayName",
    ):
        """
        Definition of a LDAP configuration

        :param name: User friendly name for this Authentication
        :param host: Fully qualified host name. Ex: ldap.domain.com
        :param port: port Ex: 636
        :param bind_cn: Bind CN
        :param bind_password: password
        :param sub_directory: Sub directory. Ex: 'ou=system'
        :param group_dn: The distinguished name(s) referencing one or more groups on the LDAP server, as a list of
            strings
        :param login_attribute: The common name(s) referencing one or more users on the LDAP record
        :param group_member_attribute: login attribute applied as a filter, e.g. "memberOf"
        :param mail_attribute: Can be used to point to the field were Email is stored on the LDAP record, for account
            metadata purposes
        :param first_name_attribute: Can be used to map to the field where first name is stored on the LDAP record, for
            account metadata purposes
        :param last_name_attribute: Can be used to point to the field where last name is stored on the LDAP reord, for
            account metadata purposes
        :param display_name_attribute: Can be used to point to the field where display name is stored on the LDAP
            record, for account metadata purposes
        """
        self.host = host
        self.port = port
        self.bind_cn = bind_cn
        self.bind_password = bind_password
        self.sub_directory = sub_directory
        self.group_dn = group_dn
        self.login_attribute = login_attribute
        self.group_member_attribute = group_member_attribute
        self.mail_attribute = mail_attribute
        self.first_name_attribute = first_name_attribute
        self.last_name_attribute = last_name_attribute
        self.display_name_attribute = display_name_attribute
        super().__init__(name, LdapAuthenticationDef.type_str)

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(name: {self.name}, host: {self.host}, port: {self.port}, "
            f"bind_cn: {self.bind_cn}, bind_password: {self.bind_password}, sub_directory: {self.sub_directory}, "
            f"group_dn: {self.group_dn}, login_attribute: {self.login_attribute}, group_member_attribute: "
            f"{self.group_member_attribute}, mail: ${self.mail_attribute}, first_name_attribute: "
            f"{self.first_name_attribute!r}, last_name_attribute: {self.last_name_attribute!r}, "
            f"display_name_attribute: {self.display_name_attribute!r})"
        )

    def _as_payload(self) -> dict:
        payload = self._base_payload()
        config = {
            "host": self.host,
            "port": self.port,
            "bindCn": self.bind_cn,
            "bindPassword": self.bind_password,
            "subDirectory": self.sub_directory,
            "providerType": self.provider_type.value,
            "groupDn": self.group_dn,
            "loginAttribute": self.login_attribute,
            "groupMemberAttribute": self.group_member_attribute,
            "mailAttribute": self.mail_attribute,
        }

        if self.first_name_attribute is not None:
            config["firstNameAttribute"] = self.first_name_attribute

        if self.last_name_attribute is not None:
            config["lastNameAttribute"] = self.last_name_attribute

        if self.display_name_attribute is not None:
            config["displayNameAttribute"] = self.display_name_attribute

        payload["config"] = config
        return payload

    @staticmethod
    def from_payload(json: dict) -> Union[DtlError, "LdapAuthenticationDef"]:
        host = json.get("host")
        if not isinstance(host, str):
            return DtlError("LDAP configuration requires a 'host' field")

        port = json.get("port")
        if not isinstance(port, str):
            return DtlError("LDAP configuration requires a 'port' field")
        else:
            port = int(port)

        bind_cn = json.get("bindCn")
        if not isinstance(bind_cn, str):
            return DtlError("LDAP configuration requires a 'bindCn' field")

        bind_password = json.get("bindPassword")
        if not isinstance(bind_password, str):
            return DtlError("LDAP configuration requires a 'bindPassword' field")

        sub_directory = json.get("subDirectory")
        if not isinstance(sub_directory, str):
            return DtlError("LDAP configuration requires a 'subDirectory' field")

        group_dn = json.get("groupDn")
        if not isinstance(group_dn, List):
            return DtlError("LDAP configuration requires a 'groupDn' field")

        login_attribute = json.get("loginAttribute")
        if not isinstance(login_attribute, str):
            return DtlError("LDAP configuration requires a 'loginAttribute' field")

        group_member_attribute = json.get("groupMemberAttribute")
        if not isinstance(group_member_attribute, str):
            return DtlError("LDAP configuration requires a 'groupMemberAttribute'")

        mail_attribute = json.get("mailAttribute")
        if not isinstance(mail_attribute, str):
            return DtlError("LDAP configuration requires a 'mailAttribute'")

        first_name_attribute = json.get("firstNameAttribute")
        last_name_attribute = json.get("lastNameAttribute")
        display_name_attribute = json.get("displayNameAttribute")

        return LdapAuthenticationDef(
            "",
            host,
            port,
            bind_cn,
            bind_password,
            sub_directory,
            group_dn,
            login_attribute,
            group_member_attribute,
            mail_attribute,
            first_name_attribute,
            last_name_attribute,
            display_name_attribute,
        )

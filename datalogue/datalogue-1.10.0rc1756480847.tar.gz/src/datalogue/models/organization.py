from uuid import UUID
from typing import List, Union, Optional

from datalogue.errors import DtlError


class Organization:
    def __init__(self, org_id: UUID, name: str):
        self.id = org_id
        self.name = name

    def __eq__(self, other: "Organization"):
        if isinstance(self, other.__class__):
            return self.id == other.id and self.name == other.name
        return False

    def __repr__(self):
        return f"{self.__class__.__name__}(id= {self.id}, name= {self.name!r})"


def _organization_from_payload(json: dict) -> Union[DtlError, Organization]:
    org_id = json.get("id")
    if org_id is None:
        return DtlError("Organization object should have an 'id' property")
    else:
        try:
            org_id = UUID(org_id)
        except ValueError:
            return DtlError("'id' field was not a proper uuid")

    name = json.get("name")
    if name is None:
        return DtlError("Organization object should have a 'name' property")

    return Organization(org_id, name)


class Group:
    def __init__(self, group_id: UUID, org_id: UUID, name: str):
        self.id = group_id
        self.name = name
        self.org_id = org_id

    def __eq__(self, other: "Group"):
        if isinstance(self, other.__class__):
            return self.id == other.id and self.name == other.name and self.org_id == other.org_id
        return False

    def __repr__(self):
        return f"{self.__class__.__name__}(id= {self.id}, name= {self.name!r}, org_id= {self.org_id!r})"


def _group_from_payload(json: dict) -> Union[DtlError, Group]:
    group_id = json.get("id")
    if group_id is None:
        return DtlError("Group object should have an 'id' property")
    else:
        try:
            group_id = UUID(group_id)
        except ValueError:
            return DtlError("'id' field was not a proper uuid")

    name = json.get("name")
    if name is None:
        return DtlError("Group object should have a 'name' property")

    org_id = json.get("orgId")
    if org_id is None:
        return DtlError("Group object should have a 'org_id' property")
    else:
        try:
            org_id = UUID(org_id)
        except ValueError:
            return DtlError("'orgId' field was not a proper uuid")

    return Group(group_id, org_id, name)


class CreateUserRequest:
    """
    Definition of request needed to create user
    """

    def __init__(self, email: str, first_name: str, last_name: Optional[str]):
        """
        constructor of CreateUserRequest
        :param email: email of the user
        :param first_name: first name of the user
        :param last_name: last name of the user
        """
        self.email = email
        self.first_name = first_name
        self.last_name = last_name

    def as_payload(self):
        """
        Dictionary representation of the object
        :return:
        """
        return {
            "email": self.email.lower(),
            "firstName": self.first_name,
            "lastName": self.last_name,
        }


class User:
    """
    Definition of user
    """

    def __init__(
        self,
        user_id: UUID,
        first_name: Optional[str],
        last_name: Optional[str],
        email: str,
        organization_ids: Union[None, List[str]],
        group_ids: Union[None, List[str]],
    ):
        """
        User constructor
        :param user_id: UUID of the user
        :param first_name: user first name
        :param last_name: user last name
        :param email: user email
        :param organization_ids: ids of organizations which users belongs to
        :param group_ids: ids of groups which users belongs to
        """
        self.id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.organization_ids = organization_ids
        self.group_ids = group_ids

    def __eq__(self, other: "User"):
        if isinstance(self, other.__class__):
            return (
                self.id == other.id
                and self.first_name == other.first_name
                and self.last_name == other.last_name
                and self.email == other.email
            )
        return False

    def __repr__(self):
        return f"{self.__class__.__name__}(id= {self.id}, first_name= {self.first_name!r}, last_name= {self.last_name!r}, email= {self.email!r}, organization_ids= {self.organization_ids!r}, group_ids= {self.group_ids!r})"


def _user_from_payload(json: dict) -> Union[DtlError, User]:
    user_id = json.get("user").get("id")
    if user_id is None:
        return DtlError("User object should have an 'id' property")
    else:
        try:
            user_id = UUID(user_id)
        except ValueError:
            return DtlError("'id' field was not a proper uuid")

    first_name = json.get("user").get("firstName")
    last_name = json.get("user").get("lastName")

    email = json.get("user").get("email")
    if email is None:
        return DtlError("User object should have a 'email' property")

    organization_ids = json.get("organizationsIds")
    # if organization_ids is None:
    #     return DtlError("User object should have a 'organizationsIds' property")

    group_ids = json.get("groupsIds")
    if group_ids is None:
        return DtlError("User object should have a 'groupsIds' property")

    return User(user_id, first_name, last_name, email, organization_ids, group_ids)


def _users_from_payload(json: dict) -> Union[DtlError, User]:
    user_id = json.get("id")
    if user_id is None:
        return DtlError("User object should have an 'id' property")
    else:
        try:
            user_id = UUID(user_id)
        except ValueError:
            return DtlError("'id' field was not a proper uuid")

    first_name = json.get("firstName")
    last_name = json.get("lastName")

    email = json.get("email")
    if email is None:
        return DtlError("User object should have a 'email' property")

    group_ids = json.get("groupIds")

    return User(user_id, first_name, last_name, email, None, group_ids)


class Domain:
    def __init__(self, org_id: UUID, domain: str):
        self.org_id = org_id
        self.domain = domain

    def __eq__(self, other: "Domain"):
        if isinstance(self, other.__class__):
            return self.org_id == other.org_id and self.domain == other.domain
        return False

    def __repr__(self):
        return f"{self.__class__.__name__}(org_id= {self.org_id}, domain= {self.domain!r})"

    def __hash__(self):
        return hash(self.org_id) ^ hash(self.domain)


def _domain_from_payload(json: dict) -> Union[DtlError, Domain]:
    org_id = json.get("orgId")
    if org_id is None:
        return DtlError("Domain object should have an 'orgId' property")
    else:
        try:
            org_id = UUID(org_id)
        except ValueError:
            return DtlError("'id' field was not a proper uuid")

    domain = json.get("domain")
    if domain is None:
        return DtlError("Domain object should have a 'domain' property")

    return Domain(org_id, domain)


class TokenCreateResult:
    def __init__(self, id: UUID, token: str, checksum: str):
        self.id = id
        self.token = token
        self.checksum = checksum

    def __repr__(self):
        return f"{self.__class__.__name__}(id= {self.id}, token= {self.token!r}, checksum= {self.checksum!r})"

    @staticmethod
    def _from_payload(json: dict) -> Union[DtlError, "TokenCreateResult"]:
        id = json.get("id")
        if id is None:
            return DtlError("TokenCreateResult should have a 'id' property")

        token = json.get("token")
        if token is None:
            return DtlError("TokenCreateResult should have a 'token' property")

        checksum = json.get("checksum")
        if checksum is None:
            return DtlError("TokenCreateResult should have a 'checksum' property")
        return TokenCreateResult(id, token, checksum)


class PublicToken:
    def __init__(self, id: UUID, user_id: UUID, name: str, organization_id: UUID, checksum: str):
        self.id = id
        self.user_id = user_id
        self.name = name
        self.organization_id = organization_id
        self.checksum = checksum

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(\n"
            f"id= {self.id!r},\n"
            f"user_id= UUID({self.user_id!r}),\n"
            f"name= {self.name!r},\n"
            f"organization_id= UUID({self.organization_id!r})\n"
            f"checksum= {self.checksum!r}\n"
            f")"
        )

    @staticmethod
    def _from_payload(payload: dict) -> Union[DtlError, "PublicToken"]:
        id = payload.get("id")
        if id is None:
            return DtlError("TokenCreateResult should have a 'id' property")

        user_id = payload.get("userId")
        if user_id is None:
            return DtlError("TokenCreateResult should have a 'userId' property")

        name = payload.get("name")
        if name is None:
            return DtlError("TokenCreateResult should have a 'name' property")

        organization_id = payload.get("organizationId")
        if organization_id is None:
            return DtlError("TokenCreateResult should have a 'organizationId' property")

        checksum = payload.get("checksum")
        if checksum is None:
            return DtlError("TokenCreateResult should have a 'checksum' property")

        return PublicToken(id, user_id, name, organization_id, checksum)

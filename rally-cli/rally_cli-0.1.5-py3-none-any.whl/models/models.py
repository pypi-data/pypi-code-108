import os
import re
import sys
from datetime import datetime
from typing import Optional, Union

from pydantic import validator, AnyHttpUrl

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from rallycli.models import RallyPydanticBase


class RallyTypeGeneric(RallyPydanticBase):
    ObjectID: Optional[str]
    VersionId: Optional[int]
    CreationDate: Optional[datetime]
    _ref: Optional[AnyHttpUrl]
    _refObjectName: Optional[str]
    _type: Optional[str]

    @staticmethod
    def get_oid_from_ref(ref: str) -> str:
        oid_from_ref = re.compile(r".*/(\d+)$")
        if match := oid_from_ref.match(ref):
            return match.group(1)
        return ""

class User(RallyTypeGeneric):
    ObjectUUID: Optional[str]
    AccountLockedUntil: Optional[datetime]
    ArtifactsCreated: Optional[Union[RallyTypeGeneric, str]]
    ArtifactsOwned: Optional[Union[RallyTypeGeneric, str]]
    CostCenter: Optional[str]
    DateFormat: Optional[str]
    DateTimeFormat: Optional[str]
    DefaultDetailPageToViewingMode: Optional[bool]
    DefaultProject: Optional[Union[RallyTypeGeneric, str]]
    Deleted: Optional[bool]
    Department: Optional[str]
    Disabled: Optional[bool]
    DisplayName: Optional[str]
    EmailAddress: Optional[str]
    EmailNotificationEnabled: Optional[str]
    FirstName: Optional[str]
    InvestmentAdmin: Optional[bool]
    LandingPage: Optional[str]
    Language: Optional[str]
    LastActiveDate: Optional[str]
    LastLoginDate: Optional[datetime]
    LastName: Optional[str]
    LastPasswordUpdateDate: Optional[datetime]
    LastSystemTimeZoneName: Optional[str]
    Locale: Optional[str]
    MiddleName: Optional[str]
    NetworkID: Optional[str]
    OfficeLocation: Optional[str]
    OnpremLdapUsername: Optional[str]
    PasswordExpires: Optional[int]
    Phone: Optional[str]
    Planner: Optional[bool]
    ProfileImage: Optional[Union[RallyTypeGeneric, str]]
    ProjectScopeDown: Optional[bool]
    ProjectScopeUp: Optional[bool]
    Role: Optional[str]
    sessionTimeout: Optional[int]
    SessionTimeoutWarning: Optional[bool]
    ShortDisplayName: Optional[str]
    SubscriptionAdmin: Optional[bool]
    Subscription: Optional[Union[RallyTypeGeneric, str]]
    SubscriptionID: Optional[int]
    SubscriptionPermission: Optional[str]
    TeamMemberships: Optional[Union[RallyTypeGeneric, str]]
    UserName: Optional[str]
    UserPermissions: Optional[Union[RallyTypeGeneric, str]]
    UserProfile: Optional[Union[RallyTypeGeneric, str]]
    WorkspacePermission: Optional[str]
    ZuulID: Optional[str]
    c_Empresa: Optional[str]
    c_Matricula: Optional[str]

    @validator('EmailAddress')
    def validate_email(cls, v: str):
        if not re.match(r"(\w|\.|_|-)+[@](\w|_|-|\.)+[.]\w{2,3}", v):
            raise ValueError("Invalid email address: ", v)
        return v

    ## @validator('c_Matricula')
    ## def validate_matricula(cls, v: str):
    ##     if not re.match(r"U01[0-9|A-Z]{5}$", v):
    ##         raise ValueError("Invalid matricula: ", v)
    ##     return v


class Project(RallyTypeGeneric):
    Name: Optional[str]


class Workspace(RallyTypeGeneric):
    Subscription: Optional[Union[RallyTypeGeneric, str]]


class AllowedValue(RallyTypeGeneric):
    AttributeDefinition: Optional[Union[str, RallyTypeGeneric]]
    IntegerValue: Optional[int]
    LocalizedStringValue: Optional[str]
    StringValue: Optional[str]
    ValueIndex: Optional[int]


class Attdefinition(RallyTypeGeneric):
    Name: Optional[str]
    ElementName: Optional[str]
    AllowedValues: Optional[Union[str, RallyTypeGeneric]]
    AttributeType: Optional[str]
    RealAttributeType: Optional[str]
    Custom: Optional[bool]
    RealAttributeType: Optional[str]
    TypeDefinition: Optional[Union[str, RallyTypeGeneric]]
    ReadOnly: Optional[bool]
    Hidden: Optional[bool]
    Required: Optional[bool]

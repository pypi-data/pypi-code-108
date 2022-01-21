from net_models.fields import GENERIC_OBJECT_NAME, PRIVILEGE_LEVEL, AAA_METHOD_NAME
from net_models.models.BaseModels import BaseNetModel, VendorIndependentBaseModel
from pydantic import root_validator
from pydantic.types import PositiveInt
from pydantic.typing import Optional, List, Literal, Union


def enable_action_prohibited(cls, values):
    return values


class IosAaaBase(VendorIndependentBaseModel):

    pass

class IosAaaAction(IosAaaBase):

    action: Literal["local", "local-case", "none", "group", "enable"]
    group: Optional[Union[Literal["radius", "tacacs+"], GENERIC_OBJECT_NAME]]

    @root_validator(allow_reuse=True)
    def verify_group_present(cls, values):
        if values.get("action") == "group":
            if values.get("group") is None:
                msg = f"When action == 'group', group is required."
                raise AssertionError(msg)
        else:
            if values.get("group") is not None:
                msg = f"Unless action == 'group', group must be None."
                raise AssertionError(msg)
        return values


class IosAaaMethodBase(IosAaaBase):

    name: AAA_METHOD_NAME
    action_list: List[IosAaaAction]


class IosAaaAuthenticationMethod(IosAaaMethodBase):

    pass

class IosAaaAuthentication(IosAaaBase):

    login: Optional[List[IosAaaAuthenticationMethod]]
    enable: Optional[List[IosAaaAuthenticationMethod]]
    dot1x: Optional[List[IosAaaAuthenticationMethod]]


class IosAaaAuthorizationMethod(IosAaaMethodBase):

    if_authenticated: Optional[bool]


class IosAaaAuthorizationCommands(IosAaaAuthorizationMethod):

    level: PRIVILEGE_LEVEL


class IosAaaAuthorization(IosAaaBase):

    exec: Optional[List[IosAaaAuthorizationMethod]]
    commands: Optional[List[IosAaaAuthorizationCommands]]
    network: Optional[List[IosAaaAuthorizationMethod]]
    authorize_console: Optional[bool]
    authorize_config_commands: Optional[bool]


class IosAaaAccountingAction(IosAaaAction):

    action: Literal["none", "group"]
    broadcast: Optional[bool]

    @root_validator(allow_reuse=True)
    def validate_broadcast(cls, values):
        if values.get("action") == "none":
            if values.get("broadcast") not in [None, False]:
                msg = f"If action == 'none', broadcast can only be in [None, False]."
                raise AssertionError(msg)
        return values


class IosAaaAccountingMethod(IosAaaMethodBase):

    action_list: Optional[List[IosAaaAccountingAction]]
    record: Literal["none", "start-stop", "stop-only"]

    @root_validator(allow_reuse=True)
    def validate_action_list(cls, values):
        record = values.get("record")
        if record == 'none':
            # action_list must be None
            if values.get("action_list") is not None:
                msg = f"If record == 'none', action_list must be None."
                raise AssertionError(msg)
        else:
            if values.get("action_list") is None:
                msg = f"Unless record == 'none', action_list cannot be None."
                raise AssertionError(msg)
        return values


class IosAaaAccountingCommands(IosAaaAccountingMethod):

    level: PRIVILEGE_LEVEL


class IosAaaAccounting(IosAaaBase):

    exec: Optional[List[IosAaaAccountingMethod]]
    commands: Optional[List[IosAaaAccountingCommands]]
    visible_keys: Optional[bool]


class IosAaaConfig(IosAaaBase):

    authentication: Optional[IosAaaAuthentication]
    authorization: Optional[IosAaaAuthorization]
    accounting: Optional[IosAaaAccounting]


class IosAaaLineCommands(BaseNetModel):

    name: GENERIC_OBJECT_NAME
    """Name of the AAA method"""
    level: PRIVILEGE_LEVEL
    """Privilege level"""


class IosAaaLineAuthorization(BaseNetModel):

    exec: Optional[AAA_METHOD_NAME]
    """Name of the authorization exec method"""
    commands: Optional[List[IosAaaLineCommands]]
    """List of Line Commands Authorization Models"""


class IosAaaLineAccounting(BaseNetModel):

    exec: Optional[AAA_METHOD_NAME]
    """Name of the accounting exec method"""
    commands: Optional[List[IosAaaLineCommands]]
    """List of Line Commands Accounting Models"""


class IosLineAaaConfig(BaseNetModel):

    authentication: Optional[AAA_METHOD_NAME]
    """Name of the authentication login method"""
    authorization: Optional[IosAaaLineAuthorization]
    """Line Authorization Model"""
    accounting: Optional[IosAaaLineAuthorization]
    """Line Accounting Model"""

class IosAaaConfig(BaseNetModel):

    authentication: Optional[IosAaaAuthentication]
    authorization: Optional[IosAaaAuthorization]
    accounting: Optional[IosAaaAccounting]


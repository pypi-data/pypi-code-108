from pydantic import BaseModel, validator
from pydantic.typing import Any, List
from datetime import datetime


class JWTTokenValidateResponseModel(BaseModel):
    user_id: str
    requested_permission: bool = False


class JWTInitTokenModel(BaseModel):
    user_id: str
    others: dict = None


class JWTInitTokenResponseModel(BaseModel):
    token: str


class OthersModel(BaseModel):
    ct: float = None
    ex: float = None
    rt: float = None
    sc: List[str] = []


class TokenModel(BaseModel):
    user_id: str
    others: OthersModel = None


class RemoveTokenResponseModel(BaseModel):
    message: str


class InitConfig(BaseModel):
    service_address: str
    enable_ws: bool = False
    key: str = None


class TokenURLs(BaseModel):
    INIT_TOKEN: str = "/jwt/token/init"
    VALIDATE_TOKEN: str = "/jwt/token/validate"
    REMOVE_TOKEN: str = "/jwt/token/remove"


class PermissionsUrls(BaseModel):
    ADD_PERMISSION: str = "/permissions/add"
    REMOVE_PERMISSION: str = "/permissions"
    GET_PERMISSION: str = "/permissions/get"
    GET_ALL_PERMISSION: str = "/permissions/get-all"


class RolesUrls(BaseModel):
    ADD_ROLE: str = "/role/add"
    REMOVE_ROLE: str = "/role/delete"
    GET_ROLE: str = "/role/get"
    GET_ALL_ROLE: str = "/role/get-all"
    UPDATE_PERMISSION: str = "/role/permissions/update"


class UserRoleUrls(BaseModel):
    ADD_USER_ROLE: str = "/user_role_permission/add"
    DELETE_USER_ROLE: str = "/user_role_permission/delete"
    GET_USER_ROLE: str = "/user_role_permission"
    UPDATE_USER_ROLE: str = "/user_role_permission/update"
    GET_ALL_USER_ROLE: str = "/user_role_permission/get-all"


class TrustedServiceUrls(BaseModel):
    ADD: str = "/trusted_service/add"
    DELETE: str = "/trusted_service/remove"
    RENEW: str = "/trusted_service/renew"
    GET: str = "/trusted_service/get"
    GET_ALL: str = "/trusted_service/get-all"


class PanelUrls(BaseModel):
    VALIDATE_USER_PANEL: str = "/user-panel/validate"


class MenuModel(BaseModel):
    name: str
    sub_menus: List[str]


class PanelModel(BaseModel):
    name: str
    menus: List[MenuModel]


class ValidateAdminResponse(BaseModel):
    user_id: str
    user_role: List[str]
    panel_scheme: PanelModel = None


class AddPermissionBodyModel(BaseModel):
    permission_name: str
    description: str


class AddPermissionResultModel(BaseModel):
    permission_added: str


class GetPermissionResultModel(BaseModel):
    id: str
    permission_name: str
    description: str
    create_at: datetime = datetime.now()


class RemovePermissionResultModel(BaseModel):
    permission_deleted: str


class GetListOfPermissionsResultModel(BaseModel):
    permissions: List[GetPermissionResultModel] = []
    page: int


class AddRoleDataModel(BaseModel):
    role_name: str
    description: str
    permission_list: List[str] = []

    @validator("role_name")
    def role_name_validator(cls, v: str):
        if v.lower() in ["root"]:
            raise Exception(f"[{v}] is invalid value for role_name")
        return v


class AddRoleResultModel(BaseModel):
    added_name: str


class RemoveRoleResultModel(BaseModel):
    removed_role: str


class GetRoleResultModel(BaseModel):
    id: str
    role_name: str
    permission_list: List[str]
    description: str


class GetAllRolesResponseModel(BaseModel):
    roles: List[GetRoleResultModel]
    page: int


class UpdateRoleResponseModel(BaseModel):
    update_count: int


class UpdateRolePermissionLists(BaseModel):
    role_name: str
    permissions: List[str]
    update_user_roles: bool = False


class AddUserRolePermissionResponseModel(BaseModel):
    added: bool
    updated: bool = False


class AddUserRolePermissionBodyModel(BaseModel):
    user_id: str
    roles_list: List[str]
    permissions_list: List[str] = []


class UpdateUserRolePermissionBodyModel(BaseModel):
    user_id: str
    roles_list: List[str]
    permissions_list: List[str] = []


class UpdateUserRoleResponseModel(BaseModel):
    updated_count: int


class RemoveUserRolePermission(BaseModel):
    user_id: str
    roles_to_remove_list: List[str] = []
    permissions_to_remove_list: List[str] = []


class RemoveUserRolePermissionResponseModel(BaseModel):
    removed: bool = True


class UserRole(BaseModel):
    id: str
    user_id: str
    roles_list: List[str]
    permissions_list: List[str]
    create_at: datetime = datetime.now()


class GetAllUserRolePermissionResponseModel(BaseModel):
    user_role_permissions: List[UserRole]
    page: int = 1


class TrustedConfigModel(BaseModel):
    TRUSTED_SERVICE_COLLECTION: str


class TrustedServiceModel(BaseModel):
    service_name: str
    service_secret: str
    create_at: datetime = datetime.now()


class AddTrustedServiceBodyModel(BaseModel):
    service_name: str


class AddTrustedServiceResponseModel(BaseModel):
    service_name: str
    service_secret: str


class RemoveTrustedServiceResponseModel(BaseModel):
    deleted_name: str


class GetAllTrustedServiceResponseModel(BaseModel):
    trusted_services: List[TrustedServiceModel]
    page: int = 1


class NewSecretTrustedServiceResponseModel(BaseModel):
    new_secret: str


class ActionPermission(BaseModel):
    ADD_PERMISSION: str = "add_permission"
    REMOVE_PERMISSION: str = "remove_permission"
    GET_PERMISSION: str = "get_permission"
    GET_ALL_PERMISSION: str = "get_permission"
    ADD_ROLE: str = "add_role"
    GET_ROLE: str = "get_role"
    REMOVE_ROLE: str = "remove_role"
    UPDATE_ROLE: str = "update_role"
    ADD_USER_ROLE: str = "add_user_role"
    DELETE_USER_ROLE: str = "delete_user_role"
    UPDATE_USER_ROLE: str = "update_user_role"
    GET_USER_ROLE: str = "get_user_role"


class ErrorModel(BaseModel):
    detail: Any

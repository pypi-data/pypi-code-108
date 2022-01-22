import jwt
import requests
from py_cas.Models import *


class CAS:
    def __init__(self, conf: InitConfig):
        self.conf = conf
        # self.ServiceAddress = conf.service_address
        # self.EnableWs = conf.enable_ws
        self.PermissionsUrls = PermissionsUrls()
        self.TokenUrls = TokenURLs()
        self.ActionPermissions = ActionPermission()
        self.RoleUrl = RolesUrls()
        self.UserRoleUrl = UserRoleUrls()
        self.TrustedServiceURL = TrustedServiceUrls()
        self.UserPanelURL = PanelUrls()

    @staticmethod
    def result_resolver(result):
        if result.status_code == 200:
            return result
        if result.status_code == 201:
            return result
        if result.status_code == 404:
            raise Exception(result.json()["detail"])
        if result.status_code == 406:
            raise Exception("access denied")
        if result.status_code == 400:
            raise Exception(result.json()["detail"])
        if result.status_code == 422:
            raise Exception(result.json()["detail"])

        if result.status_code == 500:
            raise Exception("server side error, please check the logs")

    def url_creator(self, request_url):
        return f"{self.conf.service_address}{request_url}"

    def __post(
        self, request_url, body: dict, headers: dict = None, params: dict = None
    ):
        result = requests.post(
            url=self.url_creator(request_url=request_url),
            json=body,
            headers=headers,
            params=params,
        )
        return CAS.result_resolver(result)

    def __get(self, request_url, headers: dict = None, params: dict = None):
        result = requests.get(
            url=self.url_creator(request_url=request_url),
            headers=headers,
            params=params,
        )
        return CAS.result_resolver(result)

    def __put(
        self, request_url, body: dict = None, headers: dict = None, params: dict = None
    ):
        result = requests.put(
            url=self.url_creator(request_url=request_url),
            json=body,
            headers=headers,
            params=params,
        )

        return CAS.result_resolver(result)

    def __delete(
        self, request_url, headers: dict = None, params: dict = None, body: dict = None
    ):
        result = requests.delete(
            url=self.url_creator(request_url=request_url),
            headers=headers,
            params=params,
            json=body,
        )
        return CAS.result_resolver(result)

    def init_token(
        self, user_id: str, others: dict = None, add_scopes: bool = False
    ) -> JWTInitTokenResponseModel:
        result = self.__post(
            request_url=TokenURLs().INIT_TOKEN,
            body=JWTInitTokenModel(user_id=user_id, others=others).dict(),
            params={"add_scopes": add_scopes},
        )
        return JWTInitTokenResponseModel(**result.json())

    def validate_token(
        self, token: str, permission: str = None
    ) -> JWTTokenValidateResponseModel:
        if self.conf.key:
            try:
                decoded_token = jwt.decode(token, key=self.conf.key)
                decoded_token = TokenModel(**decoded_token)
            except Exception as ex:
                raise Exception("access denied")
            # todo: token expiration checking
            if decoded_token.others and decoded_token.others.ex:
                if datetime.utcnow() > datetime.fromtimestamp(decoded_token.others.ex):
                    raise Exception("token expired")

            if not permission:
                return JWTTokenValidateResponseModel(
                    user_id=decoded_token.user_id, requested_permission=False
                )

            if permission:
                if decoded_token.others:
                    if decoded_token.others.sc.__contains__(permission):
                        return JWTTokenValidateResponseModel(
                            user_id=decoded_token.user_id, requested_permission=True
                        )

        result = self.__get(
            request_url=TokenURLs().VALIDATE_TOKEN,
            params={"token": token, "permission": permission},
        )
        if result.status_code != 200:
            raise Exception("access denied")
        return JWTTokenValidateResponseModel(**result.json())

    def remove_token(self, token: str):
        result = self.__get(
            request_url=self.TokenUrls.REMOVE_TOKEN, headers={"token": token}
        )
        return RemoveTokenResponseModel(**result.json())

    def validate_panel(self, user_id: str, panel: str) -> ValidateAdminResponse:
        result = self.__get(
            request_url=self.UserPanelURL.VALIDATE_USER_PANEL,
            params={"user_id": user_id, "panel": panel},
        )
        if result.status_code == 200:
            return ValidateAdminResponse(**result.json())
        else:
            raise Exception(result.json()["detail"])

    def add_permission(
        self, permission_name: str, description: str, token: str
    ) -> AddPermissionResultModel:
        result = self.__post(
            request_url=self.PermissionsUrls.ADD_PERMISSION,
            body=AddPermissionBodyModel(
                permission_name=permission_name, description=description
            ).dict(),
            headers={
                "token": token,
                "permission": self.ActionPermissions.ADD_PERMISSION,
            },
        )

        return AddPermissionResultModel(**result.json())

    def remove_permission(self, name: str, token: str) -> RemovePermissionResultModel:
        result = self.__delete(
            self.PermissionsUrls.REMOVE_PERMISSION,
            headers={
                "token": token,
                "permission": self.ActionPermissions.ADD_PERMISSION,
            },
            params={"name": name},
        )
        return RemovePermissionResultModel(**result.json())

    def get_permission(self, name: str, token: str) -> GetPermissionResultModel:
        result = self.__get(
            request_url=self.PermissionsUrls.GET_PERMISSION,
            params={"name": name},
            headers={
                "token": token,
                "permission": self.ActionPermissions.ADD_PERMISSION,
            },
        )
        return GetPermissionResultModel(**result.json())

    def get_all_permission(
        self, token: str, page: int = 1
    ) -> GetListOfPermissionsResultModel:
        result = self.__get(
            request_url=self.PermissionsUrls.GET_ALL_PERMISSION,
            params={"page": page},
            headers={
                "token": token,
                "permission": self.ActionPermissions.GET_ALL_PERMISSION,
            },
        )
        output: dict = result.json()
        output.update({"page": page})
        return GetListOfPermissionsResultModel(**output)

    def add_role(
        self, name: str, description: str, permissions_list: List[str], token: str
    ) -> AddRoleResultModel:
        result = self.__post(
            request_url=self.RoleUrl.ADD_ROLE,
            body=AddRoleDataModel(
                role_name=name,
                description=description,
                permission_list=permissions_list,
            ).dict(),
            headers={"token": token, "permission": self.ActionPermissions.ADD_ROLE},
        )
        return AddRoleResultModel(**result.json())

    def get_role(self, name: str, token: str) -> GetRoleResultModel:
        result = self.__get(
            request_url=self.RoleUrl.GET_ROLE,
            headers={"token": token, "permission": "get_role"},
            params={"role_name": name},
        )
        return GetRoleResultModel(**result.json())

    def update_role(
        self,
        name: str,
        new_permissions: List[str],
        token: str,
        update_all_users_role: bool = False,
    ) -> UpdateRoleResponseModel:
        result = self.__put(
            request_url=self.RoleUrl.UPDATE_PERMISSION,
            body=UpdateRolePermissionLists(
                role_name=name,
                permissions=new_permissions,
                update_user_roles=update_all_users_role,
            ).dict(),
            headers={"token": token, "permission": self.ActionPermissions.UPDATE_ROLE},
        )
        return UpdateRoleResponseModel(**result.json())

    def get_all_roles(self, token: str, page: int = 1) -> GetAllRolesResponseModel:
        result = self.__get(
            request_url=self.RoleUrl.GET_ALL_ROLE,
            headers={"token": token, "permission": self.ActionPermissions.GET_ROLE},
            params={"page": page},
        )
        output: dict = result.json()
        output.update({"page": page})
        return GetAllRolesResponseModel(**output)

    def remove_role(self, name: str, token: str) -> RemoveRoleResultModel:
        result = self.__delete(
            request_url=self.RoleUrl.REMOVE_ROLE,
            headers={"token": token, "permission": self.ActionPermissions.REMOVE_ROLE},
            params={"role_name": name},
        )
        return RemoveRoleResultModel(**result.json())

    def add_user_role(
        self,
        user_id: str,
        role_list: List[str],
        token: str,
        permissions_list: List[str] = None,
    ) -> AddUserRolePermissionResponseModel:
        if permissions_list is None:
            permissions_list = []
        result = self.__post(
            request_url=self.UserRoleUrl.ADD_USER_ROLE,
            body=AddUserRolePermissionBodyModel(
                user_id=user_id, roles_list=role_list, permissions_list=permissions_list
            ).dict(),
            headers={
                "token": token,
                "permission": self.ActionPermissions.ADD_USER_ROLE,
            },
        )

        return AddUserRolePermissionResponseModel(**result.json())

    def update_user_role(
        self,
        user_id: str,
        role_list: List[str],
        token: str,
        permissions_list: List[str] = None,
    ):
        if permissions_list is None:
            permissions_list = []
        result = self.__put(
            request_url=self.UserRoleUrl.UPDATE_USER_ROLE,
            body=UpdateUserRolePermissionBodyModel(
                user_id=user_id, roles_list=role_list, permissions_list=permissions_list
            ).dict(),
            headers={
                "token": token,
                "permission": self.ActionPermissions.UPDATE_USER_ROLE,
            },
        )
        return UpdateUserRoleResponseModel(**result.json())

    def remove_user_role(
        self,
        user_id: str,
        token: str,
        role_list: List[str] = None,
        permissions_list: List[str] = None,
    ):
        if permissions_list is None:
            permissions_list = []
        if role_list is None:
            role_list = []
        result = self.__delete(
            request_url=self.UserRoleUrl.DELETE_USER_ROLE,
            headers={
                "token": token,
                "permission": self.ActionPermissions.DELETE_USER_ROLE,
            },
            body=RemoveUserRolePermission(
                user_id=user_id,
                permissions_to_remove_list=permissions_list,
                roles_to_remove_list=role_list,
            ).dict(),
        )
        return RemoveUserRolePermissionResponseModel(**result.json())

    def get_user_role(self, user_id: str, token: str) -> UserRole:
        result = self.__get(
            request_url=self.UserRoleUrl.GET_USER_ROLE,
            headers={
                "token": token,
                "permission": self.ActionPermissions.GET_USER_ROLE,
            },
            params={"user_id": user_id},
        )
        return UserRole(**result.json())

    def get_all_user_role(
        self, token: str, page: int = 1
    ) -> GetAllUserRolePermissionResponseModel:
        result = self.__get(
            request_url=self.UserRoleUrl.GET_ALL_USER_ROLE,
            headers={
                "token": token,
                "permission": self.ActionPermissions.GET_ALL_PERMISSION,
            },
            params={"page": page},
        )
        output: dict = result.json()
        output.update({"page": page})

        return GetAllUserRolePermissionResponseModel(**output)

    def add_trusted_service(
        self, service_name: str, token: str
    ) -> AddTrustedServiceResponseModel:
        result = self.__post(
            request_url=self.TrustedServiceURL.ADD,
            headers={"token": token, "permission": "add_trusted_service"},
            body=AddTrustedServiceBodyModel(**{"service_name": service_name}).dict(),
        )
        return AddTrustedServiceResponseModel(**result.json())

    def remove_trusted_service(
        self, service_name: str, token: str
    ) -> RemoveTrustedServiceResponseModel:
        result = self.__delete(
            request_url=self.TrustedServiceURL.DELETE,
            headers={"token": token, "permission": "delete_trusted_service"},
            params={"service_name": service_name},
        )
        return RemoveTrustedServiceResponseModel(**result.json())

    def get_trusted_service(self, service_name: str, token: str) -> TrustedServiceModel:
        result = self.__get(
            request_url=self.TrustedServiceURL.GET,
            headers={"token": token, "permission": "get_trusted_service"},
            params={"service_name": service_name},
        )
        return TrustedServiceModel(**result.json())

    def get_all_trusted_service(
        self, token: str, page: int = 1
    ) -> GetAllTrustedServiceResponseModel:
        result = self.__get(
            request_url=self.TrustedServiceURL.GET_ALL,
            headers={"token": token, "permission": "get_trusted_service"},
            params={"page": page},
        )
        output: dict = result.json()
        output.update({"page": page})
        return GetAllTrustedServiceResponseModel(**output)

    def renew_trusted_service(
        self, service_name: str, token: str
    ) -> NewSecretTrustedServiceResponseModel:
        result = self.__put(
            request_url=self.TrustedServiceURL.RENEW,
            headers={"token": token, "permission": "renew_trusted_service"},
            params={"service_name": service_name},
        )
        return NewSecretTrustedServiceResponseModel(**result.json())

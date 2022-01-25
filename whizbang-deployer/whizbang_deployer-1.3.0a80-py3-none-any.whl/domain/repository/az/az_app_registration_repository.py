from abc import ABC, abstractmethod

from whizbang.data.az_cli_context import AzCliContext
from whizbang.domain.models.active_directory.app_registration import AppRegistration, AppRegistrationClientSecret
from whizbang.domain.repository.az.az_active_directory_repository import AzActiveDirectoryRepository
from whizbang.domain.repository.az.az_repository_base import IAzRepository, AzRepositoryBase

import logging
_log = logging.getLogger(__name__) 


class IAzAppRegistrationRepository(IAzRepository):
    """"""

    @abstractmethod
    def create(self, app_registration: AppRegistration) -> AppRegistration:
        """"""

    @abstractmethod
    def get_by_display_name(self, display_name) -> AppRegistration:
        """"""

    @abstractmethod
    def get_app_secrets(self, app_id) -> 'list[AppRegistrationClientSecret]':
        """"""

    @abstractmethod
    def reset_client_secret(self, app_id, password: str = None) -> str:
        """"""

    @abstractmethod
    def add_group_members_as_owner(self, app_id: str, group_object_id: str) -> None:
        """"""

class AzAppRegistrationRepository(AzRepositoryBase, IAzAppRegistrationRepository):
    def __init__(self, context: AzCliContext, az_active_directory_repository: AzActiveDirectoryRepository):
        AzRepositoryBase.__init__(self, context)
        self.__az_active_directory_repository = az_active_directory_repository

    @property
    def _resource_provider(self) -> str:
        return 'ad app'

    # stateful - will not create a new app reg w/ the same name, will create a new secret if a password is provided (keyid will be different)
    def create(self, app_registration: AppRegistration) -> AppRegistration:

        if app_registration.client_secret is None or app_registration.client_secret.value is None:
            _log.warning(f'app registration {app_registration.name} can not be saved because client_secret value (password) is required')
            return app_registration

        result = self._execute(
            f'create'
            f' --display-name {app_registration.name}'
            f' --password {app_registration.client_secret.value}'
            f' --credential-description {app_registration.client_secret.description}'
        ).results

        app_registration.app_id = result['appId']
        password_credentials = result['passwordCredentials']
        specific_password_credential = next(pc for pc in password_credentials if
                                            pc['customKeyIdentifier'] == app_registration.client_secret.description)

        app_registration.client_secret.key_id = specific_password_credential['keyId']
        app_registration.client_secret.end_date = specific_password_credential['endDate']
        app_registration.client_secret.start_date = specific_password_credential['startDate']

        return app_registration

    # todo future: update method

    # not working - query is not being formatted correctly in az class/package
    def get_by_display_name(self, display_name) -> AppRegistration:
        raise NotImplementedError

        # query = f'list --query [?displayName=={display_name}] --all'
        #
        # result = self._execute(query)
        #
        # if result is None:
        #     return None
        #
        # if len(result) > 1:
        #     raise Exception(f'more than one app registration with display-name: {display_name} found')
        #
        # app_id = result[0]['appId']
        # if len(result) == 1:
        #     return AppRegistration(
        #         name=display_name,
        #         app_id=app_id
        #     )

    def get_app_secrets(self, app_id) -> 'list[AppRegistrationClientSecret]':
        secrets = []
        result = self._execute(
            f'credential list --id {app_id}'
        ).results

        for secret in result:
            value = None if secret['value'] == 'null' else secret['value']
            secrets.append(AppRegistrationClientSecret(
                value=value,
                end_date=secret['endDate'],
                start_date=secret['startDate'],
                key_id=secret['keyId']
            ))

        return secrets

    def reset_client_secret(self, app_id, password: str = None) -> str:
        password_str_arg = f' --password {password}' if password is not None else ''

        result = self._execute(
            f'credential reset --id {app_id}{password_str_arg}'
        ).results

        return result['password']

    def add_owner(self, app_id: str, owner_object_id: str):
        # todo: try catch logic

        result = self._execute(
            f'owner add'
            f' --id {app_id}'
            f' --owner-object-id {owner_object_id}'
        ).results

        return result

    def add_group_members_as_owner(self, app_id: str, group_object_id: str) -> None:
        group_members = self.__az_active_directory_repository.get_group_members(group_object_id)
        for group_member in group_members:
            if group_member.object_type == 'User':
                self.add_owner(app_id=app_id, owner_object_id=group_member.object_id)
                _log.info(f'added {group_member.display_name} with object id: {group_member.object_id} '
                      f'as owner to app registration with app id: {app_id}')
            else:
                _log.warning(f'adding object of type {group_member.object_type} as owner to service principal is not supported')





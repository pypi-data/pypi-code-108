import logging
from enum import Enum
from uuid import UUID
from typing import Optional, Set

import fastapi.security

from ..protocol import AccessDeniedException

logger = logging.getLogger(__name__)


class Action(Enum):
    ADMIN = 'admin'
    READ_BACKUP = 'read_backup'
    CREATE_BACKUP = 'create_backup'
    DELETE_BACKUP = 'delete_backup'
    LIST = 'list'


class SimpleAuthorization:

    def __init__(self, device_id: UUID, self_permissions: Set[Action], global_permissions: Set[Action]):
        self.client_id = device_id
        self.self_permissions = self_permissions
        self.global_permissions = global_permissions

    def __call__(self, device_id: Optional[UUID], action: Action):
        # TODO actually use this
        if device_id == self.client_id:
            if action not in self.self_permissions:
                raise AccessDeniedException(
                    f'Client {self.client_id} does not have "{action.value}" permission for {device_id}')
        if device_id != self.client_id:
            permission_for = device_id if device_id is not None else 'global'
            if action not in self.global_permissions:
                raise AccessDeniedException(
                    f'Client {self.client_id} does not have "{action.value}" permission for {permission_for}')


AUTHENTICATOR = fastapi.security.HTTPBasic


def get_client_id(credentials: SimpleAuthorization) -> str:
    return str(credentials.client_id)

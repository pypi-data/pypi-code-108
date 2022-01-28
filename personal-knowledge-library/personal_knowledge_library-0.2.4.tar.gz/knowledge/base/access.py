# -*- coding: utf-8 -*-
# Copyright © 2021 Wacom. All rights reserved.
from typing import List


class AccessRight(object):
    """
    Access rights for entities within a tenant.

    Parameters
    ----------
    read: bool (default := False)
        Read access for entity within tenant.
    write: bool (default := False)
        Write access for entity within tenant.
    delete: bool (default := False)
        Delete access for entity within tenant.
    """
    READ: str = "Read"
    WRITE: str = "Write"
    DELETE: str = "Delete"

    def __init__(self, read: bool = False, write: bool = False, delete: bool = False):
        self.__read: bool = read
        self.__write: bool = write
        self.__delete: bool = delete

    @property
    def read(self) -> bool:
        """Read access for tenant."""
        return self.__read

    @read.setter
    def read(self, value: bool):
        self.__read = value

    @property
    def write(self) -> bool:
        """Write access for tenant."""
        return self.__write

    @write.setter
    def write(self, value: bool):
        self.__write = value

    @property
    def delete(self) -> bool:
        """Delete access for tenant."""
        return self.__delete

    @delete.setter
    def delete(self, value: bool):
        self.__delete = value

    def __repr__(self):
        result: str = '['
        prefix: str = ''
        if self.read:
            result += AccessRight.READ
            prefix = ", "
        if self.write:
            result += prefix + AccessRight.WRITE
        if self.delete:
            result += AccessRight.DELETE
        result += ']'
        return result

    def to_list(self) -> List[str]:
        """
        Converts the access to list of properties.

        Returns
        -------
        access_list: List[str]
            List of rights
        """
        rights: List[str] = []
        if self.read:
            rights.append(TenantAccessRight.READ)
        if self.write:
            rights.append(TenantAccessRight.WRITE)
        if self.delete:
            rights.append(TenantAccessRight.DELETE)
        return rights


class TenantAccessRight(AccessRight):
    """
    TenantAccessRight
    -----------------
    Access rights for entities within a tenant.

    Parameters
    ----------
    read: bool (default := False)
        Read access for entity within tenant.
    write: bool (default := False)
        Write access for entity within tenant.
    delete: bool (default := False)
        Delete access for entity within tenant.
    """

    def __init__(self, read: bool = False, write: bool = False, delete: bool = False):
        super().__init__(read, write, delete)

    @classmethod
    def parse(cls, param: List[str]) -> 'TenantAccessRight':
        """
        Converts the access to list of properties.

        Parameters
        ----------
        param: List[str]
            List of rights

        Returns
        -------
        tenant_rights: TenantAccessRight
            Instantiated rights.
        """
        rights: TenantAccessRight = TenantAccessRight()
        rights.read = TenantAccessRight.READ in param
        rights.write = TenantAccessRight.WRITE in param
        rights.delete = TenantAccessRight.DELETE in param
        return rights


class GroupAccessRight(AccessRight):
    """
    GroupAccessRight
    -----------------
    Group rights for entities within a group.

    Parameters
    ----------
    read: bool (default := False)
        Read access for entity within group.
    write: bool (default := False)
        Write access for entity within group.
    delete: bool (default := False)
        Delete access for entity within group.
    """

    def __init__(self, read: bool = False, write: bool = False, delete: bool = False):
        super().__init__(read, write, delete)

    @classmethod
    def parse(cls, param: List[str]) -> 'GroupAccessRight':
        """
        Converts the access to list of properties.

        Parameters
        ----------
        param: List[str]
            List of rights

        Returns
        -------
        group_rights: GroupAccessRight
            Instantiated rights.
        """
        rights: GroupAccessRight = GroupAccessRight()
        rights.read = GroupAccessRight.READ in param
        rights.write = GroupAccessRight.WRITE in param
        rights.delete = GroupAccessRight.DELETE in param
        return rights

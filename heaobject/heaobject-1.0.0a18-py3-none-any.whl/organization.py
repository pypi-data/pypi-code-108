from .root import AbstractDesktopObject
from typing import Optional, List


class Organization(AbstractDesktopObject):
    """
    Represents a directory in the HEA desktop.
    """

    def __init__(self):
        super().__init__()
        # id is a super field
        self.__aws_account_ids: List[str] = []  # allow org to have multiple aws accounts
        self.__principal_investigator_id: Optional[str] = None  # this would be a people id
        self.__manager_ids: List[str] = []  # list of user ids to be managers
        self.__member_ids: List[str] = []  # list of user ids to be members
        # super's name and display name would be used as org name(required)

    @property
    def aws_account_ids(self) -> List[str]:
        """
        The list of REST aws account ids that are served by this organization. The property's setter accepts a List of strings
        """
        return [i for i in self.__aws_account_ids]

    @aws_account_ids.setter
    def aws_account_ids(self, value: List[str]) -> None:
        if value is None:
            raise ValueError('value cannot be None')
        if not all(isinstance(i, str) for i in value):
            raise TypeError('value must contain all List of strings ')
        self.__aws_account_ids = [i for i in value]

    def add_aws_account_id(self, value: str) -> None:
        """
        Adds a REST resource to the list of resources that are served by this component.
        :param value: a Resource object.
        """
        if not isinstance(value, str):
            raise TypeError('value must be a string')
        self.__aws_account_ids.append(value)

    def remove_aws_account_id(self, value: str) -> None:
        """
        Removes a REST aws_account_id from the list of ids that are served by this organization. Ignores None values.
        :param value:  str representing the aws account id.
        """
        if not isinstance(value, str):
            raise TypeError('value must be a string')
        self.__aws_account_ids.remove(value)

    @property
    def principal_investigator_id(self) -> Optional[str]:
        """
        The principal investigator People ID.
        """
        return self.__principal_investigator_id

    @principal_investigator_id.setter
    def principal_investigator_id(self, principal_investigator_id: Optional[str]) -> None:
        self.__principal_investigator_id = str(
            principal_investigator_id) if principal_investigator_id is not None else None

    @property
    def manager_ids(self) -> List[str]:
        """
        The organization manager ids.
        """
        return [i for i in self.__manager_ids] if self.__manager_ids else []

    @manager_ids.setter
    def manager_ids(self, manager_ids: List[str]) -> None:
        self.__manager_ids = [i for i in manager_ids] if manager_ids is not None else []

    def add_manager_id(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError('value must be a string')
        self.__manager_ids.append(value)

    def remove_manager_id(self, value: str) -> None:
        """
        Removes a REST manager id from the list of ids that are served by this organization. Ignores None values.
        :param value:  str representing the manager id.
        """
        if not isinstance(value, str):
            raise TypeError('value must be a string')
        self.__manager_ids.remove(value)

    @property
    def member_ids(self) -> List[str]:
        """
        The organization member ids.
        """
        return [i for i in self.__member_ids]

    @member_ids.setter
    def member_ids(self, member_ids: List[str]) -> None:
        self.__member_ids = [i for i in member_ids] if member_ids is not None else []

    def add_member_id(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError('value must be a string')
        self.__member_ids.append(value)

    def remove_member_id(self, value: str) -> None:
        """
        Removes a REST member id from the list of member ids that are served by this organization. Ignores None values.
        :param value: a str representing the member id.
        """
        if not isinstance(value, str):
            raise TypeError('value must be a string')
        self.__member_ids.remove(value)

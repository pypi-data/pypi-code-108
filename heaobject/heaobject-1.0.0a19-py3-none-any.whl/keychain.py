"""
Classes supporting the management of user credentials and certificates.
"""
from typing import Optional
import abc
from heaobject import root


class Credentials(root.AbstractDesktopObject, abc.ABC):
    """
    Stores a user's secrets, passwords, and keys, and makes them available to applications.
    """
    def __init__(self):
        super().__init__()
        self.__account: Optional[str] = None
        self.__where: Optional[str] = None
        self.__password: Optional[str] = None

    @property  # type: ignore
    def account(self) -> Optional[str]:
        """
        The username or account name.
        """
        return self.__account

    @account.setter  # type: ignore
    def account(self, account: Optional[str]) -> None:
        self.__account = str(account) if account is not None else None

    @property  # type: ignore
    def where(self) -> Optional[str]:
        """
        The hostname, URL, service, or other location of the account.
        """
        return self.__where

    @where.setter  # type: ignore
    def where(self, where: Optional[str]) -> None:
        self.__where = str(where) if where is not None else None

    @property  # type: ignore
    def password(self) -> Optional[str]:
        """
        The account password or secret
        """
        return self.__password

    @password.setter  # type: ignore
    def password(self, password: Optional[str]) -> None:
        self.__password = str(password) if password is not None else None


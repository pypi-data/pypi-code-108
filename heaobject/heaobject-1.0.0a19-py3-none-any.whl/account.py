from typing import Optional
from . import root
from abc import ABC


class Account(root.AbstractDesktopObject, ABC):
    """
    Abstract base class for user accounts.
    """
    pass


class AWSAccount(Account):
    """
    Represents an AWS account in the HEA desktop. Contains functions that allow access and setting of the value. Below are the attributes that can be accessed.

    account_id (str)              : 1234567890
    account_name (str)            : HCI - name
    full_name (str)               : john smith
    phone_number (str)            : 123-456-7890
    alternate_contact_name (str)  : bob smith
    alternate_email_address (str) : 123@hciutah.edu
    alternate_phone_number (str)  : 123-456-7890
    """
    def __init__(self):
        super().__init__()
        self.__account_id: Optional[str] = None
        self.__account_name: Optional[str] = None
        self.__full_name: Optional[str] = None
        self.__phone_number: Optional[str] = None
        self.__alternate_contact_name: Optional[str] = None
        self.__alternate_email_address: Optional[str] = None
        self.__alternate_phone_number: Optional[str] = None

    @property
    def account_id(self) -> Optional[str]:
        """Returns the numerical account identifier"""
        return self.__account_id

    @account_id.setter
    def account_id(self, account_id: Optional[str]) -> None:
        """Sets the numerical account identifier"""
        self.__account_id = str(account_id) if account_id is not None else None

    @property
    def account_name(self) -> Optional[str]:
        """Returns the name of the account, not the full name of the person"""
        return self.__account_name

    @account_name.setter
    def account_name(self, account_name: Optional[str]) -> None:
        """Sets the name of the account, not the full name of the person"""
        self.__account_name = str(account_name) if account_name is not None else None

    @property
    def full_name(self) -> Optional[str]:
        """Returns the full name of person associated with this account"""
        return self.__full_name

    @full_name.setter
    def full_name(self, full_name: Optional[str]) -> None:
        """Sets the full name of person associated with this account"""
        self.__full_name = str(full_name) if full_name is not None else None

    @property
    def phone_number(self) -> Optional[str]:
        """Returns the phone number associated with the account"""
        return self.__phone_number

    @phone_number.setter
    def phone_number(self, phone_number: Optional[str]) -> None:
        """Sets the phone number associated with the account"""
        self.__phone_number = str(phone_number) if phone_number is not None else None

    @property
    def alternate_contact_name(self) -> Optional[str]:
        """Returns the alternate contact full name of person associated with this account"""
        return self.__alternate_contact_name

    @alternate_contact_name.setter
    def alternate_contact_name(self, alternate_contact_name: Optional[str]) -> None:
        """Sets the alternate contact full name of person associated with this account"""
        self.__alternate_contact_name = str(alternate_contact_name) if alternate_contact_name is not None else None

    @property
    def alternate_email_address(self) -> Optional[str]:
        """Returns the alternate contact phone number associated with the account"""
        return self.__alternate_email_address

    @alternate_email_address.setter
    def alternate_email_address(self, alternate_email_address: Optional[str]) -> None:
        """Sets the alternate contact phone number associated with the account"""
        self.__alternate_email_address = str(alternate_email_address) if alternate_email_address is not None else None

    @property
    def alternate_phone_number(self) -> Optional[str]:
        """Returns the alternate contact phone number associated with the account"""
        return self.__alternate_phone_number

    @alternate_phone_number.setter
    def alternate_phone_number(self, alternate_phone_number: Optional[str]) -> None:
        """Sets the alternate contact phone number associated with the account"""
        self.__alternate_phone_number = str(alternate_phone_number) if alternate_phone_number is not None else None


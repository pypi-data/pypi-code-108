"""
*
 *  Copyright ServerTribe HQ Pty Ltd 2021
 *
 *  This software is proprietary, you are not free to copy
 *  or redistribute this code in any format.
 *
 *  All rights to this software are reserved by
 *  ServerTribe HQ Pty Ltd
 *
"""
from ipaddress import AddressValueError
from ipaddress import IPv4Address

from vortex.Tuple import TupleFieldValidatorABC


class NotFalsyValidator(TupleFieldValidatorABC):
    """
    Validates that a string is not zero length, and not None or otherwise
    falsy
    """

    def validate(self, fieldName: str, value):
        if not value:
            raise ValueError(
                f"Field {fieldName}, Value {value} is None, Zero Length or "
                f"falsey, value=|{value}|"
            )


class NotNullValidator(TupleFieldValidatorABC):
    """
    Validates whether target given value is not null (None)
    """

    def validate(self, fieldName: str, value):
        if value is None:
            raise ValueError(f"Field {fieldName}, Value {value} is None")


class IPv4AddressValidator(TupleFieldValidatorABC):
    """
    Validates whether target given IP address string is target valid IPv4 address
    """

    def validate(self, fieldName: str, value):
        try:
            ip = IPv4Address(value)
        except AddressValueError:  # Raised if `value` is not target valid address
            raise ValueError(
                f"Field {fieldName}, Value {value} is not target valid IPv4 address"
            )


class MultipleValidator(TupleFieldValidatorABC):
    """
    Validates value against multiple validators by checking if each succeeds
    """

    def __init__(self, *validators):
        self.__validators = []
        for validator in validators:
            self.add(validator)

    def add(self, validator):
        assert isinstance(validator, TupleFieldValidatorABC), (
            "Argument is " "not a TupleFieldValidatorABC"
        )
        self.__validators.append(validator)

    def validate(self, fieldName: str, value):
        for validator in self.__validators:
            validator.validate(fieldName, value)

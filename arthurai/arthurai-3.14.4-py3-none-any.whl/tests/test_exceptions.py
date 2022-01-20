
import pytest

from arthurai.common.exceptions import *


def test_user_value_error_is_arthur_user_error():
    try:
        raise UserValueError("bad value")
    except ArthurUserError:
        print("expected exception caught")


def test_user_value_error_is_arthur_error():
    try:
        raise UserValueError("bad value")
    except ArthurError:
        print("expected exception caught")


def test_user_value_error_is_value_error():
    try:
        raise UserValueError("bad value")
    except ValueError:
        print("expected exception caught")


def test_internal_value_error_is_arthur_internal_error():
    try:
        raise InternalValueError("bad value")
    except ArthurInternalError:
        print("expected exception caught")


def test_internal_value_error_is_arthur_error():
    try:
        raise InternalValueError("bad value")
    except ArthurError:
        print("expected exception caught")


def test_internal_value_error_is_value_error():
    try:
        raise InternalValueError("bad value")
    except ValueError:
        print("expected exception caught")


def test_arthur_internal_error_reraised():
    @arthur_excepted("expected failure")
    def internal_error():
        raise ArthurInternalError

    with pytest.raises(ArthurInternalError):
        internal_error()


def test_arthur_user_error_reraised():
    @arthur_excepted("expected failure")
    def user_error():
        raise ArthurUserError

    with pytest.raises(ArthurUserError):
        user_error()


def test_arthur_external_error():
    @arthur_excepted("expected failure")
    def external_error():
        raise ValueError

    with pytest.raises(ArthurInternalError):
        external_error()


def test_missing_arguments():
    @arthur_excepted("expected failure")
    def my_func(pos_only, pos_or_key,  default_param=None, *, key_only):
        pass

    # missing pos_only
    with pytest.raises(MissingParameterError):
        my_func(pos_or_key=None, key_only=None)

    # missing pos_or_key
    with pytest.raises(MissingParameterError):
        my_func(None, key_only=None)

    # missing key_only
    with pytest.raises(MissingParameterError):
        my_func(None, None)

    # valid with keyword
    assert my_func(None, pos_or_key=None, key_only=None) is None

    # valid with positional
    assert my_func(None, None, key_only=None) is None

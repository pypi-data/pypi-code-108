import pytest

from sym.sdk.errors import SymIntegrationErrorEnum
from sym.sdk.integrations.pagerduty import PagerDutyError, is_on_call, users_on_call


class FakeError(SymIntegrationErrorEnum):
    SIMPLE = ("foobar {missing}", "test_hint")


class TestPagerdutyInterface:
    def test_is_on_call(self):
        user = {"username": "jon.doe@simi.org"}
        assert is_on_call(user) is None

    def test_users_on_call(self):
        assert users_on_call() is None

    def test_error_code(self):
        with pytest.raises(PagerDutyError) as error_info:
            raise PagerDutyError.UNKNOWN_ERROR({"a": "b"})

        assert error_info.value.error_code == "PagerDutyError:UNKNOWN_ERROR"
        assert error_info.value.hint == "Please contact support."
        assert error_info.value.params == {"a": "b"}

    def test_poor_formatting(self):
        with pytest.raises(FakeError) as error_info:
            raise FakeError.SIMPLE({"a": "b"})

        assert error_info.value.error_code == "FakeError:SIMPLE"
        assert error_info.value.hint == "test_hint"
        assert error_info.value.message == "foobar {missing}"

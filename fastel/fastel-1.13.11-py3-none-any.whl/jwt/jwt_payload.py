from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Sequence, Type
from uuid import uuid4


class PayloadDesc:
    """create a constant value getter"""

    def __init__(self, value: Any = None):
        self._value = value

    def __get__(self, instance: Any, cls: Any) -> Any:
        return self._value


class ClientAttrDesc(PayloadDesc):
    """read the value from instance.client's attribute"""

    def __init__(
        self, attr_name: str, default_value: Any = None, transform_method: Any = None
    ):
        self._attr_name = attr_name
        self._default_value = default_value
        self._transform_method = transform_method

    def __get__(self, instance: Any, cls: Any) -> Any:
        value = getattr(instance.client, self._attr_name, None)
        if value is None:
            return self._default_value
        if self._transform_method:
            return self._transform_method(value)
        return value


class DataValueDesc(PayloadDesc):
    """read the value from instance.data, which is a dict"""

    def __init__(
        self, attr_name: str, default_value: Any = None, transform_method: Any = None
    ):
        self._attr_name = attr_name
        self._default_value = default_value
        self._transform_method = transform_method

    def __get__(self, instance: Any, cls: Any) -> Any:
        value = instance.data.get(self._attr_name, None)
        if value is None:
            return self._default_value
        if self._transform_method:
            return self._transform_method(value)
        return value


class IatDesc(PayloadDesc):
    """get a timestamp"""

    def __get__(self, instance: Any, cls: Any) -> int:
        now = datetime.now(timezone.utc)
        return int(now.timestamp())


class JtiDesc(PayloadDesc):
    """get a random uuid string"""

    def __get__(self, instance: Any, cls: Any) -> str:
        return uuid4().__str__()


class ExpDesc(PayloadDesc):
    """get a expiration timestamp with duration"""

    exp_field: str = "default_access_exp"
    duration_unit: str = "minutes"
    default_exp: int = 120

    def __init__(self, exp_field: str, dur_unit: str, default_exp: int) -> None:
        self._exp_field = exp_field
        self._dur_unit = dur_unit
        self._default_exp = default_exp

    def __get__(self, instance: Any, cls: Any) -> int:
        exp = instance.client.get(self._exp_field, self._default_exp)
        now = datetime.now(timezone.utc)
        kwargs = {self._dur_unit: exp}
        duration = timedelta(**kwargs)
        real_exp = int((now + duration).timestamp())
        return real_exp


class MetaBuilderType(type):
    def __new__(  # type: ignore
        cls, name: str, bases: Sequence[Any], attrs: Dict[Any, Any]
    ) -> Type["JWTPayloadBuilder"]:
        attrs["_payloads"] = [
            key for key, value in attrs.items() if isinstance(value, PayloadDesc)
        ]
        return super().__new__(cls, name, bases, attrs)  # type: ignore


class JWTPayloadBuilder(metaclass=MetaBuilderType):
    _payloads: Sequence[str]

    def __init__(self, client: Any, data: Any) -> None:
        self.client = client
        self.data = data

    def get_payload(self) -> Dict[str, Any]:
        payloads = {}
        for payload in self._payloads:
            payloads[payload] = getattr(self, payload)

        return payloads

"""Helper objects and methods for the schemas.py` file."""

from datetime import datetime, timezone
from ipaddress import IPv4Address
from typing import Optional

from iso4217 import Currency
from pydantic import AnyHttpUrl, EmailStr, Field, validator
from pydantic.datetime_parse import parse_datetime

from .inbound_schemas import Timestamp as InboundTimestamp
from .outbound_schemas import Customer as OutboundCustomer
from .outbound_schemas import Data as OutboundData
from .outbound_schemas import NotificationUrl as OutboundNotificationUrl
from .outbound_schemas import Redirect as OutboundRedirect
from .outbound_schemas import Timestamp as OutboundTimestamp


def validate_currency(v: str) -> str:
    """Validate the currency so it's ISO4217 compatible."""
    try:
        Currency(v)
    except ValueError as exc:
        raise ValueError("Must be a valid ISO-4217, 3-character currency.") from exc

    return v


class UTCDatetime(datetime):
    """Custom datetime type that formats to 'Z' style."""

    @classmethod
    def __get_validators__(cls):
        """Provide validators for the datetime field."""
        yield parse_datetime  # default pydantic behavior
        yield cls.ensure_tzinfo

    @classmethod
    def ensure_tzinfo(cls, v):
        """Add timezone information to datetime objects."""
        # if TZ isn't provided, we assume UTC
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        # else we convert to utc
        return v.astimezone(timezone.utc)

    @staticmethod
    def to_str(dt: datetime) -> str:
        """Format the datetime object to a string."""
        return dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


class Timestamp(OutboundTimestamp, InboundTimestamp):
    """Timestamp model."""

    __root__: UTCDatetime = Field(
        ..., description="A timestamp of the transaction", example="2021-04-23T07:41:25.519947Z"
    )

    class Config:
        """Config for Timestamp."""

        # force the "Z" timezone formatting
        json_encoders = {datetime: UTCDatetime.to_str}


class Redirect(OutboundRedirect):
    """Override generated Redirect schema to validate URL field."""

    url: AnyHttpUrl = Field(
        ...,
        description="URL the the shopper must be redirected to in order to proceed.",
        example="https://test.yourdomain.com/link?",
    )


class Customer(OutboundCustomer):
    """Optional object sent if Partner requires customer data."""

    # Override generated Customer schema to validate email and ip.
    email: Optional[EmailStr] = Field(None, description="The customer's email address.", example="name@example.com")

    @validator("ip")
    @classmethod
    def ip_ipv4(cls, v: Optional[str]) -> Optional[str]:
        """Validate the IP address."""
        if v is None:
            return None

        try:
            IPv4Address(v)
        except ValueError as exc:
            raise ValueError("value is not a valid IPv4 or IPv6 address.") from exc

        return v


class Data(OutboundData):
    """Optional object that can be used for billing/shipping information."""

    # Override generated Data schema to validate email and ip via the Customer schema.
    customer: Optional[Customer] = None


class NotificationUrl(OutboundNotificationUrl):
    """Override generated NotificationUrl schema to validate the __root__ URL field."""

    __root__: AnyHttpUrl = Field(
        ...,
        description=(
            "The Peach provided URL at which the Partner is required to send notifications/webhooks when the"
            " transaction status is updated."
        ),
        example="https://peachnotify.com",
    )

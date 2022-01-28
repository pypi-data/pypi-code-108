"""Definitions of the [pydantic models](https://pydantic-docs.helpmanual.io/usage/models/)."""

from datetime import datetime
from typing import Optional

from peachpayments_partner.fixtures import (
    CANCEL_REQUEST,
    CANCEL_RESPONSE,
    DEBIT_REQUEST,
    DEBIT_RESPONSE,
    ERROR_400_RESPONSE,
    ERROR_RESPONSE,
    REFUND_REQUEST,
    REFUND_RESPONSE,
    STATUS_RESPONSE,
    WEBHOOK_REQUEST,
)
from pydantic import validator

from .helpers import Customer, Data, NotificationUrl, Redirect, Timestamp, UTCDatetime, validate_currency
from .inbound_schemas import Currency as InboundCurrency
from .inbound_schemas import WebhookRequest as InboundWebhookRequest
from .outbound_schemas import CancelRequest as OutboundCancelRequest
from .outbound_schemas import CancelResponse as OutboundCancelResponse
from .outbound_schemas import Currency as OutboundCurrency
from .outbound_schemas import DebitRequest as OutboundDebitRequest
from .outbound_schemas import DebitResponse as OutboundDebitResponse
from .outbound_schemas import Error400Response as OutboundError400Response
from .outbound_schemas import ErrorResponse as OutboundErrorResponse
from .outbound_schemas import PaymentType as OutboundPaymentType
from .outbound_schemas import RefundRequest as OutboundRefundRequest
from .outbound_schemas import RefundResponse as OutboundRefundResponse
from .outbound_schemas import StatusResponse as OutboundStatusResponse


class DebitRequest(OutboundDebitRequest):
    """Definition of the debit request."""

    customer: Optional[Customer] = None
    billing: Optional[Data] = None
    shipping: Optional[Data] = None
    timestamp: Timestamp
    notificationUrl: NotificationUrl

    @validator("currency")
    @classmethod
    def currency_iso4217(cls, v: OutboundCurrency) -> str:
        """Validate the currency so it's ISO4217 compatible."""
        return validate_currency(v.__root__)

    @validator("paymentType")
    @classmethod
    def payment_type_db(cls, v: OutboundPaymentType) -> OutboundPaymentType:
        """Paymentype needs to equal "DB" for DebitRequest."""
        if v.value != "DB":
            raise ValueError("Wrong payment type for the debit request")

        return v

    class Config:
        """Config for DebitRequest."""

        # Example of a valid request
        schema_extra = {"example": DEBIT_REQUEST}
        # force the "Z" timezone formatting
        json_encoders = {datetime: UTCDatetime.to_str}


class DebitResponse(OutboundDebitResponse):
    """Definition of the debit response."""

    timestamp: Timestamp
    redirect: Redirect

    @validator("currency")
    @classmethod
    def currency_iso4217(cls, v: OutboundCurrency) -> str:
        """Validate the currency so it's ISO4217 compatible."""
        return validate_currency(v.__root__)

    class Config:
        """Config for DebitResponse."""

        # Example of a valid response
        schema_extra = {"example": DEBIT_RESPONSE}
        # force the "Z" timezone formatting
        json_encoders = {datetime: UTCDatetime.to_str}


class RefundRequest(OutboundRefundRequest):
    """Definition of the refund request."""

    timestamp: Timestamp
    customer: Optional[Customer] = None
    notificationUrl: NotificationUrl

    @validator("currency")
    @classmethod
    def currency_iso4217(cls, v: OutboundCurrency) -> str:
        """Validate the currency so it's ISO4217 compatible."""
        return validate_currency(v.__root__)

    @validator("paymentType")
    @classmethod
    def payment_type_rf(cls, v: OutboundPaymentType) -> OutboundPaymentType:
        """Paymentype needs to equal "RF" for RefundRequest."""
        if v.value != "RF":
            raise ValueError("Wrong payment type for the refund request")

        return v

    class Config:
        """Config for RefundRequest."""

        # Example of a valid request
        schema_extra = {"example": REFUND_REQUEST}
        # force the "Z" timezone formatting
        json_encoders = {datetime: UTCDatetime.to_str}


class RefundResponse(OutboundRefundResponse):
    """Definition of the refund response."""

    timestamp: Timestamp

    @validator("currency")
    @classmethod
    def currency_iso4217(cls, v: OutboundCurrency) -> str:
        """Validate the currency so it's ISO4217 compatible."""
        return validate_currency(v.__root__)

    class Config:
        """Config for RefunResponse."""

        # Example of a valid response
        schema_extra = {"example": REFUND_RESPONSE}
        # force the "Z" timezone formatting
        json_encoders = {datetime: UTCDatetime.to_str}


class CancelRequest(OutboundCancelRequest):
    """Definition of the cancel request."""

    timestamp: Timestamp
    notificationUrl: NotificationUrl

    class Config:
        """Config for CancelRequest."""

        # Example of a valid request
        schema_extra = {"example": CANCEL_REQUEST}
        # force the "Z" timezone formatting
        json_encoders = {datetime: UTCDatetime.to_str}


class CancelResponse(OutboundCancelResponse):
    """Definition of the cancellation response."""

    timestamp: Timestamp

    class Config:
        """Config for CancelResponse."""

        # Example of a valid response
        schema_extra = {"example": CANCEL_RESPONSE}
        # force the "Z" timezone formatting
        json_encoders = {datetime: UTCDatetime.to_str}


class StatusResponse(OutboundStatusResponse):
    """Definition of the cancellation response."""

    timestamp: Timestamp

    @validator("currency")
    @classmethod
    def currency_iso4217(cls, v: OutboundCurrency) -> str:
        """Validate the currency so it's ISO4217 compatible."""
        return validate_currency(v.__root__)

    class Config:
        """Config for StatusResponse."""

        # Example of a valid response
        schema_extra = {"example": STATUS_RESPONSE}
        # force the "Z" timezone formatting
        json_encoders = {datetime: UTCDatetime.to_str}


class ErrorResponse(OutboundErrorResponse):
    """Definition of the Error result."""

    timestamp: Timestamp

    class Config:
        """Config for ErrorResponse."""

        # Example of a valid response
        schema_extra = {"example": ERROR_RESPONSE}
        # force the "Z" timezone formatting
        json_encoders = {datetime: UTCDatetime.to_str}


class Error400Response(OutboundError400Response):
    """Definition of the Error 400."""

    timestamp: Timestamp

    class Config:
        """Config for Error400Response."""

        # Example of a valid response
        schema_extra = {"example": ERROR_400_RESPONSE}
        # force the "Z" timezone formatting
        json_encoders = {datetime: UTCDatetime.to_str}


class WebhookRequest(InboundWebhookRequest):
    """Definition of the refund request."""

    timestamp: Timestamp

    @validator("currency")
    @classmethod
    def currency_iso4217(cls, v: InboundCurrency) -> str:
        """Validate the currency so it's ISO4217 compatible."""
        return validate_currency(v.__root__)

    class Config:
        """Config for WebhookRequest."""

        # Example of a valid request
        schema_extra = {"example": WEBHOOK_REQUEST}
        # force the "Z" timezone formatting
        json_encoders = {datetime: UTCDatetime.to_str}

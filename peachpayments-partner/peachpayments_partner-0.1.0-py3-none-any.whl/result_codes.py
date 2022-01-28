"""Module for getting Peach Payments result codes."""

from typing import Dict

from peachpayments_partner.exceptions import ResultCodeException


class ResultCode:
    """Represents a single result code.

    Attributes:
        - code (str): code representing the result
        - name (str): camelCase name of the result
        - description (str): detailed description of the result
    """

    def __init__(self, code: str, name: str, description: str = None):
        """Construct all the attributes for the ResultCode object.

        Args:
            - code (str): code representing the result
            - name (str): camelCase name of the result

        Kwargs:
            - description (str): detailed description of the result

        Raises:
            ResultCodeException if result code name or number is not provided.
        """
        if not code:
            raise ResultCodeException("Result code number not provided")

        if not name:
            raise ResultCodeException("Result code name not provided")

        self.code = code
        self.name = name
        self.description = description


class ResultCodes:
    """Collection of ResultCodes.

    Usage:
        result_codes.TRANSACTION_SUCCEEDED.code == "000.000.000"
        result_codes.get("000.000.000").name == "TRANSACTION_SUCCEEDED"
        result_codes.get("000.000.000").description == "Transaction succeeded"

    Attributes:
        - [ResultCode.name] (ResultCode)
        - by_code (dict) ResultCodes indexed by code number
    """

    by_code: Dict[str, ResultCode] = {}

    TRANSACTION_SUCCESS = ResultCode(
        code="000.000.000", name="TRANSACTION_SUCCESS", description="Transaction succeeded"
    )
    SUCCESSFUL_REQUEST = ResultCode(code="000.000.100", name="SUCCESSFUL_REQUEST", description="successful request")
    SUCCESSFULLY_PROCESSED_IN_INTEGRATOR_TEST_MODE = ResultCode(
        code="000.100.110",
        name="SUCCESSFULLY_PROCESSED_IN_INTEGRATOR_TEST_MODE",
        description="Request successfully processed in 'Merchant in Integrator Test Mode'",
    )
    TRANSACTION_PENDING = ResultCode(code="000.200.000", name="TRANSACTION_PENDING", description="transaction pending")
    TRANSACTION_NOT_FOUND = ResultCode(
        code="700.400.580", name="TRANSACTION_NOT_FOUND", description="cannot find transaction"
    )
    CANNOT_REFUND_VOLUME_EXCEEDED = ResultCode(
        code="700.400.200",
        name="CANNOT_REFUND_VOLUME_EXCEEDED",
        description="cannot refund (refund volume exceeded or tx reversed or invalid workflow?)",
    )
    TRANSACTION_DECLINED_UNKNOWN_REASON = ResultCode(
        code="800.100.100",
        name="TRANSACTION_DECLINED_UNKNOWN_REASON",
        description="transaction declined for unknown reason",
    )
    TRANSACTION_DECLINED_REFUND_ON_GAMBLING_TX_NOT_ALLOWED = ResultCode(
        code="800.100.150",
        name="TRANSACTION_DECLINED_REFUND_ON_GAMBLING_TX_NOT_ALLOWED",
        description="transaction declined (refund on gambling tx not allowed)",
    )
    TRANSACTION_DECLINED_INVALID_CARD = ResultCode(
        code="800.100.151", name="TRANSACTION_DECLINED_INVALID_CARD", description="transaction declined (invalid card)"
    )
    TRANSACTION_DECLINED_BY_AUTH_SYSTEM = ResultCode(
        code="800.100.152",
        name="TRANSACTION_DECLINED_BY_AUTH_SYSTEM",
        description="transaction declined by authorization system",
    )
    TRANSACTION_DECLINED_INVALID_CVV = ResultCode(
        code="800.100.153", name="TRANSACTION_DECLINED_INVALID_CVV", description="transaction declined (invalid CVV)"
    )
    TRANSACTION_DECLINED_MARKED_INVALID = ResultCode(
        code="800.100.154",
        name="TRANSACTION_DECLINED_MARKED_INVALID",
        description="transaction declined (transaction marked as invalid)",
    )
    TRANSACTION_DECLINED_AMOUNT_EXCEEDS_CREDIT = ResultCode(
        code="800.100.155",
        name="TRANSACTION_DECLINED_AMOUNT_EXCEEDS_CREDIT",
        description="transaction declined (amount exceeds credit)",
    )
    TRANSACTION_DECLINED_FORMAT_ERROR = ResultCode(
        code="800.100.156", name="TRANSACTION_DECLINED_FORMAT_ERROR", description="transaction declined (format error)"
    )
    TRANSACTION_DECLINED_WRONG_EXPIRY_DATE = ResultCode(
        code="800.100.157",
        name="TRANSACTION_DECLINED_WRONG_EXPIRY_DATE",
        description="transaction declined (wrong expiry date)",
    )
    TRANSACTION_DECLINED_SUSPECTING_MANIPULATION = ResultCode(
        code="800.100.158",
        name="TRANSACTION_DECLINED_SUSPECTING_MANIPULATION",
        description="transaction declined (suspecting manipulation)",
    )
    TRANSACTION_DECLINED_STOLEN_CARD = ResultCode(
        code="800.100.159", name="TRANSACTION_DECLINED_STOLEN_CARD", description="transaction declined (stolen card)"
    )
    TRANSACTION_DECLINED_CARD_BLOCKED = ResultCode(
        code="800.100.160", name="TRANSACTION_DECLINED_CARD_BLOCKED", description="transaction declined (card blocked)"
    )
    TRANSACTION_DECLINED_TOO_MANY_INVALID_TRIES = ResultCode(
        code="800.100.161",
        name="TRANSACTION_DECLINED_TOO_MANY_INVALID_TRIES",
        description="transaction declined (too many invalid tries)",
    )
    TRANSACTION_DECLINED_LIMIT_EXCEEDED = ResultCode(
        code="800.100.162",
        name="TRANSACTION_DECLINED_LIMIT_EXCEEDED",
        description="transaction declined (limit exceeded)",
    )
    TRANSACTION_DECLINED_MAXIMUM_TRANSACTION_FREQUENCY_EXCEEDED = ResultCode(
        code="800.100.163",
        name="TRANSACTION_DECLINED_MAXIMUM_TRANSACTION_FREQUENCY_EXCEEDED",
        description="transaction declined (maximum transaction frequency exceeded)",
    )
    TRANSACTION_DECLINED_MERCHANT_LIMIT_EXCEEDED = ResultCode(
        code="800.100.164",
        name="TRANSACTION_DECLINED_MERCHANT_LIMIT_EXCEEDED",
        description="transaction declined (merchants limit exceeded)",
    )
    TRANSACTION_DECLINED_CARD_LOST = ResultCode(
        code="800.100.165", name="TRANSACTION_DECLINED_CARD_LOST", description="transaction declined (card lost)"
    )
    TRANSACTION_DECLINED_INCORRECT_ID = ResultCode(
        code="800.100.166",
        name="TRANSACTION_DECLINED_INCORRECT_ID",
        description="transaction declined (Incorrect personal identification number)",
    )
    TRANSACTION_DECLINED_REFERENCING_TRANSACTION_DOES_NOT_MATCH = ResultCode(
        code="800.100.167",
        name="TRANSACTION_DECLINED_REFERENCING_TRANSACTION_DOES_NOT_MATCH",
        description="transaction declined (referencing transaction does not match)",
    )
    TRANSACTION_DECLINED_RESTRICTED_CARD = ResultCode(
        code="800.100.168",
        name="TRANSACTION_DECLINED_RESTRICTED_CARD",
        description="transaction declined (restricted card)",
    )
    TRANSACTION_DECLINED_CARD_TYPE_NOT_PROCESSED = ResultCode(
        code="800.100.169",
        name="TRANSACTION_DECLINED_CARD_TYPE_NOT_PROCESSED",
        description="transaction declined (card type is not processed by the authorization center)",
    )
    TRANSACTION_DECLINED_TRANSACTION_NOT_PERMITTED = ResultCode(
        code="800.100.170",
        name="TRANSACTION_DECLINED_TRANSACTION_NOT_PERMITTED",
        description="Transaction declined (transaction not permitted)",
    )
    TRANSACTION_DECLINED_PICK_UP_CARD = ResultCode(
        code="800.100.171", name="TRANSACTION_DECLINED_PICK_UP_CARD", description="transaction declined (pick up card)"
    )
    TRANSACTION_DECLINED_ACCOUNT_BLOCKED = ResultCode(
        code="800.100.172",
        name="TRANSACTION_DECLINED_ACCOUNT_BLOCKED",
        description="transaction declined (account blocked)",
    )
    TRANSACTION_DECLINED_INVALID_CURRENCY = ResultCode(
        code="800.100.173",
        name="TRANSACTION_DECLINED_INVALID_CURRENCY",
        description="transaction declined (invalid currency, not processed by authorization center)",
    )
    TRANSACTION_DECLINED_INVALID_AMOUNT = ResultCode(
        code="800.100.174",
        name="TRANSACTION_DECLINED_INVALID_AMOUNT",
        description="transaction declined (invalid amount)",
    )
    TRANSACTION_DECLINED_INVALID_BRAND = ResultCode(
        code="800.100.175",
        name="TRANSACTION_DECLINED_INVALID_BRAND",
        description="transaction declined (invalid brand)",
    )
    TRANSACTION_DECLINED_ACCOUNT_UNAVAILABLE = ResultCode(
        code="800.100.176",
        name="TRANSACTION_DECLINED_ACCOUNT_UNAVAILABLE",
        description="transaction declined (account temporarily not available. Please try again later)",
    )
    TRANSACTION_DECLINED_EMPTY_AMOUNT = ResultCode(
        code="800.100.177",
        name="TRANSACTION_DECLINED_EMPTY_AMOUNT",
        description="transaction declined (amount field should not be empty)",
    )
    TRANSACTION_DECLINED_WRONG_PIN = ResultCode(
        code="800.100.178",
        name="TRANSACTION_DECLINED_WRONG_PIN",
        description="transaction declined (PIN entered incorrectly too often)",
    )
    TRANSACTION_DECLINED_EXCEEDS_WITHDRAWAL_COUNT_LIMIT = ResultCode(
        code="800.100.179",
        name="TRANSACTION_DECLINED_EXCEEDS_WITHDRAWAL_COUNT_LIMIT",
        description="transaction declined (exceeds withdrawal count limit)",
    )
    TRANSACTION_DECLINED_INVALID_CONFIGURATION = ResultCode(
        code="800.100.190",
        name="TRANSACTION_DECLINED_INVALID_CONFIGURATION",
        description="transaction declined (invalid configuration data)",
    )
    TRANSACTION_DECLINED_TXN_IN_WRONG_STATE_ON_AQUIRER_SIDE = ResultCode(
        code="800.100.191",
        name="TRANSACTION_DECLINED_TXN_IN_WRONG_STATE_ON_AQUIRER_SIDE",
        description="transaction declined (transaction in wrong state on aquirer side)",
    )
    TRANSACTION_DECLINED_INVALID_CVV_AMOUNT_RESERVED = ResultCode(
        code="800.100.192",
        name="TRANSACTION_DECLINED_INVALID_CVV_AMOUNT_RESERVED",
        description=(
            "transaction declined (invalid CVV, Amount has still been reserved on the customer's card and will be "
            "released in a few business days. Please ensure the CVV code is accurate before retrying the transaction)"
        ),
    )
    TRANSACTION_DECLINED_UNKNOWN_USER_ACCOUNT_NUMBER_OR_ID = ResultCode(
        code="800.100.195",
        name="TRANSACTION_DECLINED_UNKNOWN_USER_ACCOUNT_NUMBER_OR_ID",
        description="transaction declined (UserAccount Number/ID unknown)",
    )
    TRANSACTION_DECLINED_REGISTRATION_ERROR = ResultCode(
        code="800.100.196",
        name="TRANSACTION_DECLINED_REGISTRATION_ERROR",
        description="transaction declined (registration error)",
    )
    TRANSACTION_DECLINED_REGISTRATION_CANCELLED_EXTERNALLY = ResultCode(
        code="800.100.197",
        name="TRANSACTION_DECLINED_REGISTRATION_CANCELLED_EXTERNALLY",
        description="transaction declined (registration cancelled externally)",
    )
    TRANSACTION_DECLINED_INVALID_HOLDER = ResultCode(
        code="800.100.198",
        name="TRANSACTION_DECLINED_INVALID_HOLDER",
        description="Transaction declined (invalid holder)",
    )
    TRANSACTION_DECLINED_INVALID_TAX_NUMBER = ResultCode(
        code="800.100.199",
        name="TRANSACTION_DECLINED_INVALID_TAX_NUMBER",
        description="transaction declined (invalid tax number)",
    )
    REFER_TO_PAYER_DUE_TO_REASON_NOT_SPECIFIED = ResultCode(
        code="800.100.200",
        name="REFER_TO_PAYER_DUE_TO_REASON_NOT_SPECIFIED",
        description="Refer to Payer due to reason not specified",
    )
    ACCOUNT_OR_BANK_DETAILS_INCORRECT = ResultCode(
        code="800.100.201", name="ACCOUNT_OR_BANK_DETAILS_INCORRECT", description="Account or Bank Details Incorrect"
    )
    ACCOUNT_CLOSED = ResultCode(code="800.100.202", name="ACCOUNT_CLOSED", description="Account Closed")
    INSUFFICIENT_FUNDS = ResultCode(code="800.100.203", name="INSUFFICIENT_FUNDS", description="Insufficient Funds")
    MANDATE_EXPIRED = ResultCode(code="800.100.204", name="MANDATE_EXPIRED", description="Mandate Expired")
    MANDATE_DISCARDED = ResultCode(code="800.100.205", name="MANDATE_DISCARDED", description="Mandate Discarded")
    REFUND_OF_AN_AUTHORIZED_PAYMENT_REQUESTED_BY_CUSTOMER = ResultCode(
        code="800.100.206",
        name="REFUND_OF_AN_AUTHORIZED_PAYMENT_REQUESTED_BY_CUSTOMER",
        description="Refund of an authorized payment requested by the customer",
    )
    REFUND_REQUESTED = ResultCode(code="800.100.207", name="REFUND_REQUESTED", description="Refund requested")
    DIRECT_DEBIT_NOT_ENABLED_FOR_ACCOUNT_OR_BANK = ResultCode(
        code="800.100.208",
        name="DIRECT_DEBIT_NOT_ENABLED_FOR_ACCOUNT_OR_BANK",
        description="Direct debit not enabled for the specified account or bank",
    )
    CC_OR_BANK_ACCOUNT_HOLDER_NOT_VALID = ResultCode(
        code="800.100.402", name="CC_OR_BANK_ACCOUNT_HOLDER_NOT_VALID", description="CC/bank account holder not valid"
    )
    TRANSACTION_DECLINED_REVOCATION_AUTH_ORDER = ResultCode(
        code="800.100.403",
        name="TRANSACTION_DECLINED_REVOCATION_AUTH_ORDER",
        description="transaction declined (revocation of authorisation order)",
    )
    RECURRING_PAYMENT_STOPPED = ResultCode(
        code="800.100.500",
        name="RECURRING_PAYMENT_STOPPED",
        description="Card holder has advised his bank to stop this recurring payment",
    )
    ALL_RECURRING_PAYMENTS_STOPPED_FOR_THIS_MERCHANT = ResultCode(
        code="800.100.501",
        name="ALL_RECURRING_PAYMENTS_STOPPED_FOR_THIS_MERCHANT",
        description="Card holder has advised his bank to stop all recurring payments for this merchant",
    )
    TRANSACTION_FOR_SAME_SESSION_IS_BEING_PROCESSED = ResultCode(
        code="800.700.100",
        name="TRANSACTION_FOR_SAME_SESSION_IS_BEING_PROCESSED",
        description="transaction for the same session is currently being processed, please try again later.",
    )
    FAMILY_NAME_TOO_LONG = ResultCode(
        code="800.700.101", name="FAMILY_NAME_TOO_LONG", description="family name too long"
    )
    GIVEN_NAME_TOO_LONG = ResultCode(code="800.700.201", name="GIVEN_NAME_TOO_LONG", description="given name too long")
    COMPANY_NAME_TOO_LONG = ResultCode(
        code="800.700.500", name="COMPANY_NAME_TOO_LONG", description="company name too long"
    )
    INVALID_STREET = ResultCode(code="800.800.102", name="INVALID_STREET", description="Invalid street")
    INVALID_ZIP = ResultCode(code="800.800.202", name="INVALID_ZIP", description="Invalid zip")
    INVALID_CITY = ResultCode(code="800.800.302", name="INVALID_CITY", description="Invalid city")
    PREVIOUSLY_PENDING_ONLINE_TRANSFER_TRANSACTION_TIMEOUT = ResultCode(
        code="100.395.501",
        name="PREVIOUSLY_PENDING_ONLINE_TRANSFER_TRANSACTION_TIMEOUT",
        description="Previously pending online transfer transaction timed out",
    )
    USER_CANCELLED = ResultCode(code="100.396.101", name="USER_CANCELLED", description="Cancelled by user")
    UNCERTAIN_STATUS_PROBABLY_CANCELLED_BY_USER = ResultCode(
        code="100.396.104",
        name="UNCERTAIN_STATUS_PROBABLY_CANCELLED_BY_USER",
        description="Uncertain status - probably cancelled by user",
    )
    USER_AUTHENTICATION_FAILED = ResultCode(
        code="100.380.401", name="USER_AUTHENTICATION_FAILED", description="User Authentication Failed"
    )
    RISK_MANAGEMENT_TRANSACTION_TIMEOUT = ResultCode(
        code="100.380.501",
        name="RISK_MANAGEMENT_TRANSACTION_TIMEOUT",
        description="Risk management transaction timeout",
    )
    TRANSACTION_DECLINED_WRONG_ADDRESS = ResultCode(
        code="100.400.000",
        name="TRANSACTION_DECLINED_WRONG_ADDRESS",
        description="transaction declined (Wrong Address)",
    )
    TRANSACTION_DECLINED_WRONG_IDENTIFICATION = ResultCode(
        code="100.400.001",
        name="TRANSACTION_DECLINED_WRONG_IDENTIFICATION",
        description="transaction declined (Wrong Identification)",
    )
    TRANSACTION_DECLINED_INSUFFICIENT_CREDIBILITY_SCORE = ResultCode(
        code="100.400.002",
        name="TRANSACTION_DECLINED_INSUFFICIENT_CREDIBILITY_SCORE",
        description="transaction declined (Insufficient credibility score)",
    )
    TRANSACTION_DECLINED_BAD_RATING = ResultCode(
        code="100.400.100", name="TRANSACTION_DECLINED_BAD_RATING", description="transaction declined - very bad rating"
    )
    ACCOUNT_BLACKLISTED = ResultCode(code="100.400.121", name="ACCOUNT_BLACKLISTED", description="account blacklisted")
    GATEWAY_ERROR_RESPONSE = ResultCode(
        code="900.100.200", name="GATEWAY_ERROR_RESPONSE", description="error response from connector/acquirer"
    )
    SESSION_TIMEOUT = ResultCode(code="900.300.600", name="SESSION_TIMEOUT", description="user session timeout")
    INVALID_OR_MISSING_PARAMETER = ResultCode(
        code="200.300.404", name="INVALID_OR_MISSING_PARAMETER", description="invalid or missing parameter"
    )

    INVALID_TRANSACTION_FLOW = ResultCode(
        code="900.100.202",
        name="INVALID_TRANSACTION_FLOW",
        description=(
            "invalid transaction flow, the requested function is not applicable for the referenced transaction."
        ),
    )

    def __init__(self):
        """Set each provided result code by field."""
        self.by_code = dict()
        for attr in dir(self):
            if isinstance(getattr(self, attr), ResultCode):
                self.by_code[getattr(self, attr).code] = getattr(self, attr)

    def get(self, code: str) -> ResultCode:
        """Get result code.

        Args:
            - code (str): ResultCode number

        Returns:
            the result code identified by code number.

        Raises:
            KeyError if code not instantiated.
        """
        return self.by_code[code]


result_codes = ResultCodes()

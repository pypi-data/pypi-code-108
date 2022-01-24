import json
import uuid
from base64 import b64decode, b64encode

import httpx

from .settings import (
    API_URL,
    APPLICATION_ID,
    CLIENT_SECRET,
    DEFAULT_IP_ADDRESS,
    CLIENT_ID,
    MERCHANT_UID,
)
from .adumo_types import AccountHolder, Card

from .constants import FAILED, SUCCESS
from .exceptions import (
    AdumoFailedTransaction,
    CreditCardProcessor3dsFailure,
    CreditCardProcessorCardNotEnrolled3ds,
)

from logging import getLogger

logger = getLogger(__name__)


class Adumo:
    def __init__(self):
        self.headers = None
        self.login()

    def login(self):
        result = httpx.post(
            f"{API_URL}oauth/token?grant_type=client_credentials&client_id="
            f"{CLIENT_ID}&client_secret={CLIENT_SECRET}",
        )

        response_dict = result.json()

        access_token = response_dict.get("access_token")
        self.headers = {"Authorization": f"Bearer {access_token}"}

        return access_token

    def check_3d_enrollment(
        self,
        account_holder: AccountHolder,
        card: Card,
        amount: str,
        ip_address: str = None,
    ):
        if ip_address is None:
            ip_address = DEFAULT_IP_ADDRESS

        local_transaction_id = uuid.uuid4().__str__()
        request = {
            "applicationUid": APPLICATION_ID,
            "budgetPeriod": 0,
            "cardHolderFullName": account_holder.__str__(),
            "cardNumber": card.account_number,
            "description": "SIMcontrol Credit Card Transaction",
            "expiryMonth": card.expiration_month,
            "expiryYear": card.expiration_year,
            "merchantReference": local_transaction_id,
            "merchantUid": MERCHANT_UID,
            "originatingTransactionId": local_transaction_id,
            "authCallbackUrl": "{ not currently in use }",
            "value": amount,
            "ipAddress": ip_address,
            "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2) AppleWebKit/537.36 (KHTML, "
            "like Gecko) Chrome/96.0.4645.105 Safari/537.36",
            "saveCardDetails": False,
            "uci": "",
        }
        result = httpx.post(
            f"{API_URL}products/payments/v1/card/initiate",
            json=request,
            headers=self.headers,
        )
        response_dict = self._process_response(result)

        acs_payload = response_dict.get("acsPayload")
        acs_url = response_dict.get("acsUrl")
        transaction_id = response_dict.get("transactionId")
        three_d_secure_enrolled = response_dict.get("threeDSecureAuthRequired")
        error_code = response_dict.get("errorCode")

        if error_code:
            error_message = response_dict.get("message")
            logger.error(
                f"[Creditcard] Authenticate 3ds error: {error_code=} {error_message=}"
            )
            return {
                "status": FAILED,
                "transaction_id": transaction_id,
                "message": f"3d Secure error {error_message=}",
            }

        if not three_d_secure_enrolled:
            logger.error(f"[Creditcard] Card not enrolled in 3ds")
            return {
                "status": FAILED,
                "transaction_id": transaction_id,
                "message": "Card not Enrolled in 3ds, cannot process payment",
            }

        md = self.encode_md(transaction_id, amount, card.security_code)

        return {
            "status": SUCCESS,
            "transaction_id": transaction_id,
            "md": md,
            "pareq": acs_payload,
            "acs_url": acs_url,
        }

    def authorise_and_settle_payment(self, pares, md):
        transaction_id, amount, cvv = self.decode_md(md)

        try:
            self._authenticate(pares, transaction_id)
        except Exception:
            return {"status": FAILED, "transaction_id": transaction_id}

        result = self._authorise_and_settle(
            ccv=cvv, transaction_id=transaction_id, amount=amount
        )

        return result

    def _authenticate(self, pares: str, md: str):
        url = f"{API_URL}product/authentication/v1/tds/authenticate/"
        request = {"md": md, "payload": pares}
        result = httpx.post(url, json=request, headers=self.headers)
        response_dict = self._process_response(result)
        logger.info(
            f"[CreditCard] Authenticate 3ds response {response_dict.get('errorNo')} - "
            f"{response_dict.get('errorMsg')}"
        )

    def _authorise_and_settle(self, ccv, transaction_id: str, amount: str):

        request = {"transactionId": transaction_id, "amount": amount, "cvv": ccv}
        result = httpx.post(
            f"{API_URL}products/payments/v1/card/authorise",
            json=request,
            headers=self.headers,
        )
        response_dict = self._process_response(result)

        auto_settle = response_dict.get("autoSettle")
        logger.info(
            f"[CreditCard] Authorise {response_dict.get('statusMessage')}"
            f" - {response_dict.get('amount')} - {auto_settle=}"
        )
        if not auto_settle:
            self._settle(transaction_id, amount)

        return {"status": SUCCESS, "transaction_id": transaction_id}

    def _settle(self, transaction_id: str, amount: int):
        request = {
            "transactionId": transaction_id,
            "amount": amount,
        }

        result = httpx.post(
            f"{API_URL}products/payments/v1/card/settle",
            json=request,
            headers=self.headers,
        )

        response_dict = self._process_response(result)
        logger.info(
            f"[CreditCard] Settlement {response_dict.get('statusMessage')} - {response_dict.get('amount')}"
        )

    @staticmethod
    def _process_response(response):
        response_dict = response.json()
        logger.info(f"[Creditcard] {response_dict=}")
        status_code = response_dict.get("statusCode")

        if status_code and status_code != 200:
            status_message = response_dict.get("statusMessage")
            logger.error(
                f"[Creditcard] processing card issue: {status_code=} {status_message=}"
            )
            raise AdumoFailedTransaction(
                f"Failed Credit Card payment", status_code, status_message
            )

        response.raise_for_status()

        return response_dict

    @staticmethod
    def decode_md(md):
        md = b64decode(md)
        md_decoded = json.loads(md.decode("utf8"))

        transaction_id = md_decoded.get("transaction_id")
        cvv = md_decoded.get("cvv")
        amount = md_decoded.get("amount")

        return transaction_id, amount, cvv

    @staticmethod
    def encode_md(transaction_id, amount, cvv):
        md = f'{{"transaction_id": "{transaction_id}", "cvv": "{cvv}", "amount": "{amount}"}}'
        md_encoded = b64encode(md.encode("utf8")).decode("utf8")

        return md_encoded

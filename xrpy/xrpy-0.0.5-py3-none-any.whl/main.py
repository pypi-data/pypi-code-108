from typing import Union


from xrpl.account import get_account_info as xrpl_get_account_info

from xrpl.clients import JsonRpcClient
from xrpl.wallet import generate_faucet_wallet, Wallet

from xrpl.utils import xrp_to_drops

from xrpl.models.transactions import Payment, TrustSet, TrustSetFlag, OfferCreate, OfferCancel, OfferCreateFlag
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.response import Response
from xrpl.models.requests import AccountLines

from xrpl.models.requests import BookOffers
from xrpl.models.currencies import XRP

from xrpl.transaction import safe_sign_and_autofill_transaction, send_reliable_submission


def create_wallet(client: JsonRpcClient) -> Wallet:
    """
    Create a wallet

    :param client: xrpl Client
    :type client: JsonRpcClient

    :return: XRPL Wallet
    :rtype: Wallet
    """

    _wallet = generate_faucet_wallet(client)
    return _wallet


def send_transaction(client: JsonRpcClient, from_wallet: Wallet, amount: Union[int, float],
                     destination: str) -> Response:
    """
    Send a transaction

    :param client: xrpl Client
    :type client: JsonRpcClient

    :param from_wallet: XRPL Wallet
    :type from_wallet: Wallet

    :param amount: Amount to send
    :type amount: Union[int, float]

    :param destination: Destination address
    :type destination: str

    :return: Result of transaction sending attempt
    :rtype: Response
    """

    payment = Payment(
        account=from_wallet.classic_address,
        amount=xrp_to_drops(amount),
        destination=destination,
    )

    payment_signed = safe_sign_and_autofill_transaction(payment, from_wallet, client)
    response = send_reliable_submission(payment_signed, client)

    return response


def set_trust_line(client: JsonRpcClient, from_wallet: Wallet, currency: str, value: str, issuer: str) -> Response:
    """
    Create a trust line

    :param client: xrpl Client
    :type client: JsonRpcClient

    :param from_wallet: XRPL Wallet
    :type from_wallet: Wallet

    :param currency: Trust line currency
    :type currency: str

    :param value: Trust line value
    :type value: str

    :param issuer: Trust line issuer
    :type issuer: str

    :return: Result of Trust line creation attempt
    :rtype: Response

    ex)
        trust_set = TrustSet(
            account='rfL6jD4a9coALoR35cM9kLGGThrohuKjai',
            limit_amount=IssuedCurrencyAmount(
                currency='VGB',
                value='100000000',
                issuer='rhcyBrowwApgNonehKBj8Po5z4gTyRknaU'
            ),
            flags=TrustSetFlag.TF_SET_NO_RIPPLE,
        )

    """
    trust_set = TrustSet(
        account=from_wallet.classic_address,
        limit_amount=IssuedCurrencyAmount(
            currency=currency.upper(),
            value=value,
            issuer=issuer,
        ),
        flags=TrustSetFlag.TF_SET_NO_RIPPLE
    )

    trust_set_signed = safe_sign_and_autofill_transaction(trust_set, from_wallet, client)
    response = send_reliable_submission(trust_set_signed, client)

    return response


def create_offer_buy(client: JsonRpcClient, from_wallet: Wallet, taker_gets_xrp: Union[float, int],
                     taker_pays_currency: str, taker_pays_value: str, taker_pays_issuer: str,
                     _type: str) -> Response:
    """
    Place Order

    :param client: xrpl Client
    :type client: JsonRpcClient

    :param from_wallet: XRPL Wallet
    :type from_wallet: Wallet

    :param taker_gets_xrp: amount in xrp for taker gets
    :type taker_gets_xrp: int

    :param taker_pays_currency: Currency
    :type taker_pays_currency: str

    :param taker_pays_value: Value
    :type taker_pays_value: str

    :param taker_pays_issuer: Issuer
    :type taker_pays_issuer: str

    :param _type: Offer type (market or limit)
    :type _type: str

    :return: Result of order placing attempt
    :rtype: Response

    ex)
        offer_create = OfferCreate(
            account='rfL6jD4a9coALoR35cM9kLGGThrohuKjai',
            taker_gets=xrp_to_drops(2),
            taker_pays=IssuedCurrencyAmount(
                currency='VGB',
                value='20',
                issuer='rhcyBrowwApgNonehKBj8Po5z4gTyRknaU',
            ),
            # flags=OfferCreateFlag.TF_SELL
        )
    """

    offer_create = OfferCreate(
        account=from_wallet.classic_address,
        taker_gets=xrp_to_drops(taker_gets_xrp),
        taker_pays=IssuedCurrencyAmount(
            currency=taker_pays_currency,
            value=taker_pays_value,
            issuer=taker_pays_issuer,
        ),
        flags=OfferCreateFlag.TF_SELL if _type.lower() == 'market' else 0
    )

    offer_create_signed = safe_sign_and_autofill_transaction(offer_create, from_wallet, client)
    response = send_reliable_submission(offer_create_signed, client)

    return response


def create_offer_sell(client: JsonRpcClient, from_wallet: Wallet, taker_pays_xrp: Union[float, int],
                      taker_gets_currency: str, taker_gets_value: str, taker_gets_issuer: str,
                      _type: str) -> Response:
    """
    Place Order

    :param client: xrpl Client
    :type client: JsonRpcClient

    :param from_wallet: XRPL Wallet
    :type from_wallet: Wallet

    :param taker_pays_xrp: amount in xrp for taker pays
    :type taker_pays_xrp: int

    :param taker_gets_currency: Currency
    :type taker_gets_currency: str

    :param taker_gets_value: Value
    :type taker_gets_value: str

    :param taker_gets_issuer: Issuer
    :type taker_gets_issuer: str

    :param _type: Offer type (market or limit)
    :type _type: str

    :return: Result of order placing attempt
    :rtype: Response

    ex)
        offer_create = OfferCreate(
            account='rfL6jD4a9coALoR35cM9kLGGThrohuKjai',
            taker_gets=xrp_to_drops(2),
            taker_pays=IssuedCurrencyAmount(
                currency='VGB',
                value='20',
                issuer='rhcyBrowwApgNonehKBj8Po5z4gTyRknaU',
            ),
            # flags=OfferCreateFlag.TF_SELL
        )
    """

    offer_create = OfferCreate(
        account=from_wallet.classic_address,
        taker_gets=IssuedCurrencyAmount(
            currency=taker_gets_currency,
            value=taker_gets_value,
            issuer=taker_gets_issuer,
        ),
        taker_pays=xrp_to_drops(taker_pays_xrp),
        flags=OfferCreateFlag.TF_SELL if _type.lower() == 'market' else 0
    )

    offer_create_signed = safe_sign_and_autofill_transaction(offer_create, from_wallet, client)
    response = send_reliable_submission(offer_create_signed, client)

    return response


def cancel_offer(client: JsonRpcClient, from_wallet: Wallet, sequence: int) -> Response:
    """
    Cancel order

    :param client: xrpl Client
    :type client: JsonRpcClient

    :param from_wallet: XRPL Wallet
    :type from_wallet: Wallet

    :param sequence: The sequence number (or Ticket number) of a previous OfferCreate transaction.
    :type sequence: int

    :return: Result of order canceling attempt
    :rtype: Response
    """

    offer_create = OfferCancel(
        account=from_wallet.classic_address,
        offer_sequence=sequence
    )

    offer_create_signed = safe_sign_and_autofill_transaction(offer_create, from_wallet, client)
    response = send_reliable_submission(offer_create_signed, client)

    return response


def get_account_info(client: JsonRpcClient, address: str) -> Response:
    """
    Get Account Info

    :param client: xrpl Client
    :type client: JsonRpcClient

    :param address: Wallet address
    :type address: str

    :return: Account info
    :rtype: Response
    """

    acc_info = xrpl_get_account_info(address, client)

    return acc_info


def get_account_trustlines(client: JsonRpcClient, address: str) -> Response:
    """
    Get Account Trustlines

    :param client: xrpl Client
    :type client: JsonRpcClient

    :param address: Wallet address
    :type address: str

    :return: Account Trustlines
    :rtype: Response
    """

    account_lines = AccountLines(
        account=address,
    )
    account_lines_req = client.request(account_lines)

    return account_lines_req


def order_book_sell(client: JsonRpcClient, from_wallet: Wallet,
                    taker_pays_currency: Union[str, XRP], taker_pays_issuer: str) -> Response:
    """
    Get Orderbook

    :param client: xrpl Client
    :type client: JsonRpcClient

    :param from_wallet: XRPL Wallet
    :type from_wallet: Wallet

    :param taker_pays_currency: Currency
    :type taker_pays_currency: str

    :param taker_pays_issuer: Issuer
    :type taker_pays_issuer: str

    :return: Result of order placing attempt
    :rtype: Response

    """

    book_offers = BookOffers(
        taker=from_wallet.classic_address,
        taker_gets=IssuedCurrencyAmount(
            currency=taker_pays_currency,
            value='0',
            issuer=taker_pays_issuer,
        ),
        taker_pays=XRP(),
    )

    book_offers_req = client.request(book_offers)

    return book_offers_req


def order_book_buy(client: JsonRpcClient, from_wallet: Wallet,
                   taker_pays_currency: Union[str, XRP], taker_pays_issuer: str ) -> Response:
    """
    Get Orderbook

    :param client: xrpl Client
    :type client: JsonRpcClient

    :param from_wallet: XRPL Wallet
    :type from_wallet: Wallet

    :param taker_pays_currency: Currency
    :type taker_pays_currency: str

    :param taker_pays_issuer: Issuer
    :type taker_pays_issuer: str

    :return: Result of order placing attempt
    :rtype: Response

    """

    book_offers = BookOffers(
        taker=from_wallet.classic_address,
        taker_gets=XRP(),
        taker_pays=IssuedCurrencyAmount(
            currency=taker_pays_currency,
            value='0',
            issuer=taker_pays_issuer,
        ),
    )

    book_offers_req = client.request(book_offers)

    return book_offers_req

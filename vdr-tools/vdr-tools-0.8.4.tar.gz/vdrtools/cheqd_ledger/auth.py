from ..libindy import do_call, create_cb

from ctypes import *

import logging


async def build_tx(pool_alias: str,
                   sender_public_key: str,
                   msg: bytes,
                   account_number: int,
                   sequence_number: int,
                   max_gas: int,
                   max_coin_amount: int,
                   max_coin_denom: str,
                   timeout_height: int,
                   memo: str) -> bytes:
    """
    Build txn before sending

    :param pool_alias: string alias of a pool
    :param sender_public_key: public key of sender
    :param msg: message
    :param account_number: number of accounts
    :param sequence_number: how many txns are already written
    :param max_gas: how much gas user is ready to pay
    :param max_coin_amount: how many coins user can pay
    :param max_coin_denom: which kink of coins user is ready to pay
    :param timeout_height: block height until which the transaction is valid
    :param memo: a note or comment to send with the transaction
    :return: Built transaction
    """

    logger = logging.getLogger(__name__)
    logger.debug(
        "build_tx: >>> pool_alias: %r, sender_public_key: %r, msg: %r, account_number: %r, sequence_number: %r, "
        "max_gas: %r, max_coin_amount: %r, max_coin_denom: %r, timeout_height: %r memo: %r",
        pool_alias,
        sender_public_key,
        msg,
        account_number,
        sequence_number,
        max_gas,
        max_coin_amount,
        max_coin_denom,
        timeout_height,
        memo)

    def transform_cb(arr_ptr: POINTER(c_uint8), arr_len: c_uint32):
        return bytes(arr_ptr[:arr_len]),

    if not hasattr(build_tx, "cb"):
        logger.debug("build_tx: Creating callback")
        build_tx.cb = create_cb(CFUNCTYPE(None, c_int32, c_int32, POINTER(c_uint8), c_uint32), transform_cb)

    c_pool_alias = c_char_p(pool_alias.encode('utf-8'))
    c_sender_public_key = c_char_p(sender_public_key.encode('utf-8'))
    msg_len = c_uint32(len(msg))
    c_account_number = c_uint64(account_number)
    c_sequence_number = c_uint64(sequence_number)
    c_max_gas = c_uint64(max_gas)
    c_max_coin_amount = c_uint64(max_coin_amount)
    c_max_coin_denom = c_char_p(max_coin_denom.encode('utf-8'))
    c_timeout_height = c_uint64(timeout_height)
    c_memo = c_char_p(memo.encode('utf-8'))

    signature = await do_call('cheqd_ledger_auth_build_tx',
                              c_pool_alias,
                              c_sender_public_key,
                              msg,
                              msg_len,
                              c_account_number,
                              c_sequence_number,
                              c_max_gas,
                              c_max_coin_amount,
                              c_max_coin_denom,
                              c_timeout_height,
                              c_memo,
                              build_tx.cb)

    logger.debug("build_tx: <<< res: %r", signature)
    return signature

async def sign_tx(wallet_handle: int,
                  alias: str,
                  tx_bytes: bytes) -> bytes:
    """
    Sign tx by using Cosmos signature

    :param wallet_handle - wallet handler id
    :param alias         - alias of the key for making Cosmos signature
    :tx_bytes            - bytes of transaction

    :return: signed transaction bytes
    """

    logger = logging.getLogger(__name__)
    logger.debug("sign_tx: >>> alias: %r, request_bytes: %r",
                 alias,
                 tx_bytes)

    def transform_cb(arr_ptr: POINTER(c_uint8), arr_len: c_uint32):
        return bytes(arr_ptr[:arr_len]),

    if not hasattr(sign_tx, "cb"):
        logger.debug("sign_tx: Creating callback")
        sign_tx.cb = create_cb(CFUNCTYPE(None, c_int32, c_int32, POINTER(c_uint8), c_uint32), transform_cb)

    c_wallet_handle = c_int32(wallet_handle)
    c_alias = c_char_p(alias.encode('utf-8'))
    c_msg_len = c_uint32(len(tx_bytes))

    res = await do_call('cheqd_ledger_sign_tx',
                        c_wallet_handle,
                        c_alias,
                        tx_bytes,
                        c_msg_len,
                        sign_tx.cb)
    logger.debug("sign_tx: <<< res: %r", res)
    return res


async def build_query_account(address: str) -> str:
    """
    Build query for getting info about account.

    :param address: address of queried account

    :return: Query as JSON string
    """

    logger = logging.getLogger(__name__)
    logger.debug("build_query_account: >>> address: %r",
                 address)

    if not hasattr(build_query_account, "cb"):
        logger.debug("build_query_account: Creating callback")
        build_query_account.cb = create_cb(CFUNCTYPE(None, c_int32, c_int32, c_char_p))

    c_address = c_char_p(address.encode('utf-8'))

    res = await do_call('cheqd_ledger_auth_build_query_account',
                        c_address,
                        build_query_account.cb)

    res = res.decode()
    logger.debug("build_query_account: <<< res: %r", res)
    return res


async def parse_query_account_resp(response: str) -> str:
    """
    Parse response from query account.

    :param response: string representation of response from ledger

    :return: Account information as JSON string
    """

    logger = logging.getLogger(__name__)
    logger.debug("parse_query_account_resp: >>> response: %r",
                 response)

    if not hasattr(parse_query_account_resp, "cb"):
        logger.debug("parse_query_account_resp: Creating callback")
        parse_query_account_resp.cb = create_cb(CFUNCTYPE(None, c_int32, c_int32, c_char_p))

    c_response = c_char_p(response.encode('utf-8'))

    res = await do_call('cheqd_ledger_auth_parse_query_account_resp',
                        c_response,
                        parse_query_account_resp.cb)

    res = res.decode()
    logger.debug("parse_query_account_resp: <<< res: %r", res)
    return res

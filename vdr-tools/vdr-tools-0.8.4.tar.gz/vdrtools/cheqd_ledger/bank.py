from ..libindy import do_call, create_cb

from ctypes import *

import logging


async def build_msg_send(from_: str,
                         to: str,
                         amount: str,
                         denom: str) -> bytes:
    """
    Build message to send coins to other account.

    :param from_: address of sender coins
    :param to: address of getter coins
    :param amount: amount of coins for sending
    :param denom: denomination of coins
    :return: Built message
    """

    logger = logging.getLogger(__name__)
    logger.debug("build_msg_send: >>> from_: %r, to: %r, amount: %r, denom: %r",
                 from_,
                 to,
                 amount,
                 denom)

    def transform_cb(arr_ptr: POINTER(c_uint8), arr_len: c_uint32):
        return bytes(arr_ptr[:arr_len]),

    if not hasattr(build_msg_send, "cb"):
        logger.debug("build_msg_send: Creating callback")
        build_msg_send.cb = create_cb(CFUNCTYPE(None, c_int32, c_int32, POINTER(c_uint8), c_uint32), transform_cb)

    c_from_ = c_char_p(from_.encode('utf-8'))
    c_to = c_char_p(to.encode('utf-8'))
    c_amount = c_char_p(amount.encode('utf-8'))
    c_denom = c_char_p(denom.encode('utf-8'))

    res = await do_call('cheqd_ledger_bank_build_msg_send',
                        c_from_,
                        c_to,
                        c_amount,
                        c_denom,
                        build_msg_send.cb)

    logger.debug("build_msg_send: <<< res: %r", res)
    return res


async def parse_msg_send_resp(response: str) -> str:
    """
    Parse response for send coins tx

    :param response: response from ledger with protobuf inside.

    :return: Parsed response as JSON string
    """

    logger = logging.getLogger(__name__)
    logger.debug("parse_msg_send_resp: >>> response: %r",
                 response)

    if not hasattr(parse_msg_send_resp, "cb"):
        logger.debug("parse_msg_send_resp: Creating callback")
        parse_msg_send_resp.cb = create_cb(CFUNCTYPE(None, c_int32, c_int32, c_char_p))

    c_response = c_char_p(response.encode('utf-8'))

    res = await do_call('cheqd_ledger_bank_parse_msg_send_resp',
                        c_response,
                        parse_msg_send_resp.cb)

    res = res.decode()
    logger.debug("parse_msg_send_resp: <<< res: %r", res)
    return res


async def build_query_balance(address: str,
                              denom: str) -> str:
    """
    Parse response for send coins tx

    :param address: address of account which need to get.
    :param denom: currency of balance for getting.

    :return: Parsed response as JSON string
    """

    logger = logging.getLogger(__name__)
    logger.debug("build_query_balance: >>> address: %r, denom: %r",
                 address,
                 denom)

    if not hasattr(build_query_balance, "cb"):
        logger.debug("build_query_balance: Creating callback")
        build_query_balance.cb = create_cb(CFUNCTYPE(None, c_int32, c_int32, c_char_p))

    c_address = c_char_p(address.encode('utf-8'))
    c_denom = c_char_p(denom.encode('utf-8'))

    res = await do_call('cheqd_ledger_bank_build_query_balance',
                        c_address,
                        c_denom,
                        build_query_balance.cb)

    res = res.decode()
    logger.debug("build_query_balance: <<< res: %r", res)
    return res


async def parse_query_balance_resp(response: str) -> str:
    """
    Parse response for get balance tx.

    :param response: response for get balance tx.

    :return: Parsed response as JSON string
    """

    logger = logging.getLogger(__name__)
    logger.debug("parse_query_balance_resp: >>> response: %r",
                 response)

    if not hasattr(parse_query_balance_resp, "cb"):
        logger.debug("parse_query_balance_resp: Creating callback")
        parse_query_balance_resp.cb = create_cb(CFUNCTYPE(None, c_int32, c_int32, c_char_p))

    c_response = c_char_p(response.encode('utf-8'))

    res = await do_call('cheqd_ledger_bank_parse_query_balance_resp',
                        c_response,
                        parse_query_balance_resp.cb)

    res = res.decode()
    logger.debug("parse_query_balance_resp: <<< res: %r", res)
    return res

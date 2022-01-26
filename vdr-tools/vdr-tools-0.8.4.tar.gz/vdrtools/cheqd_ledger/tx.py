from ..libindy import do_call, create_cb

from ctypes import *

import logging


async def build_query_get_tx_by_hash(hash: str) -> str:
    """
    Build txn for querying txn by hash

    :param hash: hash-string of txn which should be queried from ledger.

    :return: Query as JSON string
    """

    logger = logging.getLogger(__name__)
    logger.debug("build_query_get_tx_by_hash: >>> hash: %r",
                 hash)

    if not hasattr(build_query_get_tx_by_hash, "cb"):
        logger.debug("build_query_get_tx_by_hash: Creating callback")
        build_query_get_tx_by_hash.cb = create_cb(CFUNCTYPE(None, c_int32, c_int32, c_char_p))

    c_hash = c_char_p(hash.encode('utf-8'))

    res = await do_call('cheqd_ledger_tx_build_query_get_tx_by_hash',
                        c_hash,
                        build_query_get_tx_by_hash.cb)

    res = res.decode()
    logger.debug("build_query_get_tx_by_hash: <<< res: %r", res)
    return res


async def parse_query_get_tx_by_hash_resp(response: str) -> str:
    """
    Parse response from get tx by hash function

    :param response: response from ledger with protobuf inside.

    :return: Received transactions as JSON string
    """

    logger = logging.getLogger(__name__)
    logger.debug("parse_query_get_tx_by_hash_resp: >>> response: %r",
                 response)

    if not hasattr(parse_query_get_tx_by_hash_resp, "cb"):
        logger.debug("parse_query_get_tx_by_hash_resp: Creating callback")
        parse_query_get_tx_by_hash_resp.cb = create_cb(CFUNCTYPE(None, c_int32, c_int32, c_char_p))

    c_response = c_char_p(response.encode('utf-8'))

    res = await do_call('cheqd_ledger_cheqd_parse_query_get_tx_by_hash_resp',
                        c_response,
                        parse_query_get_tx_by_hash_resp.cb)

    res = res.decode()
    logger.debug("parse_query_get_tx_by_hash_resp: <<< res: %r", res)
    return res


async def build_query_simulate(tx: bytes) -> str:
    """
    uild tx for querying tx simulate request

    :param tx: Transaction to simulate
    :return: Query as JSON string
    """

    logger = logging.getLogger(__name__)
    logger.debug("build_query_simulate: >>> tx: %r",
                 tx)

    if not hasattr(build_query_simulate, "cb"):
        logger.debug("build_query_simulate: Creating callback")
        build_query_simulate.cb = create_cb(CFUNCTYPE(None, c_int32, c_int32, c_char_p))

    tx_len = c_uint32(len(tx))

    res = await do_call('cheqd_ledger_tx_build_query_simulate',
                        tx,
                        tx_len,
                        build_query_simulate.cb)

    res = res.decode()
    logger.debug("build_query_simulate: <<< res: %r", res)
    return res


async def parse_query_simulate_resp(response: str) -> str:
    """
    Parse response for get SimulateResponse

    :param response: response from ledger with protobuf inside.

    :return: Parsed response as JSON string
    """

    logger = logging.getLogger(__name__)
    logger.debug("parse_query_simulate_resp: >>> response: %r",
                 response)

    if not hasattr(parse_query_simulate_resp, "cb"):
        logger.debug("parse_query_simulate_resp: Creating callback")
        parse_query_simulate_resp.cb = create_cb(CFUNCTYPE(None, c_int32, c_int32, c_char_p))

    c_response = c_char_p(response.encode('utf-8'))

    res = await do_call('cheqd_ledger_tx_parse_query_simulate_resp',
                        c_response,
                        parse_query_simulate_resp.cb)

    res = res.decode()
    logger.debug("parse_query_simulate_resp: <<< res: %r", res)
    return res

from .libindy import do_call, create_cb

from ctypes import *

import logging


async def add(alias: str,
              rpc_address: str,
              chain_id: str) -> str:
    """
    Add information about pool

    :param alias: Name of a pool
    :param rpc_address: Address for making remote calls
    :param chain_id: Name of network

    :return: created pool information as JSON string
    """

    logger = logging.getLogger(__name__)
    logger.debug("add: >>> alias: %r, rpc_address: %r, chain_id: %r",
                 alias,
                 rpc_address,
                 chain_id)

    if not hasattr(add, "cb"):
        logger.debug("add: Creating callback")
        add.cb = create_cb(CFUNCTYPE(None, c_int32, c_int32, c_char_p))

    c_alias = c_char_p(alias.encode('utf-8'))
    c_rpc_address = c_char_p(rpc_address.encode('utf-8'))
    c_chain_id = c_char_p(chain_id.encode('utf-8'))

    res = await do_call('cheqd_pool_add',
                        c_alias,
                        c_rpc_address,
                        c_chain_id,
                        add.cb)

    res = res.decode()
    logger.debug("add: <<< res: %r", res)
    return res


async def get_config(pool_alias: str) -> str:
    """
    Get pool config

    :param pool_alias: Name of a pool

    :return: pool information as JSON string
    """

    logger = logging.getLogger(__name__)
    logger.debug("get_config: >>> pool_alias: %r",
                 pool_alias)

    if not hasattr(get_config, "cb"):
        logger.debug("get_config: Creating callback")
        get_config.cb = create_cb(CFUNCTYPE(None, c_int32, c_int32, c_char_p))

    c_pool_alias = c_char_p(pool_alias.encode('utf-8'))

    res = await do_call('cheqd_pool_get_config',
                        c_pool_alias,
                        get_config.cb)

    res = res.decode()
    logger.debug("get_config: <<< res: %r", res)
    return res


async def get_all_config() -> str:
    """
    Get all pool configs

    :return: List of pool configs as JSON string
    """

    logger = logging.getLogger(__name__)
    logger.debug("get_all_config: >>>")

    if not hasattr(get_all_config, "cb"):
        logger.debug("get_all_config: Creating callback")
        get_all_config.cb = create_cb(CFUNCTYPE(None, c_int32, c_int32, c_char_p))

    res = await do_call('cheqd_pool_get_all_config',
                        get_all_config.cb)

    res = res.decode()
    logger.debug("get_all_config: <<< res: %r", res)
    return res


async def broadcast_tx_commit(pool_alias: str,
                              signed_tx: bytes) -> str:
    """
    Send broadcast transaction to the whole pool

    :param pool_alias: Name of a pool
    :param signed_tx:  Signed transaction to submit
    :return: Transaction response as JSON string
    """

    logger = logging.getLogger(__name__)
    logger.debug("broadcast_tx_commit: >>> pool_alias: %r, signed_tx: %r",
                 pool_alias,
                 signed_tx)

    if not hasattr(broadcast_tx_commit, "cb"):
        logger.debug("broadcast_tx_commit: Creating callback")
        broadcast_tx_commit.cb = create_cb(CFUNCTYPE(None, c_int32, c_int32, c_char_p))

    c_pool_alias = c_char_p(pool_alias.encode('utf-8'))
    signed_tx_len = c_uint32(len(signed_tx))

    res = await do_call('cheqd_pool_broadcast_tx_commit',
                        c_pool_alias,
                        signed_tx,
                        signed_tx_len,
                        broadcast_tx_commit.cb)

    res = res.decode()
    logger.debug("broadcast_tx_commit: <<< res: %r", res)
    return res


async def abci_query(pool_alias: str,
                     query: str) -> str:
    """
    Send general ABCI request

    :param pool_alias: Name of a pool
    :param query: ABCI query in json format

    :return: Response with result of ABCI query as JSON string
    """

    logger = logging.getLogger(__name__)
    logger.debug("abci_query: >>> pool_alias: %r, query: %r",
                 pool_alias,
                 query)

    if not hasattr(abci_query, "cb"):
        logger.debug("abci_query: Creating callback")
        abci_query.cb = create_cb(CFUNCTYPE(None, c_int32, c_int32, c_char_p))

    c_pool_alias = c_char_p(pool_alias.encode('utf-8'))
    c_query = c_char_p(query.encode('utf-8'))

    res = await do_call('cheqd_pool_abci_query',
                        c_pool_alias,
                        c_query,
                        abci_query.cb)

    res = res.decode()
    logger.debug("abci_query: <<< res: %r", res)
    return res


async def abci_info(pool_alias: str) -> str:
    """
    Request ABCI information

    :param pool_alias: Name of a pool

    :return: General response with information about pool state as JSON string
    """

    logger = logging.getLogger(__name__)
    logger.debug("abci_info: >>> pool_alias: %r",
                 pool_alias)

    if not hasattr(abci_info, "cb"):
        logger.debug("abci_info: Creating callback")
        abci_info.cb = create_cb(CFUNCTYPE(None, c_int32, c_int32, c_char_p))

    c_pool_alias = c_char_p(pool_alias.encode('utf-8'))

    res = await do_call('cheqd_pool_abci_info',
                        c_pool_alias,
                        abci_info.cb)

    res = res.decode()
    logger.debug("abci_info: <<< res: %r", res)
    return res

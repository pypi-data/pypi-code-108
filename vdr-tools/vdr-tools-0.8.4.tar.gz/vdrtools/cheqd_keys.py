from .libindy import do_call, create_cb

from ctypes import *

import logging


async def add_random(wallet_handle: int,
                     alias: str) -> str:
    """
    Creates keys (signing and encryption keys) for a new account.

    :param wallet_handle: wallet handler (created by open_wallet).
    :param alias: alias for a new keys

    :return: Info about created key as JSON string
        {
            alias: string - alias for a new keys
            account_id: string - address of a new keys
            pub_key: string - public key
        }
    """

    logger = logging.getLogger(__name__)
    logger.debug("add_random: >>> wallet_handle: %r, alias: %r",
                 wallet_handle,
                 alias)

    if not hasattr(add_random, "cb"):
        logger.debug("add_random: Creating callback")
        add_random.cb = create_cb(CFUNCTYPE(None, c_int32, c_int32, c_char_p))

    c_wallet_handle = c_int32(wallet_handle)
    c_alias = c_char_p(alias.encode('utf-8'))

    res = await do_call('cheqd_keys_add_random',
                        c_wallet_handle,
                        c_alias,
                        add_random.cb)

    res = res.decode()
    logger.debug("add_random: <<< res: %r", res)
    return res


async def add_from_mnemonic(wallet_handle: int,
                            alias: str,
                            mnemonic: str,
                            passphrase: str) -> str:
    """
    Creates keys (signing and encryption keys) for a new account.

    :param wallet_handle: wallet handler (created by open_wallet).
    :param alias: alias for a new keys
    :param mnemonic: for generating keys
    :param passphrase: password for a key, default is ""

    :return: Info about created key as JSON string
        {
            alias: string - alias for a new keys
            account_id: string - address of a new keys
            pub_key: string - public key
        }
    """

    logger = logging.getLogger(__name__)
    logger.debug("add_from_mnemonic: >>> wallet_handle: %r, alias: %r, mnemonic: %r, passphrase: %r",
                 wallet_handle,
                 alias,
                 mnemonic,
                 passphrase)

    if not hasattr(add_from_mnemonic, "cb"):
        logger.debug("add_from_mnemonic: Creating callback")
        add_from_mnemonic.cb = create_cb(CFUNCTYPE(None, c_int32, c_int32, c_char_p))

    c_wallet_handle = c_int32(wallet_handle)
    c_alias = c_char_p(alias.encode('utf-8'))
    c_mnemonic = c_char_p(mnemonic.encode('utf-8'))
    c_passphrase = c_char_p(passphrase.encode('utf-8'))

    res = await do_call('cheqd_keys_add_from_mnemonic',
                        c_wallet_handle,
                        c_alias,
                        c_mnemonic,
                        c_passphrase,
                        add_from_mnemonic.cb)

    res = res.decode()
    logger.debug("add_from_mnemonic: <<< res: %r", res)
    return res


async def get_info(wallet_handle: int,
                   alias: str) -> str:
    """
    Get Key info by alias

    :param wallet_handle: wallet handler (created by open_wallet).
    :param alias: alias for a new keys

    :return: Info about key as JSON string
        {
            alias: string - alias for a new keys
            account_id: string - address of a new keys
            pub_key: string - public key
        }
    """

    logger = logging.getLogger(__name__)
    logger.debug("get_info: >>> wallet_handle: %r, alias: %r",
                 wallet_handle,
                 alias)

    if not hasattr(get_info, "cb"):
        logger.debug("get_info: Creating callback")
        get_info.cb = create_cb(CFUNCTYPE(None, c_int32, c_int32, c_char_p))

    c_wallet_handle = c_int32(wallet_handle)
    c_alias = c_char_p(alias.encode('utf-8'))

    res = await do_call('cheqd_keys_get_info',
                        c_wallet_handle,
                        c_alias,
                        get_info.cb)

    res = res.decode()
    logger.debug("get_info: <<< res: %r", res)
    return res


async def list_keys(wallet_handle: int) -> str:
    """
    List keys in specific wallet

    :param wallet_handle: wallet handler (created by open_wallet).

    :return: List of keys as JSON string
    """

    logger = logging.getLogger(__name__)
    logger.debug("list_keys: >>> wallet_handle: %r",
                 wallet_handle)

    if not hasattr(list_keys, "cb"):
        logger.debug("list_keys: Creating callback")
        list_keys.cb = create_cb(CFUNCTYPE(None, c_int32, c_int32, c_char_p))

    c_wallet_handle = c_int32(wallet_handle)

    res = await do_call('cheqd_keys_list',
                        c_wallet_handle,
                        list_keys.cb)

    res = res.decode()
    logger.debug("list_keys: <<< res: %r", res)
    return res


async def sign(wallet_handle: int,
               alias: str,
               tx: bytes) -> bytes:
    """
    Sign

    :param wallet_handle: wallet handler (created by open_wallet).
    :param alias:  account alias for getting its keys
    :param tx: SignDoc
    :return: a signature string
    """

    logger = logging.getLogger(__name__)
    logger.debug("sign: >>> wallet_handle: %r, alias: %r, tx: %r",
                 wallet_handle,
                 alias,
                 tx)

    def transform_cb(arr_ptr: POINTER(c_uint8), arr_len: c_uint32):
        return bytes(arr_ptr[:arr_len]),

    if not hasattr(sign, "cb"):
        logger.debug("sign: Creating callback")
        sign.cb = create_cb(CFUNCTYPE(None, c_int32, c_int32, POINTER(c_uint8), c_uint32), transform_cb)

    c_wallet_handle = c_int32(wallet_handle)
    c_alias = c_char_p(alias.encode('utf-8'))
    c_tx = c_uint32(len(tx))

    signature = await do_call('cheqd_keys_sign',
                              c_wallet_handle,
                              c_alias,
                              tx,
                              c_tx,
                              sign.cb)

    logger.debug("sign: <<< res: %r", signature)
    return signature

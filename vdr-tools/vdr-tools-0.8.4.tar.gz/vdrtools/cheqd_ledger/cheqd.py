from ..libindy import do_call, create_cb

from ctypes import *

import logging


async def sign_msg_write_request(wallet_handle: int,
                                 did: str,
                                 request_bytes: bytes) -> bytes:
    """
    Build txn for singing a request

    :param wallet_handle: wallet handler (created by open_wallet).
    :param did:  Fully qualified did which should sign request.
    :param request_bytes: a message to be signed
    :return: request bytes with signature inside

    :return: signature in bytes
    """

    logger = logging.getLogger(__name__)
    logger.debug("sign_msg_write_request: >>> did: %r",
                 did)

    def transform_cb(arr_ptr: POINTER(c_uint8), arr_len: c_uint32):
        return bytes(arr_ptr[:arr_len])

    if not hasattr(sign_msg_write_request, "cb"):
        logger.debug("sign_msg_write_request: Creating callback")
        sign_msg_write_request.cb = create_cb(CFUNCTYPE(None, c_int32, c_int32, POINTER(c_uint8), c_uint32), transform_cb)

    c_did = c_char_p(did.encode('utf-8'))
    c_wallet_handle = c_int32(wallet_handle)
    c_msg_len = c_uint32(len(request_bytes))

    res = await do_call('cheqd_ledger_cheqd_sign_msg_write_request',
                        c_wallet_handle,
                        c_did,
                        request_bytes,
                        c_msg_len,
                        sign_msg_write_request.cb)

    logger.debug("sign_msg_write_request: <<< res: %r", res)
    return res


async def build_msg_create_did(did: str,
                               verkey: str) -> bytes:
    """
    Build txn for creating DID in Cheqd Ledger

    :param did: DID that must be created by calling create_key or create_and_store_my_did
    :param verkey: a public key for a new DID
    :return: a request for DID creation in Cheqd Ledger.

    :return: Built message
    """

    logger = logging.getLogger(__name__)
    logger.debug("build_msg_update_did: >>> did: %r, verkey: %r",
                 did, verkey)

    def transform_cb(arr_ptr: POINTER(c_uint8), arr_len: c_uint32):
        return bytes(arr_ptr[:arr_len])

    if not hasattr(build_msg_create_did, "cb"):
        logger.debug("build_msg_create_did: Creating callback")
        build_msg_create_did.cb = create_cb(CFUNCTYPE(None, c_int32, c_int32, POINTER(c_uint8), c_uint32), transform_cb)

    c_did = c_char_p(did.encode('utf-8'))
    c_verkey = c_char_p(verkey.encode('utf-8'))

    res = await do_call('cheqd_ledger_cheqd_build_msg_create_did',
                        c_did,
                        c_verkey,
                        build_msg_create_did.cb)

    logger.debug("build_msg_create_did: <<< res: %r", res)
    return res


async def parse_msg_create_did(response: str) -> str:
    """
    Parse response for creating DID in the ledger

    :param response: response from ledger with protobuf inside.

    :return: Parsed response as JSON string
    """

    logger = logging.getLogger(__name__)
    logger.debug("parse_msg_create_did: >>> response: %r",
                 response)

    if not hasattr(parse_msg_create_did, "cb"):
        logger.debug("parse_msg_resp: Creating callback")
        parse_msg_create_did.cb = create_cb(CFUNCTYPE(None, c_int32, c_int32, c_char_p))

    c_response = c_char_p(response.encode('utf-8'))

    res = await do_call('cheqd_ledger_cheqd_parse_msg_create_did_resp',
                        c_response,
                        parse_msg_create_did.cb)

    res = res.decode()
    logger.debug("parse_msg_create_did: <<< res: %r", res)
    return res


async def build_msg_update_did(did: str,
                               verkey: str,
                               version_id: str) -> bytes:
    """
    Build txn for creating DID in Cheqd Ledger

    :param did: DID that must be created by calling create_key or create_and_store_my_did
    :param verkey: a public key for a new DID
    :param version_id: a public key for a new DID
    :return: a request for DID creation in Cheqd Ledger.

    :return: Built message
    """

    logger = logging.getLogger(__name__)
    logger.debug("build_msg_update_did: >>> did: %r, verkey: %r, version_id: %r",
                 did, verkey, version_id)

    def transform_cb(arr_ptr: POINTER(c_uint8), arr_len: c_uint32):
        return bytes(arr_ptr[:arr_len])

    if not hasattr(build_msg_update_did, "cb"):
        logger.debug("build_msg_update_did: Creating callback")
        build_msg_update_did.cb = create_cb(CFUNCTYPE(None, c_int32, c_int32, POINTER(c_uint8), c_uint32), transform_cb)

    c_did = c_char_p(did.encode('utf-8'))
    c_verkey = c_char_p(verkey.encode('utf-8'))
    c_version_id = c_char_p(version_id.encode('utf-8'))

    res = await do_call('cheqd_ledger_cheqd_build_msg_update_did',
                        c_did,
                        c_verkey,
                        c_version_id,
                        build_msg_update_did.cb)

    logger.debug("build_msg_update_did: <<< res: %r", res)
    return res


async def parse_msg_update_did(response: str) -> str:
    """
    Parse response for creating DID in the ledger

    :param response: response from ledger with protobuf inside.

    :return: Parsed response as JSON string
    """

    logger = logging.getLogger(__name__)
    logger.debug("parse_msg_update_did: >>> response: %r",
                 response)

    if not hasattr(parse_msg_update_did, "cb"):
        logger.debug("parse_msg_resp: Creating callback")
        parse_msg_update_did.cb = create_cb(CFUNCTYPE(None, c_int32, c_int32, c_char_p))

    c_response = c_char_p(response.encode('utf-8'))

    res = await do_call('cheqd_ledger_cheqd_parse_msg_update_did_resp',
                        c_response,
                        parse_msg_update_did.cb)

    res = res.decode()
    logger.debug("parse_msg_update_did: <<< res: %r", res)
    return res


async def build_query_get_did(id: str) -> str:
    """
    Build request for getting DIDDoc from the ledger

    :param id: DID from Cheqd Ledger

    :return: Request as JSON string
    """

    logger = logging.getLogger(__name__)
    logger.debug("build_query_get_did: >>> id: %r",
                 id)

    if not hasattr(build_query_get_did, "cb"):
        logger.debug("build_query_get_did: Creating callback")
        build_query_get_did.cb = create_cb(CFUNCTYPE(None, c_int32, c_int32, c_char_p))

    c_id = c_char_p(id.encode('utf-8'))

    res = await do_call('cheqd_ledger_cheqd_build_query_get_did',
                        c_id,
                        build_query_get_did.cb)

    res = res.decode()
    logger.debug("build_query_get_did: <<< res: %r", res)
    return res


async def parse_query_get_did_resp(response: str) -> str:
    """
    Parse response for getting DIDDoc.

    :param response: response for getting DIDDoc.

    :return: Parsed response as JSON string
    """

    logger = logging.getLogger(__name__)
    logger.debug("parse_query_balance_resp: >>> response: %r",
                 response)

    if not hasattr(parse_query_get_did_resp, "cb"):
        logger.debug("parse_query_balance_resp: Creating callback")
        parse_query_get_did_resp.cb = create_cb(CFUNCTYPE(None, c_int32, c_int32, c_char_p))

    c_response = c_char_p(response.encode('utf-8'))

    res = await do_call('cheqd_ledger_cheqd_parse_query_get_did_resp',
                        c_response,
                        parse_query_get_did_resp.cb)

    res = res.decode()
    logger.debug("parse_query_balance_resp: <<< res: %r", res)
    return res

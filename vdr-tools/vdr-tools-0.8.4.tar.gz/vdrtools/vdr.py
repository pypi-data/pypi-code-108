from .libindy import do_call, do_call_sync, create_cb

from typing import Optional
from ctypes import *

import logging


class VdrBuilder:
    def __init__(self, c_instance: c_void_p):
        logger = logging.getLogger(__name__)
        logger.debug("VdrBuilder.__init__: >>> self: %r, instance: %r", self, c_instance)

        self.c_instance = c_instance

    @classmethod
    def create(cls) -> 'VdrBuilder':
        logger = logging.getLogger(__name__)
        logger.debug("VdrBuilder::new: >>>")

        c_instance = c_void_p()
        do_call_sync('vdr_builder_create', byref(c_instance))

        res = cls(c_instance)

        logger.debug("VdrBuilder::new: <<< res: %r", res)
        return res

    async def register_indy_ledger(self,
                                   namespace_list: str,
                                   genesis_txn_data: str,
                                   taa_config: Optional[str] = None) -> None:
        logger = logging.getLogger(__name__)
        logger.debug("register_indy_ledger: >>> namespace_list: %r, genesis_txn_data: %r, taa_config: %r",
                     namespace_list,
                     genesis_txn_data,
                     taa_config)

        if not hasattr(self, "register_indy_ledger_cb"):
            logger.debug("register_indy_ledger: Creating callback")
            self.register_indy_ledger_cb = create_cb(CFUNCTYPE(None, c_int32, c_int32))

        c_namespace_list = c_char_p(namespace_list.encode('utf-8'))
        c_genesis_txn_data = c_char_p(genesis_txn_data.encode('utf-8'))
        c_taa_config = c_char_p(taa_config.encode('utf-8')) if taa_config is not None else None

        res = await do_call('vdr_builder_register_indy_ledger',
                            self.c_instance,
                            c_namespace_list,
                            c_genesis_txn_data,
                            c_taa_config,
                            self.register_indy_ledger_cb)

        logger.debug("register_indy_ledger: <<< res: %r", res)
        return res

    async def register_cheqd_ledger(self,
                                    namespace_list: str,
                                    chain_id: str,
                                    node_addrs_list: str) -> None:
        logger = logging.getLogger(__name__)
        logger.debug("register_cheqd_ledger: >>> namespace_list: %r, chain_id: %r, node_addrs_list: %r",
                     namespace_list,
                     chain_id,
                     node_addrs_list)

        if not hasattr(self, "register_cheqd_ledger_cb"):
            logger.debug("register_cheqd_ledger: Creating callback")
            self.register_cheqd_ledger_cb = create_cb(CFUNCTYPE(None, c_int32, c_int32))

        c_namespace_list = c_char_p(namespace_list.encode('utf-8'))
        c_chain_id = c_char_p(chain_id.encode('utf-8'))
        c_node_addrs_list = c_char_p(node_addrs_list.encode('utf-8'))

        res = await do_call('vdr_builder_register_cheqd_ledger',
                            self.c_instance,
                            c_namespace_list,
                            c_chain_id,
                            c_node_addrs_list,
                            self.register_cheqd_ledger_cb)

        logger.debug("register_cheqd_ledger: <<< res: %r", res)
        return res

    def finalize(self) -> 'Vdr':
        logger = logging.getLogger(__name__)
        logger.debug("VdrBuilder::finalize: >>>")

        c_instance = c_void_p()
        do_call_sync('vdr_builder_finalize',
                     self.c_instance,
                     byref(c_instance))

        res = Vdr(c_instance)

        logger.debug("VdrBuilder::finalize: <<< res: %r", res)
        return res


class Vdr:
    def __init__(self, c_instance: c_void_p):
        logger = logging.getLogger(__name__)
        logger.debug("Vdr.__init__: >>> self: %r, instance: %r", self, c_instance)

        self.c_instance = c_instance

    async def ping(self,
                   namespace_list: str) -> str:
        logger = logging.getLogger(__name__)
        logger.debug("ping: >>> namespace_list: %r",
                     namespace_list)

        if not hasattr(self, "ping_cb"):
            logger.debug("ping: Creating callback")
            self.ping_cb = create_cb(CFUNCTYPE(None, c_int32, c_int32, c_char_p))

        c_namespace_list = c_char_p(namespace_list.encode('utf-8'))
        res = await do_call('vdr_ping',
                            self.c_instance,
                            c_namespace_list,
                            self.ping_cb)

        res = res.decode()
        logger.debug("register_cheqd_ledger: <<< res: %r", res)
        return res

    async def resolve_did(self,
                          fqdid: str) -> str:
        logger = logging.getLogger(__name__)
        logger.debug("resolve_did: >>> fqdid: %r",
                     fqdid)

        if not hasattr(self, "resolve_did_cb"):
            logger.debug("resolve_did: Creating callback")
            self.resolve_did_cb = create_cb(CFUNCTYPE(None, c_int32, c_int32, c_char_p))

        c_fqdid = c_char_p(fqdid.encode('utf-8'))

        res = await do_call('vdr_resolve_did',
                            self.c_instance,
                            c_fqdid,
                            self.resolve_did_cb)

        res = res.decode()
        logger.debug("resolve_did: <<< res: %r", res)
        return res

    async def cleanup(self) -> None:
        logger = logging.getLogger(__name__)
        logger.debug("cleanup: >>>")

        if not hasattr(self, "cleanup_cb"):
            logger.debug("cleanup: Creating callback")
            self.cleanup_cb = create_cb(CFUNCTYPE(None, c_int32, c_int32))

        res = await do_call('vdr_cleanup',
                            self.c_instance,
                            self.cleanup_cb)

        logger.debug("cleanup: <<< res: %r", res)
        return res

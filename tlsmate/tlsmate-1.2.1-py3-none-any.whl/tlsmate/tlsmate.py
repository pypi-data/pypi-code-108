# -*- coding: utf-8 -*-
"""Module for dependency injection
"""
# import basic stuff
import pathlib
import logging
from typing import Optional

# import own stuff
import tlsmate.cert as crt
import tlsmate.cert_chain as cert_chain
import tlsmate.client as client
import tlsmate.client_auth as client_auth
import tlsmate.config as conf
import tlsmate.crl_manager as crl_manager
import tlsmate.recorder as rec
import tlsmate.server_profile as server_profile
import tlsmate.trust_store as trust_store

# from tlsmate.plugin import WorkManager
from tlsmate.key_logging import KeyLogger
from tlsmate import utils

# import other stuff

TLSMATE_DIR = pathlib.Path(__file__).parent.parent.resolve()


class TlsMate(object):
    """Class defining the tlsmate application.

    Arguments:
        config (:obj:`tlsmate.config.Configuration`): an object representing tlsmate's
            configuration.

    Attributes:
        config (:obj:`tlsmate.config.Configuration`): the configuration object
            available for most other major object as well
        server_profile (:obj:`tlsmate.server_profile.ServerProfile`): the server
            profile object, describing which features and capabilities are
            supported by the server.
        recorder (:obj:`tlsmate.recorder.Recorder`): the recorder object, available
            for most major objects as well. Used for unit tests only.
        trust_store (:obj:`tlsmate.cert.TrustStore`): the trust store which provides
            access to the root certificates
        crl_manager (:obj:`tlsmate.cert.CrlManager`): the object which manages CRLs.
        client_auth (:obj:`tlsmate.client_auth.ClientAuth`): the object which manages
            the keys and certificate chains needed for client authentication
        client (:obj:`tlsmate.client.Client`): the client object
        cert_chain_cache (:obj:`tlsmate.cert_chain.CertChainCache`): the certificate
            chain validation status cache
    """

    instance = None
    """The instance of tlsmate
    """

    def __init__(self, config: Optional[conf.Configuration] = None) -> None:
        TlsMate.instance = self
        if config is None:
            config = conf.Configuration()

        for key, val in config.items():
            logging.debug(f"using config {key}={val}")

        self.config = config
        self.server_profile = server_profile.ServerProfile()
        self.recorder = rec.Recorder(config=config)
        self.trust_store = trust_store.TrustStore(recorder=self.recorder)
        self.client_auth = client_auth.ClientAuth(recorder=self.recorder)
        self.crl_manager = crl_manager.CrlManager(recorder=self.recorder)
        self.cert_chain_cache = cert_chain.CertChainCache()
        key_log_file = config.get("key_log_file")
        if key_log_file:
            KeyLogger.open_file(key_log_file)

        read_profile = config.get("read_profile")
        if read_profile:
            self.server_profile.load(utils.deserialize_data(read_profile))

        recorder_replaying = config.get("pytest_recorder_replaying")
        if recorder_replaying is not True:
            # "Normal" init of trust store and client auth from configuration
            if recorder_replaying is False:
                self.recorder.record()

            self.trust_store.set_ca_files(config.get("ca_certs"))
            if config.get("client_key"):
                for key_file, chain_file in zip(
                    config.get("client_key"), config.get("client_chain")
                ):
                    self.client_auth.add_auth_files(key_file, chain_file)

            key_log_file = config.get("key_log_file")
            if key_log_file:
                KeyLogger.open_file(key_log_file)

        else:
            pytest_recorder_file = config.get("pytest_recorder_file")
            if pytest_recorder_file:
                self.recorder.deserialize(pytest_recorder_file)

            self.recorder.replay()
            # Init trust store and client auth from recorded data
            for cert in self.recorder.get_trust_store():
                self.trust_store.add_cert(crt.Certificate(der=bytes.fromhex(cert)))

            for key_chain in self.recorder.get_client_auth():
                # TODO: resolve type issue
                self.client_auth.deserialize_key_chain(key_chain)  # type: ignore

        self.client = client.Client(
            config=config, recorder=self.recorder, client_auth=self.client_auth
        )

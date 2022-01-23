# -*- coding: utf-8 -*-
"""Module containing the test suite
"""
# import basic stuff
import abc

# import own stuff
import tlsmate.msg as msg
import tlsmate.plugin as plg
import tlsmate.server_profile as server_profile
import tlsmate.tls as tls
import tlsmate.utils as utils

# import other stuff


class _Backend(metaclass=abc.ABCMeta):
    @staticmethod
    def get_sig_alg_from_server(client, sig_algs, cert_algs):
        raise NotImplementedError


class _BackendTls12(_Backend):
    @staticmethod
    def get_sig_alg_from_server(client, sig_algs, cert_algs):
        sig_alg = None
        cert_chain = None
        client.profile.signature_algorithms = sig_algs + cert_algs
        with client.create_connection() as conn:
            conn.send(msg.ClientHello)
            conn.wait(msg.ServerHello)
            cert_chain = conn.wait(msg.Certificate).chain
            msg_ske = conn.wait(msg.ServerKeyExchange)
            if msg_ske.ec is not None:
                sig_alg = msg_ske.ec.sig_scheme

            elif msg_ske.dh is not None:
                sig_alg = msg_ske.dh.sig_scheme

        return sig_alg, cert_chain


class _BackendTls13(_Backend):
    @staticmethod
    def get_sig_alg_from_server(client, sig_algs, cert_algs):
        sig_alg = None
        cert_chain = None
        client.profile.signature_algorithms = sig_algs + cert_algs
        with client.create_connection() as conn:
            conn.send(msg.ClientHello)
            conn.wait(msg.ServerHello)
            conn.wait(msg.ChangeCipherSpec, optional=True)
            conn.wait(msg.EncryptedExtensions)
            cert_chain = conn.wait(msg.Certificate).chain
            sig_alg = conn.wait(msg.CertificateVerify).signature_scheme

        return sig_alg, cert_chain


class ScanSigAlgs(plg.Worker):
    name = "sigalgo"
    descr = "scan for supported signature algorithms"
    prio = 20

    def _scan_auth_method(
        self, cipher_suites, sig_algs, cert_algs, prof_sig_algo, backend
    ):
        cert_algs = [alg for alg in cert_algs if alg not in sig_algs]
        sig_alg_supported = []
        if not cipher_suites:
            return sig_alg_supported
        self.client.profile.cipher_suites = cipher_suites
        self.client.profile.signature_algorithms = sig_algs

        while sig_algs:
            sig_alg, cert_chain = backend.get_sig_alg_from_server(
                self.client, sig_algs, cert_algs
            )
            if sig_alg is None or sig_alg in cert_algs:
                break

            self.server_profile.append_unique_cert_chain(cert_chain)
            if sig_alg not in sig_algs:
                if not hasattr(prof_sig_algo, "info"):
                    prof_sig_algo.info = []

                info = f"server selects sig_alg {sig_alg} even when not offered"
                if info not in prof_sig_algo.info:
                    prof_sig_algo.info.append(info)

                break

            sig_alg_supported.append(sig_alg)
            sig_algs.remove(sig_alg)

        for sig_algo in sig_alg_supported:
            prof_sig_algo.algorithms.append(sig_algo)

    def _scan_tls12(self):
        prof_version = self.server_profile.get_version_profile(tls.Version.TLS12)
        if prof_version is None:
            return

        if not hasattr(prof_version, "signature_algorithms"):
            prof_version.signature_algorithms = server_profile.SPSignatureAlgorithms()

        values = self.server_profile.get_profile_values([tls.Version.TLS12])
        self.client.init_profile(profile_values=values)

        prof_sig_algo = prof_version.signature_algorithms
        sigalg_list = tls.SignatureScheme.all()

        rsa_ciphers = utils.filter_cipher_suites(
            values.cipher_suites, key_auth=[tls.KeyAuthentication.RSA]
        )
        rsa_sigalgs = [
            x
            for x in filter(
                lambda alg: (alg.value & 0xFF) == tls.SignatureAlgorithm.RSA.value,
                sigalg_list,
            )
        ]
        cert_sig_algs = self.server_profile.get_cert_sig_algos(
            key_types=[tls.SignatureAlgorithm.RSA]
        )
        self._scan_auth_method(
            rsa_ciphers, rsa_sigalgs, cert_sig_algs, prof_sig_algo, _BackendTls12
        )

        dsa_ciphers = utils.filter_cipher_suites(
            values.cipher_suites, key_auth=[tls.KeyAuthentication.DSS]
        )
        dsa_sigalgs = [
            x
            for x in filter(
                lambda alg: (alg.value & 0xFF) == tls.SignatureAlgorithm.DSA.value,
                sigalg_list,
            )
        ]
        cert_sig_algs = self.server_profile.get_cert_sig_algos(
            key_types=[tls.SignatureAlgorithm.DSA]
        )
        self._scan_auth_method(
            dsa_ciphers, dsa_sigalgs, cert_sig_algs, prof_sig_algo, _BackendTls12
        )

        ecdsa_ciphers = utils.filter_cipher_suites(
            values.cipher_suites, key_algo=[tls.KeyExchangeAlgorithm.ECDHE_ECDSA]
        )
        ecdsa_sigalgs = [
            x
            for x in filter(
                lambda alg: (alg.value & 0xFF) == tls.SignatureAlgorithm.ECDSA.value,
                sigalg_list,
            )
        ]
        ecdsa_sigalgs.extend([tls.SignatureScheme.ED25519, tls.SignatureScheme.ED448])
        cert_sig_algs = self.server_profile.get_cert_sig_algos(
            key_types=[
                tls.SignatureAlgorithm.ECDSA,
                tls.SignatureAlgorithm.ED25519,
                tls.SignatureAlgorithm.ED448,
            ]
        )
        self._scan_auth_method(
            ecdsa_ciphers, ecdsa_sigalgs, cert_sig_algs, prof_sig_algo, _BackendTls12
        )

    def _scan_tls13(self):
        prof_version = self.server_profile.get_version_profile(tls.Version.TLS13)
        if prof_version is None:
            return

        if not hasattr(prof_version, "signature_algorithms"):
            prof_version.signature_algorithms = server_profile.SPSignatureAlgorithms()

        values = self.server_profile.get_profile_values([tls.Version.TLS12])
        self.client.init_profile(profile_values=values)
        prof_sig_algo = prof_version.signature_algorithms
        self.client.profile.supported_groups = prof_version.supported_groups.groups
        self.client.profile.key_shares = tls.SupportedGroups.all_tls13()
        self.client.profile.versions = [tls.Version.TLS13]

        self._scan_auth_method(
            prof_version.ciphers.cipher_suites,
            tls.SignatureScheme.all(),
            self.server_profile.get_cert_sig_algos(),
            prof_sig_algo,
            _BackendTls13,
        )

    def run(self):
        self._scan_tls12()
        self._scan_tls13()

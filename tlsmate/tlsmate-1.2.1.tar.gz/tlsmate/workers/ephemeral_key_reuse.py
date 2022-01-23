# -*- coding: utf-8 -*-
"""Module containing the test suite for ephemeral key reuse
"""
# import basic stuff

# import own stuff
import tlsmate.msg as msg
import tlsmate.plugin as plg
import tlsmate.server_profile as server_profile
import tlsmate.tls as tls
import tlsmate.utils as utils

# import other stuff

HANDSHAKE_COUNT = 5


def _determine_status(keys):
    if len(keys) == HANDSHAKE_COUNT:
        if len(set(keys)) == HANDSHAKE_COUNT:
            return tls.ScanState.FALSE

        else:
            return tls.ScanState.TRUE

    return tls.ScanState.UNDETERMINED


class ScanEphemeralKeyReuse(plg.Worker):
    name = "ephemeral_key_reuse"
    descr = "scan for ephemeral key reuse"
    prio = 31

    def _tls12_handshakes(self, cs, pub_key):
        if not cs:
            return tls.ScanState.NA

        self.client.profile.cipher_suites = cs
        keys = []
        for _ in range(HANDSHAKE_COUNT):
            with self.client.create_connection() as conn:
                conn.handshake()

            if conn.msg.server_key_exchange is not None:
                key = pub_key(conn.msg.server_key_exchange)
                if key in keys:
                    return tls.ScanState.TRUE

                keys.append(key)

        return _determine_status(keys)

    def _scan_tls12(self):
        versions = [
            tls.Version.SSL30,
            tls.Version.TLS10,
            tls.Version.TLS11,
            tls.Version.TLS12,
        ]
        prof_values = self.server_profile.get_profile_values(versions)
        if not prof_values.versions:
            return (tls.ScanState.NA, tls.ScanState.NA)

        self.client.init_profile(profile_values=prof_values)
        dhe_cs = utils.filter_cipher_suites(
            prof_values.cipher_suites,
            key_algo=[
                tls.KeyExchangeAlgorithm.DHE_DSS,
                tls.KeyExchangeAlgorithm.DHE_RSA,
            ],
        )
        ecdhe_cs = utils.filter_cipher_suites(
            prof_values.cipher_suites,
            key_algo=[
                tls.KeyExchangeAlgorithm.ECDHE_RSA,
                tls.KeyExchangeAlgorithm.ECDHE_ECDSA,
            ],
        )

        tls12_dhe = self._tls12_handshakes(
            dhe_cs, pub_key=lambda msg: msg.dh.public_key
        )
        tls12_ecdhe = self._tls12_handshakes(
            ecdhe_cs, pub_key=lambda msg: msg.ec.public
        )

        return tls12_dhe, tls12_ecdhe

    def _tls13_handshakes(self, shares):
        if not shares:
            return tls.ScanState.NA

        self.client.profile.supported_groups = shares
        self.client.profile.key_shares = shares
        keys = []
        for _ in range(HANDSHAKE_COUNT):
            with self.client.create_connection() as conn:
                conn.send(msg.ClientHello)
                server_hello = conn.wait(msg.ServerHello)
                key_share_ext = server_hello.get_extension(tls.Extension.KEY_SHARE)
                if not key_share_ext:
                    return tls.ScanState.UNDETERMINED

                key_share = key_share_ext.key_shares[0].key_exchange
                if key_share in keys:
                    return tls.ScanState.TRUE

                keys.append(key_share)
                self.client.profile.cipher_suites = [server_hello.cipher_suite]

        return _determine_status(keys)

    def _scan_tls13(self):
        prof_values = self.server_profile.get_profile_values([tls.Version.TLS13])
        if not prof_values.versions:
            return (tls.ScanState.NA, tls.ScanState.NA)

        self.client.init_profile(profile_values=prof_values)
        ecdhe_shares = []
        dhe_shares = []
        for share in prof_values.key_shares:
            if share.value > 255:
                dhe_shares.append(share)
            else:
                ecdhe_shares.append(share)

        return (
            self._tls13_handshakes(dhe_shares),
            self._tls13_handshakes(ecdhe_shares),
        )

    def run(self):

        tls12_dhe, tls12_ecdhe = self._scan_tls12()
        tls13_dhe, tls13_ecdhe = self._scan_tls13()

        self.server_profile.allocate_features()
        if not hasattr(self.server_profile.features, "ephemeral_key_reuse"):
            self.server_profile.features.ephemeral_key_reuse = (
                server_profile.SPEphemeralKeyReuse()
            )

        ekr = self.server_profile.features.ephemeral_key_reuse
        ekr.tls12_dhe_reuse = tls12_dhe
        ekr.tls12_ecdhe_reuse = tls12_ecdhe
        ekr.tls13_dhe_reuse = tls13_dhe
        ekr.tls13_ecdhe_reuse = tls13_ecdhe

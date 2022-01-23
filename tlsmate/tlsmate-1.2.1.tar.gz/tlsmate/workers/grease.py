# -*- coding: utf-8 -*-
"""Module scanning for protocol parameter tolerance (GREASE)
"""
# import basic stuff
import random

# import own stuff
import tlsmate.ext as ext
import tlsmate.msg as msg
import tlsmate.plugin as plg
import tlsmate.server_profile as server_profile
import tlsmate.tls as tls

# import other stuff

_grease_params = [
    0x0A0A,
    0x1A1A,
    0x2A2A,
    0x3A3A,
    0x4A4A,
    0x5A5A,
    0x6A6A,
    0x7A7A,
    0x8A8A,
    0x9A9A,
    0xAAAA,
    0xBABA,
    0xCACA,
    0xDADA,
    0xEAEA,
    0xFAFA,
]

_grease_cipher_suites = [
    0x0A0A,
    0x1A1A,
    0x2A2A,
    0x3A3A,
    0x4A4A,
    0x5A5A,
    0x6A6A,
    0x7A7A,
    0x8A8A,
    0x9A9A,
    0xAAAA,
    0xBABA,
    0xCACA,
    0xDADA,
    0xEAEA,
    0xFAFA,
]

_grease_psk_modes = [0x0B, 0x2A, 0x49, 0x68, 0x87, 0xA6, 0xC5, 0xE4]


class ScanGrease(plg.Worker):
    name = "grease"
    descr = "scan for tolerance to unknown parameter values (GREASE)"
    prio = 35

    def _get_grease_value(self, values):
        return self._tlsmate.recorder.inject(grease=random.choice(values))

    def _check_version(self, grease_prof):
        values = self.server_profile.get_profile_values(tls.Version.all(), full_hs=True)
        if not values.versions:
            state = tls.ScanState.NA

        else:
            self.client.init_profile(profile_values=values)
            self.client.profile.versions.append(self._get_grease_value(_grease_params))
            with self.client.create_connection() as conn:
                conn.handshake()

            if conn.handshake_completed:
                state = tls.ScanState.TRUE

            else:
                state = tls.ScanState.FALSE

        setattr(grease_prof, "version_tolerance", state)

    def _check_cipher_suite(self, grease_prof):
        values = self.server_profile.get_profile_values(tls.Version.all(), full_hs=True)
        if not values.versions:
            state = tls.ScanState.NA

        else:
            self.client.init_profile(profile_values=values)
            self.client.profile.cipher_suites.insert(
                0, self._get_grease_value(_grease_cipher_suites)
            )
            with self.client.create_connection() as conn:
                conn.handshake()

            if conn.handshake_completed:
                state = tls.ScanState.TRUE

            else:
                state = tls.ScanState.FALSE

        setattr(grease_prof, "cipher_suite_tolerance", state)

    def _check_extension(self, grease_prof):
        def add_unknown_extension(msg):
            unknown_ext = ext.ExtUnknownExtension(
                id=self._get_grease_value(_grease_params), bytes=b"deadbeef"
            )
            msg.extensions.insert(0, unknown_ext)

        versions = tls.Version.tls_only()
        values = self.server_profile.get_profile_values(versions, full_hs=True)
        if not values.versions:
            state = tls.ScanState.NA

        else:
            self.client.init_profile(profile_values=values)
            with self.client.create_connection() as conn:
                conn.handshake(ch_pre_serialization=add_unknown_extension)

            if conn.handshake_completed:
                state = tls.ScanState.TRUE

            else:
                state = tls.ScanState.FALSE

        setattr(grease_prof, "extension_tolerance", state)

    def _check_groups(self, grease_prof):
        versions = tls.Version.tls_only()
        values = self.server_profile.get_profile_values(versions, full_hs=True)
        if not values.versions or not values.supported_groups:
            state = tls.ScanState.NA

        else:
            self.client.init_profile(profile_values=values)
            self.client.profile.supported_groups.insert(
                0, self._get_grease_value(_grease_params)
            )
            state = tls.ScanState.UNDETERMINED
            with self.client.create_connection() as conn:
                conn.handshake()

            if conn.handshake_completed:
                state = tls.ScanState.TRUE

            else:
                state = tls.ScanState.FALSE

        setattr(grease_prof, "group_tolerance", state)

    def _check_sig_algo(self, grease_prof):
        versions = [tls.Version.TLS12, tls.Version.TLS13]
        values = self.server_profile.get_profile_values(versions, full_hs=True)
        if not values.versions:
            state = tls.ScanState.NA

        else:
            self.client.init_profile(profile_values=values)
            self.client.profile.signature_algorithms.insert(
                0, self._get_grease_value(_grease_params)
            )
            state = tls.ScanState.UNDETERMINED
            with self.client.create_connection() as conn:
                conn.handshake()

            if conn.handshake_completed:
                state = tls.ScanState.TRUE

            else:
                state = tls.ScanState.FALSE

        setattr(grease_prof, "sig_algo_tolerance", state)

    def _check_psk_mode(self, grease_prof):
        if (
            getattr(self.server_profile.features, "resumption_psk", None)
            is not tls.ScanState.TRUE
        ):
            state = tls.ScanState.NA

        else:
            values = self.server_profile.get_profile_values(
                [tls.Version.TLS13], full_hs=True
            )
            self.client.init_profile(profile_values=values)
            state = tls.ScanState.UNDETERMINED
            self.client.profile.support_psk = True
            self.client.profile.psk_key_exchange_modes = [
                self._get_grease_value(_grease_psk_modes),
                tls.PskKeyExchangeMode.PSK_DHE_KE,
                tls.PskKeyExchangeMode.PSK_KE,
            ]
            ticket_msg = None
            with self.client.create_connection() as conn:
                conn.handshake()
                ticket_msg = conn.wait(msg.NewSessionTicket, optional=True, timeout=200)

            if ticket_msg:
                with self.client.create_connection() as conn:
                    conn.handshake()

                if conn.handshake_completed:
                    state = tls.ScanState.TRUE

                else:
                    state = tls.ScanState.FALSE

        setattr(grease_prof, "psk_mode_tolerance", state)

    def run(self):
        self.server_profile.allocate_features()
        grease_prof = getattr(self.server_profile.features, "grease", None)
        if grease_prof is None:
            grease_prof = server_profile.SPGrease
            self.server_profile.features.grease = grease_prof

        self._check_version(grease_prof)
        self._check_cipher_suite(grease_prof)
        self._check_extension(grease_prof)
        self._check_groups(grease_prof)
        self._check_sig_algo(grease_prof)
        self._check_psk_mode(grease_prof)

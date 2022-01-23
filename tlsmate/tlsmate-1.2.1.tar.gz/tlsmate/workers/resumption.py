# -*- coding: utf-8 -*-
"""Module scanning for resumption support
"""
# import basic stuff

# import own stuff
import tlsmate.msg as msg
import tlsmate.plugin as plg
import tlsmate.tls as tls

# import other stuff


class ScanResumption(plg.Worker):
    name = "resumption"
    descr = "scan for resumption support (session_id and ticket)"
    prio = 30

    def _resumption_tls12(self, prof_vals, session_ticket=False):
        if not prof_vals.cipher_suites:
            # no cipher suite, for which a hull handshake is supported.
            state = tls.ScanState.UNDETERMINED
        else:
            state = tls.ScanState.FALSE
            self.client.init_profile(profile_values=prof_vals)
            if session_ticket:
                self.client.profile.support_session_ticket = True
            else:
                self.client.profile.support_session_id = True
            with self.client.create_connection() as conn:
                conn.handshake()
            if conn.handshake_completed:
                if session_ticket:
                    resumption_possible = ...
                else:
                    resumption_possible = bool(len(conn.msg.server_hello.session_id))
                if resumption_possible:
                    self.client.profile.cipher_suites = [
                        conn.msg.server_hello.cipher_suite
                    ]
                    with self.client.create_connection() as conn2:
                        conn2.handshake()
                    if conn2.handshake_completed and conn2.abbreviated_hs:
                        state = tls.ScanState.TRUE
        return state

    def _run_tls12(self):
        versions = [tls.Version.TLS10, tls.Version.TLS11, tls.Version.TLS12]
        prof_vals = self.server_profile.get_profile_values(versions, full_hs=True)
        prof_features = self.server_profile.features

        session_id_support = tls.ScanState.NA
        session_ticket_support = tls.ScanState.NA
        if prof_vals.versions:
            session_id_support = self._resumption_tls12(prof_vals, session_ticket=False)
            session_ticket_support = self._resumption_tls12(
                prof_vals, session_ticket=True
            )

        prof_features.session_ticket = session_ticket_support
        prof_features.session_id = session_id_support
        if session_ticket_support is tls.ScanState.TRUE:
            prof_features.session_ticket_lifetime = (
                self.client.session.session_state_ticket.lifetime
            )

    def _run_tls13(self):
        resumption_psk = tls.ScanState.NA
        early_data = tls.ScanState.NA
        psk_lifetime = None
        prof_vals = self.server_profile.get_profile_values(
            [tls.Version.TLS13], full_hs=True
        )
        if prof_vals.versions:
            self.client.init_profile(profile_values=prof_vals)
            self.client.profile.support_psk = True
            self.client.profile.psk_key_exchange_modes = [
                tls.PskKeyExchangeMode.PSK_DHE_KE,
                tls.PskKeyExchangeMode.PSK_KE,
            ]
            ticket_msg = None
            with self.client.create_connection() as conn:
                conn.handshake()
                ticket_msg = conn.wait(msg.NewSessionTicket, optional=True, timeout=200)
                if ticket_msg is not None:
                    psk_lifetime = ticket_msg.lifetime
                else:
                    resumption_psk = tls.ScanState.FALSE

            if ticket_msg:
                resumption_psk = tls.ScanState.TRUE
                early_data = tls.ScanState.FALSE

                self.client.profile.early_data = b"This is EarlyData (0-RTT)"
                with self.client.create_connection() as conn:
                    conn.handshake()

                if conn.early_data_accepted:
                    early_data = tls.ScanState.TRUE

        self.server_profile.features.resumption_psk = resumption_psk
        self.server_profile.features.early_data = early_data
        if psk_lifetime is not None:
            self.server_profile.features.psk_lifetime = psk_lifetime

    def run(self):
        self.server_profile.allocate_features()
        self._run_tls12()
        self._run_tls13()

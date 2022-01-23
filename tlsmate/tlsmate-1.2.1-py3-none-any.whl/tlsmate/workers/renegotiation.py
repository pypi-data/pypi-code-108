# -*- coding: utf-8 -*-
"""Module scanning for renegotiation support
"""
# import basic stuff

# import own stuff
import tlsmate.plugin as plg
import tlsmate.tls as tls

# import other stuff


class ScanRenegotiation(plg.Worker):
    name = "renegotiation"
    descr = "scan for renegotiation support"
    prio = 30

    def run(self):

        self.server_profile.allocate_features()
        versions = [tls.Version.TLS10, tls.Version.TLS11, tls.Version.TLS12]
        prof_values = self.server_profile.get_profile_values(versions, full_hs=True)
        if not prof_values.versions:
            self.server_profile.features.insecure_renegotiation = tls.ScanState.NA
            self.server_profile.features.secure_renegotation = tls.ScanState.NA
            self.server_profile.features.scsv_renegotiation = tls.ScanState.NA
            return

        self.server_profile.features.insecure_renegotiation = tls.ScanState.UNDETERMINED
        self.server_profile.features.secure_renegotation = tls.ScanState.UNDETERMINED
        self.server_profile.features.scsv_renegotiation = tls.ScanState.UNDETERMINED
        self.client.init_profile(profile_values=prof_values)
        self.server_profile.features.insecure_renegotiation = tls.ScanState.FALSE
        with self.client.create_connection() as conn:
            conn.handshake()
            conn.handshake()
            if conn.handshake_completed:
                self.server_profile.features.insecure_renegotiation = tls.ScanState.TRUE

        self.server_profile.features.secure_renegotation = tls.ScanState.FALSE
        self.client.profile.support_secure_renegotiation = True
        with self.client.create_connection() as conn:
            conn.handshake()
            conn.handshake()
            if conn.handshake_completed:
                self.server_profile.features.secure_renegotation = tls.ScanState.TRUE

        self.server_profile.features.scsv_renegotiation = tls.ScanState.FALSE
        self.client.profile.support_secure_renegotiation = False
        self.client.profile.support_scsv_renegotiation = True
        with self.client.create_connection() as conn:
            conn.handshake()
            conn.handshake()
            if conn.handshake_completed:
                self.server_profile.features.scsv_renegotiation = tls.ScanState.TRUE

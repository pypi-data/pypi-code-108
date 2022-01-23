# -*- coding: utf-8 -*-
"""Module scanning for the CCS-injection vulnerability

Refer to CVE-2014-0224

OpenSSL 1.0.1g and before was vulnerable.

ChangeCipherSpec is injected directly after receiving the ServerHelloDone. The server
then updated its connection state which means subsequent sent messages by the client
were regarded as protected records.
"""
# import basic stuff

# import own stuff
import tlsmate.msg as msg
import tlsmate.plugin as plg
import tlsmate.tls as tls

# import other stuff


class ScanCcsInjection(plg.Worker):
    name = "ccsinjection"
    descr = "scan for CCS injection vulnerability (CVE-2014-0224)"
    prio = 40

    def run(self):
        status = tls.ScanState.NA
        values = self.server_profile.get_profile_values(
            [tls.Version.TLS10, tls.Version.TLS11, tls.Version.TLS12], full_hs=True
        )
        if values.versions:
            status = tls.ScanState.UNDETERMINED
            self.client.init_profile(profile_values=values)
            with self.client.create_connection() as conn:
                conn.send(msg.ClientHello)
                conn.wait(msg.ServerHello)
                conn.wait(msg.Certificate, optional=True)
                conn.wait(msg.ServerKeyExchange, optional=True)
                conn.wait(msg.CertificateRequest, optional=True)
                conn.wait(msg.ServerHelloDone)

                # Normal handshake up to here. Now prematurely inject the CCS.
                conn.send(msg.ChangeCipherSpec)

                # And now send any other message. We use CCS again
                conn.send(msg.ChangeCipherSpec)

                try:
                    rec_msg = conn.wait(msg.Alert, timeout=2000, fail_on_timeout=False)
                    if isinstance(rec_msg, msg.Alert) and (
                        rec_msg.description is tls.AlertDescription.BAD_RECORD_MAC
                        or rec_msg.description is tls.AlertDescription.DECRYPTION_FAILED
                    ):
                        # vulnerable
                        status = tls.ScanState.TRUE

                    else:
                        status = tls.ScanState.FALSE

                except tls.TlsConnectionClosedError:
                    status = tls.ScanState.FALSE

        self.server_profile.allocate_vulnerabilities()
        self.server_profile.vulnerabilities.ccs_injection = status

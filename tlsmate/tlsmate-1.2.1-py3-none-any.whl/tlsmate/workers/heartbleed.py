# -*- coding: utf-8 -*-
"""Module scanning for the Heartbleet vulnerability

Refer to CVE-2014-0160, bug in openssl versions, no proper length check
for the heartbeat request. Refer to https://heartbleed.com/
"""
# import basic stuff

# import own stuff
import tlsmate.msg as msg
import tlsmate.plugin as plg
import tlsmate.tls as tls

# import other stuff


class ScanHeartbleed(plg.Worker):
    name = "heartbleed"
    descr = "scan for Heartbleed vulnerability"
    prio = 41

    def run(self):
        if not hasattr(self.server_profile, "features"):
            hb = tls.HeartbeatState.UNDETERMINED

        else:
            hb = getattr(
                self.server_profile.features,
                "heartbeat",
                tls.HeartbeatState.UNDETERMINED,
            )

        state = tls.HeartbleedStatus.UNDETERMINED
        if hb in (tls.HeartbeatState.FALSE, tls.HeartbeatState.NA):
            state = tls.HeartbleedStatus.NOT_APPLICABLE

        elif hb is tls.HeartbeatState.TRUE:
            values = self.server_profile.get_profile_values(
                tls.Version.all(), full_hs=True
            )
            self.client.init_profile(profile_values=values)
            self.client.profile.heartbeat_mode = tls.HeartbeatMode.PEER_ALLOWED_TO_SEND
            with self.client.create_connection() as conn:
                conn.handshake()
                request = msg.HeartbeatRequest()
                request.payload = b"abc"
                request.payload_length = 4
                request.padding = b""
                conn.send(request)
                try:
                    response = conn.wait(msg.HeartbeatResponse, timeout=2000)
                    if response is not None:
                        state = (
                            tls.HeartbleedStatus.VULNERABLE
                            if response.payload_length == 4
                            else tls.HeartbleedStatus.NOT_VULNERABLE
                        )

                except tls.TlsMsgTimeoutError:
                    state = tls.HeartbleedStatus.TIMEOUT

                except tls.TlsConnectionClosedError:
                    state = tls.HeartbleedStatus.CONNECTION_CLOSED

        self.server_profile.allocate_vulnerabilities()
        self.server_profile.vulnerabilities.heartbleed = state

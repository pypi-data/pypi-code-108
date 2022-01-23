# -*- coding: utf-8 -*-
"""Module scanning for heartbeat support
"""
# import basic stuff

# import own stuff
import tlsmate.msg as msg
import tlsmate.plugin as plg
import tlsmate.tls as tls

# import other stuff


class ScanHeartbeat(plg.Worker):
    name = "heartbeat"
    descr = "scan for heartbeat support"
    prio = 30

    def run(self):
        state = tls.HeartbeatState.UNDETERMINED
        versions = [
            tls.Version.TLS10,
            tls.Version.TLS11,
            tls.Version.TLS12,
            tls.Version.TLS13,
        ]
        prof_values = self.server_profile.get_profile_values(versions, full_hs=True)
        if not prof_values.versions:
            state = tls.HeartbeatState.NA

        else:
            self.client.init_profile(profile_values=prof_values)
            self.client.profile.heartbeat_mode = tls.HeartbeatMode.PEER_ALLOWED_TO_SEND
            with self.client.create_connection() as conn:
                conn.handshake()
                if conn.handshake_completed:
                    hb = conn.msg.server_hello.get_extension(tls.Extension.HEARTBEAT)
                    if hb:
                        if hb.heartbeat_mode is tls.HeartbeatMode.PEER_ALLOWED_TO_SEND:
                            req = msg.HeartbeatRequest()
                            req.payload = b"abracadabra"
                            req.payload_length = len(req.payload)
                            req.padding = b"\xff" * 16
                            conn.send(req)
                            rec_msg = conn.wait(
                                msg.Any, timeout=2000, fail_on_timeout=False,
                            )
                            if rec_msg is None:
                                state = tls.HeartbeatState.NOT_REPONDING

                            elif isinstance(rec_msg, msg.HeartbeatResponse):
                                if (
                                    req.payload_length == rec_msg.payload_length
                                    and req.payload == rec_msg.payload
                                ):
                                    state = tls.HeartbeatState.TRUE

                                else:
                                    state = tls.HeartbeatState.WRONG_RESPONSE

                            else:
                                state = tls.HeartbeatState.UNEXPECTED_MESSAGE

                        else:
                            state = tls.HeartbeatState.FALSE

                    else:
                        state = tls.HeartbeatState.FALSE

        self.server_profile.allocate_features()
        self.server_profile.features.heartbeat = state

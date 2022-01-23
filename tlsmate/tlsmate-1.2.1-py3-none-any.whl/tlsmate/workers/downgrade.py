# -*- coding: utf-8 -*-
"""Module for downgrade attack prevention worker
"""
# import basic stuff

# import own stuff
import tlsmate.msg as msg
import tlsmate.plugin as plg
import tlsmate.tls as tls

# import other stuff


class ScanDowngrade(plg.Worker):
    name = "downgrade"
    descr = "scan for downgrade attack prevention"
    prio = 30

    def run(self):
        versions = self.server_profile.get_versions()
        nbr_versions = len(versions)
        if tls.Version.SSL20 in versions:
            nbr_versions -= 1

        if nbr_versions < 2:
            status = tls.ScanState.NA

        else:
            prof_values = self.server_profile.get_profile_values([versions[-2]])
            self.client.init_profile(profile_values=prof_values)
            self.client.profile.cipher_suites.append(tls.CipherSuite.TLS_FALLBACK_SCSV)

            status = tls.ScanState.UNDETERMINED
            with self.client.create_connection() as conn:
                conn.send(msg.ClientHello)
                response = conn.wait(msg.Any)
                if isinstance(response, msg.ServerHello):
                    status = tls.ScanState.FALSE

                elif isinstance(response, msg.Alert):
                    status = tls.ScanState.TRUE

        self.server_profile.allocate_features()
        self.server_profile.features.downgrade_attack_prevention = status

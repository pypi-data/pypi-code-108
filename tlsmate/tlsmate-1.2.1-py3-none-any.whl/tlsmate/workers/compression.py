# -*- coding: utf-8 -*-
"""Module scanning for compression support
"""
# import basic stuff

# import own stuff
import tlsmate.msg as msg
import tlsmate.plugin as plg
import tlsmate.tls as tls

# import other stuff


class ScanCompression(plg.Worker):
    name = "compression"
    descr = "scan for compression support"
    prio = 30

    def _compression(self, version):
        self.server_profile.allocate_features()
        features = self.server_profile.features
        if not hasattr(features, "compression"):
            features.compression = []

        values = self.server_profile.get_profile_values([version])
        self.client.init_profile(profile_values=values)
        comp_methods = tls.CompressionMethod.all()

        while comp_methods:
            self.client.profile.compression_methods = comp_methods
            server_hello = None
            with self.client.create_connection() as conn:
                conn.send(msg.ClientHello)
                server_hello = conn.wait(msg.ServerHello)

            if server_hello is None:
                break

            if server_hello.version is not version:
                break

            if server_hello.compression_method not in comp_methods:
                break

            comp_methods.remove(server_hello.compression_method)
            if server_hello.compression_method not in features.compression:
                features.compression.append(server_hello.compression_method)

    def run(self):
        for version in self.server_profile.get_versions(exclude=[tls.Version.SSL20]):
            self._compression(version)

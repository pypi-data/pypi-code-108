# -*- coding: utf-8 -*-
"""Module providing infos about the scanner
"""
# import basic stuff
import sys
import time
import datetime

# import own stuff
import tlsmate.plugin as plg
import tlsmate.resolver as resolver
import tlsmate.server_profile as server_profile
import tlsmate.tls as tls
import tlsmate.version as version

# import other stuff


class ScanStart(plg.Worker):
    """Provide basic infos without actually really scanning against the server.
    """

    name = "scanstart"
    descr = "determine basic settings"
    prio = 0

    def run(self):
        """The entry point for the worker.
        """

        if not hasattr(self.server_profile, "scan_info"):
            self.server_profile.scan_info = server_profile.SPScanInfo()

        scan_info = self.server_profile.scan_info
        start_time = time.time()
        scan_info.command = " ".join(sys.argv)
        scan_info.version = version.__version__
        scan_info.start_timestamp = start_time
        scan_info.start_date = datetime.datetime.fromtimestamp(int(start_time))
        endp = resolver.determine_l4_addr(
            self.config.get("host"), self.config.get("port")
        )
        data = {"port": endp.port}
        if endp.host_type is tls.HostType.HOST:
            name_res_data = {"domain_name": endp.host}
            ips = resolver.resolve_hostname(endp.host, self.config.get("proxy"))
            if ips.ipv4_addresses:
                name_res_data["ipv4_addresses"] = ips.ipv4_addresses

            if ips.ipv6_addresses:
                name_res_data["ipv6_addresses"] = ips.ipv6_addresses

            endp = resolver.get_ip_endpoint(endp)
            data["name_resolution"] = server_profile.SPNameResolution(
                data=name_res_data
            )

        data["ip"] = endp.host
        try:
            data["sni"] = self.client.get_sni()

        except ValueError:
            pass

        proxy = self.config.get("proxy")
        if proxy:
            data["proxy"] = proxy

        self.server_profile.server = server_profile.SPServer(data=data)


class ScanEnd(plg.Worker):
    """Complement the info after the scan is finished.
    """

    name = "scanend"
    descr = "conclude the scan"
    prio = 1000

    def run(self):
        """The entry point for the worker.
        """

        if self.client.server_issues:
            if not hasattr(self.server_profile, "server_malfunctions"):
                self.server_profile.server_malfunctions = []

            for malfunction in self.client.server_issues:
                self.server_profile.server_malfunctions.append(
                    server_profile.SPServerMalfunction(malfunction=malfunction)
                )

        scan_info = self.server_profile.scan_info
        start_time = scan_info.start_timestamp
        stop_time = time.time()
        scan_info.stop_timestamp = stop_time
        scan_info.stop_date = datetime.datetime.fromtimestamp(int(stop_time))
        scan_info.run_time = float(f"{stop_time - start_time:.3f}")

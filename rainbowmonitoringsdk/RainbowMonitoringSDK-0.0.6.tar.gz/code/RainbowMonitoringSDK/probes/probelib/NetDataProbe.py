import re
import subprocess
import requests
import yaml
from yaml.loader import SafeLoader
from RainbowMonitoringSDK.probes.Metric import SimpleMetric
from RainbowMonitoringSDK.probes.Probe import Probe
from RainbowMonitoringSDK.probes.utils import NetDataController


class NetDataProbe(Probe):
    # overall cpu, memomory, disk, disk i/o
    __REGEX_METRIC_NAME_FOR_DEMO = {
        '_SYSTEM_CPU_IDLE': 'cpu_idle',
        '_SYSTEM_CPU_VISIBLETOTAL': 'cpu_ptc',
        '_APPS_SOCKETS_VISIBLETOTAL': '',
        '_SYSTEM_RAM_FREE': 'memory_free',
        '_SYSTEM_RAM_USED': 'memory_used',
        '_SYSTEM_RAM_CACHED': 'memory_cached',
        '_SYSTEM_RAM_BUFFERS': 'memory_buffers',
        '_SYSTEM_RAM_VISIBLETOTAL': 'memory_total',

        '_IPV6_PACKETS_RECEIVED': 'ipv6_packets_received',  # packets/s
        '_IPV6_PACKETS_SENT': 'ipv6_packets_sent',  # packets/s
        '_IPV6_PACKETS_FORWARDED': 'ipv6_packets_forwarded',  # packets/s
        '_IPV6_PACKETS_DELIVERS': 'ipv6_packets_delivers',  # packets/s
        '_IPV6_PACKETS_VISIBLETOTAL': 'ipv6_packets_total',  # packets/s

        '_IPV4_PACKETS_RECEIVED': 'ipv4_packets_received',  # packets/s
        '_IPV4_PACKETS_SENT': 'ipv4_packets_sent',  # packets/s
        '_IPV4_PACKETS_FORWARDED': 'ipv4_packets_forwarded',  # packets/s
        '_IPV4_PACKETS_DELIVERS': 'ipv4_packets_delivers',  # packets/s
        '_IPV4_PACKETS_VISIBLETOTAL': 'ipv4_packets_total',  # packets/s

        '_SYSTEM_IPV6_RECEIVED': 'ipv6_kb_received', # kilobits/s
        '_SYSTEM_IPV6_SENT': 'ipv6_kb_sent',  # kilobits/s
        '_SYSTEM_IPV6_VISIBLETOTAL': 'ipv6_kb_total',  # kilobits/s
        '_SYSTEM_IP_RECEIVED': 'ipv4_kb_received' , # kilobits/s
        '_SYSTEM_IP_SENT': 'ipv4_kb_sent',  # kilobits/s
        '_SYSTEM_IP_VISIBLETOTAL': 'ipv4_kb_total',  # kilobits/s
        '_DISK_SPACE___AVAIL': 'disk_available',
        '_DISK_SPACE___USED': 'disk_used',
        '_DISK_SPACE___RESERVED_FOR_ROOT': 'disk_reserved_for_root',
        '_DISK_SPACE___VISIBLETOTAL': 'disk_total'
        }
    __NETDATA_URL_TEMPLATE = "http://%s:%s/api/v1/allmetrics"

    __NETDATA_STARTED = 0

    def __init__(self,
                 periodicity,
                 prefix="",
                 ip_address='0.0.0.0',
                 port='19999',
                 debug=False,
                 logging=False,
                 *args,
                 **kwargs):
        Probe.__init__(self, "NetData", periodicity, debug, logging)
        self.controller = NetDataController()
        self.ip_address = ip_address
        self.port = port
        self.url = self.__NETDATA_URL_TEMPLATE % (self.ip_address, self.port)
        self.prefix = prefix

    def get_desc(self):
        return "The monitoring probe of netdata"

    def collect(self):
        raw_metrics = self.retrieve_metrics()
        for raw_metric in raw_metrics:
            high_level_name = self.__is_in_demo_metrics(raw_metric['name'])
            if not high_level_name: continue
            metric = self.get_metric(high_level_name)
            if not metric:
                metric = SimpleMetric(high_level_name, raw_metric['unit'], raw_metric['name'])
                self.add_metric(metric)
            metric.set_val(raw_metric['value'])
            metric.set_group('NETDATA')  # TODO Change to be more group specific

    def __is_in_demo_metrics(self, metric_name):
        for regex in self.__REGEX_METRIC_NAME_FOR_DEMO:
            if re.search(regex, metric_name):
                return self.__REGEX_METRIC_NAME_FOR_DEMO.get(regex)
        return False

    def retrieve_metrics(self):
        res = []
        try:
            metrics = requests.get(self.url).text
            self.__NETDATA_STARTED = 1
        except Exception as e:
            print("NetData is not working: ", e)
            return []
        for metric_line in metrics.splitlines():
            name, value, unit = self.__extract_information_from_line(metric_line)
            try:
                float(value)
            except Exception:
                continue
            res.append(dict(name=name, value=value, unit=unit))
        return res

    def __extract_information_from_line(self, metric_line):
        try:
            value_and_unit = metric_line.split("#")
            if len(value_and_unit) == 1:
                value, unit = value_and_unit[0], None
            else:
                value, unit = value_and_unit[0], value_and_unit[1]

            unit = unit.strip().replace(" ", "_")
            value = value.strip().split("=")
            name, value = value[0], value[1].replace('"', "")
            name = name.replace('NETDATA', self.prefix)
            return name, value, unit
        except Exception:
            return None, None, None

    def activate(self):
        # Open the file and load the file
        with open('/code/configs.yaml') as f:
            data = yaml.load(f, Loader=SafeLoader)
            self.controller.update_configs(data["sensing-units"])

        self.a_child_process = subprocess.Popen(["bash", "/usr/sbin/run.sh", "-c", "/code/RainbowMonitoringSDK/probes/net-data.cfg"], shell=False,
                                                stdout=open("netdata-stdout.txt", "w"),
                                                stderr=open("netdata-stderr.txt", "w"))
        Probe.activate(self)

    def cleanup(self):
        self.a_child_process.terminate()


def main():
    p = NetDataProbe("netdata", 5, ip_address="0.0.0.0", port=19999)
    p.set_debugmode(True)
    p.set_logging()

    p.activate()


if __name__ == "__main__":
    main()

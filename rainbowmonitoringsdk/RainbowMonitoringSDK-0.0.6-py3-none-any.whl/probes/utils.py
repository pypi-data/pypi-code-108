import json
import logging
import os
import subprocess
from functools import wraps
from random import randint
from configupdater import ConfigUpdater
from time import time, sleep
from RainbowMonitoringSDK.probes.Metric import SimpleMetric, Metric

DOCKER_ID_LENGTH = 64


class ConfigFileIsNotValid(Exception):
    """Raised when the config file does not contain name"""
    pass


class NetDataController:
    disable_config_netdata = {
        "cpu": {
            "plugin:proc": ["/proc/stat"]
        },
        "memory": {
            "plugin:proc": ["/proc/meminfo"]
        },
        "disk": {
            "plugin:proc": ["/proc/diskstats"],
            "plugins": ["diskspace"]
        },
        "network": {
            "plugin:proc": [
                "/proc/net/dev", "/proc/net/wireless",
                "/proc/net/sockstat", "/proc/net/sockstat6",
                "/proc/net/netstat", "/proc/net/snmp",
                "/proc/net/snmp6", "/proc/net/sctp/snmp",
                "/proc/net/softnet_stat", "/proc/net/ip_vs/stats",
                "/proc/net/stat/conntrack", "/proc/net/stat/synproxy"
            ]
        }
    }

    set_config_netdata = {
        "cpu": "stat", "memory": "meminfo", "disk": "disk", "network": "net"
    }

    disable_configs = [
        "space usage", "enable", "inodes usage"
    ]

    def update_configs(self, config: dict = None):
        parser = ConfigUpdater()
        parser.read("/code/RainbowMonitoringSDK/probes/net-data.cfg")

        self.__set_periodicity(config, parser)
        disabled_groups = config["DefaultMonitoring"]["disabled-groups"]
        metric_groups = config["DefaultMonitoring"]["metric-groups"]

        # disable groups
        if disabled_groups is not None:
            for key in disabled_groups:
                print("disabled")
                print(self.disable_config_netdata[key].keys())
                for config_netdata_key in self.disable_config_netdata[key].keys():
                    for config_key in parser.sections():
                        if config_key == config_netdata_key:
                            # iterate in each subcategory the disabled category has
                            for key_category in self.disable_config_netdata[key].values():
                                if key_category in parser[config_netdata_key]:
                                    print(key_category)
                                    parser[config_netdata_key][key_category].value = "no"
                        if key in config_key and "plugin" in config_key:
                            for disabled_config in self.disable_configs:
                                if disabled_config in parser[config_key]:
                                    parser[config_key][disabled_config].value = "no"

        # override configurations
        if metric_groups is not None:
            for key in metric_groups:
                print("metric")
                if "name" in key:
                    for config_key in parser.sections():
                        # make key to lower case
                        key["name"] = key["name"].lower()
                        if self.set_config_netdata[key["name"]] in config_key and "plugin" in config_key:
                            print(config_key)
                            '''
                            warning!: if custom periodicity if smaller than general periodicity, 
                            then the general periodicity is applied
                            '''
                            if "periodicity" in key:
                                specific_periodicity = None
                                if "adaptive" in key["periodicity"]:
                                    if "minimum_periodicity" in key["params"]:
                                        specific_periodicity = key["params"]["minimum_periodicity"]
                                else:
                                    specific_periodicity = key["periodicity"]
                                if "update every" in parser[config_key]:
                                    parser[config_key]["update every"].value = specific_periodicity
                                else:
                                    parser[config_key]["update every"] = str(specific_periodicity)
                else:
                    raise ConfigFileIsNotValid()

        parser.update_file()

    def __set_periodicity(self, config: dict = None, parser=None):
        # set NetData periodicity
        periodicity = None
        if "periodicity" in config["DefaultMonitoring"]:
            periodicity = config["DefaultMonitoring"]["periodicity"]
        elif "general-periodicity" in config["general-periodicity"]:
            periodicity = config["general-periodicity"]
        if periodicity is not None:
            parser["global"]["update every"] = periodicity


def get_entity_id():
    res = subprocess.Popen("head -1 /proc/self/cgroup|cut -d/ -f3", shell=True, stdout=subprocess.PIPE)
    encoded_first_line = res.stdout.readlines()[0].decode().replace("\n", "")
    if len(encoded_first_line) != DOCKER_ID_LENGTH:
        logging.warning("This node probably is not containerised because has not container id")
        return None
    return encoded_first_line[:12]


class RainbowUtils:
    __ENTITY_ID__ = get_entity_id()
    __STORAGE_FILE__ = os.getenv("RAINBOW_METRIC_PATH", "./") + "rainbow.metrics.jsonl"
    __COUNT_IT_FUNCTIONS__ = {}

    @classmethod
    def store(cls, value, name, units, desc,
              minVal=float('-inf'), maxVal=float('inf'), higherIsBetter=True):
        simple_metric = SimpleMetric(name, units, desc, minVal, maxVal, higherIsBetter=higherIsBetter)
        simple_metric.set_val(value)
        cls.__store(simple_metric)

    @classmethod
    def __store(cls, metric: Metric):
        with open(cls.__STORAGE_FILE__, mode='a', encoding='utf-8') as file:
            new_name = cls.__container_enconded_name(metric)
            metric.set_name(new_name)
            metric_dict = metric.to_dict()
            json_metric = json.dumps(metric_dict) + '\n'
            file.write(json_metric)

    @classmethod
    def __container_enconded_name(cls, metric):
        if metric.name.startswith('_CGROUP_'):
            return metric.name
        prefix = '_CGROUP_' + cls.__ENTITY_ID__ + '__' if cls.__ENTITY_ID__ else ''
        new_name = prefix + metric.name  # Special name for
        return new_name

    @classmethod
    def timeit(cls, f):
        @wraps(f)
        def wrap(*args, **kw):
            ts = time()
            result = f(*args, **kw)
            te = time()
            name, unit, desc = "time__%s" % (f.__name__), 'ms', 'Execution duration from %s function' % (f.__name__)
            simple_metric = SimpleMetric(name, unit, desc, minVal=0.0, higherIsBetter=False)
            simple_metric.set_val(te - ts)
            cls.__store(simple_metric)
            return result

        return wrap

    @classmethod
    def export(cls, name, units, desc, minVal=float('-inf'), maxVal=float('inf'), higherIsBetter=True):
        def _export(f):
            simple_metric = SimpleMetric(name, units, desc, minVal=minVal, maxVal=maxVal, higherIsBetter=higherIsBetter)
            if not callable(f):
                simple_metric.set_val(f)
                cls.__store(simple_metric)
                return f

            @wraps(f)
            def wrap(*args, **kw):
                result = f(*args, **kw)
                if result is not None:
                    simple_metric.set_val(result)
                    cls.__store(simple_metric)
                else:
                    warning = "Function %s returned None as result, monitoring can not capture this value" % f.__name__
                    logging.warning(warning)
                return result

            return wrap

        return _export

    @classmethod
    def countit(cls, f):
        @wraps(f)
        def wrap(*args, **kw):
            result = f(*args, **kw)
            functions, function_name = cls.__COUNT_IT_FUNCTIONS__, f.__name__
            if function_name not in functions:
                functions[function_name] = 0
            functions[function_name] += 1
            name, unit, desc = "countit__%s" % function_name, 'runs', 'The running times of %s function' % function_name
            simple_metric = SimpleMetric(name, unit, desc, minVal=0.0, higherIsBetter=False)
            simple_metric.set_val(functions[function_name])
            cls.__store(simple_metric)
            return result

        return wrap


# Example of usage ---------------

@RainbowUtils.export("energy-consumption", "watt", "Energy consumption of the running node")
def energy_consumption_calculator():
    # current node's energy consumption
    return randint(1, 10)


@RainbowUtils.timeit
def intensive_workload_function():
    sleep(3)
    return randint(1, 10)


@RainbowUtils.countit
def http_endpoint():
    return randint(1, 10)


def main():
    variable = randint(1, 10)
    RainbowUtils.store(variable, "an_exported_variable", "some_unit",
                       "This variable is very crucial", minVal=float('-inf'),
                       maxVal=float('inf'), higherIsBetter=True)

    energy_consumption_calculator()
    intensive_workload_function()
    for times in range(20):
        http_endpoint()
        sleep(5)


if __name__ == "__main__":
    main()

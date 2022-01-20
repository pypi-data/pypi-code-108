
import docker
from RainbowMonitoringSDK.probes.Probe import Probe
from RainbowMonitoringSDK.probes.Metric import SimpleMetric

class DockerProbe(Probe):

    def __init__(self,
                 periodicity, debug=False, _logging=False,
                 docker_client=None,
                 **kwargs):
        Probe.__init__(self, "DockerProbe", periodicity,  debug, _logging)
        self.docker_client = docker.from_env() if docker_client is None else docker_client
        self.config = kwargs

    def get_desc(self):
        return "The monitoring probe of docker containers"

    def collect(self):
        raw_metrics = self.retrieve_metrics()
        for raw_metric in raw_metrics:
            metric = self.get_metric(raw_metric.get_name())
            if not metric:
                metric = raw_metric
                self.add_metric(metric)
            metric.set_val(raw_metric.get_val())
            metric.set_group('DOCKER')  # TODO Change to be more group specific

    def retrieve_metrics(self) -> [SimpleMetric]:
        containers = self.docker_client.containers.list()
        metrics = []
        pod_stats = {}
        for container in containers:
            curr_metrics = []
            attrs = container.attrs
            attributes = container.attrs.get('Config', {})
            stats = container.stats(stream=False)

            is_pod = attributes.get("Labels", {}).get("io.kubernetes.container.name") == "POD"
            
            if is_pod: continue
            container_id = attrs.get("Id")[:12]
            pod_uid = attributes.get("Labels", {}).get("io.kubernetes.pod.uid")
            pod_name = attributes.get("Labels", {}).get("io.kubernetes.pod.name")
            container_name = attributes.get("Labels", {}).get("io.kubernetes.container.name")
            pod_namespace = attributes.get("Labels", {}).get("io.kubernetes.pod.namespace")
            prefix = f"CONTAINER_{container_id}"
            if pod_uid:
                prefix = f"CONTAINER_{pod_namespace}|{pod_name}|{pod_uid}|{container_name}|{container_id}|"
            curr_metrics.append(self.get_cpu_ms(stats, prefix))
            curr_metrics.append(self.get_cpu_ptc(stats, prefix))
            curr_metrics.append(self.get_memory_usage(stats, prefix))
            curr_metrics.append(self.get_memory_usage_ptc(stats, prefix))

            all_net_metrics = {}

            for eth, net_stats in stats.get('networks', {}).items():
                for i in net_stats:
                    all_net_metrics[i] = all_net_metrics.get(i, 0) + net_stats[i]
                curr_metrics.extend(self.get_network_metrics(net_stats, eth, prefix, stats['read']))

            curr_metrics.extend(self.get_network_metrics(all_net_metrics, "overall_network", prefix, stats['read']))

            if pod_uid:
                pod_prefix = f"POD_{pod_namespace}|{pod_name}|{pod_uid}|"
                cpu_ms = self.get_cpu_ms(stats, pod_prefix)
                cpu_ptc = self.get_cpu_ptc(stats, pod_prefix)
                memory_usage = self.get_memory_usage(stats, pod_prefix)
                memory_usage_ptc = self.get_memory_usage_ptc(stats, pod_prefix)
                self.update_pod_stats(cpu_ms, pod_stats)
                self.update_pod_stats(cpu_ptc, pod_stats)
                self.update_pod_stats(memory_usage, pod_stats)
                self.update_pod_stats(memory_usage_ptc, pod_stats)
                network_usage = self.get_network_metrics(all_net_metrics, "overall_network", pod_prefix, stats['read'])
                for net in network_usage:
                    self.update_pod_stats(net, pod_stats)
            metrics.extend(curr_metrics)
        for _, metric in pod_stats.items():
            metrics.append(metric)
        return metrics

    def update_pod_stats(self, curr_metric, pod_stats):
        pod_curr_metric = pod_stats.get(curr_metric.get_name(),
                                   SimpleMetric(curr_metric.get_name(), curr_metric.get_units(), curr_metric.get_desc(),
                                                higherIsBetter=curr_metric.get_higherisbetter()))
        value = pod_curr_metric.get_val()
        pod_curr_metric.set_val(value + curr_metric.get_val() if value else curr_metric.get_val())
        pod_stats[curr_metric.get_name()] = pod_curr_metric

    def get_network_metrics(self, stats, net, prefix, timestamp):
        metrics = []
        for i in stats:
            usage = stats[i]
            simple_metric = SimpleMetric(
                f"{prefix}_{net}_{i}", i.split("_")[1], f"Network metric ({i}) of the container for {net} interface", minVal=0,
                                         higherIsBetter=False)

            simple_metric.set_val(usage)
            simple_metric.set_timestamp(timestamp)
            metrics.append(simple_metric)

        return metrics

    def get_memory_usage(self, stats, prefix=""):
        try:
            usage = stats['memory_stats']['usage']
        except Exception:
            usage = 0
        simple_metric = SimpleMetric(f"{prefix}_memory", "bytes", "Occupied memory of the container", minVal=0, higherIsBetter=False)

        simple_metric.set_val(usage)
        simple_metric.set_timestamp(stats['read'])
        return simple_metric

    def get_memory_usage_ptc(self, stats, prefix=""):
        try:
            usage = stats['memory_stats']['usage']
            limit = stats['memory_stats']['limit']
            percentage = usage/limit
            percent = round(percentage, 5)
        except Exception:
            percent = 0
        simple_metric = SimpleMetric(f"{prefix}_memory_ptc", "%", "Percentage memory of the container", minVal=0,
                                     higherIsBetter=False)
        simple_metric.set_val(percent)
        simple_metric.set_timestamp(stats['read'])
        return simple_metric

    def get_cpu_ms(self, stats, prefix=""):
        try:
            total_cpu_usage = stats['cpu_stats']['cpu_usage']['total_usage']
        except Exception:
            total_cpu_usage = 0
        simple_metric = SimpleMetric(f"{prefix}_cpu", "ms", "cpu runtime of the container", minVal=0,
                                     higherIsBetter=False)
        simple_metric.set_val(total_cpu_usage)
        simple_metric.set_timestamp(stats['read'])
        return simple_metric

    def get_cpu_ptc(self, stats, prefix=""):
        try:
            UsageDelta = stats['cpu_stats']['cpu_usage']['total_usage'] - stats['precpu_stats']['cpu_usage']['total_usage']
            SystemDelta = stats['cpu_stats']['system_cpu_usage'] - stats['precpu_stats']['system_cpu_usage']
            len_cpu = len(stats['cpu_stats']['cpu_usage']['percpu_usage'])
            percentage = (UsageDelta / SystemDelta) * len_cpu * 100
            percent = round(percentage, 2)
        except Exception:
            percent = 0
        simple_metric = SimpleMetric(f"{prefix}_cpu_ptc", "%", "cpu percent utilization of the container", minVal=0, higherIsBetter=False)
        simple_metric.set_val(percent)
        simple_metric.set_timestamp(stats['read'])
        return simple_metric

    def get_metrics(self):
        self.collect()
        return Probe.get_metrics(self)

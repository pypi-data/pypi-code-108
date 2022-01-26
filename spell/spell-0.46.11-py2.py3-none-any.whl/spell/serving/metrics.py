""" Utils for reporting custom metrics from a spell model server -> Prometheus"""
import base64
import re
from prometheus_client import Gauge

import prometheus_client as prometheus

from numbers import Number
from typing import Dict, Optional

__all__ = ["prometheus", "send_metric"]

# from https://prometheus.io/docs/concepts/data_model/#metric-names-and-labels
valid_prometheus_metric_name = re.compile(r"[a-zA-Z_:][a-zA-Z0-9_:]*")


def _generate_prometheus_metric_name(from_name: str) -> str:
    """Generate a valid prometheus metric name from a spell metric name
    (since the former cannot contain any of './-' or whitespace)"""
    if valid_prometheus_metric_name.fullmatch(from_name):
        metric_name = from_name
    else:  # base16-encode the from_name to force validity of resulting name
        metric_name = base64.b16encode(from_name.encode()).decode()
    return "spell:custom:{}".format(metric_name)


def make_send_metrics():
    """This is a closure that caches created Prometheus metrics."""
    metrics_cache: Dict[str, Gauge] = dict()

    def send_metric(name: str, value: Number, tag: Optional[str] = None):
        """Send a metric to the model server.

        Args:
            name: Name for metric rendered in Spell Web console; can be any valid unicode text
            value: Value of metric; should be numeric.
        Kwargs:
            tag: An extra tag rendered by the web UI, can be used to hold metadata such as prediction result
        """
        sanitized_tag = "" if tag is None else str(tag)
        metric = metrics_cache.get(name)
        if metric:
            metric.labels(spell_metric_name=name, spell_tag=sanitized_tag).set(value)
        else:
            metric_name = _generate_prometheus_metric_name(name)

            # the 'service' label is automatically filled to model-serving-<server-id>
            # by kube-prometheus, so no need to add additional info on model server here
            # The 'documentation' arg is filled in to 'name' because Prometheus' API
            # doesn't expose it well
            metric = Gauge(metric_name, name, ["spell_metric_name", "spell_tag"])
            metrics_cache[name] = metric

            # don't cache the labelled metric obj, since the 'tag' can change and
            # the .labels() method cannot be chained
            metric.labels(spell_metric_name=name, spell_tag=sanitized_tag).set(value)

    return send_metric


send_metric = make_send_metrics()

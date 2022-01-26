from abc import ABC, abstractmethod
from ctypes import c_char_p, c_double
from daltons_tensorflow.python.core.binding import lib

_daltons_model_metric_counter_add = lib.daltons_model_metric_counter_add
_daltons_model_metric_counter_add.argtypes = [c_char_p, c_char_p, c_char_p, c_double]

_daltons_model_metric_gauge_set = lib.daltons_model_metric_gauge_set
_daltons_model_metric_gauge_set.argtypes = [c_char_p, c_char_p, c_char_p, c_double]

_daltons_enable_metrics = lib.daltons_enable_metrics
_daltons_enable_metrics.argtypes = [c_char_p]

_daltons_disable_metrics = lib.daltons_disable_metrics

def enable_metrics(addr=":8080"):
    _daltons_enable_metrics(c_char_p(addr.encode('utf-8')))

def disable_metrics():
    _daltons_disable_metrics()

class Metric(ABC):
    def __init__(self, policy_id, model_id, metric_type):
        self._policy_id = c_char_p(policy_id.encode('utf-8'))
        self._model_id = c_char_p(model_id.encode('utf-8'))
        self._metric_type = c_char_p(metric_type.encode('utf-8'))

class Counter(Metric):
    def add(self, value):
        _daltons_model_metric_counter_add(
            self._policy_id, self._model_id, self._metric_type, value)

class Gauge(Metric):
    def set(self, value):
        _daltons_model_metric_gauge_set(
            self._policy_id, self._model_id, self._metric_type, value)

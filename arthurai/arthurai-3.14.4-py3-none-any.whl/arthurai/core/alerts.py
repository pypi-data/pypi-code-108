from dataclasses import dataclass
from typing import Union, Optional, Dict, Any

from arthurai.common.constants import ListableStrEnum
from arthurai.core.base import ArthurBaseJsonDataclass, NumberType


class AlertRuleBound(ListableStrEnum):
    Upper = "upper"
    Lower = "lower"


class AlertRuleSeverity(ListableStrEnum):
    Warning = "warning"
    Critical = "critical"


class AlertStatus(ListableStrEnum):
    Resolved = "resolved"
    Acknowledged = "acknowledged"


@dataclass
class AlertRule(ArthurBaseJsonDataclass):
    bound: AlertRuleBound
    threshold: NumberType
    metric_id: str
    severity: AlertRuleSeverity
    name: Optional[str] = None
    lookback_period: Optional[NumberType] = None
    subsequent_alert_wait_time: Optional[NumberType] = None
    enabled: bool = True
    id: Optional[str] = None
    metric_name: Optional[str] = None


@dataclass
class Alert(ArthurBaseJsonDataclass):
    id: str
    timestamp: str
    metric_value: float
    message: str
    model_id: str
    status: str
    alert_rule: AlertRule
    window_start: Optional[str] = None
    window_end: Optional[str] = None
    batch_id: Optional[str] = None


class MetricType(ListableStrEnum):
    ModelOutputMetric = "model_output_metric"
    ModelInputDataMetric = "model_input_data_metric"
    ModelPerformanceMetric = "model_performance_metric"
    ModelDataDriftMetric = "model_data_drift_metric"


@dataclass
class Metric(ArthurBaseJsonDataclass):
    id: str
    name: str
    query: Dict[str, Any]
    is_default: bool
    type: Optional[MetricType] = None
    attribute: Optional[str] = None

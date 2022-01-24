from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Tuple, Optional, TypeVar

from .metric import Metric


class WithMetricTrait(ABC):
    T = TypeVar("T", bound="WithMetricTrait")

    @abstractmethod
    def with_metric(self: T, key: str, value: float) -> T:
        """

        :param key:
        :param value:
        :return: iself
        """
        pass

    @abstractmethod
    def with_metrics(self: T, metrics: List[Tuple[str, float]]) -> T:
        """

        :param metrics:
        :return: iself
        """
        pass

    @abstractmethod
    def with_extended_metrics(self: T, metrics: List[Metric]) -> T:
        """

        :param metrics:
        :return: iself
        """
        pass


@dataclass
class WithMetrics(WithMetricTrait):
    metrics: Optional[List[Metric]] = None

    T = TypeVar("T", bound="WithMetrics")

    def with_metric(self: T, key: str, value: float) -> T:
        if key is not None and value is not None:
            if self.metrics is None:
                self.metrics = []
            self.metrics.append(Metric(key, value))
        return self

    def with_metrics(self: T, metrics: List[Tuple[str, float]]) -> T:
        if self.metrics is None:
            self.metrics = []
        for (key, value) in metrics:
            self.metrics.append(Metric(key, value))
        return self

    def with_extended_metrics(self: T, metrics: List[Metric]) -> T:
        if self.metrics is None:
            self.metrics = []
        if metrics is not None and len(metrics) > 0:
            self.metrics.extend(metrics)
        return self


class WithDelegatedMetrics(WithMetricTrait, ABC):
    T = TypeVar("T", bound="WithDelegatedMetrics")

    @abstractmethod
    def _get_delegate(self) -> WithMetricTrait:
        pass

    def with_metric(self: T, key: str, value: float) -> T:
        self._get_delegate().with_metric(key, value)
        return self

    def with_metrics(self: T, metrics: List[Tuple[str, float]]) -> T:
        self._get_delegate().with_metrics(metrics)
        return self

    def with_extended_metrics(self: T, metrics: List[Metric]) -> T:
        self._get_delegate().with_extended_metrics(metrics)
        return self

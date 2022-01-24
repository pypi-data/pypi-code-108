# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Base for all metrics."""
import logging
import numpy as np
import itertools
import collections

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, DefaultDict

from azureml.automl.core.shared import logging_utilities
from azureml.automl.core.shared.exceptions import DataErrorException


_logger = logging.getLogger(__name__)


class Metric(ABC):
    """Abstract class for all metrics."""

    def __init__(self) -> None:
        """Initialize the metric class."""
        self._data = {}  # type: Dict[Union[str, int], Any]

    @staticmethod
    @abstractmethod
    def aggregate(
        scores: List[Any]
    ) -> Any:
        """
        Fold several scores from a computed metric together.

        :param scores: List of computed scores.
        :return: Aggregated score.
        """
        ...

    @staticmethod
    def check_aggregate_scores(
        scores: List[Any],
        metric_name: str
    ) -> bool:
        """
        Check that a list of scores can be successfully aggregated.

        :param scores: Scores computed for a metric.
        :param metric_name: Name of metric being aggregated.
        :return: Whether the scores can be aggregated.
        """
        if scores is None:
            raise DataErrorException("Scores list passed for aggregation was None",
                                     reference_code="_metric_base.Metric.check_aggregate_scores",
                                     target="scores", has_pii=False)
        if len(scores) == 0:
            raise DataErrorException("At least one score is required to aggregate",
                                     reference_code="_metric_base.Metric.check_aggregate_scores",
                                     target="scores", has_pii=False)
        if np.nan in scores:
            _logger.error("Score aggregation failed with nan score for metric {}".format(metric_name))
            return False

        for score in scores:
            if isinstance(score, dict) and NonScalarMetric.is_error_metric(score):
                _logger.error("Score aggregation failed with error indicator for metric {}".format(metric_name))
                return False

        return True


class NonScalarMetric(Metric):
    """Abstract class for non-scalar metrics."""

    SCHEMA_TYPE = 'schema_type'
    SCHEMA_VERSION = 'schema_version'
    DATA = 'data'

    ERRORS = 'errors'

    """Abstract class for a metric which produces a nonscalar score."""
    @staticmethod
    def is_error_metric(score: Dict[str, Any]) -> bool:
        """
        Get whether the given score is an error metric.

        :param score: the score to test
        :return: True if the metric errored on computation, otherwise False
        """
        return NonScalarMetric.ERRORS in score

    @staticmethod
    def get_error_metric(message: Optional[str] = None) -> Dict[str, List[str]]:
        """
        Get a dictionary representation of a failed nonscalar metric.

        :param message: the error message that was thrown
        :return: dictionary with the error message
        """
        if message is None:
            message = "Unexpected error occurred while calculating metric"
        return {
            NonScalarMetric.ERRORS: [str(message)]
        }

    @staticmethod
    def _data_to_dict(schema_type, schema_version, data):
        return {
            NonScalarMetric.SCHEMA_TYPE: schema_type,
            NonScalarMetric.SCHEMA_VERSION: schema_version,
            NonScalarMetric.DATA: data
        }


class ScalarMetric(Metric):
    """Abstract class for a metric which produces a scalar score."""

    @staticmethod
    def aggregate(
        scores: List[Any]
    ) -> float:
        """
        Fold several scores from a computed metric together.

        :param scores: List of computed scores.
        :return: Aggregated score.
        """
        if np.isnan(scores).sum() == len(scores):
            _logger.error("Score aggregation failed with all nan scores")
            return float(np.nan)
        return float(np.nanmean(scores))


class ClassMetric(Metric):
    """Abstract class for a metric which produces a scalar score."""
    @staticmethod
    def aggregate(
        scores: List[Dict[str, float]]
    ) -> Dict[str, float]:
        """
        Fold several scores from a computed metric together.
        :param scores: List of computed scores.
        :return: Aggregated score.
        """
        agg_score = collections.defaultdict(float)  # type: DefaultDict[str, float]
        for class_name, metric_val in itertools.chain.from_iterable([score.items() for score in scores]):
            agg_score[class_name] += metric_val
        for class_name, metric_val in agg_score.items():
            agg_score[class_name] = metric_val / len(scores)
        agg_score_dict = dict(agg_score)
        return agg_score_dict

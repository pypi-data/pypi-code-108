# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Activity-based loggers."""
from typing import Any, Dict, Iterator, MutableMapping, Optional, Tuple
from abc import ABC, abstractmethod
import contextlib
import copy
import logging


def _merge_kwarg_extra(properties: Dict[str, Any],
                       **kwargs: Any) -> Tuple[MutableMapping[str, Any], Any]:
    """Update and return the kwargs['extra'] as extra and the kwargs that pops extra key."""
    if "extra" in kwargs:
        properties = copy.deepcopy(properties)
        extra = kwargs.pop("extra")
        if "properties" in extra:
            properties.update(extra['properties'])
        extra['properties'] = properties
    else:
        # no need to update properties if no extra
        extra = {'properties': properties}
    return extra, kwargs


class ActivityLogger(ABC):
    """Abstract base class for activity loggers."""

    @abstractmethod
    def _log_activity(self,
                      logger: logging.Logger,
                      activity_name: str,
                      activity_type: Optional[str] = None,
                      custom_dimensions: Optional[Dict[str, Any]] = None) -> Iterator[Optional[Any]]:
        """
        Log activity - should be overridden by subclasses with a proper implementation.

        :param logger:
        :param activity_name:
        :param activity_type:
        :param custom_dimensions:
        :return:
        """
        raise NotImplementedError

    @contextlib.contextmanager
    def log_activity(self,
                     logger: logging.Logger,
                     activity_name: str,
                     activity_type: Optional[str] = None,
                     custom_dimensions: Optional[Dict[str, Any]] = None) -> Iterator[Optional[Any]]:
        """
        Log an activity using the given logger.

        :param logger:
        :param activity_name:
        :param activity_type:
        :param custom_dimensions:
        :return:
        """
        return self._log_activity(logger, activity_name, activity_type, custom_dimensions)

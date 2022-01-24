# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Class to hold sampler configuration."""
from typing import Any, Dict, Optional

import logging

from azureml._common._error_definition import AzureMLError
from azureml._common._error_definition.user_error import ArgumentBlankOrEmpty
from azureml.automl.core.shared.exceptions import ConfigException
from azureml.automl.core.shared.reference_codes import ReferenceCodes


logger = logging.getLogger(__name__)


class SamplerConfig:
    """Class to hold sampler configuration."""

    def __init__(self, _id: str,
                 sampler_args: Any = None,
                 sampler_kwargs: Any = None) -> None:
        """
        Initialize all attributes.

        :param _id: Id of the sampler.
        :param sampler_args: Arguments to be send to the sampler.
        :param sampler_kwargs: Keyword arguments to be send to the sampler.
        """
        self._id = _id
        self._args = sampler_args or []
        self._kwargs = sampler_kwargs or {}

    @classmethod
    def from_dict(cls, dct: Dict[str, Any]) -> "SamplerConfig":
        """
        Load from dictionary.

        :param cls: Class object of :class:`azureml.automl.core.configuration.sampler_config.SamplerConfig`
        :param dct: Dictionary holding all the needed params.
        :return: Created object.
        """
        if 'id' in dct:
            obj = SamplerConfig(dct['id'], sampler_args=dct.get('args', []), sampler_kwargs=dct.get('kwargs', {}))
        else:
            raise ConfigException._with_error(
                AzureMLError.create(ArgumentBlankOrEmpty, target="id", argument_name='id',
                                    reference_code=ReferenceCodes._SAMPLER_CONFIG_FROM_DICT)
            )
        return obj

    @property
    def id(self) -> str:
        """
        Get the id of the object.

        :return: The id.
        """
        return self._id.lower()

    @property
    def sampler_args(self) -> Any:
        """
        Get the sampler args to be sent to the instance of the sampler.

        :return: The args.
        """
        return self._args

    @property
    def sampler_kwargs(self) -> Any:
        """
        Get the sampler kwargs to be sent to the instance of the sampler.

        :return: The key word arguments.
        """
        return self._kwargs

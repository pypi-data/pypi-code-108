# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Base model factory class to be used by object detection and classification"""

from typing import Any, Dict, Optional

from azureml.automl.dnn.vision.common.exceptions import AutoMLVisionValidationException
from azureml.automl.dnn.vision.common.pretrained_model_utilities import PretrainedModelFactory


class BaseModelFactory:
    """Base class defining interface to be used by object detection and classification model factories"""

    def __init__(self) -> None:
        """Init method."""
        self._models_dict: Dict[str, Any] = {}
        self._pre_trained_model_names_dict: Dict[str, Any] = {}
        self._default_model: Optional[str] = None

    def download_model_weights(self, model_name: Optional[str] = None) -> str:
        """ Download model weights to a predefined location for a model.
        These weights will be later used to setup model wrapper.

        :param model_name: string name of the model if specified or None if not specified
        :type model_name: str or NoneType
        :return: model_name: String name of the chosen model
        :rtype: model_name: str
        """
        if model_name is None:
            model_name = self._default_model

        if model_name not in self._pre_trained_model_names_dict:
            raise AutoMLVisionValidationException('The provided model_name is not supported.',
                                                  has_pii=False)

        PretrainedModelFactory.download_pretrained_model_weights(
            self._pre_trained_model_names_dict[model_name], progress=True)
        return model_name

    def model_supported(self, model_name: str) -> bool:
        """ Check if model is supported by the ModelFactory.

        :param model_name: string name of the model
        :type model_name: str
        :return: True if model is supported, None otherwise
        :rtype: bool
        """
        return model_name in self._models_dict

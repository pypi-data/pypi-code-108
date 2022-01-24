# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Hold sweeper configuration."""
from typing import Any, cast, Dict, List, Optional, Union
import logging
import json
import os

from azureml._common._error_definition import AzureMLError
from azureml._common._error_definition.user_error import NotFound
from azureml.automl.core.shared import activity_logger, logging_utilities
from azureml.automl.core.shared.exceptions import ConfigException
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from .._downloader import Downloader


logger = logging.getLogger(__name__)


class SweeperConfig:
    """Holder for sweeper configurations."""

    CONFIG_DOWNLOAD_PREFIX = "https://aka.ms/automl-resources/configs/"
    CONFIG_DOWNLOAD_FILE = "config_v1.3.json"

    DEFAULT_CONFIG_PATH = "../../sweeping/config.json"

    def __init__(self) -> None:
        """
        Dummy initializer for feature sweeping configuration object.

        No arguments are meant to be passed in directly. The below class methods are the intended
        functions for creating usable SweeperConfig objects.

        :param _enabled: Boolean flag for whether this particular sweeping experiment is enabled.
        :param _name: Name of this sweeping experiment, e.g. "PreTrainedDNNEmbeddings".
        :param _type: The type of Sweeper to use for this experiment, as needed by Sweepers.get method.
        :param _experiment_result_override: Whether to override the experiment result to be a win, such
        as if force_text_dnn is specified by the user and we're testing BERT.
        :param _sampler: Property dict specifying which Sampler to use for this experiment, as needed
        by SamplerConfig.from_dict method.
        :param _estimator: Which estimator to use for this experiment, e.g. "logistic_regression".
        :param _scorer: The metric to use during the experiment, which is used alongside the task type to
        instantiate the Scorer object.
        :param _baseline: Dict specifying the baseline featurizers for this experiment.
        :param _experiment: Dict specifying the experimental featurizers for this experiment.
        :param _column_purposes: List of col purposes for which this experiment applies and other related settings.
        :param _epsilon: The minimum lift the experimental featurizer must provide in order to be chosen over
        the baseline, subject to scaling based on sample size.
        :param _scale_epsilon: Whether or not to scale epsilon inversely with sample size for this experiment.
        """
        self._enabled = False
        self._name = ''
        self._type = ''
        self._experiment_result_override = None  # type: Optional[bool]
        self._sampler = {}  # type: Dict[str, Any]
        self._estimator = ''
        self._scorer = ''
        self._baseline = {}     # type: Dict[str, Any]
        self._experiment = {}   # type: Dict[str, Any]
        self._column_purposes = []  # type: List[Dict[str, Any]]
        self._epsilon = 0.0
        self._scale_epsilon = True

    @classmethod
    def from_dict(cls, dct: Dict[str, Any]) -> "SweeperConfig":
        """
        Load from dictionary.

        :param cls: Class object of :class:`azureml.automl.core.configuration.sweeper_config.SweeperConfig`
        :param dct: The dictionary containing all the needed params.
        :return: Created sweeper configuration.
        """
        obj = SweeperConfig()
        obj._name = dct.get('name', '')
        obj._experiment_result_override = dct.get('experiment_result_override', None)
        obj._enabled = dct.get('enabled', False)
        obj._type = dct.get('type', '')
        obj._sampler = dct.get('sampler', {})
        obj._estimator = dct.get('estimator', '')
        obj._scorer = dct.get('scorer', '')
        obj._baseline = cast(Dict[str, Any], dct.get('baseline'))
        obj._experiment = cast(Dict[str, Any], dct.get('experiment'))
        obj._column_purposes = dct.get('column_purposes', [])
        obj._epsilon = dct.get('epsilon', 0.0)
        obj._scale_epsilon = dct.get('scale_epsilon', True)
        return obj

    @classmethod
    def _validate(cls, config: "SweeperConfig") -> None:
        """Validate the configuration."""
        assert config._type is not None
        assert config._sampler is not None
        assert config._estimator is not None
        assert config._baseline is not None
        assert config._experiment is not None
        assert config._column_purposes is not None
        assert len(config._column_purposes) > 0, "At least one column purpose should be specified"
        assert config._scorer is not None

    def get_config(self) -> Dict[str, Any]:
        """Provide configuration."""
        try:
            file_path = Downloader.download(self.CONFIG_DOWNLOAD_PREFIX, self.CONFIG_DOWNLOAD_FILE, os.getcwd())
            if file_path is None:
                raise ConfigException._with_error(
                    AzureMLError.create(NotFound, target="configuration_url", resource_name=file_path)
                )

            with open(file_path, 'r') as f:
                cfg = json.load(f)  # type: Dict[str, Any]
                return cfg
        except Exception as e:
            logging_utilities.log_traceback(e, logger, is_critical=False)
            logger.debug("Exception when trying to load config from the remote.")
            return self.default()

    @classmethod
    def default(cls) -> Dict[str, Any]:
        """Return the default back up configuration."""
        default_config_path = os.path.abspath(os.path.join(__file__, cls.DEFAULT_CONFIG_PATH))
        with open(default_config_path, "r") as f:
            result = json.loads(f.read())  # type: Dict[str, Any]
            return result

    @classmethod
    def set_default(cls, overide_config_path: str) -> None:
        """
        Override configuration path.

        :param cls: Class object of :class:`azureml.automl.core.configuration.sweeper_config.SweeperConfig`
        :param overide_config_path: Overriden config path.
        """
        cls.DEFAULT_CONFIG_PATH = overide_config_path

    def __getstate__(self):
        """
        Get state picklable objects.

        :return: state
        """
        state = dict(self.__dict__)
        return state

    def __setstate__(self, state):
        """
        Set state for object reconstruction.

        :param state: pickle state
        """
        self.__dict__.update(state)

    def __json__(self) -> Dict[str, Any]:
        """JSON representation of the class."""
        return {
            "type": self._type,
            "sampler": self._sampler,
            "estimator": self._estimator,
            "scorer": self._scorer,
            "baseline": self._baseline,
            "experiment": self._experiment,
            "column_purposes": self._column_purposes,
            "epsilon": self._epsilon
        }

    def __str__(self) -> str:
        """Human readable representation of this object."""
        return json.dumps(self.__json__())

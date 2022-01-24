# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Contains functionality for automated ML feature engineering in Azure Machine Learning."""
import json
import logging
from typing import Any, Dict, List, Optional, Union, SupportsFloat, cast

from azureml._common._error_definition import AzureMLError
from azureml.automl.core.constants import (SupportedTransformers as _SupportedTransformers,
                                           SupportedTransformersInternal,
                                           FeatureType as _FeatureType,
                                           TransformerParams as _TransformerParams,
                                           PredictionTransformTypes as _PredictionTransformTypes,
                                           TextDNNLanguages)
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    ConflictingFeaturizationConfigDroppedColumns, FeaturizationConfigEmptyFillValue,
    InvalidArgumentWithSupportedValues, FeaturizationConfigInvalidFillValue)
from azureml.automl.core.shared.constants import TimeSeriesInternal
from azureml.automl.core.shared.exceptions import ConfigException
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.core.shared.types import ColumnTransformerParamType
from azureml.automl.core import _codegen_utilities as codegen_utilities


class FeaturizationConfig:
    """
    Defines feature engineering configuration for automated machine learning experiments in Azure Machine Learning.

    Use the FeaturizationConfig class in the ``featurization`` parameter of the
    :class:`azureml.train.automl.automlconfig.AutoMLConfig` class. For more information,
    see `Configure automated ML experiments
    <https://docs.microsoft.com/azure/machine-learning/how-to-configure-auto-train>`_.

    .. remarks::

        Featurization customization has methods that allow you to:

        * Add or remove column purpose. With the  ``add_column_purpose`` and ``remove_column_purpose`` methods
          you can override the feature type for specified columns, for example, when the feature type of column does
          not correctly reflect its purpose. The add method supports adding all the feature types given in the
          FULL_SET attribute of the  :class:`azureml.automl.core.constants.FeatureType` class.

        * Add or remove transformer parameters. With the ``add_transformer_params`` and
          ``remove_transformer_params`` methods you can change the parameters of customizable transformers like
          Imputer, HashOneHotEncoder, and TfIdf. Customizable transformers are listed in
          the :class:`azureml.automl.core.constants.SupportedTransformers` class CUSTOMIZABLE_TRANSFORMERS
          attribute. Use the ``get_transformer_params`` to lookup customization parameters.

        * Block transformers. Block transformers to be used for the featurization process with the
          ``add_blocked_transformers`` method. The transformers must be one of the transformers listed in the
          :class:`azureml.automl.core.constants.SupportedTransformers` class BLOCKED_TRANSFORMERS attribute.

        * Add a drop column to ignore for featurization and training with the ``add_drop_columns`` method.
          For example, you can drop a column that doesn't contain useful information.

        * Add or remove prediction transform type. With ``add_prediction_transform_type`` and
        ``remove_prediction_transform_type`` methods you can override the existing target column type.
          Prediction transform types are listed in the :class:`azureml.automl.core.constants.PredictionTransformTypes`
          attribute.

        The following code example shows how to customize featurization in automated ML for forecasting.
        In the example code, dropping a column and adding transform parameters are shown.

        .. code-block:: python

            featurization_config = FeaturizationConfig()
            # Force the CPWVOL5 feature to be numeric type.
            featurization_config.add_column_purpose("CPWVOL5", "Numeric")
            # Fill missing values in the target column, Quantity, with zeros.
            featurization_config.add_transformer_params(
                "Imputer", ["Quantity"], {"strategy": "constant", "fill_value": 0}
            )
            # Fill missing values in the INCOME column with median value.
            featurization_config.add_transformer_params(
                "Imputer", ["INCOME"], {"strategy": "median"}
            )
            # Fill missing values in the Price column with forward fill (last value carried forward).
            featurization_config.add_transformer_params("Imputer", ["Price"], {"strategy": "ffill"})

        Full sample is available from
        https://github.com/Azure/MachineLearningNotebooks/blob/master/how-to-use-azureml/automated-machine-learning/forecasting-orange-juice-sales/auto-ml-forecasting-orange-juice-sales.ipynb


        The next example shows customizing featurization in a regression problem using the Hardware Performance
        Dataset. In the example code, a blocked transformer is defined, column purposes are added, and transformer
        parameters are added.

        .. code-block:: python

            featurization_config = FeaturizationConfig()
            featurization_config.blocked_transformers = ['LabelEncoder']
            #featurization_config.drop_columns = ['MMIN']
            featurization_config.add_column_purpose('MYCT', 'Numeric')
            featurization_config.add_column_purpose('VendorName', 'CategoricalHash')
            #default strategy mean, add transformer param for for 3 columns
            featurization_config.add_transformer_params('Imputer', ['CACH'], {"strategy": "median"})
            featurization_config.add_transformer_params('Imputer', ['CHMIN'], {"strategy": "median"})
            featurization_config.add_transformer_params('Imputer', ['PRP'], {"strategy": "most_frequent"})
            #featurization_config.add_transformer_params('HashOneHotEncoder', [], {"number_of_bits": 3})

        Full sample is available from
        https://github.com/Azure/MachineLearningNotebooks/blob/master/how-to-use-azureml/automated-machine-learning/regression-explanation-featurization/auto-ml-regression-explanation-featurization.ipynb


        The FeaturizationConfig defined in the code example above can then used in the configuration of an
        automated ML experiment as shown in the next code example.

        .. code-block:: python

            automl_settings = {
                "enable_early_stopping": True,
                "experiment_timeout_hours" : 0.25,
                "max_concurrent_iterations": 4,
                "max_cores_per_iteration": -1,
                "n_cross_validations": 5,
                "primary_metric": 'normalized_root_mean_squared_error',
                "verbosity": logging.INFO
            }

            automl_config = AutoMLConfig(task = 'regression',
                                         debug_log = 'automl_errors.log',
                                         compute_target=compute_target,
                                         featurization=featurization_config,
                                         training_data = train_data,
                                         label_column_name = label,
                                         **automl_settings
                                        )

        Full sample is available from
        https://github.com/Azure/MachineLearningNotebooks/blob/master/how-to-use-azureml/automated-machine-learning/regression-explanation-featurization/auto-ml-regression-explanation-featurization.ipynb


    :param blocked_transformers:
        A list of transformer names to be blocked during featurization.
    :type blocked_transformers: list(str)
    :param column_purposes:
        A dictionary of column names and feature types used to update column purpose.
    :type column_purposes: dict
    :param transformer_params:
        A dictionary of transformer and corresponding customization parameters.
    :type transformer_params: dict
    :param drop_columns:
        A list of columns to be ignored in the featurization process. This setting is being deprecated.
        Please drop columns from your datasets as part of your data preparation process before providing the datasets
        to AutoML.
    :type drop_columns: list(str)
    :param prediction_transform_type:
        A str of target transform type to be used to cast target column type.
    :type prediction_transform_type: str
    """

    def __init__(
            self,
            blocked_transformers: Optional[List[str]] = None,
            column_purposes: Optional[Dict[str, str]] = None,
            transformer_params: Optional[Dict[str, List[ColumnTransformerParamType]]] = None,
            drop_columns: Optional[List[str]] = None,
            dataset_language: Optional[str] = None,
            prediction_transform_type: Optional[str] = None) -> None:
        """
        Create a FeaturizationConfig.

        :param blocked_transformers:
            A list of transformer names to be blocked during featurization.
        :type blocked_transformers: list(str)
        :param column_purposes:
            A dictionary of column names and feature types used to update column purpose.
        :type column_purposes: dict
        :param transformer_params:
            A dictionary of transformer and corresponding customization parameters.
        :type transformer_params: dict
        :param drop_columns:
            A list of columns to be ignored in the featurization process. This setting is being deprecated.
            Please drop columns from your datasets as part of your data preparation process before providing the
            datasets to AutoML.
        :type drop_columns: list(str)
        :param dataset_language: Three character ISO 639-3 code for the language(s) contained in the dataset.
            Languages other than English are only supported if you use GPU-enabled compute.  The langugage_code
            'mul' should be used if the dataset contains multiple languages. To find ISO 639-3 codes for different
            languages, please refer to https://en.wikipedia.org/wiki/List_of_ISO_639-3_codes.
        :type dataset_language: str
        :param prediction_transform_type:
            A str of target transform type to be used to cast target column type.
        :type prediction_transform_type: str
        """
        self._blocked_transformers = blocked_transformers
        self._column_purposes = column_purposes
        self._transformer_params = transformer_params
        self._dataset_language = dataset_language
        self._drop_columns = drop_columns
        self._prediction_transform_type = prediction_transform_type

        # Deprecation of drop_columns
        if drop_columns is not None:
            logging.warning(
                "Parameter 'drop_columns' in class FeaturizationConfig will be deprecated. Please drop "
                "columns from your datasets as part of your data preparation process before providing the datasets "
                "to AutoML.")

        self._validate_featurization_config_input()

    def __setstate__(self, state):
        if "_prediction_transform_type" not in state:
            state["_prediction_transform_type"] = None
        self.__dict__.update(state)

    def __repr__(self) -> str:
        params = {
            "blocked_transformers": self._blocked_transformers,
            "column_purposes": self._column_purposes,
            "transformer_params": self._transformer_params,
            "dataset_language": self._dataset_language,
            "drop_columns": self._drop_columns,
            "prediction_transform_type": self._prediction_transform_type
        }

        return codegen_utilities.generate_repr_str(self.__class__, params)

    def add_column_purpose(self, column_name: str, feature_type: str) -> None:
        """
        Add a feature type for the specified column.

        :param column_name: A column name to update.
        :type column_name: str
        :param feature_type: A feature type to use for the column. Feature types must be one given in the FULL_SET
          attribute of the  :class:`azureml.automl.core.constants.FeatureType` class.
        :type feature_type: azureml.automl.core.constants.FeatureType
        """
        self._validate_feature_type(feature_type=feature_type)

        if self._column_purposes is None:
            self._column_purposes = {column_name: feature_type}
        else:
            self._column_purposes[column_name] = feature_type
        self._validate_column_purpose_column_names()

    def remove_column_purpose(self, column_name: str) -> None:
        """
        Remove the feature type for the specified column.

        If no feature is specified for a column, the detected default feature is used.

        :param column_name: The column name to update.
        :type column_name: str
        """
        if self._column_purposes is not None:
            self._column_purposes.pop(column_name, None)

    def add_blocked_transformers(self, transformers: Union[str, List[str]]) -> None:
        """
        Add transformers to be blocked.

        :param transformers: A transformer name or list of transformer names. Transformer names must be one of the
          transformers listed in the BLOCKED_TRANSFORMERS attribute of the
          :class:`azureml.automl.core.constants.SupportedTransformers` class.
        :type transformers: str or list[str]
        """
        # validation
        self._validate_blocked_transformer_names(transformers)
        self._blocked_transformers = self._append_to_list(transformers, self._blocked_transformers)

    def add_drop_columns(self, drop_columns: Union[str, List[str]]) -> None:
        """
        Add column name or list of column names to ignore.

        :param drop_columns: A column name or list of column names.
        :type drop_columns: str or list[str]
        """
        logging.warning(
            "Parameter 'drop_columns' in class FeaturizationConfig will be deprecated. Please drop "
            "columns from your datasets as part of your data preparation process before providing the datasets "
            "to AutoML.")
        self._drop_columns = self._append_to_list(drop_columns, self._drop_columns)
        self._validate_column_purpose_column_names()
        self._validate_transformer_column_names()

    def add_transformer_params(self, transformer: str, cols: List[str], params: Dict[str, Any]) -> None:
        """
        Add customized transformer parameters to the list of custom transformer parameters.

        Apply to all columns if column list is empty.

        .. remarks::

            The following code example shows how to customize featurization in automated ML for forecasting.
            In the example code, dropping a column and adding transform parameters are shown.

            .. code-block:: python

                featurization_config = FeaturizationConfig()
                # Force the CPWVOL5 feature to be numeric type.
                featurization_config.add_column_purpose("CPWVOL5", "Numeric")
                # Fill missing values in the target column, Quantity, with zeros.
                featurization_config.add_transformer_params(
                    "Imputer", ["Quantity"], {"strategy": "constant", "fill_value": 0}
                )
                # Fill missing values in the INCOME column with median value.
                featurization_config.add_transformer_params(
                    "Imputer", ["INCOME"], {"strategy": "median"}
                )
                # Fill missing values in the Price column with forward fill (last value carried forward).
                featurization_config.add_transformer_params("Imputer", ["Price"], {"strategy": "ffill"})

            Full sample is available from
            https://github.com/Azure/MachineLearningNotebooks/blob/master/how-to-use-azureml/automated-machine-learning/forecasting-orange-juice-sales/auto-ml-forecasting-orange-juice-sales.ipynb


        :param transformer: The transformer name. The transformer name must be one of the CUSTOMIZABLE_TRANSFORMERS
            listed in the :class:`azureml.automl.core.constants.SupportedTransformers` class.
        :type transformer: str
        :param cols: Input columns for specified transformer.
            Some transformers can take multiple columns as input specified as a list.
        :type cols: list(str)
        :param params: A dictionary of keywords and arguments.
        :type params: dict
        """
        self._validate_customizable_transformers(transformer=transformer, params=params)

        if self._transformer_params is None:
            self._transformer_params = {transformer: [(cols, params)]}
        else:
            self.remove_transformer_params(transformer, cols)
            if transformer in self._transformer_params:
                self._transformer_params[transformer].append((cols, params))
            else:
                self._transformer_params[transformer] = [(cols, params)]
        self._validate_transformer_column_names()

    def get_transformer_params(self, transformer: str, cols: List[str]) -> Dict[str, Any]:
        """
        Retrieve transformer customization parameters for columns.

        :param transformer: The transformer name. The transformer name must be one of the CUSTOMIZABLE_TRANSFORMERS
            listed in the :class:`azureml.automl.core.constants.SupportedTransformers` class.
        :type transformer: str
        :param cols: The columns names to get information for. Use an empty list to specify all columns.
        :type cols: list[str]
        :return: Transformer parameter settings.
        :rtype: dict
        """
        if self._transformer_params is not None and transformer in self._transformer_params:

            separator = '#'
            column_transformer_params = list(
                filter(lambda item: separator.join(item[0]) == separator.join(cols),
                       self._transformer_params[transformer]))
            if len(column_transformer_params) == 1:
                return column_transformer_params[0][1]
        return {}

    def remove_transformer_params(
            self,
            transformer: str,
            cols: Optional[List[str]] = None
    ) -> None:
        """
        Remove transformer customization parameters for specific column or all columns.

        :param transformer: The transformer name. The transformer name must be one of the CUSTOMIZABLE_TRANSFORMERS
            listed in the :class:`azureml.automl.core.constants.SupportedTransformers` class.
        :type transformer: str
        :param cols: The columns names to remove customization parameters from. Specify None (the default)
            to remove all customization params for the specified transformer.
        :type cols: list[str] or None
        """
        self._validate_transformer_names(transformer)

        if self._transformer_params is not None and transformer in self._transformer_params:
            if cols is None:
                self._transformer_params.pop(transformer, None)
            else:
                # columns = cols  # type: List[str]
                separator = '#'
                column_transformer_params = [item for item in self._transformer_params[transformer]
                                             if separator.join(item[0]) != separator.join(cols)]
                if len(column_transformer_params) == 0:
                    self._transformer_params.pop(transformer, None)
                else:
                    self._transformer_params[transformer] = column_transformer_params

    def add_prediction_transform_type(self, prediction_transform_type: str) -> None:
        """
        Add a prediction transform type for target column.

        :param prediction_transform_type: A prediction transform type to be used for casting target column.
            Feature types must be one given in the FULL_SET attribute of the
        :class:`azureml.automl.core.constants.PredictionTransformTypes` class.
        :type prediction_transform_type: str
        """
        self._validate_prediction_transform_type(prediction_transform_type=prediction_transform_type)
        self._prediction_transform_type = prediction_transform_type

    def remove_prediction_transform_type(self) -> None:
        """
        Revert the prediction transform type to default for target column.
        """
        if self._prediction_transform_type is not None:
            self._prediction_transform_type = None

    def _validate_featurization_config_input(self):
        if self._blocked_transformers is not None:
            self._validate_transformer_names(self._blocked_transformers)
        if self._column_purposes is not None:
            for feature_type in self._column_purposes.values():
                self._validate_feature_type(feature_type)
        self._validate_column_purpose_column_names()
        if self._transformer_params is not None:
            for transformer_name, column_transformer_params in self._transformer_params.items():
                for col, params in column_transformer_params:
                    self._validate_customizable_transformers(transformer=transformer_name, params=params)
        self._validate_transformer_column_names()
        if self._dataset_language is not None:
            self._validate_dataset_language(self._dataset_language)
        if self._prediction_transform_type is not None:
            self._validate_prediction_transform_type(self._prediction_transform_type)

    def _validate_transformer_names(self, transformer: Union[str, List[str]]) -> None:
        if isinstance(transformer, str):
            self._validate_transformer_fullset(transformer)
        else:
            for t in transformer:
                self._validate_transformer_fullset(t)

    def _validate_blocked_transformer_names(self, transformer: Union[str, List[str]]) -> None:
        if isinstance(transformer, str):
            self._validate_transformer_fullset(transformer)
            self._validate_transformer_blockedlist(transformer)
        else:
            for t in transformer:
                self._validate_transformer_fullset(t)
                self._validate_transformer_blockedlist(t)

    def _validate_transformer_column_names(self) -> None:
        if self.drop_columns is None or self.transformer_params is None:
            return None
        column_list = []
        for column_transformer_params in self.transformer_params.values():
            for cols, _ in column_transformer_params:
                column_list.extend([col for col in cols])
        self._validate_columns_list_in_drop_columns(
            column_list, "transformer_params", "featurization_config.transformer_params",
            ReferenceCodes._FEATURIZATION_CONFIG_IMPUTE_COLUMN_DROPPED)

    def _validate_column_purpose_column_names(self) -> None:
        if self.drop_columns is None or self.column_purposes is None:
            return None
        column_list = [col for col in self.column_purposes.keys()]
        self._validate_columns_list_in_drop_columns(
            column_list, "column_purposes", "featurization_config.column_purposes",
            ReferenceCodes._FEATURIZATION_CONFIG_COLUNN_PURPOSE_DROPPED)

    def _validate_columns_list_in_drop_columns(
            self,
            columns_list: List[str],
            config_name: str,
            target_name: str,
            reference_code: str
    ) -> None:
        dropped_columns = [col for col in columns_list if col in self.drop_columns]
        if len(dropped_columns) > 0:
            raise ConfigException._with_error(
                AzureMLError.create(
                    ConflictingFeaturizationConfigDroppedColumns, target=target_name, sub_config_name=config_name,
                    dropped_columns=",".join(dropped_columns), reference_code=reference_code
                )
            )

    @staticmethod
    def _append_to_list(items: Union[str, List[str]], origin_list: Optional[List[str]]) -> List[str]:
        extend_list = [items] if isinstance(items, str) else items
        new_list = [] if origin_list is None else origin_list
        new_list.extend(extend_list)
        return new_list

    @staticmethod
    def _validate_feature_type(feature_type: str) -> None:
        if feature_type not in _FeatureType.FULL_SET:
            raise ConfigException._with_error(
                AzureMLError.create(
                    InvalidArgumentWithSupportedValues, target="feature_type",
                    arguments=feature_type, supported_values=", ".join(_FeatureType.FULL_SET)
                )
            )

    @staticmethod
    def _validate_dataset_language(dataset_language: str) -> None:
        if dataset_language not in TextDNNLanguages.supported:
            raise ConfigException._with_error(
                AzureMLError.create(
                    InvalidArgumentWithSupportedValues, target="dataset_language",
                    arguments=dataset_language, supported_values=", ".join(TextDNNLanguages.supported)
                )
            )

    @staticmethod
    def _validate_prediction_transform_type(prediction_transform_type: str) -> None:
        # Validate whether prediction transform type is supported for target column
        if prediction_transform_type not in _PredictionTransformTypes.FULL_SET:
            raise ConfigException._with_error(
                AzureMLError.create(
                    InvalidArgumentWithSupportedValues, target="prediction_transform_type",
                    arguments=prediction_transform_type, supported_values=", ".join(_PredictionTransformTypes.FULL_SET)
                )
            )

    @staticmethod
    def _validate_customizable_transformers(transformer: str, params: Dict[str, Any]) -> None:
        # Validate whether transformer is supported for customization
        # while allowing some internal transformers to be customizable as well (time index featurizers)
        if transformer not in _SupportedTransformers.CUSTOMIZABLE_TRANSFORMERS.union(
            {SupportedTransformersInternal.TimeIndexFeaturizer}
        ):
            raise ConfigException._with_error(
                AzureMLError.create(
                    InvalidArgumentWithSupportedValues, target="transformer", arguments=transformer,
                    supported_values=", ".join(_SupportedTransformers.CUSTOMIZABLE_TRANSFORMERS),
                    reference_code=ReferenceCodes._FEATURIZATION_CONFIG_VALIDATE_CUSTOMIZABLE
                )
            )
        if transformer == _SupportedTransformers.Imputer:
            strategy = params.get(_TransformerParams.Imputer.Strategy)
            if strategy == _TransformerParams.Imputer.Constant:
                if params.get(_TransformerParams.Imputer.FillValue) is None:
                    raise ConfigException._with_error(
                        AzureMLError.create(
                            FeaturizationConfigEmptyFillValue, target=_TransformerParams.Imputer.FillValue,
                            argument_name=_TransformerParams.Imputer.FillValue,
                            reference_code=ReferenceCodes._FEATURIZATION_CONFIG_MISSING_IMPUTE_VALUE
                        )
                    )
                # We need to make sure user did not set FillValue to nan or inf,
                # but we can not import numpy here as it is not a dependency.
                # 1. We are converting FillValue to float if we can;
                # 2. If FillValue is float, we are checking if multiplication by 0
                # will give 0. In the opposite case it will result in inf or nan.
                constant_as_numeric = None  # type: Optional[float]
                try:
                    # We are using cast to avoid mypy errors, because we are in try-except.
                    constant_as_numeric = float(
                        cast(SupportsFloat, params.get(_TransformerParams.Imputer.FillValue)))
                except BaseException:
                    pass
                if constant_as_numeric is not None and 0 * constant_as_numeric != 0:
                    raise ConfigException._with_error(
                        AzureMLError.create(
                            FeaturizationConfigInvalidFillValue, target=_TransformerParams.Imputer.FillValue,
                            reference_code=ReferenceCodes._FEATURIZATION_CONFIG_WRONG_IMPUTE_VALUE
                        )
                    )

    @staticmethod
    def _validate_transformer_fullset(transformer: str) -> None:
        if transformer not in _SupportedTransformers.FULL_SET:
            raise ConfigException._with_error(
                AzureMLError.create(
                    InvalidArgumentWithSupportedValues, target="transformer", arguments=transformer,
                    supported_values=", ".join(_SupportedTransformers.FULL_SET),
                    reference_code=ReferenceCodes._FEATURIZATION_CONFIG_VALIDATE_FULLSET
                )
            )

    @staticmethod
    def _validate_transformer_blockedlist(transformer: str) -> None:
        if transformer not in _SupportedTransformers.BLOCK_TRANSFORMERS:
            raise ConfigException._with_error(
                AzureMLError.create(
                    InvalidArgumentWithSupportedValues, target="transformer", arguments=transformer,
                    supported_values=", ".join(_SupportedTransformers.BLOCK_TRANSFORMERS),
                    reference_code=ReferenceCodes._FEATURIZATION_CONFIG_VALIDATE_BLOCKEDLIST
                )
            )

    @staticmethod
    def _is_featurization_dict_empty(featurization_dict: Dict[str, Any]) -> bool:
        if len(featurization_dict) == 0:
            return True
        for _, value in featurization_dict.items():
            if value is not None and len(value) > 0:
                return False
        return True

    @property
    def dataset_language(self):
        return self._dataset_language

    @dataset_language.setter
    def dataset_language(self, dataset_language: str) -> None:
        self._validate_dataset_language(dataset_language)
        self._dataset_language = dataset_language

    @property
    def prediction_transform_type(self):
        return self._prediction_transform_type

    @prediction_transform_type.setter
    def prediction_transform_type(self, prediction_transform_type: str) -> None:
        self._validate_prediction_transform_type(prediction_transform_type)
        self._prediction_transform_type = prediction_transform_type

    @property
    def blocked_transformers(self):
        return self._blocked_transformers

    @blocked_transformers.setter
    def blocked_transformers(self, blocked_transformers: List[str]) -> None:
        if blocked_transformers is not None:
            self._validate_blocked_transformer_names(blocked_transformers)
        self._blocked_transformers = blocked_transformers

    @property
    def column_purposes(self):
        return self._column_purposes

    @column_purposes.setter
    def column_purposes(self, column_purposes: Dict[str, str]) -> None:
        if column_purposes is not None:
            for column_name, feature_type in column_purposes.items():
                self._validate_feature_type(feature_type=feature_type)
        self._column_purposes = column_purposes

    @property
    def drop_columns(self):
        return self._drop_columns

    @drop_columns.setter
    def drop_columns(self, drop_columns: List[str]) -> None:
        self._drop_columns = drop_columns

    @property
    def transformer_params(self):
        return self._transformer_params

    @transformer_params.setter
    def transformer_params(self, transformer_params: Dict[str, List[ColumnTransformerParamType]]) -> None:
        if transformer_params is not None:
            for transformer, list_of_tuples in transformer_params.items():
                self._validate_transformer_names(transformer=transformer)
                for cols, params in list_of_tuples:
                    self._validate_customizable_transformers(transformer=transformer, params=params)
        self._transformer_params = transformer_params

    def _from_dict(self, dict):
        for key, value in dict.items():
            if key not in self.__dict__.keys():
                logging.warning("Received unrecognized parameters for FeaturizationConfig")
            else:
                setattr(self, key, value)

    def _convert_timeseries_target_column_name(self, label_column_name: str) -> None:
        if self.transformer_params is not None:
            if self.transformer_params.get(_SupportedTransformers.Imputer) is not None:
                for cols, params in self.transformer_params[_SupportedTransformers.Imputer]:
                    if label_column_name in cols:
                        cols.remove(label_column_name)
                        cols.append(TimeSeriesInternal.DUMMY_TARGET_COLUMN)

    def __str__(self):
        return json.dumps(self.__dict__)

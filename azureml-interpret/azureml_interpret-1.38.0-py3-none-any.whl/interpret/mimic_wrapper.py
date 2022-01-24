# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines functionality to wrap machine learning interpretability into a single API."""

import joblib
import math
import numpy as np
import pandas as pd
import scipy
import sys

from operator import itemgetter

from interpret_community.mimic.mimic_explainer import MimicExplainer
from interpret_community.explanation.explanation import _create_global_explanation

from azureml._common._error_definition import AzureMLError
from azureml._logging import ChainedIdentity
from azureml.core import Model, Dataset, Experiment
from azureml.interpret._internal.explanation_client import ExplanationClient
from azureml.interpret.common._errors.error_definitions import (
    ExplainBeforeUploadConflict, EvalDatasetMissing,
    InitDatasetMissing, InvalidExplanationTypes,
    MissingFeatureMapGettingRaw,
    RawTransformArgumentMismatch,
    SampleLimitExceeded)
from azureml.interpret.common.constants import ExplainParams, History, ModelTask
from azureml.interpret.common.exceptions import (
    ConflictingRawTransformationsException, InitDatasetMissingException,
    MissingExplainException, MissingRawTransformationsException,
    MissingEvalDataException, MissingExplanationTypesException, SamplesExceededException)


class MimicWrapper(ChainedIdentity):
    """A wrapper explainer which reduces the number of function calls necessary to use the explain model package.

    .. remarks::

        The MimicWrapper can be used for explaining machine learning models, and is particularly effective in
        conjunction with AutoML. For example, using the ``automl_setup_model_explanations`` function in the
        :mod:`azureml.train.automl.runtime.automl_explain_utilities` module, you can use the MimicWrapper
        to compute and visualize feature importance. For more information, see `Interpretability: model
        explanations in automated machine
        learning <https://docs.microsoft.com/azure/machine-learning/how-to-machine-learning-interpretability-automl>`_.

        In the following example, the MimicWrapper is used in a classification problem.

        .. code-block:: python

            from azureml.interpret.mimic_wrapper import MimicWrapper
            explainer = MimicWrapper(ws, automl_explainer_setup_obj.automl_estimator,
                         explainable_model=automl_explainer_setup_obj.surrogate_model,
                         init_dataset=automl_explainer_setup_obj.X_transform, run=automl_run,
                         features=automl_explainer_setup_obj.engineered_feature_names,
                         feature_maps=[automl_explainer_setup_obj.feature_map],
                         classes=automl_explainer_setup_obj.classes,
                         explainer_kwargs=automl_explainer_setup_obj.surrogate_model_params)

        For more information about this example, see this `notebook
        <https://github.com/Azure/MachineLearningNotebooks/blob/master/how-to-use-azureml/automated-machine-learning/local-run-classification-credit-card-fraud/auto-ml-classification-credit-card-fraud-local.ipynb>`_.

    :param workspace: The workspace object where the Models and Datasets are defined.
    :type workspace: azureml.core.Workspace
    :param model: The model ID of a model registered to MMS or a regular machine learning model or pipeline
        to explain. If a model is specified, it must implement sklearn.predict() or sklearn.predict_proba(). If
        a pipeline is specified, it must include a function that accepts a 2d ndarray.
    :type model: str or model that implements sklearn.predict() or sklearn.predict_proba() or
        pipeline function that accepts a 2d ndarray
    :param explainable_model: The uninitialized surrogate model used to explain the black box model.
        Also known as the student model.
    :type explainable_model: azureml.interpret.mimic.models.BaseExplainableModel
    :param explainer_kwargs: Any keyword arguments that go with the chosen explainer not otherwise covered here.
        They will be passed in as kwargs when the underlying explainer is initialized.
    :type explainer_kwargs: dict
    :param init_dataset: The dataset ID or regular dataset used for initializing the explainer (e.g., x_train).
    :type init_dataset: str or numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
    :param run: The run this explanation should be associated with.
    :type run: azureml.core.Run
    :param features: A list of feature names.
    :type features: list[str]
    :param classes: Class names as a list of strings. The order of the class names should match
        that of the model output. Only required if explaining classifier.
    :type classes: list[str]
    :param model_task: Optional parameter to specify whether the model is a classification or regression model.
        In most cases, the type of the model can be inferred based on the shape of the output, where a classifier
        has a predict_proba method and outputs a 2 dimensional array, while a regressor has a predict method and
        outputs a 1 dimensional array.
    :type model_task: str
    :param explain_subset: A list of feature indices. If specified, Azure only selects a subset of the
        features in the evaluation dataset for explanation, which will speed up the explanation
        process when number of features is large and you already know the set of interesting
        features. The subset can be the top-k features from the model summary. This parameter is not supported when
        transformations are set.
    :type explain_subset: list[int]
    :param transformations: A sklearn.compose.ColumnTransformer or a list of tuples describing the column name and
        transformer. When transformations are provided, explanations are of the features before the
        transformation. The format for a list of transformations is same as the one here:
        https://github.com/scikit-learn-contrib/sklearn-pandas.

        If you are using a transformation that is not in the list of sklearn.preprocessing transformations
        that are supported by the `interpret-community <https://github.com/interpretml/interpret-community>`_
        package, then this parameter cannot take a list of more than one column
        as input for the transformation. You can use the following sklearn.preprocessing transformations with
        a list of columns since these are already one to many or one to one: Binarizer, KBinsDiscretizer,
        KernelCenterer, LabelEncoder, MaxAbsScaler, MinMaxScaler, Normalizer, OneHotEncoder, OrdinalEncoder,
        PowerTransformer, QuantileTransformer, RobustScaler, StandardScaler.

        Examples for transformations that work::

            [
                (["col1", "col2"], sklearn_one_hot_encoder),
                (["col3"], None) #col3 passes as is
            ]
            [
                (["col1"], my_own_transformer),
                (["col2"], my_own_transformer),
            ]

        An example of a transformation that would raise an error since it cannot be interpreted as one to many::

            [
                (["col1", "col2"], my_own_transformer)
            ]

        The last example would not work since the interpret-community package can't determine whether
        my_own_transformer gives a many to many or one to many mapping when taking a sequence of columns.

        Only one parameter from 'transformations' or 'feature_maps' should be specified to generate raw
        explanations. Specifying both will result in configuration exception.
    :type transformations: sklearn.compose.ColumnTransformer or list[tuple]
    :param feature_maps: A list of feature maps from raw to generated feature.
        This parameter can be list of numpy arrays or sparse matrices where each array entry
        (raw_index, generated_index) is the weight for each raw, generated feature pair. The other entries are set
        to zero. For a sequence of transformations [t1, t2, ..., tn] generating generated features from raw
        features, the list of feature maps correspond to the raw to generated maps in the same order as t1, t2,
        etc. If the overall raw to generated feature map from t1 to tn is available, then just that feature map
        in a single element list can be passed.

        Only one parameter from 'transformations' or 'feature_maps' should be specified to generate raw
        explanations. Specifying both will result in configuration exception.
    :type feature_maps: list[numpy.array] or list[scipy.sparse.csr_matrix]
    :param allow_all_transformations: Whether to allow many to many and many to one transformations.
    :type allow_all_transformations: bool
    """

    def __init__(self, workspace, model, explainable_model, explainer_kwargs=None,
                 init_dataset=None, run=None, features=None, classes=None, model_task=ModelTask.Unknown,
                 explain_subset=None, transformations=None, feature_maps=None, allow_all_transformations=None):
        """Initialize the MimicWrapper.

        :param workspace: The workspace object where the Models and Datasets are defined.
        :type workspace: azureml.core.Workspace
        :param model: The model ID of a model registered to MMS or a regular machine learning model or pipeline
            to explain. If a model is specified, it must implement sklearn.predict() or sklearn.predict_proba(). If
            a pipeline is specified, it must include a function that accepts a 2d ndarray.
        :type model: str or model that implements sklearn.predict() or sklearn.predict_proba() or pipeline function
        `that accepts a 2d ndarray
        :param explainable_model: The uninitialized surrogate model used to explain the black box model.
            Also known as the student model.
        :type explainable_model: azureml.interpret.mimic.models.BaseExplainableModel
        :param explainer_kwargs: Any keyword arguments that go with the chosen explainer not otherwise covered here.
            They will be passed in as kwargs when the underlying explainer is initialized.
        :type explainer_kwargs: dict
        :param init_dataset: The dataset ID or regular dataset used for initializing the explainer (e.g. x_train).
        :type init_dataset: str or numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
        :param run: The run this explanation should be associated with.
        :type run: azureml.core.Run
        :param features: A list of feature names.
        :type features: list[str]
        :param classes: Class names as a list of strings. The order of the class names should match
            that of the model output.  Only required if explaining classifier.
        :type classes: list[str]
        :param model_task: Optional parameter to specify whether the model is a classification or regression model.
            In most cases, the type of the model can be inferred based on the shape of the output, where a classifier
            has a predict_proba method and outputs a 2 dimensional array, while a regressor has a predict method and
            outputs a 1 dimensional array.
        :type model_task: str
        :param explain_subset: List of feature indices. If specified, only selects a subset of the
            features in the evaluation dataset for explanation, which will speed up the explanation
            process when number of features is large and the user already knows the set of interested
            features. The subset can be the top-k features from the model summary. This argument is not supported when
            transformations are set.
        :type explain_subset: list[int]
        :param transformations: A sklearn.compose.ColumnTransformer or a list of tuples describing the column name and
            transformer. When transformations are provided, explanations are of the features before the
            transformation. The format for a list of transformations is same as the one here:
            https://github.com/scikit-learn-contrib/sklearn-pandas.

            If you are using a transformation that is not in the list of sklearn.preprocessing transformations
            that are supported by the `interpret-community <https://github.com/interpretml/interpret-community>`_
            package, then this parameter cannot take a list of more than one column
            as input for the transformation. You can use the following sklearn.preprocessing transformations with
            a list of columns since these are already one to many or one to one: Binarizer, KBinsDiscretizer,
            KernelCenterer, LabelEncoder, MaxAbsScaler, MinMaxScaler, Normalizer, OneHotEncoder, OrdinalEncoder,
            PowerTransformer, QuantileTransformer, RobustScaler, StandardScaler.

            Examples for transformations that work::

                [
                    (["col1", "col2"], sklearn_one_hot_encoder),
                    (["col3"], None) #col3 passes as is
                ]
                [
                    (["col1"], my_own_transformer),
                    (["col2"], my_own_transformer),
                ]

            An example of a transformation that would raise an error since it cannot be interpreted as one to many::

                [
                    (["col1", "col2"], my_own_transformer)
                ]

            The last example would not work since the interpret-community package can't determine whether
            my_own_transformer gives a many to many or one to many mapping when taking a sequence of columns.

            Only one parameter from 'transformations' or 'feature_maps' should be specified to generate raw
            explanations. Specifying both will result in configuration exception.
        :type transformations: sklearn.compose.ColumnTransformer or list[tuple]
        :param feature_maps: A list of feature maps from raw to generated feature.
            This parameter can be list of numpy arrays or sparse matrices where each array entry
            (raw_index, generated_index) is the weight for each raw, generated feature pair. The other entries are set
            to zero. For a sequence of transformations [t1, t2, ..., tn] generating generated features from raw
            features, the list of feature maps correspond to the raw to generated maps in the same order as t1, t2,
            etc. If the overall raw to generated feature map from t1 to tn is available, then just that feature map
            in a single element list can be passed.

            Only one parameter from 'transformations' or 'feature_maps' should be specified to generate raw
            explanations. Specifying both will result in configuration exception.
        :type feature_maps: list[numpy.array] or list[scipy.sparse.csr_matrix]
         :param allow_all_transformations: Whether to allow many to many and many to one transformations.
        :type allow_all_transformations: bool
        """
        if transformations is not None and feature_maps is not None:
            raise ConflictingRawTransformationsException._with_error(
                AzureMLError.create(
                    RawTransformArgumentMismatch, target="feature_maps"
                )
            )

        super(MimicWrapper, self).__init__()
        self._logger.debug('Initializing MimicWrapper')
        kwargs = {} if explainer_kwargs is None else explainer_kwargs
        self._workspace = workspace
        self._run = run
        self._model_id = None
        self._init_dataset_id = None
        if isinstance(model, str):
            self._logger.debug('Model ID passed in')
            self._model_id = model
            model_obj = Model(self._workspace, id=self._model_id)
            path = model_obj.download(exist_ok=True)
            model = joblib.load(path)
        if isinstance(init_dataset, str):
            self._logger.debug('Init Dataset ID passed in')
            self._init_dataset_id = init_dataset
            init_dataset_obj = Dataset.get(self._workspace, id=init_dataset)
            init_dataset = init_dataset_obj.to_pandas_dataframe().values.astype('float64')
        if init_dataset is None:
            self._logger.debug('No init dataset passed into MimicWrapper')
            raise InitDatasetMissingException._with_error(
                AzureMLError.create(
                    InitDatasetMissing, target="init_dataset"
                )
            )
        self._feature_maps = feature_maps
        self._internal_explainer = MimicExplainer(model,
                                                  init_dataset,
                                                  explainable_model,
                                                  features=features,
                                                  classes=classes,
                                                  model_task=model_task,
                                                  explain_subset=explain_subset,
                                                  transformations=transformations,
                                                  allow_all_transformations=allow_all_transformations,
                                                  **kwargs)
        self._client = None

    def _explain_local(self, evals):
        """Explain a model's behavior on individual data instances.

        :param evals: The data instances to explain.
        :type evals: numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
        :return: A local explanation.
        :rtype: DynamicLocalExplanation
        """
        return self._internal_explainer.explain_local(evals)

    def _explain_global(self, evals=None, include_local=True, batch_size=None):
        """Explain a model's behavior at the global level.

        :param evals: Representative data instances used to construct the explanation.
        :type evals: numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
        :return: A global explanation.
        :rtype: DynamicGlobalExplanation
        """
        if batch_size is not None:
            return self._internal_explainer.explain_global(evaluation_examples=evals, include_local=include_local,
                                                           batch_size=batch_size)
        return self._internal_explainer.explain_global(evaluation_examples=evals, include_local=include_local)

    def explain(self, explanation_types, eval_dataset=None, top_k=None, upload=True, upload_datasets=False,
                tag="", get_raw=False, raw_feature_names=None, experiment_name='explain_model', raw_eval_dataset=None,
                true_ys=None):
        """Explain a model's behavior and optionally upload that explanation for storage and visualization.

        :param explanation_types: A list of strings representing types of explanations desired. Currently,
            'global' and 'local' are supported. Both may be passed in at once; only one explanation will be returned.
        :type explanation_types: list[str]
        :param eval_dataset: The dataset ID or regular dataset used to generate the explanation.
        :type eval_dataset: str or numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
        :param top_k: Limit to the amount of data returned and stored in Run History to top k features, when possible.
        :type top_k: int
        :param upload: If True, the explanation is automatically uploaded to Run History for storage and
            visualization. If a run was not passed in at initialization, one is created.
        :type upload: bool
        :param upload_datasets: If set to True and no dataset IDs are passed in, the evaluation dataset will be
            uploaded to Azure storage. This will improve the visualization available in the web view.
        :type upload_datasets: bool
        :param tag: A string to attach to the explanation to distinguish it from others after upload.
        :type tag: str
        :param get_raw: If True and the parameter ``feature_maps`` was passed in during initialization,
            the explanation returned will be for the raw features. If False or not specified, the explanation
            will be for the data exactly as it is passed in.
        :type get_raw: bool
        :param raw_feature_names: The list of raw feature names, replacing engineered feature names from the
            constructor.
        :type raw_feature_names: list[str]
        :param experiment_name: The desired name to give an explanation if ``upload`` is True but no run was passed
            in during initialization
        :type experiment_name: str
        :param raw_eval_dataset: Raw eval data to be uploaded for raw explanations.
        :type raw_eval_dataset: str or numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
        :param true_ys: The true labels for the evaluation examples.
        :type true_ys: list | pandas.Dataframe | numpy.ndarray
        :return: An explanation object.
        :rtype: Explanation
        """
        eval_dataset_id = eval_dataset if isinstance(eval_dataset, str) else None
        if eval_dataset_id is not None:
            eval_dataset = self._get_dataset_from_id(eval_dataset_id)

        explanation = self._get_eng_explanation(explanation_types, eval_dataset=eval_dataset)
        # Note this can be a raw explanation if transformations were passed to mimic explainer
        if not explanation._is_raw:
            explanation._is_eng = True

        if get_raw:
            explanation = self._handle_get_raw(explanation,
                                               raw_feature_names=raw_feature_names,
                                               raw_eval_dataset=raw_eval_dataset)

        if upload:
            self._client = self._get_explanation_client(experiment_name)
            self._client.upload_model_explanation(explanation,
                                                  model_id=self._model_id,
                                                  init_dataset_id=self._init_dataset_id,
                                                  eval_dataset_id=eval_dataset_id,
                                                  upload_datasets=upload_datasets,
                                                  comment=tag,
                                                  top_k=top_k,
                                                  true_ys=true_ys)
        return explanation

    def _explain_large_data(self, eval_dataset, classes=1, memory_cap=8, raw_feature_names=None,
                            top_k=None, local_samples=None):
        """Run explanation for large data.

        Streams global explanations using a dynamically calculated batch size. Samples randomly or uses local_samples
        from the user to get local importances for a subset of data.

        :param eval_dataset: The dataset used to generate the explanation.
        :type eval_dataset: numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
        :param classes: The number of target classes.
        :type classes: int
        :param memory_cap: The amount of memory calculation should be limited to. In gigabytes. We recommend setting
            this limit below total system memory to leave space for process and system overhead.
        :type memory_cap: int
        :param raw_feature_names: The list of raw feature names, replacing engineered feature names from the
            constructor.
        :type raw_feature_names: list[str]
        :param top_k: Limit the amount of data returned and stored in run history to top k features when possible.
        :type top_k: int
        :param local_samples: A list of points to generate local importances for. The number of local samples must be
            less than the calculated batch size.
        :type local_samples: list[int]
        """
        size_in_bytes = memory_cap * (10 ** 9)  # because gigabytes
        # TODO reduce overall memory usage
        size_in_bytes //= 5

        if scipy.sparse.issparse(eval_dataset):
            rows = eval_dataset.shape[0]
            indices_size = eval_dataset.indices.nbytes
            data_size = eval_dataset.data.nbytes
            indptr_size = eval_dataset.indptr.nbytes
            # estimate eval dataset size
            eval_dataset_size = max(indices_size + data_size + indptr_size, sys.getsizeof(eval_dataset))
        elif isinstance(eval_dataset, np.ndarray):
            rows = eval_dataset.shape[0]
            eval_dataset_size = max(eval_dataset.nbytes, sys.getsizeof(eval_dataset))
        elif isinstance(eval_dataset, pd.DataFrame):
            rows = eval_dataset.values.shape[0]
            eval_dataset_size = eval_dataset.memory_usage(index=True, deep=True).sum()
        elif isinstance(eval_dataset, list):
            rows = len(eval_dataset)
            cols = len(eval_dataset[0])
            # this is correct as long as the list contains python standard objects
            eval_dataset_size = rows * cols * sys.getsizeof(eval_dataset[0][0])

        # 1.5 necessary to get close to the memory limit from the user
        memory_factor = 1.5
        batch_size = math.floor(size_in_bytes / (memory_factor * eval_dataset_size * classes / rows))

        if batch_size < rows:
            self._logger.debug('Data size is too large. Only a subset of local importances will be available.')
        global_eng = self._explain_global(evals=eval_dataset, include_local=False, batch_size=batch_size)

        if local_samples is None:
            if batch_size > rows:
                local_indices = list(range(rows))
                self._logger.debug('All local importances will be available, consider using explain method instead.')
            else:
                local_indices = sorted(np.random.choice(rows, batch_size, replace=False))
        else:
            if len(local_samples) > batch_size:
                raise SamplesExceededException._with_error(
                    AzureMLError.create(
                        SampleLimitExceeded, actual=len(local_samples), limit=batch_size,
                        target="local_samples"
                    )
                )
            else:
                local_indices = np.array(local_samples)

        if scipy.sparse.issparse(eval_dataset):
            sampled_dataset = eval_dataset[local_indices, :]
        elif isinstance(eval_dataset, np.ndarray):
            sampled_dataset = eval_dataset[local_indices, :]
        elif isinstance(eval_dataset, pd.DataFrame):
            features = eval_dataset.columns.values.tolist()
            sampled_dataset = pd.DataFrame(eval_dataset.values[local_indices, :], columns=features)
        elif isinstance(eval_dataset, list):
            local_indices = local_indices.tolist()
            index_getter = itemgetter(*local_indices)
            sampled_dataset = list(index_getter(eval_dataset))
        local_eng = self._explain_local(sampled_dataset)

        kwargs = {
            ExplainParams.METHOD: global_eng.method,
            ExplainParams.MODEL_TASK: global_eng.model_task,
            ExplainParams.MODEL_TYPE: global_eng.model_type,
            ExplainParams.FEATURES: global_eng.features,
            History.NUM_FEATURES: global_eng.num_features,
            ExplainParams.IS_RAW: global_eng.is_raw,
            ExplainParams.IS_ENG: global_eng.is_engineered,
            ExplainParams.LOCAL_EXPLANATION: local_eng,
            ExplainParams.GLOBAL_IMPORTANCE_VALUES: global_eng.global_importance_values,
            ExplainParams.GLOBAL_IMPORTANCE_RANK: global_eng.global_importance_rank,
            History.RANKED_GLOBAL_NAMES: global_eng.get_ranked_global_names(),
            History.RANKED_GLOBAL_VALUES: global_eng.get_ranked_global_values(),
            ExplainParams.EXPECTED_VALUES: global_eng.expected_values,
            ExplainParams.CLASSES: global_eng.classes,
            History.NUM_CLASSES: global_eng.num_classes,
            History.PER_CLASS_VALUES: global_eng.per_class_values,
            History.PER_CLASS_RANK: global_eng.per_class_rank,
            History.RANKED_PER_CLASS_NAMES: global_eng.get_ranked_per_class_names(),
            History.RANKED_PER_CLASS_VALUES: global_eng.get_ranked_per_class_values(),
            History.INIT_DATA: global_eng.init_data,
            History.EVAL_DATA: global_eng.eval_data,
            History.EVAL_Y_PRED: global_eng.eval_y_predicted,
            History.EVAL_Y_PRED_PROBA: global_eng.eval_y_predicted_proba
        }

        if hasattr(global_eng, History.MODEL_ID):
            kwargs[History.MODEL_ID] = global_eng.model_id

        full_eng = _create_global_explanation(explanation_id=global_eng.id, **kwargs)

        self._client = self._get_explanation_client(experiment_name='explain_model')
        self._client.upload_model_explanation(full_eng,
                                              model_id=self._model_id,
                                              init_dataset_id=self._init_dataset_id,
                                              top_k=top_k)

        if self._feature_maps is not None:
            full_raw = full_eng.get_raw_explanation(self._feature_maps, raw_feature_names=raw_feature_names)

            self._client.upload_model_explanation(full_raw,
                                                  model_id=self._model_id,
                                                  init_dataset_id=self._init_dataset_id,
                                                  top_k=top_k)
            return full_raw
        else:
            return full_eng

    @property
    def explainer(self):
        """Get the explainer that is being used internally by the wrapper.

        :return: The explainer that is being used internally by the wrapper.
        :rtype: azureml.interpret.mimic.MimicExplainer
        """
        return self._internal_explainer

    def _automl_aggregate_and_upload(self, eng_explanation, upload_datasets=False, tag='',
                                     raw_feature_names=None, top_k=None, eval_dataset_id=None,
                                     raw_eval_dataset=None, true_ys=None):
        """Explain a model's behavior on raw and engineered features and upload that explanation.

        This is an AutoML specific internal function.

        :param eng_explanation: A regular Explanation.
        :type eng_explanation: Explanation
        :param upload_datasets: If set to True and no dataset IDs are passed in, the evaluation dataset will be
            uploaded to Azure storage. This will improve the visualization available in the web view.
        :type upload_datasets: bool
        :param tag: A string to attach to the explanation to distinguish it from others after upload.
        :type tag: str
        :param raw_feature_names: The list of raw feature names, replacing engineered feature names from the
            constructor.
        :type raw_feature_names: list[str]
        :param top_k: Limit the amount of data returned and stored in run history to top k features when possible.
        :type top_k: int
        :param eval_dataset_id: The ID of the Dataset in which evaluation data is stored (only use if this is
            already the case).
        :type eval_dataset_id: str
        :param raw_eval_dataset: Raw eval data to be uploaded for raw explanations.
        :type raw_eval_dataset: str or numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
        :param true_ys: The true labels for the evaluation examples.
        :type true_ys: list | pandas.Dataframe | numpy.ndarray
        :return: An explanation object.
        :rtype: Explanation
        """
        eng_explanation._is_eng = True
        raw_explanation = self._handle_get_raw(eng_explanation,
                                               raw_feature_names=raw_feature_names,
                                               raw_eval_dataset=raw_eval_dataset)

        if self._client is not None:
            self._client.upload_model_explanation(raw_explanation,
                                                  model_id=self._model_id,
                                                  init_dataset_id=self._init_dataset_id,
                                                  eval_dataset_id=None,
                                                  upload_datasets=upload_datasets,
                                                  comment=tag,
                                                  top_k=top_k,
                                                  true_ys=true_ys)
            return raw_explanation
        else:
            raise MissingExplainException._with_error(AzureMLError.create(ExplainBeforeUploadConflict))

    def _handle_get_raw(self, explanation, raw_feature_names=None, raw_eval_dataset=None):
        """Get raw explanation from a given engineered explanation.

        :param explanation: A regular Explanation.
        :type explanation: Explanation
        :param raw_feature_names: The list of raw feature names, replacing engineered feature names from the
            constructor.
        :type raw_feature_names: list[str]
        :param raw_eval_dataset: Raw eval data to be uploaded for raw explanations.
        :type raw_eval_dataset: str or numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
        :return: A raw explanation constructed from the engineered one.
        :rtype: Explanation
        """
        if self._feature_maps is None:
            raise MissingRawTransformationsException._with_error(AzureMLError.create(MissingFeatureMapGettingRaw))
        else:
            self._logger.debug('Creating a raw explanation')
            return explanation.get_raw_explanation(self._feature_maps,
                                                   raw_feature_names=raw_feature_names,
                                                   eval_data=raw_eval_dataset)

    def _get_dataset_from_id(self, id):
        """Get data from a given dataset ID.

        :param id: The ID of the Azure ML Dataset.
        :type id: str
        :return: The data.
        :rtype: numpy, pandas
        """
        self._logger.debug('Eval Dataset ID passed in')
        eval_dataset_obj = Dataset.get(self._workspace, id=id)
        return eval_dataset_obj.to_pandas_dataframe().values.astype('float64')

    def _get_eng_explanation(self, explanation_types, eval_dataset=None):
        """Get the engineered explanation.

        :param explanation_types: A list of strings representing types of explanations desired. Currently, we support
            'global' and 'local'. Both may be passed in at once; only one explanation will be returned. If local is
            not passed in but data is passed in for eval_dataset, the global explanation will run with
            include_local=False, which will use local importances to aggregate to the global importance, but will not
            store them or return them.
        :type explanation_types: list[str]
        :param eval_dataset: The dataset ID or regular dataset used to generate the explanation.
        :type eval_dataset: str or numpy.array or pandas.DataFrame or scipy.sparse.csr_matrix
        :return: An explanation object.
        :rtype: Explanation
        """
        if 'global' in explanation_types:
            if 'local' in explanation_types:
                return self._explain_global(evals=eval_dataset)
            elif eval_dataset is not None:
                return self._explain_global(evals=eval_dataset, include_local=False)
            else:
                return self._explain_global()
        elif 'local' in explanation_types:
            if eval_dataset is None:
                raise MissingEvalDataException._with_error(
                    AzureMLError.create(
                        EvalDatasetMissing, target="eval_dataset"
                    )
                )
            return self._explain_local(eval_dataset)
        else:
            raise MissingExplanationTypesException._with_error(
                AzureMLError.create(
                    InvalidExplanationTypes, explanation_types=explanation_types,
                    target="explanation_types"
                )
            )

    def _get_explanation_client(self, experiment_name):
        """Create the explanation client given an experiment name.

        If there is no run available, create one.

        :param experiment_name: The name to give an experiment if a new run is needed.
        :type experiment_name: str
        :return: A new explanation client
        :rtype: ExplanationClient
        """
        self._logger.debug('Uploading model explanation from MimicWrapper')
        if self._run is None:
            experiment = Experiment(self._workspace, experiment_name)
            self._run = experiment.start_logging(snapshot_directory=None)
        return ExplanationClient.from_run(self._run)

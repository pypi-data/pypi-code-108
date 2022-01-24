# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Main module of onnx conversion."""
from typing import Any, cast, Dict, List, Tuple, Union, Optional
import numbers
import numpy as np
import pandas as pd
import six
import copy
from collections import deque
import traceback
import os
import sys
from os import path
import json
import logging
import scipy
from azureml.automl.core.onnx_convert.onnx_convert_constants import OnnxConvertConstants, SplitOnnxModelName
from azureml.automl.core.constants import FeatureType  # noqa: E402
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.runtime.shared.types import DataInputType

import sklearn
# Make sure the sklearn is compatible with skl2onnx.
from .operator_converters._utilities \
    import _make_sklearn_compatible_with_skl2onnx, _raise_exception_if_python_ver_doesnot_support_onnx

_make_sklearn_compatible_with_skl2onnx()

from sklearn.pipeline import Pipeline  # noqa: E402
from sklearn.preprocessing import LabelEncoder  # noqa: E402
from sklearn_pandas.pipeline import TransformerPipeline  # noqa: E402
from sklearn.base import ClassifierMixin  # noqa: E402
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor  # noqa: E402

# -----------------------------------
# Import the onnx related packages, only if the python version is compatible.
if sys.version_info < OnnxConvertConstants.OnnxIncompatiblePythonVersion:
    from sklearn.feature_extraction.text import CountVectorizer  # noqa: E402
    from sklearn.feature_extraction.text import TfidfVectorizer  # noqa: E402

    # Import skl2onnx modules.
    import onnx  # noqa: E402

    from skl2onnx.convert import convert_sklearn  # noqa: E402
    from skl2onnx.common.data_types import Int64TensorType  # noqa: E402
    from skl2onnx.common.data_types import FloatTensorType  # noqa: E402
    from skl2onnx.common.data_types import StringTensorType  # noqa: E402
    from skl2onnx.common.data_types import DictionaryType  # noqa: E402
    from skl2onnx.common.data_types import SequenceType  # noqa: E402

    from skl2onnx.proto import onnx_proto  # noqa: E402

    from skl2onnx.common._container import SklearnModelContainerNode, ModelComponentContainer  # noqa: E402
    from skl2onnx.common._topology import Topology, convert_topology  # noqa: E402

    from skl2onnx import _parse as _sklearn_parse  # noqa: E402
    from skl2onnx import _supported_operators as _sklearn_supported_operators  # noqa: E402

    # -----------------------------------
    # onnxmltools modules.
    import onnxmltools.convert.common.data_types  # noqa: E402

    # -----------------------------------
    # Redefine the onnxmltools data type classes, this is needed to fix issue with onnxmltools.
    onnxmltools.convert.common.data_types.Int64TensorType = Int64TensorType
    onnxmltools.convert.common.data_types.StringTensorType = StringTensorType
    onnxmltools.convert.common.data_types.FloatTensorType = FloatTensorType
    onnxmltools.convert.common.data_types.DictionaryType = DictionaryType
    onnxmltools.convert.common.data_types.SequenceType = SequenceType

    from lightgbm import LGBMClassifier, LGBMRegressor  # noqa: E402
    from onnxmltools.convert.lightgbm.operator_converters.LightGbm import convert_lightgbm  # noqa: E402
    from onnxmltools.convert.lightgbm.shape_calculators.Classifier import (  # noqa: E402
        calculate_linear_classifier_output_shapes as omt_calculate_linear_classifier_output_shapes)
    from onnxmltools.convert.lightgbm.shape_calculators.Regressor import \
        calculate_linear_regressor_output_shapes  # noqa: E402

    try:
        # Try import xgboost.
        from xgboost import XGBClassifier, XGBRegressor  # noqa: E402

        _xgboost_present = True

        from onnxmltools.convert.xgboost.operator_converters.XGBoost import convert_xgboost  # noqa: E402
        from onnxmltools.convert.xgboost.shape_calculators.Classifier import \
            calculate_xgboost_classifier_output_shapes  # noqa: E402

    except ImportError:
        _xgboost_present = False

# -----------------------------------
# AutoML modules.
# Model wrappers.
SOURCE_WRAPPER_MODULES = [
    'automl.client.core.runtime.model_wrappers',
    'azureml.automl.runtime.shared.model_wrappers'
]

from azureml.automl.core.shared.constants import (  # noqa: E402
    NumericalDtype, DatetimeDtype, TextOrCategoricalDtype)

from azureml.automl.runtime.shared.model_wrappers import _AbstractModelWrapper  # noqa: E402
from azureml.automl.runtime.shared.model_wrappers import PipelineWithYTransformations  # noqa: E402
from azureml.automl.runtime.shared.model_wrappers import PreFittedSoftVotingClassifier  # noqa: E402
from azureml.automl.runtime.shared.model_wrappers import PreFittedSoftVotingRegressor  # noqa: E402
from azureml.automl.runtime.shared.model_wrappers import NBWrapper  # noqa: E402
from azureml.automl.runtime.shared.model_wrappers import IdentityTransformer  # noqa: E402

from ..column_purpose_detection import ColumnPurposeDetector  # noqa: E402
# Transformers.
from ..featurizer.transformer import CatImputer  # noqa: E402
from ..featurizer.transformer import HashOneHotVectorizerTransformer  # noqa: E402
from ..featurizer.transformer import LaggingTransformer  # noqa: E402
from ..featurizer.transformer import ImputationMarker  # noqa: E402
from ..featurizer.transformer import StringCastTransformer  # noqa: E402
from ..featurizer.transformer import DateTimeFeaturesTransformer  # noqa: E402
from ..featurization import DataTransformer  # noqa: E402

from azureml.automl.core.shared.exceptions import AutoMLException, OnnxConvertException  # noqa: E402

from .operator_converters import (  # noqa: E402
    DataTransformerFeatureConcatenatorConverter)
from .operator_converters import (  # noqa: E402
    MissingValReplaceProcessorConverter)
from .operator_converters import (  # noqa: E402
    _YTransformLabelEncoder)
from .operator_converters import (  # noqa: E402
    YTransformerLabelEncoderConverter)
from .operator_converters import (  # noqa: E402
    PrefittedVotingClassifierConverter)
from .operator_converters import (  # noqa: E402
    PrefittedVotingRegressorConverter)

from . import OperatorConverterManager  # noqa: E402

from azureml.automl.core.shared.logging_utilities import function_debug_log_wrapped, _CustomStackSummary  # noqa: E402

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------
# The Converter class.
# ----------------------------------------------------------------
class OnnxConverter:
    """
    The converter that converts the pipeline/model objects from pkl format to onnx format.

    Before the input data is fitted/transformed, call Initialize to setup the signature of the X.
    Then the convert method can be called multi times, to convert given sklearn pipeline.
    """

    class _InitPhaseMetadata:
        """The metadata of the initialization phase."""
        InitialTypes = 'InitialTypes'
        IniTypeToInferTypeMap = 'IniTypeToInferTypeMap'
        IniTypeToInputDfColMap = 'IniTypeToInputDfColMap'
        DfColToDfColMapIdxInInput = 'DfColToDfColMapIdxInInput'
        IfInputDataHasColName = 'IfInputDataHasColName'
        IfModelCanUseBatchMode = 'IfModelCanUseBatchMode'

        def __init__(self, ini_types, ini_tp_to_infer_type_map, ini_tp_to_input_df_col_map,
                     df_col_to_df_col_idx_in_input, if_input_data_has_col_name,
                     if_model_can_use_batch_mode, *args, **kwargs):
            self._metadata_dict = {
                self.InitialTypes: ini_types,
                self.IniTypeToInferTypeMap: ini_tp_to_infer_type_map,
                self.IniTypeToInputDfColMap: ini_tp_to_input_df_col_map,
                self.DfColToDfColMapIdxInInput: df_col_to_df_col_idx_in_input,
                self.IfInputDataHasColName: if_input_data_has_col_name,
                self.IfModelCanUseBatchMode: if_model_can_use_batch_mode
            }

        def get_metadata_dict(self) -> Dict[str, Any]:
            return self._metadata_dict

        def is_valid(self):
            return self.is_metadata_dict_valid(self._metadata_dict)

        @classmethod
        def is_metadata_dict_valid(cls, metadata_dict: Dict[str, Any]) -> bool:
            return (metadata_dict is not None
                    and metadata_dict[cls.InitialTypes]
                    and metadata_dict[cls.IniTypeToInferTypeMap]
                    and metadata_dict[cls.IniTypeToInputDfColMap]
                    and metadata_dict[cls.DfColToDfColMapIdxInInput]
                    and metadata_dict[cls.IfInputDataHasColName] is not None
                    and metadata_dict[cls.IfModelCanUseBatchMode] is not None
                    )

    def __init__(self,
                 version='',
                 is_onnx_compatible=False,
                 enable_split_onnx_featurizer_estimator_models=False, **kwargs):
        """Construct the Onnx converter."""

        # The package version is used when saving the onnx model.
        self.producer_version = version

        # ----------------------------------
        # Common config.
        # The inner retry times.
        self._retry_count = 2

        # If the user is using onnx compatible mode, if so, we will post error
        # to the log when the conversion fails, if not, we will post warning.
        self.is_onnx_compatible = is_onnx_compatible

        # If we convert the splited featurizer/estimator models.
        self._enable_split_onnx_featurizer_estimator_models = enable_split_onnx_featurizer_estimator_models

        # ----------------------------------
        # Input initialization phase metadatas.
        # The individual (unbatched) initial types of input X.
        self.init_phase_initial_types = []  # type: List[Tuple[str, Any]]
        # The inidividual initial type index to the infer data type map.
        self.idx_indiv_ini_tp_to_infer_type_map = {}  # type: Dict[int, str]
        # The individual initial types index to the input data frame column map.
        self.idx_indiv_ini_tp_to_input_df_column_map = {}  # type: Dict[int, Union[str, int]]
        # The column object to index map, in the user input X.
        self.df_column_to_df_col_idx_in_input = {}  # type: Dict[Union[str, int], Any]

        # If the input training data has column names.
        self._if_input_data_has_column_name = False

        # If the ONNX model can accept batch input (multiple rows).
        self._if_model_can_use_batch_mode = False

        # The initialization phase metadata.
        self._init_phase_metadata = None  # type: Optional[OnnxConverter._InitPhaseMetadata]

        # ----------------------------------
        # If we are initialized.
        self._is_initialized = False

        # ----------------------------------
        # Conversion phase metadatas.
        # The unbatched initial types of user input X.
        self.conversion_phase_initial_types = []  # type: List[Tuple[Any, Any]]
        # The index of final generated initial types to the infer data type map.
        self.idx_selected_initial_type_to_infer_dtype_map = {}  # type: Dict[int, str]
        # The column object to index map, in the generated initial types.
        self.df_column_to_selected_initial_types_idx = {}  # type: Dict[Union[str, int], Any]
        # If the python single or ensemble model contains XGBoost classifier or regressor.
        self._python_model_contains_xgboost_estimator = False
        # If the python model contains count vectorizer or tfidf vectorizer.
        self._trans_contain_ct_tfidf_vectorizer = False

        # ----------------------------------
        # The resource of last succesfully converted onnx model.
        # TODO: Return this in the convert method with a convert result object.
        self._last_converted_onnx_model_res_dict = {}  # type: Dict[Any, Any]
        # If the ONNX model can accept batch input (multiple rows).
        self._last_converted_model_can_use_batch_mode = True

        # Register the custome shape calculators and the custom op converters
        # for our custom transformers.
        self.operator_manager = OperatorConverterManager()
        if sys.version_info < OnnxConvertConstants.OnnxIncompatiblePythonVersion:
            # Only initialize the operator manager when the python runtime is compatible with ONNX.
            self.operator_manager.initialize()

    def initialize_input(self,
                         X: Union[np.ndarray, pd.DataFrame],
                         x_raw_column_names: Optional[np.ndarray] = None,
                         model_name: str = '',
                         model_desc: Optional[Dict[Any, Any]] = None) -> None:
        """Initialize the converter with given training data X.

        NOTE.The X must be the original value, before it's transformed.
        :param X: The original input X before transformation applied.
        """
        err = None
        try:
            if self.is_onnx_compatible:
                err_log_level = logging.ERROR
            else:
                err_log_level = logging.WARNING
            self._logger_wrapper(logging.INFO, evt_name=OnnxConvertConstants.EvtInitInput,
                                 status=OnnxConvertConstants.StatusStart,
                                 model_name=model_name, model_desc=model_desc,
                                 message='Input initialization started.')
            # Check the Python version, now onnx package only supports < 3.8.
            _raise_exception_if_python_ver_doesnot_support_onnx()

            # Check type.
            if not isinstance(X, pd.DataFrame) and not isinstance(X, np.ndarray):
                raise OnnxConvertException("X should be a pandas dataframe or numpy array.", has_pii=False)

            Contract.assert_true(not scipy.sparse.issparse(X),
                                 "The ONNX converter doesn't support X of a sparse matrix type.", log_safe=True)

            # Clear initial types.
            self.init_phase_initial_types = []

            # We use data frame to parse the X.
            if isinstance(X, np.ndarray):
                # In case the X only has 1 column and got shrinked by data preparer to 1 dimension,
                # we get the number of columns here.
                num_cols_x = 0
                if len(X.shape) < 2:
                    num_cols_x = 1
                else:
                    num_cols_x = X.shape[1]
                if x_raw_column_names is not None and isinstance(x_raw_column_names, np.ndarray) \
                        and x_raw_column_names.shape[0] == num_cols_x:
                    # If the raw column names is passed in, and the column number is same as X,
                    # add the columns to the DataFrame.
                    X = pd.DataFrame(data=X, columns=x_raw_column_names.tolist())
                else:
                    X = pd.DataFrame(X)

            X = X.dropna(axis=1, how="all")

            # Setup the initial types for onnxmltool,
            # e.g.  [('input1', FloatTensorType(shape=[1, 1])), ('input2', Int64TensorType(shape=[1, 1]))].
            self._if_input_data_has_column_name = False
            for c in X.columns:
                if isinstance(c, str) and not self._if_input_data_has_column_name:
                    self._if_input_data_has_column_name = True
                self.df_column_to_df_col_idx_in_input[c] = X.columns.get_loc(c)

            # For each column we init a tuple (column_name, onnx_type).
            self._if_model_can_use_batch_mode = True
            self.idx_indiv_ini_tp_to_infer_type_map = {}
            stats_and_column_purposes = ColumnPurposeDetector.get_raw_stats_and_column_purposes(X)

            for i_init_tp, tpl in enumerate(stats_and_column_purposes):
                fea_stat, feature_type_detected, column = tpl
                tp_str = fea_stat.column_type
                tp_str = fea_stat.column_type
                if fea_stat.is_datetime and tp_str not in DatetimeDtype.FULL_SET:
                    # Need to handle the datetime feature state,
                    # if the column type is not a datetime type.
                    tp_str = DatetimeDtype.Datetime
                onnx_type = self._convert_np_to_onnx_type(tp_str)
                if self._if_input_data_has_column_name:
                    Contract.assert_true(isinstance(column, str),
                                         "Expected column to be a string.", log_safe=True)
                    col_name = column
                else:
                    col_name = 'input_' + str(i_init_tp)

                if self._if_model_can_use_batch_mode:
                    # We use Batch input feed mode, which uses the symbolic dimension.
                    onnx_tp = onnx_type(shape=['n', 1])
                else:
                    onnx_tp = onnx_type(shape=[1, 1])
                self.init_phase_initial_types.append((col_name, onnx_tp))
                self.idx_indiv_ini_tp_to_infer_type_map[i_init_tp] = tp_str
                self.idx_indiv_ini_tp_to_input_df_column_map[i_init_tp] = column

            if len(self.init_phase_initial_types) != 0:
                # Setup the initialization phase metadata for caching.
                self._setup_init_metadata()
                self._is_initialized = True

        except Exception as e:
            msg = "Inner Exception raised. Error message is hidden."
            stack_trace = self._get_stack_trace_msg()
            err = {
                'Info': 'Initialization of Input data failed.',
                'Class': e.__class__.__name__,
                'ErrorMsg': msg,
                'StackTrace': stack_trace
            }
            self._logger_wrapper(err_log_level, evt_name=OnnxConvertConstants.EvtInitInput,
                                 status=OnnxConvertConstants.StatusError,
                                 model_name=model_name, model_desc=model_desc,
                                 message=err)
            pass
        finally:
            if err is None:
                self._logger_wrapper(logging.INFO, evt_name=OnnxConvertConstants.EvtInitInput,
                                     status=OnnxConvertConstants.StatusEndSucceeded,
                                     model_name=model_name, model_desc=model_desc,
                                     message='Input initialization succeeded.')
            else:
                self._logger_wrapper(logging.WARNING, evt_name=OnnxConvertConstants.EvtInitInput,
                                     status=OnnxConvertConstants.StatusEndFailed,
                                     model_name=model_name, model_desc=model_desc,
                                     message='Input initialization failed.')

    def initialize_with_metadata(self,
                                 metadata_dict: Optional[Dict[str, Any]],
                                 model_name: str = '',
                                 model_desc: Optional[Dict[Any, Any]] = None) -> None:
        """Initialize the onnx converter with the previously generated init phase metadata."""
        self._logger_wrapper(logging.INFO, evt_name=OnnxConvertConstants.EvtInitWithMetadata,
                             status=OnnxConvertConstants.StatusStart,
                             model_name=model_name, model_desc=model_desc,
                             message='Initialize with metadata started.')
        if not self._is_initialized:
            if self.is_onnx_compatible:
                err_log_level = logging.ERROR
            else:
                err_log_level = logging.WARNING
            try:
                if (metadata_dict is not None and metadata_dict
                        and self._InitPhaseMetadata.is_metadata_dict_valid(metadata_dict=metadata_dict)):
                    self.init_phase_initial_types = metadata_dict[self._InitPhaseMetadata.InitialTypes]
                    self.idx_indiv_ini_tp_to_infer_type_map = \
                        metadata_dict[self._InitPhaseMetadata.IniTypeToInferTypeMap]
                    self.idx_indiv_ini_tp_to_input_df_column_map = \
                        metadata_dict[self._InitPhaseMetadata.IniTypeToInputDfColMap]
                    self.df_column_to_df_col_idx_in_input = \
                        metadata_dict[self._InitPhaseMetadata.DfColToDfColMapIdxInInput]
                    self._if_input_data_has_column_name = metadata_dict[self._InitPhaseMetadata.IfInputDataHasColName]
                    self._if_model_can_use_batch_mode = metadata_dict[self._InitPhaseMetadata.IfModelCanUseBatchMode]
                    self._is_initialized = True
                    self._logger_wrapper(logging.INFO, evt_name=OnnxConvertConstants.EvtInitWithMetadata,
                                         status=OnnxConvertConstants.StatusEndSucceeded,
                                         model_name=model_name,
                                         model_desc=model_desc,
                                         message='Initialize with metadata succeeded.')
                else:
                    raise OnnxConvertException("Invalid metadata. {}".format(metadata_dict)) \
                        .with_generic_msg("Invalid metadata.")
            except Exception:
                pass

                self._logger_wrapper(err_log_level, evt_name=OnnxConvertConstants.EvtInitWithMetadata,
                                     status=OnnxConvertConstants.StatusError,
                                     model_name=model_name, model_desc=model_desc,
                                     message="[Scrubbed]")
                self._logger_wrapper(err_log_level, evt_name=OnnxConvertConstants.EvtInitWithMetadata,
                                     status=OnnxConvertConstants.StatusEndFailed,
                                     model_name=model_name, model_desc=model_desc,
                                     message='Initialize with metadata failed.')
        else:
            self._logger_wrapper(logging.INFO, evt_name=OnnxConvertConstants.EvtInitWithMetadata,
                                 status=OnnxConvertConstants.StatusEndSucceeded,
                                 model_name=model_name, model_desc=model_desc,
                                 message='Initialize with metadata Succeeded. The converter is already initialized.')

    def get_init_metadata_dict(self) -> Optional[Dict[str, Any]]:
        """Return the metadata dictionary of the onnx converter in the init phase."""
        if self.is_initialized():
            return cast(OnnxConverter._InitPhaseMetadata, self._init_phase_metadata).get_metadata_dict()
        else:
            return None

    def is_initialized(self):
        """Return if the converter is initialized or not."""
        return self._is_initialized

    def convert(self,
                raw_model: Pipeline,
                model_name: str = '',
                model_desc: Optional[Union[str, Dict[str, Any]]] = None) \
            -> Tuple[Optional[onnx_proto.ModelProto],
                     Optional[onnx_proto.ModelProto],
                     Optional[onnx_proto.ModelProto], Optional[Dict[str, Any]]]:
        """
        Convert the Python model with given child run object into ONNX model.

        :param raw_model: The sklearn pipeline object to convert to ONNX.
        :param model_name: The name of the model.
        :param model_desc: The model description.
        """
        onnx_model = None
        featurizer_onnx_model = None
        estimator_onnx_model = None
        err = None
        if self.is_onnx_compatible:
            err_log_level = logging.ERROR
        else:
            err_log_level = logging.WARNING
        try:
            msg_obj = {
                'Info': 'Model conversion started.',
                'IsOnnxCompatibleMode': self.is_onnx_compatible
            }

            self._logger_wrapper(logging.INFO, evt_name=OnnxConvertConstants.EvtConvert,
                                 status=OnnxConvertConstants.StatusStart,
                                 model_name=model_name, model_desc=model_desc,
                                 message=msg_obj)
            # Check the Python version, now onnx package only supports < 3.8.
            _raise_exception_if_python_ver_doesnot_support_onnx()

            # Check if the input is initialized or not.
            if not self.is_initialized():
                raise OnnxConvertException("initialize_input() must be called before convert the model.")
            # Validate the model.
            self._validate_raw_model(raw_model)

            # Convert. We retry the convert for 3 times to improve success rate.
            # This is needed since sometimes there's random issue in dependent packages, when loading
            # the sklearn/lightgbm model object in memory.
            num_retried = 0
            err_inner = None
            while num_retried < self._retry_count:
                try:
                    # Prepare the pipeline with original model objects.
                    pipe = self._reconstruct_pipeline_by_extracting_inner_models(raw_model)
                    onnx_model, featurizer_onnx_model, estimator_onnx_model = self._convert(
                        pipe, model_name, model_desc)
                except Exception as inner_e:
                    if num_retried < self._retry_count - 1:
                        stack_trace = self._get_stack_trace_msg()
                        err_inner = {
                            'Info': 'Converting Model encountered error, retrying.',
                            'Class': inner_e.__class__.__name__,
                            'ErrorMsg': "[Scrubbed]",
                            'IsOnnxCompatibleMode': self.is_onnx_compatible,
                            'StackTrace': stack_trace
                        }
                        # Retrying, fire a warning event.
                        self._logger_wrapper(err_log_level, evt_name=OnnxConvertConstants.EvtConvert,
                                             status=OnnxConvertConstants.StatusWarning,
                                             model_name=model_name, model_desc=model_desc,
                                             message=err_inner)
                    else:
                        # Let the outter cache handle the error in the last retry.
                        raise inner_e
                finally:
                    if err_inner is None:
                        break
                    num_retried = num_retried + 1

        except Exception as e:
            err = {
                'Info': 'Failed to convert Model.',
                'Class': e.__class__.__name__,
                'ErrorMsg': "[Scrubbed]",
                'RawModelString': "[Scrubbed]",
                'IsOnnxCompatibleMode': self.is_onnx_compatible,
                'StackTrace': self._get_stack_trace_msg()
            }
            if self.is_onnx_compatible:
                err_st = OnnxConvertConstants.StatusError
            else:
                err_st = OnnxConvertConstants.StatusWarning
            self._logger_wrapper(err_log_level, evt_name=OnnxConvertConstants.EvtConvert,
                                 status=err_st,
                                 model_name=model_name, model_desc=model_desc, message=err)
            pass
        finally:
            msg_obj = {'IsOnnxCompatibleMode': self.is_onnx_compatible}
            status = None
            if err is None:
                msg_obj['Info'] = 'Model conversion succeeded.'
                status = OnnxConvertConstants.StatusEndSucceeded
            else:
                msg_obj['Info'] = 'Model conversion failed.'
                status = OnnxConvertConstants.StatusEndFailed
                # Reset the model resource if conversion failed.
                self._reset_onnx_model_res()
            self._logger_wrapper(logging.INFO, evt_name=OnnxConvertConstants.EvtConvert,
                                 status=status,
                                 model_name=model_name, model_desc=model_desc,
                                 message=msg_obj)
        return onnx_model, featurizer_onnx_model, estimator_onnx_model, err

    def get_converted_onnx_model_resource(self) -> Dict[Any, Any]:
        """Get the resource of the converted ONNX model."""
        return self._last_converted_onnx_model_res_dict

    @staticmethod
    def save_onnx_model(onnx_model: onnx_proto.ModelProto, file_path: str) -> None:
        """
        Save an ONNX model to a ProtoBuf object binary file.

        :param model: ONNX model
        :param file_path: ONNX file (full file name)
        """
        _raise_exception_if_python_ver_doesnot_support_onnx()
        if onnx_model is None or not isinstance(onnx_model, onnx_proto.ModelProto):
            raise ValueError("Model is not a valid ONNX model.")
        directory = os.path.dirname(os.path.abspath(file_path))
        if not path.exists(directory):
            raise FileNotFoundError("Directory does not exist {0}".format(directory))
        with open(file_path, 'wb') as f:
            f.write(onnx_model.SerializeToString())

    @staticmethod
    def save_onnx_model_to_text_file(onnx_model: onnx_proto.ModelProto, file_path: str) -> None:
        """
        Save the ONNX model in text format.

        :param model: ONNX model (object)
        :param file_path: the path including file name to save the model
        """
        _raise_exception_if_python_ver_doesnot_support_onnx()
        if onnx_model is None or not isinstance(onnx_model, onnx_proto.ModelProto):
            raise ValueError("Model is not a valid ONNX model.")
        with open(file_path, "w") as f:
            f.write(str(onnx_model))

    @staticmethod
    def load_onnx_model(file_path: str) -> onnx_proto.ModelProto:
        """
        Load the binary format ONNX model.

        :param file_path: the path including file name to save the model
        :return: the loaded onnx model object.
        """
        _raise_exception_if_python_ver_doesnot_support_onnx()
        abs_path = os.path.abspath(file_path)
        if not path.exists(abs_path):
            raise FileNotFoundError("File does not exist {0}".format(file_path))

        return onnx.load(abs_path)

    # ----------------------------------------------------------------
    # 'Private' methods.
    # -----------------------------
    # Initialization phase methods.
    def _convert_np_to_onnx_type(self, tp_str):
        if tp_str == NumericalDtype.Floating or tp_str == NumericalDtype.MixedIntegerFloat:
            return FloatTensorType
        elif tp_str == NumericalDtype.Integer:
            return Int64TensorType
        elif tp_str in DatetimeDtype.FULL_SET or \
                tp_str == TextOrCategoricalDtype.String or \
                tp_str == TextOrCategoricalDtype.Categorical or \
                tp_str == NumericalDtype.Decimal or \
                tp_str == OnnxConvertConstants.Boolean or \
                tp_str == OnnxConvertConstants.Mixed:
            return StringTensorType
        else:
            raise OnnxConvertException("Unsupported data type for converting to ONNX.")

    def _setup_init_metadata(self):
        self._init_phase_metadata = self._InitPhaseMetadata(
            ini_types=self.init_phase_initial_types,
            ini_tp_to_infer_type_map=self.idx_indiv_ini_tp_to_infer_type_map,
            ini_tp_to_input_df_col_map=self.idx_indiv_ini_tp_to_input_df_column_map,
            df_col_to_df_col_idx_in_input=self.df_column_to_df_col_idx_in_input,
            if_input_data_has_col_name=self._if_input_data_has_column_name,
            if_model_can_use_batch_mode=self._if_model_can_use_batch_mode
        )

    # -----------------------------
    # Conversion phase methods.
    def _preprocess(self, pipe):
        # If the model contains ensemble estimator, we need to register
        # onnxmltools shape calculator and our own converter, for the lightgbm model.
        # Note, with one given Python model, this only needs to be done once,
        # since we check if the final estimator is an ensemble estimator.
        ensemble_estimator = self._check_and_get_ensemble_estimator(pipe._final_estimator)
        if ensemble_estimator is not None:
            self.operator_manager._register_lightgbm_converter_for_ensemble_conversion()
        self._reset_onnx_model_res()
        self._python_model_contains_xgboost_estimator = False
        self._trans_contain_ct_tfidf_vectorizer = False

        # Suppress the logging in skl2onnx.
        skl2onnx_logger = logging.getLogger('skl2onnx')
        skl2onnx_logger.propagate = False
        skl2onnx_logger.disabled = True

    def _postprocess(self, onnx_model, featurizer_onnx_model, estimator_onnx_model):
        # Signature of the models.
        self._post_process_setup_onnx_model_signature(onnx_model)
        self._post_process_setup_onnx_model_signature(featurizer_onnx_model)
        self._post_process_setup_onnx_model_signature(estimator_onnx_model)

        self._python_model_contains_xgboost_estimator = False
        self._trans_contain_ct_tfidf_vectorizer = False
        # Restore to default converters.
        self.operator_manager._register_default_converters_for_lightgbm()

        # Reset the logging in skl2onnx.
        skl2onnx_logger = logging.getLogger('skl2onnx')
        skl2onnx_logger.propagate = True
        skl2onnx_logger.disabled = False

    def _post_process_setup_onnx_model_signature(self, onnx_model):
        if onnx_model is not None:
            onnx_model.producer_name = OnnxConvertConstants.OnnxModelProducer
            onnx_model.producer_version = self.producer_version

    def _reset_onnx_model_res(self):
        self._last_converted_onnx_model_res_dict = {}

    def _validate_raw_model(self, raw_model):
        if raw_model is None:
            raise OnnxConvertException('Null raw model passed in!')
        if not isinstance(raw_model, Pipeline):
            raise OnnxConvertException('Invalid raw model type.')

    def _reconstruct_pipeline_by_extracting_inner_models(self, raw_model):
        # Reset the input data feed mode to initialization mode for this conversion.
        self._last_converted_model_can_use_batch_mode = self._if_model_can_use_batch_mode
        # Construct a new pipeline with extracted inner models (which are inside model wrappers).
        steps_of_inner_mdl = []  # type: List[Tuple[str, Any]]
        self._setup_inner_model_steps_for_pipeline(raw_model, steps_of_inner_mdl)
        pipe = Pipeline(steps_of_inner_mdl)
        if isinstance(raw_model, PipelineWithYTransformations):
            pipe = PipelineWithYTransformations(pipeline=pipe,
                                                y_trans_name=raw_model.y_transformer_name,
                                                y_trans_obj=raw_model.y_transformer)
        return pipe

    def _setup_inner_model_steps_for_pipeline(self, raw_model, steps_of_inner_mdl):
        # Recursively parse the steps in the pipeline with extracted inner models.
        # If the model is a model wrapper, extract the inner model.
        # If the model is a pipeline, recusive call this method.
        for step in raw_model.steps:
            if step is not None:
                step_name = step[0]
                model_obj = step[1]

                # Parse the inner pipeline object that is one of the steps in
                # the outer pipeline.
                if isinstance(model_obj, Pipeline):
                    self._setup_inner_model_steps_for_pipeline(model_obj, steps_of_inner_mdl)
                else:
                    # If the step is a model wrapper, get inner model object.
                    if isinstance(model_obj, _AbstractModelWrapper):
                        if isinstance(model_obj, NBWrapper):
                            # If the model is a NBWrapper, the converted ONNX model cannot accept
                            # the Batch input, since the NativeBayes converter relies on the
                            # shape[0] to be a integer, where batch mode we will use the symbolic
                            # dimension.
                            self._last_converted_model_can_use_batch_mode = False
                        self._extract_model_wrapper(step_name, model_obj, steps_of_inner_mdl)
                    else:
                        if self._if_estimator_contains_knn(model_obj):
                            # If the model is or it's inner pipelines contains a KNN Classifier or KNN regressor,
                            # the converted ONNX model cannot accept the Batch input,
                            # since the skl2onnx converter applies broadcast to the Sub op.
                            self._last_converted_model_can_use_batch_mode = False
                        steps_of_inner_mdl.append((step_name, model_obj))

    def _extract_model_wrapper(self, name, wrapper, steps_of_inner_mdl):
        inner_model = wrapper.get_model()
        if isinstance(inner_model, _AbstractModelWrapper):
            self._extract_model_wrapper(name, inner_model, steps_of_inner_mdl)
        elif isinstance(inner_model, Pipeline):
            self._setup_inner_model_steps_for_pipeline(inner_model, steps_of_inner_mdl)
        else:
            steps_of_inner_mdl.append((name, inner_model))

    def _if_estimator_contains_knn(self, model_obj):
        if isinstance(model_obj, KNeighborsClassifier) or isinstance(model_obj, KNeighborsRegressor):
            return True

        # Check if the object is an ensemble estimator.
        ensemble_estimator = self._check_and_get_ensemble_estimator(model_obj)
        if ensemble_estimator is not None:
            is_classification = False
            if type(ensemble_estimator) == PreFittedSoftVotingClassifier:
                is_classification = True

            if is_classification:
                estimators = ensemble_estimator.estimators_
            else:
                estimators = ensemble_estimator._wrappedEnsemble.estimators_

            for est in estimators:
                if isinstance(est, Pipeline):
                    for step_est in est.steps:
                        est_obj = step_est[1]
                        if isinstance(est_obj, KNeighborsClassifier) or isinstance(est_obj, KNeighborsRegressor):
                            return True
        return False

    def _convert(self, model, model_name, model_desc):
        target_opset = OnnxConvertConstants.CurrentOnnxOPSetVersion
        onnx_model = None
        featurizer_onnx_model = None
        estimator_onnx_model = None

        # Preprocess. Setup and register correct converters to the skl2onnx package.
        self._preprocess(model)
        onnx_model = self._convert_whole_model(model=model,
                                               model_name=model_name,
                                               model_desc=model_desc,
                                               target_opset=target_opset)
        if self._enable_split_onnx_featurizer_estimator_models:
            # Note: if conversion of split models fails, the entire method will raise exception.
            # This means that if this method succeeds, and user set this config to true,
            # all the 3 models will be successfully converted.
            # There's no possibility that only the whole model conversion succeeds and saved to the output but
            # the split onnx models failed to be converted and saved.
            featurizer_onnx_model, estimator_onnx_model = self._convert_split_models(model=model,
                                                                                     model_name=model_name,
                                                                                     model_desc=model_desc,
                                                                                     target_opset=target_opset)

        # Postprocess.
        self._postprocess(onnx_model, featurizer_onnx_model, estimator_onnx_model)
        return onnx_model, featurizer_onnx_model, estimator_onnx_model

    def _convert_whole_model(self, model, model_name, model_desc, target_opset):
        # Parse scikit-learn model to generate the topology.
        topology = self._parse_model(model, target_opset)

        # Infer variable shapes.
        self._compile_model(topology)

        # Convert our Topology object into ONNX.
        if isinstance(model_desc, dict):
            desc_str = json.dumps(model_desc)
        else:
            desc_str = str(model_desc)
        onnx_model = convert_topology(topology=topology,
                                      model_name=model_name,
                                      doc_string=desc_str,
                                      target_opset=OnnxConvertConstants.CurrentOnnxOPSetVersion)

        return onnx_model

    def _convert_split_models(self, model, model_name, model_desc, target_opset):
        featurizer_onnx_model = None
        estimator_onnx_model = None
        trans = self._get_data_transformer(model)
        if trans is None:
            # Do nothing if there's no data transformer.
            self._logger_wrapper(logging.WARNING, evt_name=OnnxConvertConstants.EvtConvert,
                                 status=OnnxConvertConstants.StatusWarning,
                                 model_name=model_name, model_desc=model_desc,
                                 message='No data transformer in the raw pipeline,'
                                         'ignored the conversion of featurizer and estimator models.')
            return featurizer_onnx_model, estimator_onnx_model

        # Convert the featurizer/data transformer part of the pipeline to onnx model.
        featurizer_output_vars = None
        featurizer_onnx_model, featurizer_output_vars = self._convert_featurizer_model(model=model,
                                                                                       model_name=model_name,
                                                                                       model_desc=model_desc,
                                                                                       target_opset=target_opset)

        # Convert the estimator part of the pipeline to onnx model.
        estimator_onnx_model = self._convert_estimator_model(model=model,
                                                             model_name=model_name,
                                                             model_desc=model_desc,
                                                             target_opset=target_opset,
                                                             featurizer_output_vars=featurizer_output_vars)

        return featurizer_onnx_model, estimator_onnx_model

    def _convert_featurizer_model(self, model, model_name, model_desc, target_opset):
        # Clone the raw model and remove the steps after the data transformer (scaler and the estimator).
        featurizer_model = self._get_featurizer_pipeline(model)

        # Parse scikit-learn model to generate the topology.
        topology = self._parse_model(model=featurizer_model,
                                     target_opset=target_opset,
                                     ignore_onnx_resource=True)

        # Infer variable shapes.
        self._compile_model(topology)

        # Record the output variables.
        # It will be used as the conversion phase initial input types for converting the estimator model.
        featurizer_output_vars = self._get_featurizer_output_variables(topology)

        # Convert our Topology object into ONNX.
        if isinstance(model_desc, dict):
            desc_str = json.dumps(model_desc)
        else:
            desc_str = str(model_desc)
        mdl_name = "{}_{}".format(model_name, SplitOnnxModelName.FeaturizerOnnxModel.name)
        featurizer_onnx_model = convert_topology(topology=topology,
                                                 model_name=mdl_name,
                                                 doc_string=desc_str,
                                                 target_opset=OnnxConvertConstants.CurrentOnnxOPSetVersion)

        return featurizer_onnx_model, featurizer_output_vars

    def _convert_estimator_model(self, model, model_name, model_desc, target_opset,
                                 featurizer_output_vars):
        # Generate the conversion phase initial types based on the output var of featurizer model (step).
        self.conversion_phase_initial_types = self._get_estimator_conversion_phase_initial_types(
            featurizer_output_vars=featurizer_output_vars)
        # Clone the raw model and remove the data transformer step.
        estimator_model = self._get_estimator_pipeline(model)

        # Parse scikit-learn model to generate the topology.
        # We use the above conversion phase initial types which is generated from the output var of
        # the featurizer model, and ignore the setup of them in parse model method.
        topology = self._parse_model(model=estimator_model,
                                     target_opset=target_opset,
                                     ignore_onnx_resource=True,
                                     ignore_initial_types_setup=True)

        # Infer variable shapes.
        self._compile_model(topology)

        # Convert our Topology object into ONNX.
        if isinstance(model_desc, dict):
            desc_str = json.dumps(model_desc)
        else:
            desc_str = str(model_desc)
        mdl_name = "{}_{}".format(model_name, SplitOnnxModelName.EstimatorOnnxModel.name)
        estimator_onnx_model = convert_topology(topology=topology,
                                                model_name=mdl_name,
                                                doc_string=desc_str,
                                                target_opset=OnnxConvertConstants.CurrentOnnxOPSetVersion)

        return estimator_onnx_model

    def _get_featurizer_pipeline(self, original_pipe):
        # The model in the 1st step must be a data transformer.
        # We use the 1st step of the original pipeline to construct the featurizer pipe.
        data_transformer_step = original_pipe.steps[0]
        assert isinstance(data_transformer_step[1], DataTransformer)
        steps = [data_transformer_step]
        # For the featurizer onnx model conversion, we ignore if the original
        # pipeline is a y transform pipeline or not, we use a simple pipeline.
        featurizer_pipe = Pipeline(steps)
        return featurizer_pipe

    def _get_estimator_pipeline(self, original_pipe):
        # We remove the 1st step of the original pipeline to construct the featurizer pipe.
        estimator_steps = original_pipe.steps[1:]
        estimator_pipe = Pipeline(estimator_steps)
        # For the estimator pipeline we need to construct the y trans pipeline if the original
        # is a y trans pipe.
        if isinstance(original_pipe, PipelineWithYTransformations):
            estimator_pipe = PipelineWithYTransformations(pipeline=estimator_pipe,
                                                          y_trans_name=original_pipe.y_transformer_name,
                                                          y_trans_obj=original_pipe.y_transformer)
        return estimator_pipe

    def _get_featurizer_output_variables(self, topology):
        final_concatenator_op = None
        for operator in topology.scopes[0].operators.values():
            if operator.onnx_name.startswith(DataTransformerFeatureConcatenatorConverter.OPERATOR_ALIAS):
                final_concatenator_op = operator
                break
        # There must be one feature concatenator op.
        assert final_concatenator_op is not None
        return final_concatenator_op.outputs

    def _get_estimator_conversion_phase_initial_types(self, featurizer_output_vars):
        initial_types = []
        for var in featurizer_output_vars:
            initial_types.append((var.raw_name, var.type))
        return initial_types

    # -----------------------------
    # Model parsing methods.
    def _setup_initial_types_based_on_model(self, model):
        trans = self._get_data_transformer(model)
        # Copy the original initial_types, since it will be used in multiple conversions.
        init_phase_types_cpy = copy.deepcopy(self.init_phase_initial_types)
        if not self._last_converted_model_can_use_batch_mode:
            # We need to replace the shape of initial types with Per-Record datafeed mode.
            for _, onnx_tp in init_phase_types_cpy:
                onnx_tp.shape = [1, 1]

        if trans is not None:
            # Need to check if the dataframe mapper has a valid build_default,
            # if not, we erase those input columns that are not used(selected) in our transformer.
            self.conversion_phase_initial_types = []
            if self._get_is_built_default(trans):
                new_idx = 0
                for idx_indi_ini_types, input_var in enumerate(init_phase_types_cpy):
                    df_column = self.idx_indiv_ini_tp_to_input_df_column_map[idx_indi_ini_types]
                    infer_dtype = self.idx_indiv_ini_tp_to_infer_type_map[idx_indi_ini_types]
                    self.conversion_phase_initial_types.append(input_var)
                    self.df_column_to_selected_initial_types_idx[df_column] = new_idx
                    self.idx_selected_initial_type_to_infer_dtype_map[new_idx] = infer_dtype
                    new_idx = new_idx + 1
            else:
                self.conversion_phase_initial_types = init_phase_types_cpy
                self.df_column_to_selected_initial_types_idx = self.df_column_to_df_col_idx_in_input
                self.idx_selected_initial_type_to_infer_dtype_map = self.idx_indiv_ini_tp_to_infer_type_map
        else:
            self.conversion_phase_initial_types = init_phase_types_cpy
            self.idx_selected_initial_type_to_infer_dtype_map = self.idx_indiv_ini_tp_to_infer_type_map

    def _get_data_transformer(self, model):
        trans = None
        for step in model.steps:
            if isinstance(step[1], DataTransformer):
                trans = step[1]
                break
        return trans

    def _if_model_contains_xgboost_estimator(self, model):
        if _xgboost_present:
            # Check each step of the model pipeline, if any estimator is XGBoost classifier or regressor,
            # we return true.
            for step_inner in model.steps:
                mdl_obj = step_inner[1]
                if isinstance(mdl_obj, DataTransformer):
                    continue
                elif type(mdl_obj) in _sklearn_supported_operators.sklearn_operator_name_map:
                    if isinstance(mdl_obj, XGBClassifier) or isinstance(mdl_obj, XGBRegressor):
                        return True
                else:
                    # Check if it's a ensemble estimator.
                    ensemble_estimator = self._check_and_get_ensemble_estimator(mdl_obj)
                    if ensemble_estimator is not None:
                        # Check the ensemble estimator.
                        if type(ensemble_estimator) == PreFittedSoftVotingClassifier:
                            estimators = ensemble_estimator.estimators_
                        else:
                            estimators = ensemble_estimator._wrappedEnsemble.estimators_

                        # Check the inner estimators of the ensemble.
                        for _, estimator in enumerate(estimators):
                            if estimator is None:
                                continue
                            if isinstance(estimator, Pipeline):
                                # Reconstruct the pipeline with inner models inside the wrapper objects.
                                pipe = self._reconstruct_pipeline_by_extracting_inner_models(estimator)

                                # Check the inner pipeline inside the inner estimator.
                                for step_inner in pipe.steps:
                                    if step_inner is not None:
                                        mdl_obj_inner = step_inner[1]
                                        if (isinstance(mdl_obj_inner, XGBClassifier)
                                                or isinstance(mdl_obj_inner, XGBRegressor)):
                                            return True
                            else:
                                if isinstance(estimator, XGBClassifier) or isinstance(estimator, XGBRegressor):
                                    return True

        return False

    def _if_transformer_contains_countvectorizer_tfidfvectorizer(self, dt):
        for _, transformers, _ in self._get_built_features(dt):
            if not isinstance(transformers, TransformerPipeline):
                raise OnnxConvertException("transformers object in DataFrameMapper has wrong type!")

            # Iterate each step inside the transformer pipeline to check the actual transformer.
            for j, trans_step in enumerate(transformers.steps):
                transformer = trans_step[1]
                # Get the inner transformer object if it's a model wrapper.
                if isinstance(transformer, _AbstractModelWrapper):
                    transformer = transformer.get_model()
                if isinstance(transformer, CountVectorizer) or isinstance(transformer, TfidfVectorizer):
                    return True

        return False

    def _add_missing_val_replacement_processor(self, scope, inputs):
        # If the model contains the xgboost estimator and the data transformer contains the
        # CountVectorizer or the TfidfVectorizer, we apply the missing value replacement ops.
        missing_val_repl_op = scope.declare_local_operator(
            MissingValReplaceProcessorConverter.OPERATOR_ALIAS)
        missing_val_repl_op.inputs = inputs
        missing_val_repl_out_name = scope.get_unique_variable_name('missing_val_repl_op_out')
        missing_val_repl_output = scope.declare_local_variable(missing_val_repl_out_name, FloatTensorType())
        missing_val_repl_op.outputs.append(missing_val_repl_output)
        return missing_val_repl_op.outputs

    def _parse_model(self, model, target_opset, ignore_onnx_resource=False,
                     ignore_initial_types_setup=False):
        if not ignore_initial_types_setup:
            # Setup the initial types after parsing the model operators.
            self._setup_initial_types_based_on_model(model)

        # Init the model container.
        raw_model_container = SklearnModelContainerNode(model)

        # Declare a computational graph.
        topology = Topology(
            raw_model_container, initial_types=self.conversion_phase_initial_types, target_opset=target_opset)

        # Declare an scope to provide variables' and operators' naming mechanism.
        scope = topology.declare_scope('__root__')

        # Declare input variables and init the dictionaries in onnx resource.
        inputs = []
        idx_ini_tp = 0
        input_raw_name_to_onnx_name_map = {}
        input_raw_schema = {}
        input_onnx_schema = {}
        var_name = None  # type: Optional[Any]
        initial_type = None  # type: Optional[Any]
        for var_name, initial_type in self.conversion_phase_initial_types:
            var = scope.declare_local_variable(var_name, initial_type)
            inputs.append(var)
            if not ignore_onnx_resource and self._if_input_data_has_column_name:
                input_raw_name_to_onnx_name_map[var.raw_name] = var.onnx_name
                input_raw_schema[var.raw_name] = self.idx_selected_initial_type_to_infer_dtype_map[idx_ini_tp]
                ini_tp_str = type(initial_type).__name__
                input_onnx_schema[var.onnx_name] = ini_tp_str
            idx_ini_tp = idx_ini_tp + 1

        # Init the onnx resource of this conversion.
        if not ignore_onnx_resource:
            # Add the input raw column name to onnx name map to the resource.
            res_key = OnnxConvertConstants.RawColumnNameToOnnxNameMap
            self._last_converted_onnx_model_res_dict[res_key] = input_raw_name_to_onnx_name_map
            # Add the raw and onnx input schema to the resource.
            res_key = OnnxConvertConstants.InputRawColumnSchema
            self._last_converted_onnx_model_res_dict[res_key] = input_raw_schema
            res_key = OnnxConvertConstants.InputOnnxColumnSchema
            self._last_converted_onnx_model_res_dict[res_key] = input_onnx_schema
            res_key = OnnxConvertConstants.CanEnableBatchMode
            self._last_converted_onnx_model_res_dict[res_key] = self._last_converted_model_can_use_batch_mode

        # Store input vars in the container. Later they will be used when
        # converting the computational graph (the topology obj).
        for variable in inputs:
            raw_model_container.add_input(variable)

        # Parse the input scikit-learn model as a Topology object.
        outputs = self._parse_pipeline_steps(scope, model, inputs)

        # Store output vars in the container.
        for variable in outputs:
            raw_model_container.add_output(variable)

        return topology

    def _compile_model(self, topology):
        topology._prune()
        topology._resolve_duplicates()
        topology._fix_shapes()
        topology._infer_all_types()

    def _parse_pipeline_steps(self, scope, model, inputs):
        # Iterate all the steps of the pipeline to build the topology.
        # - For the 1st step DataTransformer, parse the inner data frame
        #   mapper, built features, and inner pipeline/steps for each column.
        # - For later steps returned by miro, call normal single step parsing
        #   method in the onnxmltool.
        is_y_trans_pipe = False
        if isinstance(model, PipelineWithYTransformations):
            is_y_trans_pipe = True
        is_final_estimator_classifier = False
        if isinstance(model._final_estimator, ClassifierMixin):
            is_final_estimator_classifier = True

        # Check if the model contains a XGBoost estimator.
        # If it's already true it means during converting the whole onnx model it has detected the xgboost
        # estimator, we still use this state during converting the featurizer and estimator parts of the ONNX
        # models, since for featurizer part the given python model doesn't contain estimator.
        if self._python_model_contains_xgboost_estimator is False:
            self._python_model_contains_xgboost_estimator = self._if_model_contains_xgboost_estimator(model)

        # Parse the inputs if there's no data transformer in the pipeline.
        transformer = self._get_data_transformer(model)
        if transformer is None:
            inputs = self._preprocess_for_non_transformer_pipeline(scope, inputs)

        for step in model.steps:
            mdl_obj = step[1]
            if isinstance(mdl_obj, DataTransformer):
                inputs = self._parse_data_transformer(scope,
                                                      mdl_obj,
                                                      inputs,
                                                      self._python_model_contains_xgboost_estimator)
            elif type(mdl_obj) in _sklearn_supported_operators.sklearn_operator_name_map:
                # If this step is an xgboost estimator, and the data transformer contains count/tfidf vectorizer,
                # And the model contains xgboost estimator, we add the missing value replacement.
                if self._trans_contain_ct_tfidf_vectorizer and self._python_model_contains_xgboost_estimator and (
                    isinstance(mdl_obj, XGBClassifier) or isinstance(mdl_obj, XGBRegressor)
                ):
                    inputs = self._add_missing_val_replacement_processor(scope, inputs)
                if model._final_estimator == mdl_obj and is_final_estimator_classifier and is_y_trans_pipe:
                    # We use our own classifier parser if the model is a y trans pipeline.
                    inputs = self._parse_classifier(scope, mdl_obj, inputs)
                else:
                    inputs = _sklearn_parse.parse_sklearn(scope, mdl_obj, inputs)
            else:
                # Check if it's an IdentityTransformer.
                is_identity_trans = self._is_identity_transformer(mdl_obj)
                # Check if it's a ensemble estimator.
                ensemble_estimator = self._check_and_get_ensemble_estimator(mdl_obj)
                if ensemble_estimator is not None:
                    # Parse the ensemble estimator.
                    inputs = self._parse_ensemble_estimator(scope, ensemble_estimator, inputs)
                elif is_identity_trans:
                    # The variables pass through the IdentityTransformer, no need to convert.
                    inputs = self._dummy_parse(scope, mdl_obj, inputs)
                else:
                    raise OnnxConvertException("model object is not supported for ONNX conversion!")

        # If the pipeline is a PipelineWithYTransformations, parse the last step of y transform model.
        if is_y_trans_pipe:
            y_trans = model.y_transformer
            if isinstance(y_trans, LabelEncoder):
                # Parse the y transformer.
                inputs = self._parse_y_transformer(scope, y_trans, inputs)

        return inputs

    def _get_built_features(self, dt):
        if dt.mapper:
            return dt.mapper.built_features
        else:
            build_features = []
            for tm in dt.transformer_and_mapper_list:
                build_features += tm.mapper.built_features
            return build_features

    def _get_is_built_default(self, dt):
        if dt.mapper:
            return dt.mapper.built_default is None or dt.mapper.built_default is False
        else:
            for tm in dt.transformer_and_mapper_list:
                if tm.mapper.built_default is None or tm.mapper.built_default is False:
                    return True
            return False

    def _parse_data_transformer(self, scope, dt, inputs, model_contains_xgboost_estimator):
        concat_output = None

        if not dt._is_onnx_compatible:
            raise OnnxConvertException("transformer is not ONNX compatible")

        assert (len(inputs) == len(self.conversion_phase_initial_types))

        # Check if there's CountVectorizer or TfidfVectorizer in the data transformer,
        # if so, and if the whole model contains the xgboost estimator,
        # we need to apply the missing value replacement ops to change 0 value to Nan,
        # otherwise the converted xgboost estimator will loss this info and produce wrong inference result.
        if model_contains_xgboost_estimator:
            self._trans_contain_ct_tfidf_vectorizer = self._if_transformer_contains_countvectorizer_tfidfvectorizer(dt)

        df_mapper_selected_column_indicies = set()
        # For each input column, we treat it as an variable.
        # For each column's transformers, create corresponding op, and link
        # them to this column's output var.
        output_vars_of_last_op_in_each_col = []
        for columns, transformers, _ in self._get_built_features(dt):
            # Ignore built_features that contains any unsupported ops.
            unsupported_mdl_type = self._get_unsupported_model_type(transformers)
            if unsupported_mdl_type is not None:
                raise OnnxConvertException(
                    "Transformer object {0} are not supported for ONNX conversion.".format(str(unsupported_mdl_type)))
            if isinstance(columns, list):
                columns = columns[0]

            # The column index of intial_types is mapped from the original column index of
            # the user's original X. Note, some of the columns can be dropped by the data transformer.
            initial_types_idx = self.df_column_to_selected_initial_types_idx[columns]

            # Add the col index (int) to selected set.
            df_mapper_selected_column_indicies.add(initial_types_idx)
            input_var = inputs[initial_types_idx]
            assert (input_var is not None)
            if not isinstance(transformers, TransformerPipeline):
                raise OnnxConvertException("transformers object in DataFrameMapper has wrong type!")

            op_out = None
            # Iterate each step inside the transformer pipeline, they are the
            # actual ops our preprocessor/featurizer uses (e.g. Imputer, CatImputer, etc).
            for j, trans_step in enumerate(transformers.steps):
                transformer = trans_step[1]
                # Get the inner transformer object if it's a model wrapper.
                if isinstance(transformer, _AbstractModelWrapper):
                    transformer = transformer.get_model()

                trans_op = scope.declare_local_operator(
                    _sklearn_parse._get_sklearn_operator_name(type(transformer)), transformer)
                trans_op.inputs.append(input_var)
                var_out_name = 'variable_c' + str(initial_types_idx) + '_t' + str(j)
                # The default output type is float tensor, if needed, the shape
                # calculator will change this later.
                op_out = scope.declare_local_variable(var_out_name, FloatTensorType())
                trans_op.outputs.append(op_out)

                # Link this op's output to next op's input.
                input_var = op_out

            # Record all the output variable names of each column's last op.
            output_vars_of_last_op_in_each_col.append(op_out)

        inputs_of_concatenator = output_vars_of_last_op_in_each_col

        # Add those columns which are not used/transformed by the transformer
        # to the tail of the inputs of cancatenator.
        if not self._get_is_built_default(dt):
            # This is the same behavior of the DataFrameMapper.
            for idx, input_var in enumerate(inputs):
                if idx not in df_mapper_selected_column_indicies:
                    inputs_of_concatenator.append(input_var)

        # Concat the output variables of each column's final operator into one tensor.
        concat_op = scope.declare_local_operator(DataTransformerFeatureConcatenatorConverter.OPERATOR_ALIAS)
        concat_op.inputs = inputs_of_concatenator
        concat_out_name = scope.get_unique_variable_name('variable_all_trans_op_out_concated')
        concat_output = scope.declare_local_variable(concat_out_name, FloatTensorType())
        concat_op.outputs.append(concat_output)

        # Return the output vars of the concatenator.
        return concat_op.outputs

    def _preprocess_for_non_transformer_pipeline(self, scope, inputs):
        if len(inputs) > 1:
            # Concat the input variables of each column's final operator into one tensor.
            concat_op = scope.declare_local_operator(DataTransformerFeatureConcatenatorConverter.OPERATOR_ALIAS)
            concat_op.inputs = inputs
            concat_out_name = scope.get_unique_variable_name('variable_all_inputs_concated')
            concat_output = scope.declare_local_variable(concat_out_name, FloatTensorType())
            concat_op.outputs.append(concat_output)

            # Return the output vars of the concatenator.
            return concat_op.outputs
        else:
            # Do nothing if only 1 input var.
            return inputs

    def _parse_ensemble_estimator(self, scope, ensemble_estimator, inputs):
        # Parse the ensemble estimator models with below steps:
        # 1. Process all the inner estimators, link the inputs parameter to
        #    all the estimator model/pipelines.
        #    1.2. If the inner estimator is a pipeline:
        #       - Reconstruct the pipeline with inner models.
        #       - If the ensemble estimator is a classifier:
        #         * Call sklearn parse method to parse the n-1 inner steps in the
        #           pipeline.
        #         * Store the last step, later use our own parse method to parse it.
        #           NOTE:
        #           We don't want the sklearn parse method to generate the zipmap
        #           probability output var, but we link the last step output to the
        #           later concatenator, and generate our own zipmap probability out
        #           var later.
        #       - Else it's a regressor, call sklearn parse to parse all steps.
        #    1.3. If the inner estimator is a single model,
        #         * If it's a classifier:
        #         Do nothing here, store objects.
        #         Store the last step, later use our own parse method to parse it.
        #         * Else it's a regressor, call sklearn parse to parse all steps.
        # 2. Parse the last step of each classifier stored above, using our own
        #    classifier parser.
        #    This parse method will not generate the ZipMap probability output var,
        #    but it outputs a simple tensor prob var.
        # 3. Get all outputs (including step 2) of each pipeline or single model,
        #    based on type of estimator (classifier or reggresor).
        # 4. Create a virtual ensemble op, store the actual ensemble estimator.
        #    4.1. Link the step 3 outputs to this op's input.
        #    4.2. Init the output variables based on type of estimator.
        #    4.3. Link the final outputs to it's output.
        #
        # The virtual ensemble op is used for calculate shapes of variables and finally convert
        # the actual ensemble operation into ONNX ops.
        ensemble_outputs = None
        err_msg = None
        # Get the problem type of the ensemble estimator (classification or regression).
        # Note, the ensemble object and all it's inner estimators must have same problem type.
        is_classification = False
        if type(ensemble_estimator) == PreFittedSoftVotingClassifier:
            is_classification = True
            assert (ensemble_estimator._estimator_type != "regressor")
        else:
            # This must be the regressor.
            assert (type(ensemble_estimator) == PreFittedSoftVotingRegressor)

        outputs_of_estimators = {}
        classifier_last_steps = {}
        # 1. Process all the inner estimators.
        if is_classification:
            estimators = ensemble_estimator.estimators_
        else:
            estimators = ensemble_estimator._wrappedEnsemble.estimators_
        for idx_est, estimator in enumerate(estimators):
            # Save the current estimator outputs.
            cur_est_outputs = None
            if estimator is None:
                continue
            # 1.2. If the inner estimator is a pipeline:
            if isinstance(estimator, Pipeline):
                # Reconstruct the pipeline with inner models.
                pipe = self._reconstruct_pipeline_by_extracting_inner_models(estimator)

                steps_to_parse = []  # type: List[Any]
                if is_classification:
                    # If the ensemble estimator is a classifier:
                    # Call parse sklearn to parse the [0, n-1] inner steps in the pipeline.
                    if len(pipe.steps) > 1:
                        steps_to_parse = pipe.steps[0:-1]
                    # Store the last step estimator, later use our own parse method to parse it.
                    classifier_last_steps[idx_est] = pipe.steps[-1][1]
                else:
                    # Else it's a regressor, call sklearn parse to parse ALL steps.
                    steps_to_parse = pipe.steps

                # Parse steps.
                pipe_step_inputs = inputs
                for step in steps_to_parse:
                    if step is not None:
                        mdl_obj = step[1]
                        is_identity_trans = self._is_identity_transformer(mdl_obj)
                        if type(mdl_obj) in _sklearn_supported_operators.sklearn_operator_name_map:
                            # Check if this step is a xgboost regressor.
                            if (
                                self._trans_contain_ct_tfidf_vectorizer
                                and self._python_model_contains_xgboost_estimator
                                and isinstance(mdl_obj, XGBRegressor)
                            ):
                                pipe_step_inputs = self._add_missing_val_replacement_processor(scope, pipe_step_inputs)
                            pipe_step_inputs = _sklearn_parse.parse_sklearn(scope, mdl_obj, pipe_step_inputs)
                        elif is_identity_trans:
                            # The variables pass through the IdentityTransformer, no need to convert.
                            pipe_step_inputs = self._dummy_parse(scope, mdl_obj, pipe_step_inputs)
                        else:
                            # There should not be other types.
                            err_msg = ("model object inside ensemble estimator inner pipeline "
                                       "is not supported for ONNX conversion! The model: ")
                            err_msg += str(mdl_obj)
                            break

                cur_est_outputs = pipe_step_inputs
            else:
                # 1.3. If it's a single model, call parse sklearn to get the outputs.
                # If the inner estimator is a classifier:
                if is_classification:
                    # Do nothing here, store objects.
                    # Store the single model, later use our own parse method to parse it.
                    classifier_last_steps[idx_est] = estimator
                    # The first inputs (passed in method parameter) is stored to cur estimator output.
                    cur_est_outputs = inputs
                else:
                    # Else it's a regressor, call sklearn parse to parse all steps.
                    is_identity_trans = self._is_identity_transformer(estimator)
                    if type(estimator) in _sklearn_supported_operators.sklearn_operator_name_map:
                        # Check if this step is a xgboost regressor.
                        if (
                            self._trans_contain_ct_tfidf_vectorizer
                            and self._python_model_contains_xgboost_estimator
                            and isinstance(estimator, XGBRegressor)
                        ):
                            inputs = self._add_missing_val_replacement_processor(scope, inputs)
                        cur_est_outputs = _sklearn_parse.parse_sklearn(scope, estimator, inputs)
                    elif is_identity_trans:
                        # The variables pass through the IdentityTransformer.
                        cur_est_outputs = inputs
                    else:
                        # There should not be other types.
                        err_msg = ("model object inside ensemble estimator "
                                   "is not supported for ONNX conversion! The model: ")
                        err_msg += str(estimator)
                        break

            # Store the output vars from the last step in pipe, or from the single model.
            outputs_of_estimators[idx_est] = cur_est_outputs
        if err_msg is not None:
            raise OnnxConvertException(err_msg)

        # 2. Parse the last step of each classifier, using our own classifier parser.
        for idx_est, estimator in classifier_last_steps.items():
            # Get the stored last step outputs.
            last_step_inputs = outputs_of_estimators[idx_est]
            # Check if this estimator is a xgboost classifier.
            if (
                self._trans_contain_ct_tfidf_vectorizer
                and self._python_model_contains_xgboost_estimator
                and isinstance(estimator, XGBClassifier)
            ):
                last_step_inputs = self._add_missing_val_replacement_processor(scope, last_step_inputs)
            last_step_inputs = self._parse_classifier(scope, estimator, last_step_inputs)
            # Replace the outputs of this estimator with this outputs.
            outputs_of_estimators[idx_est] = last_step_inputs

        # 3. Get all outputs of each pipeline or single model, concat them,
        #    based on type of the ensemble estimator (classifier or reggresor).
        all_outputs = []
        for idx_est, out_vars_one_est in outputs_of_estimators.items():
            if is_classification:
                # There are 2 output vars output by sklearn parser,
                # we use the 2nd probability var.
                all_outputs.append(out_vars_one_est[1])
            else:
                # There's only 1 output var for regressor.
                all_outputs.append(out_vars_one_est[0])

        # 4. Create a virtual ensemble op, store the actual ensemble estimator,
        #    based on type of estimator (classifier or reggresor)
        # 4.1. Init the output variables.
        if is_classification:
            virtual_ensemble_op = scope.declare_local_operator(PrefittedVotingClassifierConverter.OPERATOR_ALIAS)
            label_variable = scope.declare_local_variable('label_out', FloatTensorType())
            probability_tensor_variable = scope.declare_local_variable('probabilities_out', FloatTensorType())
            virtual_ensemble_op.outputs.append(label_variable)
            virtual_ensemble_op.outputs.append(probability_tensor_variable)
            virtual_ensemble_op.raw_operator = ensemble_estimator
        else:
            virtual_ensemble_op = scope.declare_local_operator(PrefittedVotingRegressorConverter.OPERATOR_ALIAS)
            virtual_ensemble_out_name = scope.get_unique_variable_name('variable_out')
            virtual_ensemble_output = scope.declare_local_variable(virtual_ensemble_out_name, FloatTensorType())
            virtual_ensemble_op.outputs.append(virtual_ensemble_output)
            # Add the inner wrapped ensemble object to the raw operator, which is a PreFittedSoftVotingClassifier.
            virtual_ensemble_op.raw_operator = ensemble_estimator._wrappedEnsemble

        # Link the step 3 outputs to this op's input.
        virtual_ensemble_op.inputs = all_outputs

        # 4.2. Link the final outputs to it's input.
        ensemble_outputs = virtual_ensemble_op.outputs

        return ensemble_outputs

    def _parse_classifier(self, scope, model, inputs):
        alias = _sklearn_parse._get_sklearn_operator_name(type(model))
        this_operator = scope.declare_local_operator(alias, model)
        this_operator.inputs = inputs

        # For classifiers, we may have two outputs, one for label and the other one for probabilities of all classes.
        # Notice that their types here are not necessarily correct and they will be fixed in shape inference phase
        label_variable = scope.declare_local_variable('label', FloatTensorType())
        probability_tensor_variable = scope.declare_local_variable('probabilities', FloatTensorType())
        this_operator.outputs.append(label_variable)
        this_operator.outputs.append(probability_tensor_variable)

        return this_operator.outputs

    def _parse_y_transformer(self, scope, y_transformer, inputs):
        y_trans_op = scope.declare_local_operator(YTransformerLabelEncoderConverter.OPERATOR_ALIAS, y_transformer)
        # Link the final estimator output of former operators generated by skl2onnx/onnxmltools or ourself.
        # The classifier operators has 2 outputs, the 1st one is the label.
        # The regressor ops only has 1 output var.
        in_vars = inputs

        y_trans_op.raw_operator = y_transformer
        y_trans_op.inputs = in_vars
        y_trans_out_name = scope.get_unique_variable_name('output_label')
        y_trans_output = scope.declare_local_variable(y_trans_out_name, FloatTensorType())
        y_trans_op.outputs.append(y_trans_output)

        if len(inputs) > 0:
            prob_name = scope.get_unique_variable_name('output_probabity')
            prob_output = scope.declare_local_variable(prob_name, FloatTensorType())
            y_trans_op.outputs.append(prob_output)

        return y_trans_op.outputs

    def _dummy_parse(self, scope, model, inputs):
        # We do nothing but pass through the inputs as output variables.
        return inputs

    # -----------------------------
    # Utility methods.
    def _check_and_get_ensemble_estimator(self, mdl_obj):
        # Ensemble estimator objects are not instanciated by the pipeline spec,
        # this causes that the object has different type (the obj.__class__),
        # and especially different __module__.
        # An easy solution is to create another object and copy all properties.
        res = None
        if any(m in mdl_obj.__class__.__module__ for m in SOURCE_WRAPPER_MODULES):
            est_cls = PreFittedSoftVotingClassifier  # type: Any
            if est_cls.__name__ == mdl_obj.__class__.__name__:
                cl_obj = est_cls(
                    estimators=mdl_obj.estimators,
                    weights=mdl_obj.weights,
                    flatten_transform=mdl_obj.flatten_transform
                )
                # Explicitly set these attributes.
                cl_obj.estimators_ = mdl_obj.estimators_
                cl_obj.le_ = mdl_obj.le_
                cl_obj.classes_ = mdl_obj.classes_
                return cl_obj
            est_cls = PreFittedSoftVotingRegressor
            if est_cls.__name__ == mdl_obj.__class__.__name__:
                if sklearn.__version__ >= '0.21.0':
                    cl_obj = est_cls(
                        estimators=mdl_obj._wrappedEnsemble.estimators,
                        weights=mdl_obj._wrappedEnsemble.weights
                    )
                    return cl_obj
                else:
                    cl_obj = est_cls(
                        estimators=mdl_obj._wrappedEnsemble.estimators,
                        weights=mdl_obj._wrappedEnsemble.weights,
                        flatten_transform=mdl_obj._wrappedEnsemble.flatten_transform
                    )
                    return cl_obj

        return res

    def _is_identity_transformer(self, mdl_obj):
        return isinstance(mdl_obj, IdentityTransformer)

    def _get_unsupported_model_type(self, transformers):
        for trans_step in transformers.steps:
            mdl = trans_step[1]
            if isinstance(mdl, _AbstractModelWrapper):
                mdl = mdl.get_model()
            if type(mdl) not in _sklearn_supported_operators.sklearn_operator_name_map:
                return type(mdl)

        return None

    def _logger_wrapper(self, level, evt_name, status, model_name, model_desc, message):
        try:
            log_evt = {
                'Module': OnnxConvertConstants.LoggingTagPrefix,
                'Event': evt_name,
                'Status': status,
                'ModelName': model_name,
                'ModelDesc': model_desc,
                'Message': message
            }
            msg = json.dumps(log_evt)
            logger.log(level, msg)
        except Exception:
            # Make sure the logging method won't throw any exceptions.
            return

    def _get_stack_trace_msg(self):
        traceback_obj = sys.exc_info()[2]
        if traceback_obj is not None:
            stack_trace = _CustomStackSummary.get_traceback_message(traceback_obj)
        else:
            stack_trace = 'Not available (exception was not raised but was returned directly)'
        return stack_trace

    @staticmethod
    def get_onnx_metadata(
            X: DataInputType,
            x_raw_column_names: Optional[np.ndarray] = None
    ) -> Optional[Dict[str, Any]]:
        """
        given the training data, generate metadata needed for ONNX conversion

        :param X: Input data.

        :return: A metadata dictionary used by ONNX conversion.
        """
        onnx_cvt = OnnxConverter()

        onnx_cvt.initialize_input(X=X, x_raw_column_names=x_raw_column_names)

        return onnx_cvt.get_init_metadata_dict()

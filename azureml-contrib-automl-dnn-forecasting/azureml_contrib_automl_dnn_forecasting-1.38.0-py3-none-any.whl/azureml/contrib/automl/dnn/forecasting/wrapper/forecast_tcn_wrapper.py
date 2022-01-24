# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module for creating a model based on TCN."""
import argparse
import datetime
import math
import os
import sys
import logging
from typing import List, Optional, Tuple
import numpy as np
import pandas as pd
import torch

from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared.reference_codes import ReferenceCodes
import azureml.automl.runtime.featurizer.transformer.timeseries as automl_transformer
from azureml.automl.runtime.shared.model_wrappers import ForecastingPipelineWrapper
from azureml.automl.core.shared.exceptions import ClientException
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    ExperimentTimedOut,
    IterationTimedOut,
    TCNWrapperRuntimeError)
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.shared.limit_function_call_exceptions import TimeoutException
from azureml.automl.runtime.featurizer.transformer.timeseries.timeseries_transformer import TimeSeriesTransformer
from azureml.contrib.automl.dnn.forecasting.wrapper._distributed_helper import DistributedHelper
from azureml.contrib.automl.dnn.forecasting.wrapper import _wrapper_util
from azureml.core.run import Run
from azureml.train.hyperdrive.run import HyperDriveRun
import azureml.automl.core   # noqa: F401
from torch.utils.data.dataloader import DataLoader
from .forecast_wrapper import DNNForecastWrapper, DNNParams
from .tcn_model_utl import build_canned_model
from ..constants import ForecastConstant, TCNForecastParameters
from ..callbacks.run_update import RunUpdateCallback
from ..callbacks.distributed_epoch_shuffler import DistributedEpochShufflerCallback

from ..datasets.timeseries_datasets import TimeSeriesDataset, EmbeddingColumnInfo
from ..datasets.timeseries_datasets_utils import create_timeseries_datasets
from ..metrics.primary_metrics import get_supported_metrics
from ..types import DataInputType
from forecast.callbacks.callback import MetricCallback
from forecast.callbacks.optimizer import (  # noqa: F401
    EarlyStoppingCallback, ReduceLROnPlateauCallback,
    PreemptTimeLimitCallback
)
from forecast.data.batch_transforms import (
    BatchFeatureTransform,
    BatchSubtractOffset,
    FeatureTransform,
    GenericBatchTransform,
)
from forecast.data.sources.data_source import DataSourceConfig
from forecast.forecaster import Forecaster
from forecast.losses import QuantileLoss
from forecast.models import ForecastingModel
from forecast.utils import create_timestamped_dir
from torch.utils.data.distributed import DistributedSampler
import warnings


try:
    import horovod.torch as hvd
except ModuleNotFoundError:
    hvd = None


logger = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stderr)
handler.setLevel(logging.INFO)
logger.addHandler(handler)

# If the remaining time is less than a minute, we will
# raise the timeout exception.
REMAINING_TIME_TOLERANCE = pd.Timedelta(minutes=1)


class ForecastTCNWrapper(DNNForecastWrapper):
    """Wrapper for TCN model adapted to work with automl Forecast Training."""

    required_params = [ForecastConstant.Learning_rate, ForecastConstant.Lookback,
                       ForecastConstant.Batch_size, ForecastConstant.num_epochs, ForecastConstant.Loss,
                       ForecastConstant.Device, ForecastConstant.primary_metric]
    loss = QuantileLoss(ForecastConstant.QUANTILES)
    default_params = {ForecastConstant.Loss: loss,  # torch.distributions.StudentT,
                      ForecastConstant.Device: 'cuda' if torch.cuda.is_available() else 'cpu'}
    # configure our loss function

    def __init__(self) -> None:
        """Construct the new instance of ForecastTCNWrapper."""
        super().__init__()

    def train(self, n_epochs: int, X: DataInputType = None, y: DataInputType = None,
              X_train: DataInputType = None, y_train: DataInputType = None,
              X_valid: DataInputType = None, y_valid: DataInputType = None,
              featurizer: TimeSeriesTransformer = None) -> None:
        """
        Start the DNN training.

        :param n_epochs: number of epochs to try.
        :param X: data for training.
        :param y: target data for training.
        :param X_train: training data to use.
        :param y_train: training target to use.
        :param X_valid: validation data to use.
        :param y_valid: validation target to use.
        :param featurizer: trained featurizer.
        :param automl_settings: dictionary of automl settings
        """
        settings = self.automl_settings
        assert(ForecastConstant.primary_metric in self.automl_settings)
        num_samples = 0
        ds = None
        ds_train = None
        ds_valid = None
        run_update_callback = None
        self._pre_transform = featurizer
        horizon, _ = self._get_metadata_from_featurizer()
        self.params.set_parameter(ForecastConstant.Horizon, horizon)
        if X_train is None:
            X_train = X
            y_train = y

        ds = create_timeseries_datasets(X_train,
                                        y_train,
                                        X_valid,
                                        y_valid,
                                        horizon,
                                        1,
                                        True,
                                        False,
                                        True,
                                        **settings)
        dset_config = ds.dset_config

        sample_epoch_setter_callback = DistributedEpochShufflerCallback()

        if self.forecaster is None:
            run_update_callback = self._create_runupdate_callback()
            # set the grain info if embedding is needed from the model
            embedding_col_infos = ds.embedding_col_infos
            self._build_model_forecaster(run_update_callback, dset_config, embedding_col_infos,
                                         sample_epoch_setter_callback)
        # set the lookback as the receptive field of the model for the dataset
        ds.set_lookback(self.forecaster.model.receptive_field)
        # store history with the model to use later for inference that comes with out history.
        self._data_for_inference = ds.get_last_lookback_items()

        num_samples = len(ds.dataset)
        # set the transformations used along with the wrapper, so can be used during validation and inference.
        self.set_transforms(ds.dataset.feature_count(), ds.dataset.sample_transform)
        ds_train, ds_valid = ds.ds_train, ds.ds_valid

        if run_update_callback is not None:
            run_update_callback.set_evaluation_dataset(ds_train, ds_valid)

        fraction_samples = math.floor(num_samples * 0.05)
        if fraction_samples <= 1:
            batch_size = 1
        else:
            batch_size = int(math.pow(2, math.floor(math.log(fraction_samples, 2)))) \
                if fraction_samples < 1024 else 1024
        while True:
            Contract.assert_true(batch_size > 0,
                                 "Cannot proceed with batch_size: {}".format(batch_size), log_safe=True)
            try:
                logger.info("Trying with batch_size: {}".format(batch_size))
                train_data_sampler = self._get_data_sampler(ds_train, True)
                if train_data_sampler:
                    shuffle = False
                    sample_epoch_setter_callback.set_sampler(train_data_sampler)
                else:
                    # when train sampler exists, manages the shuffle otherwise shuffle should be true
                    shuffle = True
                dataloader_train = self.create_data_loader(ds_train, shuffle, batch_size=batch_size,
                                                           sampler=train_data_sampler, drop_last=True)
                dataloader_valid = self.create_data_loader(ds_valid, False, batch_size=batch_size)
                self.forecaster.fit(
                    dataloader_train=dataloader_train,
                    loss=self.loss,
                    optimizer=self.optimizer,
                    epochs=n_epochs,
                    dataloader_val=dataloader_valid)
                break
            except RuntimeError as e:
                if 'out of memory' in str(e):
                    logger.info("Couldn't allocate memory for batch_size: {}".format(batch_size))
                    batch_size = batch_size // 2
                else:
                    raise ClientException._with_error(
                        AzureMLError.create(
                            TCNWrapperRuntimeError, target="TCNWrapper",
                            reference_code=ReferenceCodes._TCN_WRAPPER_RUNTIME_ERROR,
                            inner_exception=e)) from e

        self.batch_size = batch_size

        # Reset the distributed optimizer.
        # (The optimizer is no longer needed since trainng has completed. Also, the optimizer may not be
        # serializable, which is needed when saving the model.)
        self.optimizer = None

        # At the end of the training upload the tabular metric and model.
        if run_update_callback is not None:
            run_update_callback.upload_model_and_tabular_metrics()

    def _get_data_sampler(self, ds: TimeSeriesDataset, shuffle: bool = True) -> Optional[DistributedSampler]:
        """Build a distributed sampler for a dataset."""
        if hvd is None:
            return None
        return DistributedSampler(ds, num_replicas=hvd.size(), rank=hvd.rank(), shuffle=shuffle)

    def _create_runupdate_callback(self) -> RunUpdateCallback:
        # Only instantiate the callbaack to update the run from the master node. This ensures that
        # only one worker uploads the model, metrics, run properties, etc.
        if not DistributedHelper.is_master_node():
            return None
        return RunUpdateCallback(
            model_wrapper=self, run_context=Run.get_context(), params=self.params, featurizer=self._pre_transform)

    def _raise_timeout_err(self, ref_code: str, experiment_timeout: bool = True) -> None:
        """
        Raise the timeout error.

        :param ref_code: the reference code to use for raised exception.
        :param experiment: If True, the ExperimentTimedOut,
                           otherwise IterationTimedOut will be raised.
        :raises: TimeoutException.
        """
        raise TimeoutException._with_error(
            AzureMLError.create(
                ExperimentTimedOut if experiment_timeout else IterationTimedOut,
                target="DNN child run",
                reference_code=ref_code
            ))

    def _build_model_forecaster(self, run_update_callback: RunUpdateCallback,
                                dset_config: DataSourceConfig,
                                embedding_column_info: List[EmbeddingColumnInfo],
                                sample_epoch_setter_callback: DistributedEpochShufflerCallback) -> None:
        logger.info('Building model')
        # create a model based on the hyper parameters.
        model = build_canned_model(params=self.params, dset_config=dset_config,
                                   horizon=self.params.get_value(ForecastConstant.Horizon),
                                   num_quantiles=len(ForecastConstant.QUANTILES),
                                   embedding_column_info=embedding_column_info)

        device = self.params.get_value(ForecastConstant.Device)
        model = model.to(device)
        # checkpoint directory to save model state.
        chkpt_base = create_timestamped_dir('./chkpts')
        out_dir = create_timestamped_dir(chkpt_base)
        model.to_json(os.path.join(out_dir, 'model_arch.json'))

        # set callbacks.
        lr = self.params.get_value(ForecastConstant.Learning_rate, 0.001)
        self.optimizer = torch.optim.Adam(model.parameters(), lr=lr)
        if hvd is not None:
            self.optimizer = hvd.DistributedOptimizer(
                self.optimizer, named_parameters=model.named_parameters(), compression=hvd.Compression.fp16)
            hvd.broadcast_parameters(model.state_dict(), root_rank=0)
            hvd.broadcast_optimizer_state(self.optimizer, root_rank=0)

        # number epochs to wait before early stopping evaluation start.
        self.patience = self.params.get_value(TCNForecastParameters.EARLY_STOPPING_DELAY_STEPS,
                                              TCNForecastParameters.EARLY_STOPPING_DELAY_STEPS_DEFAULT)
        # learning rate reduction with adam optimizer
        self.lr_factor = self.params.get_value(TCNForecastParameters.LR_DECAY_FACTOR,
                                               TCNForecastParameters.LR_DECAY_FACTOR_DEFAULT)
        lr_sched = torch.optim.lr_scheduler.ReduceLROnPlateau(self.optimizer, patience=int(self.patience / 2),
                                                              factor=self.lr_factor)
        # minimum improvement from the previous epoch to continue experiment, we are using relative improvement.
        self.min_improvement = self.params.get_value(TCNForecastParameters.EARLY_STOPPING_MIN_IMPROVEMENTS,
                                                     TCNForecastParameters.EARLY_STOPPING_MIN_IMPROVEMENTS_DEFAULT)
        # metric to use for early stopping.
        metric = self.primary_metric
        if metric not in get_supported_metrics():
            metric = ForecastConstant.DEFAULT_EARLY_TERM_METRIC
            logger.warn(f'Selected primary metric is not supported for early stopping, using {metric} instead')

        # metric object that computes the training and validation metric
        train_valid_metrics = {metric: get_supported_metrics()[metric]}
        callbacks = [
            MetricCallback(train_valid_metrics, train_valid_metrics),
            # LR reduction was performing with loss metric than any of the custom metric specified.
            ReduceLROnPlateauCallback(lr_sched, ForecastConstant.Loss),
            EarlyStoppingCallback(patience=self.patience, min_improvement=self.min_improvement, metric=metric),
        ]

        if run_update_callback is not None:
            callbacks.append(run_update_callback)
        if hvd is not None and sample_epoch_setter_callback:
            callbacks.append(sample_epoch_setter_callback)

        # Get the remaining time for this experiment.
        run_obj = Run.get_context()
        hd_run_obj = None
        # Handle the situation, when run_obj is _OfflineRun.
        if hasattr(run_obj, 'parent'):
            hd_run_obj = run_obj.parent
        if isinstance(hd_run_obj, HyperDriveRun):
            # Calculate the end time in UTC time zone.
            start_time = pd.Timestamp(hd_run_obj._run_dto['start_time_utc'])
            end_time = start_time + pd.Timedelta(
                minutes=hd_run_obj.hyperdrive_config._max_duration_minutes)
            if (end_time - pd.Timestamp.now(tz=start_time.tzinfo)) < REMAINING_TIME_TOLERANCE:
                self._raise_timeout_err(ReferenceCodes._TCN_HD_RUN_TIMEOUT)
            preempt_callback = PreemptTimeLimitCallback(
                end_time=end_time.to_pydatetime())
            callbacks.append(preempt_callback)
            logger.info(f'Start time: {hd_run_obj._run_dto["start_time_utc"]}, '
                        f'latest permissible end time: {end_time.to_pydatetime()}')

        logger.info(f'the name of the metric used EarlyStoppingCallback {metric}')
        logger.info(f'The patience used in used EarlyStoppingCallback {self.patience}')
        logger.info(f'the name of the improvement passed to EarlyStoppingCallback {self.min_improvement}')
        logger.info(f'LR Factor {self.lr_factor}')
        label_index = 0
        label_log_tranform = FeatureTransform(label_index, self._log, self._exp)
        feature_transforms = BatchFeatureTransform(past_regressand=label_log_tranform,
                                                   future_regressand=label_log_tranform)
        batch_transform = GenericBatchTransform(feature_transforms=feature_transforms,
                                                subtract_offset=BatchSubtractOffset(label_index),
                                                )
        self.batch_transform = batch_transform

        # set up the model for training.
        self.forecaster = Forecaster(model=model,
                                     device=device,
                                     metrics=train_valid_metrics,
                                     callbacks=callbacks,
                                     batch_transform=batch_transform)

    def predict(self, X: DataInputType, y: DataInputType, n_samples: int = 1) -> np.ndarray:
        """
        Return the predictions for the passed in `X` and `y` values.

        :param X: data values.
        :param y: label for look back and nan for the rest.
        :param n_samples: number of samples to be returned with each prediction.
        :return: numpy ndarray with shape (n_samples, n_rows, horizon).
        """
        X, y = _wrapper_util.convert_X_y_to_pandas(X, y)
        assert(ForecastConstant.primary_metric in self.automl_settings)
        if y is None:
            y = pd.DataFrame([None] * X.shape[0])
        time_column = self.automl_settings[ForecastConstant.time_column_name]
        grains = None
        if ForecastConstant.automl_constants.TimeSeries.GRAIN_COLUMN_NAMES in self.automl_settings:
            grains = self.automl_settings[ForecastConstant.automl_constants.TimeSeries.GRAIN_COLUMN_NAMES]
        grains_list = grains if grains else []
        X, y = ForecastingPipelineWrapper.static_preaggregate_data_set(self._pre_transform, time_column,
                                                                       grains_list, X, y)
        X, y = _wrapper_util.transform_data(self._pre_transform, X, y)
        ds = self._get_timeseries(X, y)
        return self._predict(ds).reshape(-1)

    def _get_metadata_from_featurizer(self) -> Tuple[int, str]:
        """Get metadata from the trained featurizer."""
        max_horizon = self._pre_transform.max_horizon

        grain_feature_col_prefix = None
        grain_index_featurizer = [a[1] for a in self._pre_transform.pipeline.steps
                                  if isinstance(a[1], automl_transformer.GrainIndexFeaturizer)]
        if grain_index_featurizer:
            grain_feature_col_prefix = grain_index_featurizer[0].grain_feature_prefix + \
                grain_index_featurizer[0].prefix_sep

        return max_horizon, grain_feature_col_prefix

    def _get_timeseries(self, X: DataInputType, y: DataInputType, step: str = None) -> TimeSeriesDataset:
        """
        Get timeseries for given inputs and set_lookback for model.

        :param X: data values
        :param y: label for lookback and nan for rest
        :param n_samples: number of samples to be returned with each prediction.
        :param step: number of samples to skip to get to the next block of data(lookback+horzon)
        :return: Timeseries dataset
        """
        if step is None:
            step = self.params.get_value(ForecastConstant.Horizon)
        X_df, y_df = _wrapper_util.convert_X_y_to_pandas(X, y)
        ds = TimeSeriesDataset(X_df,
                               y_df,
                               horizon=self.params.get_value(ForecastConstant.Horizon),
                               step=step,
                               has_past_regressors=True,
                               one_hot=False,
                               sample_transform=self._sample_transform,
                               **self.automl_settings)
        ds.set_lookback(self.forecaster.model.receptive_field)
        return ds

    def _predict(
            self,
            ds: Optional[TimeSeriesDataset] = None,
            n_samples: int = 1,
            data_loader: Optional[DataLoader] = None) -> np.ndarray:
        """
        Return the predictions for the passed timeseries dataset.

        :param ds: TimeSeriesDataset to use for prediction.
        :param n_samples:  number of samples to be returned with each prediction.
        :param data_loader: the data loader to use for prediction.
        :return: numpy ndarray with shape (n_samples, n_rows, horizon).
        """
        if data_loader is None:
            data_loader = self.create_data_loader(ds, False)

        predictions = np.asarray(self.forecaster.predict(data_loader))
        # Currently returning only one prediction: median
        return_predict_index = predictions.shape[0] // 2
        return predictions[return_predict_index:return_predict_index + 1]

    def get_lookback(self):
        """Get lookback used by model."""
        if self.forecaster is not None:
            return self.forecaster.model.receptive_field
        else:
            return self.params.get_value(ForecastConstant.Lookback)

    @property
    def name(self):
        """Name of the Model."""
        return ForecastConstant.ForecastTCN

    def parse_parameters(self) -> DNNParams:
        """
        Parse parameters from command line.

        return: returns the  DNN  param object from the command line arguments
        """
        parser = argparse.ArgumentParser()

        parser.add_argument(DNNForecastWrapper.get_arg_parser_name(ForecastConstant.num_epochs), type=int,
                            default=25, help='number of epochs to train')
        parser.add_argument(DNNForecastWrapper.get_arg_parser_name(ForecastConstant.Lookback), type=int,
                            default=8, help='lookback for model')
        parser.add_argument(DNNForecastWrapper.get_arg_parser_name(ForecastConstant.Horizon), type=int,
                            default=4, help='horizon for prediction')
        parser.add_argument(DNNForecastWrapper.get_arg_parser_name(ForecastConstant.Batch_size), type=int,
                            default=8, help='batch_size for training')
        parser.add_argument(DNNForecastWrapper.get_arg_parser_name(ForecastConstant.primary_metric), type=str,
                            default='', help='primary metric for training')

        # Model hyper-parameters
        parser.add_argument(DNNForecastWrapper.get_arg_parser_name(ForecastConstant.Learning_rate), type=float,
                            default=0.001, help='learning rate')
        parser.add_argument(DNNForecastWrapper.get_arg_parser_name(TCNForecastParameters.NUM_CELLS), type=int,
                            help='num cells')
        parser.add_argument(DNNForecastWrapper.get_arg_parser_name(TCNForecastParameters.MULTILEVEL), type=str,
                            help='multilevel')
        parser.add_argument(DNNForecastWrapper.get_arg_parser_name(TCNForecastParameters.DEPTH), type=int,
                            help='depth')
        parser.add_argument(DNNForecastWrapper.get_arg_parser_name(TCNForecastParameters.NUM_CHANNELS), type=int,
                            help='number of channels')
        parser.add_argument(DNNForecastWrapper.get_arg_parser_name(TCNForecastParameters.DROPOUT_RATE), type=float,
                            help='dropout rate')
        parser.add_argument(DNNForecastWrapper.get_arg_parser_name(TCNForecastParameters.DILATION), type=int,
                            default=TCNForecastParameters.DILATION_DEFAULT, help='tcn dilation')

        # EarlyStopping Parameters
        parser.add_argument(DNNForecastWrapper.
                            get_arg_parser_name(TCNForecastParameters.EARLY_STOPPING_MIN_IMPROVEMENTS),
                            type=float,
                            default=TCNForecastParameters.EARLY_STOPPING_MIN_IMPROVEMENTS_DEFAULT,
                            help='min improvement required between epochs to continue training')
        parser.add_argument(DNNForecastWrapper.get_arg_parser_name(TCNForecastParameters.LR_DECAY_FACTOR),
                            type=float,
                            default=TCNForecastParameters.LR_DECAY_FACTOR_DEFAULT,
                            help='LR decay factor used in reducing Learning Rate by LR schedular.')

        # Embedding defaults
        parser.add_argument(DNNForecastWrapper.
                            get_arg_parser_name(TCNForecastParameters.MIN_GRAIN_SIZE_FOR_EMBEDDING),
                            type=int,
                            default=TCNForecastParameters.MIN_GRAIN_SIZE_FOR_EMBEDDING_DEFAULT,
                            help='min grain size to enable grain embedding')
        parser.add_argument(DNNForecastWrapper.
                            get_arg_parser_name(TCNForecastParameters.EMBEDDING_TARGET_CALC_TYPE),
                            type=str,
                            default=TCNForecastParameters.EMBEDDING_TARGET_CALC_TYPE_DEFAULT,
                            help='method to use when computing embedding output size')
        parser.add_argument(DNNForecastWrapper.
                            get_arg_parser_name(TCNForecastParameters.EMBEDDING_MULT_FACTOR),
                            type=float,
                            default=TCNForecastParameters.EMBEDDING_MULT_FACTOR_DEFAULT,
                            help='multiplaction factor to use output size when MULT method is selected')
        parser.add_argument(DNNForecastWrapper.
                            get_arg_parser_name(TCNForecastParameters.EMBEDDING_ROOT),
                            type=float,
                            default=TCNForecastParameters.EMBEDDING_ROOT_DEFAULT,
                            help='the number to use as nth root for output sise when ROOT method is selectd')

        args, unknown = parser.parse_known_args()
        arg_dict = vars(args)
        arg_dict[ForecastConstant.n_layers] = max(int(math.log2(args.lookback)), 1)
        dnn_params = DNNParams(ForecastTCNWrapper.required_params, arg_dict, ForecastTCNWrapper.default_params)
        return dnn_params

    def __getstate__(self):
        """
        Get state picklable objects.

        :return: state
        """
        state = super(ForecastTCNWrapper, self).__getstate__()
        state['model_premix_config'] = self.forecaster.model.premix_config
        state['model_backbone_config'] = self.forecaster.model.backbone_config
        state['model_head_configs'] = self.forecaster.model.head_configs
        state['model_channels'] = self.forecaster.model.channels
        state['model_depth'] = self.forecaster.model.depth
        state['model_dropout_rate'] = self.forecaster.model.dropout_rate
        state['model_state_dict'] = self.forecaster.model.state_dict()
        state['batch_transform'] = self.batch_transform
        return state

    def __setstate__(self, state):
        """
        Set state for object reconstruction.

        :param state: pickle state
        """
        super(ForecastTCNWrapper, self).__setstate__(state)
        model = ForecastingModel(state['model_premix_config'],
                                 state['model_backbone_config'],
                                 state['model_head_configs'],
                                 state['model_channels'],
                                 state['model_depth'],
                                 state['model_dropout_rate'])
        model.load_state_dict(state['model_state_dict'])
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.batch_transform = state['batch_transform']
        self.forecaster = Forecaster(model=model,
                                     device=device,
                                     batch_transform=self.batch_transform)

    @staticmethod
    def _log(x: torch.Tensor):
        """
        Log natural log of the tensor used in batch transform in base forecaster package.

        :param x: the value to transform, which is the subset of feature[index]
        tensors based on index in feature transform.
        """
        return torch.log(1 + x)

    @staticmethod
    def _exp(x: torch.Tensor):
        """
        Exponential of the tensor used in batch transform in base forecaster package.

        :param x: the value to transform/reverse transform.
        """
        return torch.exp(x) - 1

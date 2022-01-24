# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
A class for training a TabNet model.
This expects a dataset that is a numpy array but has the preprocessed in the way that Tabnet Requires
1) categorical columns are label encoded and there are no new categories in test. These can be mapped to a new class.
2) continuous columns are standardized to 0 mean and 1 std, or apply_standard_scaler is True
3) classification targets are label encoded
4) Batch size is not too large for the GPU,  if using one
"""

import logging
import os
import time
from typing import Any, Optional, Tuple, Union

import numpy as np
import pandas as pd
import scipy.sparse
import torch
import torch.nn as nn

from sklearn.base import BaseEstimator, ClassifierMixin, RegressorMixin
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics import accuracy_score, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler, LabelEncoder

from azureml.automl.runtime.shared._tabularnetworks.model import AutoGluonTabularNN, TabNet, TabularNNConfig
from azureml.automl.runtime.shared._tabularnetworks.tabular_dataset import TabularDataset
from azureml.automl.runtime.shared._tabularnetworks.tabular_nn_constants import FEATURES, TARGET, SharedBlockTypes

logging.basicConfig(
    format="%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
    datefmt="%Y-%m-%d:%H:%M:%S",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


class NNTrainerBase(BaseEstimator):
    """Helper class that encapsulates helper functions to train a Tabular Network Model"""

    def __init__(
        self,
        random_state=0,
        n_jobs: int = 1,
        problem_info=None,
        class_weights: bool = False,
        num_steps: int = 4,
        hidden_features: int = 64,
        relaxation_factor: float = 1.2,
        block_depth: int = 4,
        embedding_dimension: Optional[int] = None,
        dropout: Optional[float] = None,
        residual: Optional[bool] = True,
        # optimization hyperparameters below,
        batch_size: int = 1024,
        epochs: int = 100,
        learning_rate: float = 0.01,
        learning_rate_decay: Optional[float] = 0.995,
        regularization_penalty: float = 1e-4,
        weight_decay: Optional[float] = None,
        loss: Optional[str] = None,
        apply_standard_scaler: Optional[bool] = True,
        truncated_svd_pct: Optional[float] = 0.25,
        shared_block_type: Optional[str] = SharedBlockTypes.FC,
        calculate_train_metrics: Optional[bool] = False,
    ):
        """
        Creates the NNTrainer
        Parameters
        ----------
        :param random_state:
            RandomState instance or None, optional (default=None)
            If int, random_state is the seed used by the random number
            generator.
            If RandomState instance, random_state is the random number
            generator.
            If None, the random number generator is the RandomState instance
            used by `np.random`.
        :type random_state: int or RandomState
        :param n_jobs: Number of parallel threads for dataloaders
        :type n_jobs: int
        class_weights: bool:
            whether or not to have balanced weights for all classes
        num_steps: int
            The number of decision steps in the model
        hidden_features: int
            The number of features within each decision step
        relaxation_factor: float
            Controls how many times a feature can be reused (lower --> less frequently reused)
        block_depth: int, optional
            The number of transforms within each decision step, defaults to 4
        embedding_dimension: int, optional
            The dimension of the embedding for categorical features. If none, recommended by the model.
        dropout: float, optional
            The dropout probability to use for dropout after fully connected layers
        residual: bool, optional
            Whether to include the side residual network
        batch_size: int, optional
            Number of data instances in a batch
        epochs: int, optional
            Number of full passes of the data to do during training
        learning_rate: float, optional
            Learning rate for the weights of the network
        learning_rate_decay:  float, optional
            Factor that learning rate gets decayed by at the end of every epoch
        regularization_penalty: float, optional
            Encourages sparsity in the attention
        weight_decay: float, optional
            Regulization for trainable weights
        loss: str, optional
            Pytorch loss function to use during training
        apply_standard_scaler: bool, optional
            whether to apply the standard scaler
        truncated_svd_pct: float, optional
            amount of original data size to keep in the case of sparse data
        shared_block_type: str, optional
            string indicating whether to use the default shared block or convolutional shared block
        calculate_train_metrics: bool, optional
            whether to calculate training metrics, takes time but can be helpful to know
        """
        super().__init__()
        self.fitted = False
        self.random_state = random_state
        self.n_jobs = n_jobs
        self.class_weights = class_weights
        self.params = {
            "num_steps": num_steps,
            "hidden_features": hidden_features,
            "pred_features": hidden_features // 2,
            "relaxation_factor": relaxation_factor,
            "block_depth": block_depth,
            "embedding_dimension": embedding_dimension,
            "dropout": dropout,
            "residual": residual,
            "shared_block_type": shared_block_type,
        }

        self.nn_model = None  # created during fit

        self.batch_size = batch_size
        self.epochs = epochs
        self.learning_rate = learning_rate
        self.learning_rate_decay = learning_rate_decay
        self.weight_decay = weight_decay
        self.regularization_penalty = regularization_penalty
        self.loss = loss

        self.trained_epoch = 0  # not trained yet
        self._val_scores = []
        self._train_scores = []
        self._val_metrics = []
        self._train_metrics = []
        self._early_stopping_iterations = max(min(9, 3 * epochs // 4), 3)
        self._grad_clip = 1
        self.tensorboard_logging = None
        self.apply_standard_scaler = apply_standard_scaler
        self.scaler = None
        self.truncated_svd_pct = truncated_svd_pct
        self._calculate_train_metrics = calculate_train_metrics

        self._update_problem_info(problem_info)

    def _update_problem_info(self, problem_info):
        self.problem_info = problem_info
        if (
            problem_info is not None
            and problem_info.gpu_training_param_dict is not None
            and problem_info.gpu_training_param_dict.get("processing_unit_type", "cpu") == "gpu"
            and torch.cuda.is_available()
        ):
            self.device = "cuda"  # support specifying the device
        else:
            self.device = "cpu"
        if (
            problem_info is not None
            and hasattr(problem_info, "runtime_constraints")
            and problem_info.runtime_constraints['wall_time_in_s'] is not None
        ):
            self.max_time = problem_info.runtime_constraints['wall_time_in_s']
        else:
            self.max_time = None
        self.params.update(
            {
                "input_features": problem_info.dataset_features if self.problem_info else None,
                "out_features": max(
                    self.problem_info.dataset_classes
                    if self.problem_info and self.problem_info.dataset_classes
                    else 2,
                    1,
                ),  # if regression use 1 not -1
                "categorical_features": self.problem_info.dataset_categoricals
                if self.problem_info and self.problem_info.dataset_categoricals is not None
                else None,
            }
        )

    def _create_optimizer_and_schedule(self):
        if self.weight_decay:
            optimizer_flags = {"weight_decay": self.weight_decay}
        else:
            optimizer_flags = {}
        self._optimizer = torch.optim.Adam(self.nn_model.parameters(), lr=self.learning_rate, **optimizer_flags)
        if self.learning_rate_decay:
            # steps the learning rate every epoch
            self._schedule = torch.optim.lr_scheduler.ExponentialLR(self._optimizer, self.learning_rate_decay)
        else:
            self._schedule = None

    def predict(
        self,
        X: np.ndarray,
        y: Optional[np.ndarray] = None,
        batch_size: Optional[int] = None,
        device: Optional[Union[str, torch.device]] = None,
        n_jobs: Optional[int] = None,
    ):
        """
        Generates a set of predictions on the given data
        :param X: Input data.
        :type X: numpy.ndarray
        :param y: Optional, Input target values.
        :type y: numpy.ndarray
        :param batch_size: Optional, if want to use a different batch size than during training
        :type batch_size: int
        :param device: str, if want to use a different device than during training
        :type device: str
        :param n_jobs: int, if want to use a different number of cpus for dataloading than during training
        :type n_jobs: int
        """
        if self.nn_model is None:
            logger.error("Trying to call predict on an untrained model")
            raise ValueError("Untrained Model")
        X, y_transformed, _, _ = self._prepare_data_for_dataloader(X, y, None, None)
        data = TabularDataset.from_numpy(X, y_transformed, label_dtype=self.get_label_dtype())
        batch_size = self.batch_size if batch_size is None else batch_size
        device = self.device if device is None else device
        if device != 'cpu' and not torch.cuda.is_available():
            device = 'cpu'
        n_jobs = self.n_jobs if n_jobs is None else n_jobs
        dl = torch.utils.data.DataLoader(
            data,
            batch_size=batch_size,
            shuffle=False,
            num_workers=self.n_jobs,
            pin_memory=device != "cpu",
        )
        predictions = self.predict_dataloader(dl, device=device, return_prob=False, return_targets=False)
        return predictions

    def get_params(self, deep=True):
        """
        Return parameters for the Tabnet model.

        :param deep: If True, returns the model parameters for sub-estimators as well. No effect.
        :return: Parameters for the Tabnet model.
        """
        return self.params

    def _fit_one_epoch_dataloader(self, dl: torch.utils.data.DataLoader, time_limit=1e9):
        self.nn_model.train()  # make sure the model is in training mode before fitting
        self.nn_model = self.nn_model.to(self.device)
        data_iter = iter(dl)
        start_time = time.time()
        for batch in range(len(data_iter)):
            if time.time() - start_time > time_limit:
                logger.warning("Exceeded Time Limit")
                return False
            self._optimizer.zero_grad()
            # get batch
            try:
                batch = next(data_iter)
            except StopIteration:
                continue
            inputs = batch[FEATURES].to(self.device)
            labels = batch[TARGET].to(self.device)
            output = self.nn_model(inputs)
            loss = self._calculate_loss(output, labels)
            loss.backward()
            # clip gradients by their norm
            if self._grad_clip:
                nn.utils.clip_grad_norm_(self.nn_model.parameters(), self._grad_clip)
            any_nans = False
            for p in self.nn_model.parameters():
                any_nans = any_nans or torch.any(torch.isnan(p.grad.data))
            if not any_nans and not torch.isnan(loss):
                self._optimizer.step()
            else:
                logger.warning("Skipping batch with nan error")
                # all batches will be nan after this
                return False
        if self._schedule is not None:
            self._schedule.step(self.trained_epoch)
        # step the learning rate
        self.trained_epoch += 1
        return True

    def _calculate_loss(self, output: Tuple[torch.Tensor, torch.Tensor], labels: [torch.Tensor]):
        return self._loss(output[0], labels) + output[1] * self.regularization_penalty

    def partial_fit(
        self,
        X: np.ndarray,
        y: np.ndarray,
        sample_weights: Optional[np.ndarray] = None,
        problem_info: Optional[Any] = None,
    ):
        """
        Partial Fit function for Tabnet.

        :param X: Input training data.
        :type X: numpy.ndarray
        :param y: Input target values.
        :type y: numpy.ndarray
        :param sample_weights: Input sample weights
        :type sample_weights: Input sample weights
        :param X_valid: Input valid data.
        :param problem_info: Optional, Any problem_info to tell model about dataset, only impacts first call
        :return: self: Returns an instance of self.
        :rtype: NNTrainerBase
        """

        # tabnet requires specific transformations, do them here if the dataset can be stored in memory
        if self.nn_model is None:
            self._prepare_model(y)
            if problem_info is not None:
                self._update_problem_info(problem_info)
        X, y_transformed, X_valid, y_valid_transformed = self._prepare_data_for_dataloader(X, y, None, None)

        if self.nn_model is None:
            if self.device != 'cpu' and not torch.cuda.is_available():
                self.device = 'cpu'
            self.params["input_features"] = X.shape[1]
            self.nn_model = self._build_nn_model().to(self.device)
            self._create_optimizer_and_schedule()
            self._loss = self._get_loss()
            self._loss = self._loss.to(self.device)

        train_dl, valid_dl = self._create_dataloaders(
            X,
            y_transformed,
            sample_weights,
            X_valid,
            y_valid_transformed,
        )
        self._fit_one_epoch_dataloader(train_dl)  # maybe don't want to step learning rate here but probably fine
        if self.device != "cpu":
            self.nn_model = self.nn_model.cpu()
        return self

    def _prepare_data_for_dataloader(
        self,
        X: np.ndarray,
        y: np.ndarray,
        X_valid: Optional[np.ndarray] = None,
        y_valid: Optional[np.ndarray] = None,
    ):
        y_transformed = self._transform_y(y)  # the first call calculates the mean and std of y
        if isinstance(X, pd.DataFrame):
            X = X.values
        X_return = X.copy()
        if self.scaler is None:
            if self.problem_info:
                self.numeric_columns = (
                    np.array(self.problem_info.dataset_categoricals) == 0
                    if self.problem_info.dataset_categoricals is not None
                    else np.ones(X_return.shape[1], dtype=bool)
                )
            else:
                logger.warning("Assuming no categorical columns since problem_info is not defined")
                self.numeric_columns = np.ones(X_return.shape[1], dtype=bool)
            if scipy.sparse.issparse(X):
                MAX_DIM = 500
                MIN_DIM = 2
                # may want to raise an error instead of trying
                logger.warning("Converting sparse data to dense with a truncated svd, may cause memory issues")
                # tabnet uses dense data (pytorch sparse support is not great)
                # probably shouldn't be used on tfidf text data
                recommended_shape = int(X.shape[1] * self.truncated_svd_pct)
                n_components = np.clip(recommended_shape, MIN_DIM, MAX_DIM)
                if self.numeric_columns is not None and self.numeric_columns.any():
                    self.scaler = make_pipeline(TruncatedSVD(n_components=n_components), StandardScaler())
                    self.scaler.fit(X_return[:, self.numeric_columns])
            else:
                if self.apply_standard_scaler:
                    if self.numeric_columns is not None and self.numeric_columns.any():
                        self.scaler = StandardScaler()
                        self.scaler.fit(X_return[:, self.numeric_columns])
        # scaler only exists if there are numeric columns
        if scipy.sparse.issparse(X):
            if self.scaler and self.numeric_columns is not None and self.numeric_columns.any():
                X_return_num = self.scaler.transform(X_return[:, self.numeric_columns])
                if (~self.numeric_columns).any():
                    X_return = np.hstack([X_return[:, ~self.numeric_columns].toarray(), X_return_num])
                    self.params['categorical_features'] = np.array(
                        np.concatenate(
                            [
                                np.array(self.problem_info.dataset_categoricals)[~self.numeric_columns],
                                np.zeros(X_return_num.shape[1]),
                            ]
                        ),
                        dtype=int,
                    )
                else:
                    X_return = X_return_num
        else:
            if self.scaler is not None and self.numeric_columns.any():
                X_return[:, self.numeric_columns] = self.scaler.transform(X_return[:, self.numeric_columns])

        if y_valid is not None and X_valid is not None:
            if isinstance(X_valid, pd.DataFrame):
                X_valid = X_valid.values
            X_valid_return = X_valid.copy()
            y_valid_transformed = self._transform_y(y_valid)
            if self.scaler:
                if scipy.sparse.issparse(X):
                    X_valid_return_num = self.scaler.transform(X_valid_return[:, self.numeric_columns])
                    if (~self.numeric_columns).any():
                        X_valid_return = np.hstack(
                            [X_valid_return[:, ~self.numeric_columns].toarray(), X_valid_return_num]
                        )
                    else:
                        X_valid_return = X_valid_return_num

                else:
                    X_valid_return[:, self.numeric_columns] = self.scaler.transform(
                        X_valid_return[:, self.numeric_columns]
                    )
        else:
            X_valid_return = None
            y_valid_transformed = None
        return X_return, y_transformed, X_valid_return, y_valid_transformed

    def fit(
        self,
        X: np.ndarray,
        y: np.ndarray,
        sample_weights: Optional[np.ndarray] = None,
        X_valid: Optional[np.ndarray] = None,
        y_valid: Optional[np.ndarray] = None,
        verbosity: Optional[int] = None,
        time_limit: Optional[Union[float, int]] = None,
        tensorboard_logging: Optional[bool] = False,
        problem_info: Optional[Any] = None,
        **kwargs: Any,
    ) -> "NNTrainerBase":
        """
        Fit function for NNTrainerBase.

        :param X: Input training data.
        :type X: numpy.ndarray
        :param y: Input target values.
        :type y: numpy.ndarray
        :param sample_weights: Input sample weights
        :type sample_weights: Input sample weights
        :param X_valid: Input valid data.
        :type y_valid: numpy.ndarray
        :param y_valid: Input valid target values.
        :type y_valid: numpy.ndarray
        :param verbosity: level of verbosity in printing
        :type verbosity: Int
        :param time_limit: Optional, amount of time in seconds to not exceed
        :type time_limit: Int, float
        :param tensoboard_logging: Optional, bool to log to tensorboard
        :param problem_info: Optional, Any problem_info to tell model about dataset
        :return: self: Returns an instance of self.
        :rtype: NNTrainerBase
        Calls _fit with lowering batch_size in the case of cuda_memory_error
        """
        num_retries = 5
        attempts = 0
        if problem_info is not None:
            self._update_problem_info(problem_info)
        if self.device != 'cpu' and not torch.cuda.is_available():
            self.device = 'cpu'
        while attempts < num_retries and self.batch_size > 10:
            try:
                # TODO: NOW THAT WE AREN'T HAVING MEMORY ERRORS, may want to increase batch sizes we try initially
                # higher batchsizes seem more stable and train more quickly
                self._fit(
                    X,
                    y,
                    sample_weights=sample_weights,
                    X_valid=X_valid,
                    y_valid=y_valid,
                    verbosity=verbosity,
                    time_limit=time_limit,
                    tensorboard_logging=tensorboard_logging,
                    **kwargs,
                )
                return self
            except RuntimeError as e:
                attempts += 1
                if 'out of memory' in str(e):
                    logger.info("Couldn't allocate memory for batch_size: {}".format(self.batch_size))
                    self.batch_size = self.batch_size // 2
                else:
                    raise e
            except KeyboardInterrupt:
                logger.info('KeyboardInterrupt, stopping and returning current state')
                return self
        raise ValueError('Failed to fit due to GPU memory constraints')

    def _fit(
        self,
        X: np.ndarray,
        y: np.ndarray,
        sample_weights: Optional[np.ndarray] = None,
        X_valid: Optional[np.ndarray] = None,
        y_valid: Optional[np.ndarray] = None,
        verbosity: Optional[int] = None,
        time_limit: Optional[Union[float, int]] = None,
        tensorboard_logging: Optional[bool] = False,
        **kwargs: Any,
    ) -> "NNTrainerBase":
        """
        Fit function for NNTrainerBase.

        :param X: Input training data.
        :type X: numpy.ndarray
        :param y: Input target values.
        :type y: numpy.ndarray
        :param sample_weights: Input sample weights
        :type sample_weights: Input sample weights
        :param X_valid: Input valid data.
        :type y_valid: numpy.ndarray
        :param y_valid: Input valid target values.
        :type y_valid: numpy.ndarray
        :param verbosity: level of verbosity in printing
        :type verbosity: Int
        :param time_limit: Optional, amount of time in seconds to not exceed
        :type time_limit: Int, float
        :param tensoboard_logging: Optional, bool to log to tensorboard
        :return: self: Returns an instance of self.
        :rtype: NNTrainerBase
        """
        start_time = time.time()
        # if fit is called multiple times without reinitializing
        self._clear_traces()
        self.tensorboard_logging = tensorboard_logging
        if self.tensorboard_logging:
            self.writer = torch.utils.tensorboard.SummaryWriter()  # use a temp dir?
        best_state_dict = None
        self._prepare_model(y)
        # tabnet requires specific transformations, do them here if the dataset can be stored in memory
        X, y_transformed, X_valid, y_valid_transformed = self._prepare_data_for_dataloader(X, y, X_valid, y_valid)

        self.params["input_features"] = X.shape[1]
        self.nn_model = self._build_nn_model().to(self.device)
        self._create_optimizer_and_schedule()
        self._loss = self._get_loss()
        self._loss = self._loss.to(self.device)

        if X_valid is None and y_valid_transformed is None and self.epochs > 10:
            # if very few epochs, you won't end up early stopping anyway
            # automatically split out 10% of the data to early stop on
            automatically_split = True
            X, X_valid, y_transformed, y_valid_transformed = train_test_split(
                X, y_transformed, test_size=0.1, random_state=0
            )
        else:
            automatically_split = False

        train_dl, valid_dl = self._create_dataloaders(
            X,
            y_transformed,
            sample_weights,
            X_valid,
            y_valid_transformed,
        )

        if time_limit is None and self.max_time is not None:
            time_limit = self.max_time
        timed_out = False
        epoch_runtime_limit = 1e9
        training_successful = True
        for i in range(self.epochs):
            current_time = time.time()
            if i != 0 and time_limit is not None and time_limit > 0:
                time_per_epoch = (current_time - start_time) / i  # epochs take roughly the same amount of time
                if current_time > start_time + time_limit:
                    if verbosity:
                        logger.info("Time limit passed, stopping fitting")
                    break
                elif current_time + time_per_epoch > start_time + time_limit:
                    if verbosity:
                        logger.info("Not enough time to fit another epoch, stopping early")
                    timed_out = True
                    break
            if time_limit is not None and time_limit > 0:
                epoch_runtime_limit = start_time + time_limit - current_time
            training_successful = self._fit_one_epoch_dataloader(train_dl, time_limit=epoch_runtime_limit)
            if self._calculate_train_metrics:
                loss, predictions, targets = self._score_dataloader_loss(train_dl)
                self.add_train_score(loss)
                if torch.isnan(loss):
                    logger.info("Loss is nan, stopping training")
                    break
                self.add_train_metric(self._compute_metric(predictions, targets))
            if valid_dl is not None:
                loss, predictions, targets = self._score_dataloader_loss(valid_dl)
                self.add_val_score(loss)
                if torch.isnan(loss):
                    logger.info("Loss is nan, stopping training")
                    break
                self.add_val_metric(self._compute_metric(predictions, targets))
                # save best model to prevent against overfitting, account for 0 based indexing
                if np.argmin(self._val_scores) == len(self._val_scores) - 1:
                    best_state_dict = self.nn_model.state_dict()
            # TODO: add support for passing in test data
            if self._should_early_stop():
                if verbosity:
                    logger.info("Early Stopping")
                break
            if not training_successful:
                logger.info("Stopping, unstable region")
                break
        if best_state_dict is not None:
            self.nn_model.load_state_dict(best_state_dict)
        if automatically_split and not timed_out and training_successful:
            # ensure we have some contribution from the validation data
            self._fit_one_epoch_dataloader(valid_dl)
        # move the model back to the cpu
        if self.device != "cpu":
            self.nn_model = self.nn_model.cpu()
            self._loss = self._loss.cpu()
        if self.tensorboard_logging:
            self.writer.close()
        return self

    def _clear_traces(self):
        self._val_scores = []
        self._train_scores = []
        self._val_metrics = []
        self._train_metrics = []

    def _get_loss(self):
        raise NotImplementedError

    def _transform_y(self, y: np.ndarray):
        return y

    def _inverse_transform_y(self, y: np.ndarray):
        return y

    def get_label_dtype(self):
        raise NotImplementedError

    def _create_dataloaders(
        self,
        X: np.ndarray,
        y: np.ndarray,
        sample_weights: Optional[np.ndarray],
        X_valid: Optional[np.ndarray],
        y_valid: Optional[np.ndarray],
    ):
        """
        Create dataloaders from numpy arrays.

        :param X: Input data.
        :param y: Input target values.
        :param X_valid: Input valid data.
        :param y_valid: Input valid target values.
        """
        train_data = TabularDataset.from_numpy(X, y, label_dtype=self.get_label_dtype())
        if self.class_weights:
            sampler = self.create_balanced_sampler(y)
            train_dl = torch.utils.data.DataLoader(
                train_data,
                batch_size=self.batch_size,
                sampler=sampler,
                num_workers=self.n_jobs,
                pin_memory=self.device != "cpu" and torch.cuda.is_available(),
            )
        elif sample_weights is not None:
            sampler = torch.utils.data.WeightedRandomSampler(
                weights=sample_weights, num_samples=len(sample_weights), replacement=True
            )
            train_dl = torch.utils.data.DataLoader(
                train_data,
                batch_size=self.batch_size,
                sampler=sampler,
                num_workers=self.n_jobs,
                pin_memory=self.device != "cpu" and torch.cuda.is_available(),
            )
        else:
            train_dl = torch.utils.data.DataLoader(
                train_data,
                batch_size=self.batch_size,
                shuffle=True,
                num_workers=self.n_jobs,
                pin_memory=self.device != "cpu" and torch.cuda.is_available(),
            )
        if X_valid is not None and y_valid is not None:
            valid_data = TabularDataset.from_numpy(X_valid, y_valid, label_dtype=self.get_label_dtype())
            valid_dl = torch.utils.data.DataLoader(
                valid_data,
                batch_size=self.batch_size,
                shuffle=False,
                num_workers=0,
                pin_memory=self.device != "cpu" and torch.cuda.is_available(),
            )
        else:
            valid_dl = None
        return train_dl, valid_dl

    def _build_nn_model(self):
        raise NotImplementedError

    def get_model(self):
        """
        Return the base nn_model

        :return: Returns the fitted model if fit method has been called.
        Else returns None.
        """
        return self.nn_model

    def add_val_score(self, score: Optional[Union[float, torch.Tensor]]):
        """
        Add epoch validation loss to the stored values.

        Parameters
        ----------
        score: float
            loss value for the latest epoch

        """
        if score is not None:
            if isinstance(score, torch.Tensor):
                score = score.item()
            self._val_scores.append(score)
            if self.tensorboard_logging:
                self.writer.add_scalar("val/loss", score, self.trained_epoch)

    def add_train_score(self, score: Optional[Union[float, torch.Tensor]]):
        """
        Add epoch train loss to the stored values.

        Parameters
        ----------
        score: float
            loss value for the latest epoch

        """
        if score is not None:
            if isinstance(score, torch.Tensor):
                score = score.item()
            self._train_scores.append(score)
            if self.tensorboard_logging:
                self.writer.add_scalar("train/loss", score, self.trained_epoch)

    def add_train_metric(self, score: Optional[Union[float, torch.Tensor]]):
        """
        Add epoch validation loss to the stored values.

        Parameters
        ----------
        score: float
            loss value for the latest epoch

        """
        if score is not None:
            if isinstance(score, torch.Tensor):
                score = score.item()
            self._train_metrics.append(score)
            if self.tensorboard_logging:
                self.writer.add_scalar("train/metric", score, self.trained_epoch)

    def add_val_metric(self, score: Optional[Union[float, torch.Tensor]]):
        """
        Add epoch validation metric to the stored values.

        Parameters
        ----------
        score: float
            loss value for the latest epoch

        """
        if score is not None:
            if isinstance(score, torch.Tensor):
                score = score.item()
            self._val_metrics.append(score)
            if self.tensorboard_logging:
                self.writer.add_scalar("val/metric", score, self.trained_epoch)

    def _should_early_stop(self):
        """Determine if the model should early stop."""
        if len(self._val_scores) < self._early_stopping_iterations:
            return False
        # deal with maximization and minimization here
        elif np.argmin(self._val_scores) < len(self._val_scores) - self._early_stopping_iterations:
            # want the best val score to be in the last 20 epochs
            # we are keeping track of loss here so we want to minimize
            return True
        else:
            return False

    def save(
        self,
        directory: str,
        fname: str = "epoch_model_state.pt",
    ) -> None:
        """
        Save the model state for use later.

        Parameters
        ----------
        directory: str
            directory to save the file in
        fname: str
            file name to create
        Returns
        -------
        None

        Creates files in specified directory
        """
        save_dict = {
            "model": self.nn_model.state_dict(),
            "optimizer": self._optimizer.state_dict(),
            "epoch": self.trained_epoch,
        }

        torch.save(save_dict, os.path.join(directory, fname))

    def _get_pred(self, logit: torch.Tensor, return_prob: bool = False) -> torch.Tensor:
        """
        Get the predictions from model output.

        Parameters
        ----------
        logit: torch.Tensor
            output of nn_model, either class probabilities if classification or prediction if regression
        return_prob: bool
            Whether to return probabilities or not

        Returns
        -------
        torch.Tensor
            predicted class or value
        """
        if self.nn_model.is_classification():
            if return_prob:
                pred = torch.nn.functional.softmax(logit, -1)  # ensure that the probabilities sum to 1
            else:
                pred = logit.argmax(dim=-1)
        else:
            pred = logit
        return pred

    def _score_dataloader_loss(
        self, dl: torch.utils.data.DataLoader
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Helper function for scoring on training or validation during training.
        Calculates loss in the transformed y space, if applicable

        Parameters
        ----------
        dl: torch.utils.data.DataLoader
            dataloader for the dataset of interest
        Returns
        -------
        Value of loss on the predictions, the predictions, and the targets
        """
        predictions, targets = self.predict_dataloader(dl, device=self.device, return_prob=True, return_targets=True)
        return self._loss(predictions, targets), predictions, targets

    def predict_dataloader(
        self, dl: torch.utils.data.DataLoader, device: str = "cpu", return_prob: bool = False, return_targets=False
    ) -> torch.Tensor:
        """
        Creates prediction for entire dataset, concatenates individual batches.
        Parameters
        ----------
        dl: torch.utils.data.DataLoader
            dataloader for the dataset of interest
        device: str
            what type of device to compute on, can be cpu or a specifc gpu. Tensors will be returned on the cpu.
        return_prob: bool
            Whether or not to predict probabilities or the predicted class
        return_targets: bool
            Whether or not to return the targets as well as the predictions
        Returns
        -------
        torch.Tensor
            The prediction for the entire dataset
        """
        # put the model in eval mode for predictions and put it on the device
        self.nn_model.eval()
        self.nn_model = self.nn_model.to(device)
        dl_iter = iter(dl)
        with torch.no_grad():
            preds = []
            if return_targets:
                targets = []
            for batch in dl_iter:
                features = batch[FEATURES].to(device)
                if return_targets:
                    target = batch[TARGET]  # not calculating anything on device so don't need to move to device
                    targets.append(target)
                pred = self.nn_model(features)  # ignore reg when making predictions
                pred = self._get_pred(pred, return_prob=return_prob)
                if pred.device.type != "cpu":
                    pred = pred.cpu()
                preds.append(pred)
            if len(preds) == 1 and pred.ndim == 0:
                preds = torch.tensor(preds)
            else:
                preds = torch.cat(preds)
            if return_targets:
                if len(targets) == 1 and pred.ndim == 0:
                    targets = torch.tensor(targets)
                else:
                    targets = torch.cat(targets)
                return preds, targets
            preds = preds.numpy()
            # when used with the targets, the targets are also assumed to be transformed
            preds = self._inverse_transform_y(preds)
            if device != "cpu":
                self.nn_model = self.nn_model.cpu()
            return preds

    def _score_dataloader_metric(self, dl: torch.utils.data.DataLoader) -> float:
        """
        Helper function for scoring on training or validation during training.

        Parameters
        ----------
        dl: torch.utils.data.DataLoader
            dataloader for the dataset of interest
        Returns
        -------
        Value of loss on the predictions
        """
        raise NotImplementedError

    def _prepare_model(self, y: Optional[np.ndarray] = None):
        raise NotImplementedError


class NNTrainerClassifier(NNTrainerBase, ClassifierMixin):
    def get_label_dtype(self):
        return np.int64

    def score(
        self,
        X: np.ndarray,
        y: np.ndarray,
        batch_size: Optional[int] = None,
        device: Optional[Union[str, torch.device]] = None,
        n_jobs: Optional[int] = None,
    ):
        """
        Returns the accuracy on the given data
        :param X: Input data.
        :type X: numpy.ndarray
        :param y: Optional, Input target values.
        :type y: numpy.ndarray
        :param batch_size: Optional, if want to use a different batch size than during training
        :type batch_size: int
        :param device: str, if want to use a different device than during training
        :type device: str
        :param n_jobs: int, if want to use a different number of cpus for dataloading than during training
        :type n_jobs: int
        """
        if self.nn_model is None:
            logger.error("Trying to call score on an untrained model")
            raise ValueError("Untrained Model")
        X, y_transformed, _, _ = self._prepare_data_for_dataloader(X, y, None, None)
        data = TabularDataset.from_numpy(X, y_transformed, label_dtype=self.get_label_dtype())
        batch_size = self.batch_size if batch_size is None else batch_size
        device = self.device if device is None else device
        if device != 'cpu' and not torch.cuda.is_available():
            device = 'cpu'
        n_jobs = self.n_jobs if n_jobs is None else n_jobs
        dl = torch.utils.data.DataLoader(
            data,
            batch_size=batch_size,
            shuffle=False,
            num_workers=n_jobs,
            pin_memory=device != "cpu",
        )
        predictions, targets = self.predict_dataloader(dl, device, return_prob=False, return_targets=True)
        return accuracy_score(targets, predictions)

    def predict_proba(
        self,
        X: np.ndarray,
        y: Optional[np.ndarray] = None,
        batch_size: Optional[int] = None,
        device: Optional[Union[str, torch.device]] = None,
        n_jobs: Optional[int] = None,
    ):
        """
        Generates a set of predictions on the given data
        :param X: Input data.
        :type X: numpy.ndarray
        :param y: Optional, Input target values.
        :type y: numpy.ndarray
        :param batch_size: Optional, if want to use a different batch size than during training
        :type batch_size: int
        :param device: str, if want to use a different device than during training
        :type device: str
        :param n_jobs: int, if want to use a different number of cpus for dataloading than during training
        :type n_jobs: int
        """
        if self.nn_model is None:
            logger.error("Trying to call predict_proba on an untrained model")
            raise ValueError("Untrained Model")
        X, y_transformed, _, _ = self._prepare_data_for_dataloader(X, y, None, None)
        data = TabularDataset.from_numpy(X, y_transformed, label_dtype=self.get_label_dtype())
        batch_size = self.batch_size if batch_size is None else batch_size
        device = self.device if device is None else device
        if device != 'cpu' and not torch.cuda.is_available():
            device = 'cpu'
        n_jobs = self.n_jobs if n_jobs is None else n_jobs
        dl = torch.utils.data.DataLoader(
            data,
            batch_size=batch_size,
            shuffle=False,
            num_workers=n_jobs,
            pin_memory=device != "cpu",
        )
        return self.predict_dataloader(dl, device, return_prob=True, return_targets=False)

    def _get_loss(self):
        return nn.CrossEntropyLoss()

    def _score_dataloader_metric(self, dl: torch.utils.data.DataLoader) -> float:
        """
        Helper function for scoring on training or validation during training.
        Calculates accuracy.

        Parameters
        ----------
        dl: torch.utils.data.DataLoader
            dataloader for the dataset of interest
        Returns
        -------
        Value of loss on the predictions
        """
        predictions, targets = self.predict_dataloader(dl, device=self.device, return_prob=True, return_targets=True)
        return accuracy_score(targets, predictions)  # perhaps allow passing in a callable

    def _transform_y(self, y: np.ndarray):
        if self.classes_ is None:
            self.classes_ = np.unique(y)  # set classes that the model was trained on
        return y

    def create_balanced_sampler(self, y: np.ndarray) -> torch.utils.data.WeightedRandomSampler:
        """Creates a balanced sampler for classification."""
        pd_y = pd.Series(y)
        weight_by_label = (pd_y.shape[0] - pd_y.value_counts()) / pd_y.shape[0]
        weights = pd_y.apply(lambda x: weight_by_label.loc[x]).values
        sampler = torch.utils.data.WeightedRandomSampler(
            weights=weights.values, num_samples=len(weights), replacement=True
        )
        return sampler

    def _compute_metric(
        self, predictions: Union[np.ndarray, torch.Tensor], targets: Union[np.ndarray, torch.Tensor]
    ) -> float:
        """
        Helper function for scoring on training or validation during training.
        Calculates accuracy

        Parameters
        ----------
        predictions: Union[np.ndarray, torch.Tensor]
            Predictions from the model
        targets: Union[np.ndarray, torch.Tensor]
            Actual results
        Returns
        -------
        Value of accuracy of the predictions
        """
        return accuracy_score(targets, predictions.argmax(1))

    def _prepare_model(self, y: Optional[np.ndarray] = None):
        self.params["model_type"] = "classification"
        self.classes_ = None
        if y is not None and (self.problem_info is None or self.problem_info.dataset_classes is None):
            self.params["out_features"] = np.unique(y).shape[0]


class NNTrainerRegressor(NNTrainerBase, RegressorMixin):
    def get_label_dtype(self):
        return np.float32

    def score(
        self,
        X: np.ndarray,
        y: np.ndarray,
        batch_size: Optional[int] = None,
        device: Optional[Union[str, torch.device]] = None,
        n_jobs: Optional[int] = None,
    ) -> float:
        """
        Returns the r2_score of the predictions

        :param X: Input data.
        :type X: numpy.ndarray
        :param y: Input target values.
        :type y: numpy.ndarray
        :param batch_size: Optional, if want to use a different batch size than during training
        :type batch_size: int
        :param device: str, if want to use a different device than during training
        :type device: str
        :param n_jobs: int, if want to use a different number of cpus for dataloading than during training
        :type n_jobs: int
        """
        if self.nn_model is None:
            logger.error("Trying to call score on an untrained model")
            raise ValueError("Untrained Model")
        X, y_transformed, _, _ = self._prepare_data_for_dataloader(X, y, None, None)
        data = TabularDataset.from_numpy(X, y_transformed, label_dtype=self.get_label_dtype())
        batch_size = self.batch_size if batch_size is None else batch_size
        device = self.device if device is None else device
        if device != 'cpu' and not torch.cuda.is_available():
            device = 'cpu'
        n_jobs = self.n_jobs if n_jobs is None else n_jobs
        dl = torch.utils.data.DataLoader(
            data,
            batch_size=batch_size,
            shuffle=False,
            num_workers=n_jobs,
            pin_memory=device != "cpu",
        )
        # dont need the targets here but easy to keep everything the same
        predictions, targets = self.predict_dataloader(dl, device, return_prob=False, return_targets=True)
        return r2_score(targets, predictions)

    def _score_dataloader_metric(self, dl: torch.utils.data.DataLoader) -> float:
        """
        Helper function for scoring on training or validation during training.
        Calculates r2_score in the transformed y space, if applicable

        Parameters
        ----------
        dl: torch.utils.data.DataLoader
            dataloader for the dataset of interest
        Returns
        -------
        Value of loss on the predictions
        """
        predictions, targets = self.predict_dataloader(dl, device=self.device, return_prob=True, return_targets=True)
        return r2_score(targets, predictions)  # r2_score needs this order

    def _compute_metric(
        self, predictions: Union[np.ndarray, torch.Tensor], targets: Union[np.ndarray, torch.Tensor]
    ) -> float:
        """
        Helper function for scoring on training or validation during training.
        Calculates r2_score in the transformed y space, if applicable

        Parameters
        ----------
        predictions: Union[np.ndarray, torch.Tensor]
            Predictions from the model
        targets: Union[np.ndarray, torch.Tensor]
            Actual results
        Returns
        -------
        Value of r2_score of the predictions
        """
        return r2_score(targets, predictions)  # r2_score needs this order

    def _transform_y(self, y: Optional[np.ndarray] = None):
        # if loss is root mean squared log error, transform y should also take the log
        if y is None:
            return y
        if self.y_mean is None:
            self.y_mean = y.ravel().mean()
            self.y_std = y.ravel().std()
        # ensure that y isn't stored as an int
        return (np.array(y, dtype=self.y_mean.dtype) - self.y_mean) / self.y_std

    def _inverse_transform_y(self, y: np.ndarray):
        # if loss is root mean squared log error, inv transform y should also take the exponent
        if self.y_mean is None:
            logger.error("Trying to call _inverse_transform_y on an untrained model")
            raise ValueError("Untrained Model")
        return y * self.y_std + self.y_mean

    def _get_loss(self):
        if self.loss is None:
            return nn.MSELoss()
        else:
            return getattr(nn, self.loss)()

    def create_balanced_sampler(self, y: np.ndarray) -> torch.utils.data.WeightedRandomSampler:
        raise NotImplementedError("Balanced Sampler not valid for regression.")

    def _prepare_model(self, y: Optional[np.ndarray] = None):
        self.params["model_type"] = "regression"
        self.params["out_features"] = 1
        self.y_mean = None
        self.y_std = None
        if self.class_weights:
            raise ValueError("class weights are not valid for regression")


class TabnetRegressor(NNTrainerRegressor):
    def _build_nn_model(self):
        return TabNet(TabularNNConfig.fromdict(self.params))


class AutoGluonRegressor(NNTrainerRegressor):
    def _build_nn_model(self):
        return AutoGluonTabularNN(TabularNNConfig.fromdict(self.params))

    def _calculate_loss(self, output: Tuple[torch.Tensor, torch.Tensor], labels: [torch.Tensor]):
        return self._loss(output, labels)


class TabnetClassifier(NNTrainerClassifier):
    def _build_nn_model(self):
        return TabNet(TabularNNConfig.fromdict(self.params))


class AutoGluonClassifier(NNTrainerClassifier):
    def _build_nn_model(self):
        return AutoGluonTabularNN(TabularNNConfig.fromdict(self.params))

    def _calculate_loss(self, output: Tuple[torch.Tensor, torch.Tensor], labels: [torch.Tensor]):
        return self._loss(output, labels)

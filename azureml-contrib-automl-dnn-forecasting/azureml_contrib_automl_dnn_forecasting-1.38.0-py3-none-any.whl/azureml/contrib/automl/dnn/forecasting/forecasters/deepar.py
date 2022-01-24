# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Forecaster for DeepAr model."""
import copy
import time
from math import inf

import numpy as np
import torch

from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.core.shared.exceptions import ClientException
from azureml.automl.core.shared._diagnostics.automl_error_definitions import TCNForecastDeepARNaN
from Deep4Cast.deep4cast import Forecaster


class ForecasterDeepAr(Forecaster):
    """Handles training of a PyTorch model.

    This class can be used to generate samples
    from approximate posterior predictive distribution.
    """

    def __init__(self,
                 model,
                 loss,
                 optimizer,
                 n_epochs=1,
                 device='cpu',
                 checkpoint_path='./',
                 verbose=True,
                 clip_grad_norm=0.5):
        """Init the forecaster.

        :param model: (``torch.nn.Module``): Instance of Deep4cast :class:`models`.
        :param loss: (``any``): Model specific loss.
        :param optimizer: (``torch.optim``): Instance of PyTorch
            `optimizer <https://pytorch.org/docs/stable/optim.html#torch.optim.Optimizer>`_.
        :param n_epochs: (int): Number of training epochs.
        :param device: (str): Device used for training (`cpu` or `cuda`).
        :param checkpoint_path: (str): File system path for writing model checkpoints.
        :param verbose: (bool): Verbosity of forecaster.
        :param clip_grad_norm: (float): Norm for gradient clipping.
        """
        super(ForecasterDeepAr, self).__init__(model,
                                               loss,
                                               optimizer,
                                               n_epochs,
                                               device,
                                               checkpoint_path,
                                               verbose)
        self.clip_grad_norm = clip_grad_norm

    def _train(self, dataloader, epoch, start_time):
        """Perform training for one epoch.

        Arguments:
            * dataloader (``torch.utils.data.DataLoader``): Training data.
            * epoch (int): Current training epoch.
            * start_time (``time.time``): Clock time of training start.

        """
        n_trained = 0
        total_loss = 0

        self.model.train()

        for idx, batch in enumerate(dataloader):

            # Send batch to device
            inputs = batch['X'].to(self.device)
            targets = batch['y'].to(self.device)

            # Backpropagation
            self.optimizer.zero_grad()
            past_and_future = torch.cat((inputs, targets), dim=2)

            self.model(past_and_future)

            loss = self.loss(inputs, targets)
            total_loss += loss.item()

            if torch.isnan(loss):
                raise ClientException._with_error(AzureMLError.create(
                    TCNForecastDeepARNaN, target="X",
                    reference_code=ReferenceCodes._TCN_FORECAST_DEEP_AR_NAN)
                )
            loss.backward()

            torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.clip_grad_norm)

            self.optimizer.step()

            # Status update for the user
            if self.verbose:
                self._print_train_status_update(dataloader, epoch, idx, inputs,
                                                loss, n_trained, start_time, total_loss)

    def _print_train_status_update(self, dataloader, epoch, idx, inputs, loss, n_trained, start_time, total_loss):
        n_trained += len(inputs)
        n_total = len(dataloader.dataset)
        percentage = 100.0 * (idx + 1) / len(dataloader)
        elapsed = time.time() - start_time
        remaining = elapsed * ((self.n_epochs * n_total) / ((epoch - 1) * n_total + n_trained) - 1)
        status = '\rEpoch {}/{} [{}/{} ({:.0f}%)]\t' \
                 + 'Loss: {:.6f}\t' \
                 + 'Total Loss: {:.6f}\t' \
                 + 'Elapsed/Remaining: {:.0f}m{:.0f}s/{:.0f}m{:.0f}s   '
        print(
            status.format(
                epoch,
                self.n_epochs,
                n_trained,
                n_total,
                percentage,
                loss.mean().item(),
                total_loss,
                elapsed // 60,
                elapsed % 60,
                remaining // 60,
                remaining % 60
            ),
            end=""
        )

    def _evaluate(self, dataloader, n_samples=10):
        """Return the approximate min negative log likelihood of the model averaged over dataset.

        Arguments:
            * dataloader (``torch.utils.data.DataLoader``): Evaluation data.
            * n_samples (int): Number of forecast samples.

        """
        max_llikelihood = float(-inf)
        with torch.no_grad():
            self.model.eval()
            for batch in dataloader:
                inputs = batch['X'].to(self.device)
                targets = batch['y'].to(self.device)

                # Forward pass through the model
                # The inputs and the targets are assumed to be of shape
                # [batch_size, input_features, lookback /(respective horizon)].
                # The first feature is considered to be the timeseries, so we need to remove
                # it from the targets for evaluation.
                past_and_future = torch.cat((inputs, targets), dim=2)
                if targets.shape[1] > 1:
                    self.model(past_and_future, targets[:, 1:, :])
                else:
                    self.model(past_and_future, None)

                loss = -self.loss(inputs, targets)
                max_llikelihood = max(loss.item(), max_llikelihood)

        return -max_llikelihood / len(dataloader.dataset)

    def predict(self, dataloader, n_samples=100) -> np.array:
        """Generate predictions.

        Arguments:
            * dataloader (``torch.utils.data.DataLoader``): Data to make forecasts.
            * n_samples (int): Number of forecast samples.

        """
        with torch.no_grad():
            self.model.eval()
            predictions = []
            for batch in dataloader:
                inputs = batch['X'].to(self.device)
                samples = []
                # TODO RK: change to predict all samples at once.
                for i in range(n_samples):
                    # assume target is first feature if we have multiple ones
                    if batch['y'].shape[1] > 1:
                        results = self.model(inputs, batch['y'][:, 1:, :].to(self.device))
                    else:
                        results = self.model(inputs, None)
                    batch_copy = copy.deepcopy(batch)
                    batch_copy['y'] = results
                    untransformed_batch_copy = dataloader.dataset.transform.untransform(batch_copy)
                    samples.append(untransformed_batch_copy['y'][None, :])
                samples = np.concatenate(samples, axis=0)
                predictions.append(samples)
            predictions = np.concatenate(predictions, axis=1)

        return predictions

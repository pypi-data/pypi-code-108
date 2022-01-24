# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module for creating a model based on Deep4Cast."""
import math
import numpy as np
import argparse

import torch
from Deep4Cast.deep4cast.forecasters import Forecaster
from Deep4Cast.deep4cast.models import WaveNet
from .forecast_wrapper import DNNForecastWrapper, DNNParams
from ..constants import ForecastConstant
import azureml.dataprep as dprep


class Deep4CastWrapper(DNNForecastWrapper):
    """Wrapper for Deeep4Cast adapted to work with automl Forecast Training."""

    required_params = [ForecastConstant.Learning_rate, ForecastConstant.Horizon, ForecastConstant.Lookback,
                       ForecastConstant.Batch_size, ForecastConstant.num_epochs, ForecastConstant.Loss,
                       ForecastConstant.Device]
    default_params = {ForecastConstant.Loss: torch.distributions.StudentT,
                      ForecastConstant.Device: 'cuda' if torch.cuda.is_available() else 'cpu'}

    def _init__(self):
        super().__init__()

    def train(self, n_epochs: int, X: dprep.Dataflow, y: dprep.Dataflow) -> None:
        """
        Start the DNN training.

        :param X: data for training.
        :param y:  label for training.
        :param n_epochs: number of epochs to try.
        :return: Nothing, the model is trained.
        """
        ds = self._get_timeseries(X, y)
        dataloader_train = self.create_data_loader(ds, True, self.params.get_value(ForecastConstant.Batch_size))
        if self.model is None:
            self.model = WaveNet(input_channels=self.input_channels,
                                 output_channels=self.output_channels,
                                 horizon=self.params.get_value(ForecastConstant.Horizon),
                                 n_layers=self.params.get_value(ForecastConstant.n_layers))
            optim = torch.optim.Adam(self.model.parameters(), lr=self.params.get_value(ForecastConstant.Learning_rate))
            # Fit the forecaster
            self.forecaster = Forecaster(self.model,
                                         loss=self.params.get_value(ForecastConstant.Loss),
                                         optimizer=optim,
                                         n_epochs=n_epochs,
                                         device=self.params.get_value(ForecastConstant.Device))
        self.forecaster.fit(dataloader_train, eval_model=False)

    def predict(self, X: dprep.Dataflow, y: dprep.Dataflow, n_samples: int) -> np.ndarray:
        """
        Return the predictions for the passed in `X` and `y` values.

        :param X: data values.
        :param y: Target values for look back and nan for the rest.
        :param n_samples:  number of samples to be retured with each prediction.
        :return: a ndarray with shape (n_samples, n_rows, horizon).
        """
        ds = self._get_timeseries(X, y)
        dataloader_test = self.create_data_loader(ds, True, self.params.get_value(ForecastConstant.Batch_size))

        return self.forecaster.predict(dataloader_test, n_samples=n_samples)

    def parse_parameters(self) -> DNNParams:
        """
        Parse parameters from command line.

        :return: returns the  DNN  param object from the command line arguments
        """
        parser = argparse.ArgumentParser()
        parser.add_argument(DNNForecastWrapper.get_arg_parser_name(ForecastConstant.num_epochs), type=int, default=25,
                            help='number of epochs to train')
        parser.add_argument(DNNForecastWrapper.get_arg_parser_name(ForecastConstant.Learning_rate), type=float,
                            default=0.001, help='learning rate')
        parser.add_argument(DNNForecastWrapper.get_arg_parser_name(ForecastConstant.Lookback), type=int,
                            default=8, help='lookback for model')
        parser.add_argument(DNNForecastWrapper.get_arg_parser_name(ForecastConstant.Horizon), type=int,
                            default=4, help='horizon for prediction')
        parser.add_argument(DNNForecastWrapper.get_arg_parser_name(ForecastConstant.Batch_size), type=int,
                            default=8, help='batch_size for training')

        args, unknown = parser.parse_known_args()
        arg_dict = vars(args)
        arg_dict[ForecastConstant.n_layers] = max(int(math.log2(args.lookback)), 1)
        dnn_params = DNNParams(Deep4CastWrapper.required_params, arg_dict, Deep4CastWrapper.default_params)
        return dnn_params

# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""DeepAR model implementation."""

import math

import torch

from .base_model import BaseModel


class DeepAr(BaseModel):
    """Implementation of DeepAr model from: https://arxiv.org/abs/1704.04110."""

    # TODO RK
    # - add support for negative binomial distribution for positive count data
    # - add support for learning embeddings for some features (categorical?)
    # - add scaling
    # - paper mentions that some of the timeseries are sampled to start after the lookback.
    #   Then they are padded and model learns how to deal with smaller timeseries
    # - gluonts uses weighting for the loss terms - masking out the terms where the target is missing

    def __init__(self, input_size, horizon, hidden_size=128, num_layers=1, dropout=0.2,
                 distribution=torch.distributions.Normal):
        """Build a DeepAr model.

        :param input_size: Number of input features.
        :param horizon: Prediction length.
        :param hidden_size: Hidden size of the lstm.
        :param num_layers: Number of lstm layers.
        :param dropout: Lstm dropout.
        """
        super(DeepAr, self).__init__()

        self.input_size = input_size
        self.horizon = horizon

        assert (self.horizon > 0), "Horizon needs to be greater than 0. Got {}.".format(self.horizon)

        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.dropout = dropout

        self.lstm = torch.nn.LSTM(input_size=input_size,
                                  hidden_size=hidden_size,
                                  num_layers=num_layers,
                                  batch_first=True,
                                  dropout=dropout,
                                  bidirectional=False)

        self.distribution_mean = torch.nn.Linear(hidden_size, 1)
        self.distribution_std = torch.nn.Linear(hidden_size, 1)
        self.distribution_std_softplus = torch.nn.Softplus()

        self.distribution = distribution

        self.lstm_out = None
        self.lstm_hidden = None

        self._init_weights()

    def _init_weights(self):
        """Initialize weights.

        Use orthogonal init for recurrent layers, xavier uniform for input layers
        Bias is 0 except for forget gate
        """
        for name, param in self.named_parameters():
            if "weight_hh" in name:
                torch.nn.init.orthogonal_(param.data)
            elif "weight_ih" in name:
                torch.nn.init.xavier_uniform_(param.data)
            elif "bias" in name:
                torch.nn.init.zeros_(param.data)
                # bias order: ingate, forgetgate, cellgate, outgate
                param.data[self.hidden_size:2 * self.hidden_size] = 1

    def _hidden_init(self, batch_size, device):
        return (torch.zeros(self.num_layers, batch_size, self.hidden_size).to(device),
                torch.zeros(self.num_layers, batch_size, self.hidden_size).to(device))

    def _train(self, inputs: torch.Tensor):
        """Train this model.

        Unrolls the lstm on the given inputs.
        :param inputs: inputs for the forward pass. Shape [batch_size, input_size, lookback].
        :returns a tuple (lstm_out, lstm_hidden).
        """
        # Arrange inputs to have the shape expected by the LSTM: [batch_size, lookback, input_size]
        inputs_lstm = torch.transpose(inputs, 1, 2)

        # shape of lstm_out: [batch_size, lookback, hidden_dim]
        # shape of self.hidden: (a, b), where a and b both
        # have shape (num_layers, batch_size, hidden_dim).
        lstm_out, lstm_hidden = self.lstm(inputs_lstm,
                                          self._hidden_init(inputs.shape[0], inputs_lstm.device))

        return lstm_out, lstm_hidden

    def forward(self, inputs: torch.Tensor, horizon_features: torch.Tensor = None):
        """Forward function.

        :param inputs: inputs for the forward pass. Shape [batch_size, input_size, lookback].
        :param horizon_features: features for the horizon timestamps. Shape [batch_size, input_size - 1, horizon].
        :return the output of the lstm if in training, the samples otherwise.
        """
        assert (inputs is not None), "Inputs cannot be None."

        if horizon_features is not None:
            assert inputs.shape[0] == horizon_features.shape[0], \
                "Batch size should be the same for inputs " \
                "and horizon_features. Got {}, expected {}.".format(horizon_features.shape[0], inputs.shape[0])
            assert inputs.shape[1] == horizon_features.shape[1] + 1, \
                "Horizon and inputs features size should have a difference of 1. " \
                "Got {}, expected {}.".format(horizon_features.shape[1], inputs.shape[1])
            assert horizon_features.shape[2] == self.horizon, \
                "Horizon features span is not the same as horizon. " \
                "Got {}, expected {}.".format(horizon_features.shape[2], self.horizon)

        lstm_out, lstm_hidden = self._train(inputs)
        self.lstm_out = lstm_out
        self.lstm_hidden = lstm_hidden

        if self.training:
            return lstm_out, lstm_hidden
        else:
            return self._predict(horizon_features)

    def _get_mean_std(self, lstm_out: torch.Tensor):
        output_mean = self.distribution_mean(lstm_out)
        output_std = self.distribution_std_softplus(self.distribution_std(lstm_out))

        return output_mean, output_std

    def _predict(self, horizon_features: torch.Tensor = None):
        """Predict a given horizon based on the forward pass output.

        :param horizon_features: features for the horizon timestamps. Shape [batch_size, input_size - 1, horizon].
        :return: a tensor with `horizon` number of samples. Shape [batch_size, 1].
        """
        assert (self.lstm_out is not None), "The model needs to be trained before evaluation."
        assert (self.lstm_hidden is not None), "The model needs to be trained before evaluation."

        if horizon_features is not None:
            # Arrange inputs to have the shape expected by the LSTM: [batch_size, lookback, input_size]
            horizon_features = torch.transpose(horizon_features, 1, 2)

        # Shape of lstm_out: [batch_size, lookback, hidden_dim]
        # Use last output as a starting point: [batch_size, hidden_size]
        out = self.lstm_out.select(1, -1)
        # [batch_size, hidden_size] to [batch_size, 1, hidden_size]
        out = out.view(out.shape[0], 1, out.shape[1])

        all_samples = []

        hidden = self.lstm_hidden
        for idx in range(0, self.horizon):
            # Build the distribution on the output and draw a sample
            output_mean, output_std = self._get_mean_std(out)
            distribution = self.distribution(loc=output_mean, scale=output_std)

            # shape [batch_size, 1, 1]
            sample = distribution.sample()

            all_samples.append(sample)

            if horizon_features is not None:
                step_features = horizon_features[:, idx, :]
                # [batch_size, input_size] to [batch_size, 1, input_size]
                step_features = step_features.view(step_features.shape[0], 1, step_features.shape[1])
                out, hidden = self.lstm(torch.cat((sample, step_features), dim=2), hidden)
            else:
                out, hidden = self.lstm(sample, hidden)

        return torch.cat(all_samples, dim=2).cpu()

    def loss(self, inputs: torch.Tensor, targets: torch.Tensor):
        """Compute the loss for the given inputs and targets.

        :param inputs: inputs of the forward pass. Shape [batch_size, input_size, lookback].
        :param targets: targets to compute the loss for. Shape [batch_size, input_size, horizon].
        :return: the loss to minimize.
        """
        assert (self.lstm_out is not None), "The model needs to be trained before computing the loss."

        # result shape should be [batch_size, lookback + horizon, 1]
        output_mean, output_std = self._get_mean_std(self.lstm_out)

        assert torch.min(output_std) > 0, "Unexpected negative " \
                                          "value in std: {}, {}".format(torch.min(output_std), torch.isnan(output_std))

        assert not torch.isnan(output_mean).any(), "Unexpected nan values in mean"
        assert not torch.isnan(output_std).any(), "Unexpected nan values in mean"

        # Ignore thus the last output of the lstm which would be used
        # to compute the likelihood of the horizon + 1
        output_mean = output_mean[:, :-1, :]
        output_std = output_std[:, :-1, :]

        # The targets are the inputs + targets shifted left by 1 step:
        #  the i_1 is actually the expected output of the likelihood
        #  computed on the output of the lstm on input i_0
        loss_targets = torch.cat((inputs[:, :, 1:], targets), dim=2)

        # [batch_size, input_size, lookback+horizon] to [batch_size, lookback+horizon, input_size].
        distrib_inputs = torch.transpose(loss_targets, 1, 2)

        if distrib_inputs.shape[2] != 1:
            # assume that the target is the first index
            distrib_inputs = distrib_inputs[:, :, [0]]

        assert distrib_inputs.shape[2] == 1, "Loss should only be computed on the target value"

        # [batch_size, ]
        log_likelihood = -1.0 * (torch.log(output_std) + 0.5 * math.log(2 * math.pi)
                                 + 0.5 * torch.pow((distrib_inputs - output_mean) / output_std, 2))

        # - torch.sum(log_likelihood, (1, 2)).mean()
        loss = - log_likelihood.mean()

        return loss

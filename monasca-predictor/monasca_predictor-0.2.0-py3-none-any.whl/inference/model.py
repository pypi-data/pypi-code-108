import logging
import pathlib

import numpy as np
import tensorflow as tf
import joblib
import statsmodels.api as sm
import torch
import torch.nn as nn
from sklearn.linear_model import LinearRegression

log = logging.getLogger(__name__)


class Model:
    def __init__(self):
        self._model = None
        self._scaler = None
        self._model_dump_path = None
        self._scaler_dump_path = None

    def load(self, model_dump, scaler_dump=None):
        self._model_dump_path = pathlib.Path(model_dump)

        # Assuming tf.keras model
        if self._model_dump_path.suffix == ".h5":
            self._model = tf.keras.models.load_model(model_dump)
        # Assuming pytorch model
        if self._model_dump_path.suffix == ".pt":
            # TODO: drop assumptions on underlying model.
            if "rnn" in str(self._model_dump_path):
                self._model = Model.RNN(1, 200, 1, 3)
            elif "mlp" in str(self._model_dump_path):
                self._model = Model.MLP(
                    int(self._model_dump_path.name.split("_")[0].split("-")[1]),
                    [10, 10],
                    1,
                )
            self._model.load_state_dict(torch.load(model_dump))
            self._model.eval()
        # Assuming sklearn model
        elif self._model_dump_path.suffix == ".joblib":
            self._model = joblib.load(model_dump)
        # Assuming statsmodels model
        elif self._model_dump_path.suffix == ".sm":
            self._model = sm.load(model_dump)
        else:
            raise ValueError(
                f"Unsupported model dump format '{self._model_dump_path.suffix}'."
            )

        log.debug("Loaded model of type '%s'.", type(self._model))

        if scaler_dump:
            self._scaler_dump_path = pathlib.Path(scaler_dump)

            if self._scaler_dump_path.suffix == ".joblib":
                self._scaler = joblib.load(self._scaler_dump_path)
            else:
                raise ValueError(
                    f"Unsupported scaler dump format '{self._scaler_dump_path.suffix}'."
                )

        log.debug("Loaded scaler of type '%s'.", type(self._scaler))

    def predict(self, x, steps=None):
        if not isinstance(x, np.ndarray):
            log.debug("Input is of type '%s', converting to 'numpy.ndarray'.", type(x))
            x = np.array(x)

        # scaler expects 2D inputs
        if len(x.shape) == 1:
            x = x.reshape(-1, 1)
        x_scaled = self._scaler.transform(x)

        log.debug("x_scaled (shape=%s):\n%s", str(x_scaled.shape), str(x_scaled))
        log.debug("prediction steps: %d", steps)

        if self._model_dump_path.suffix == ".pt":
            # TODO: drop assumptions on underlying model input shape.
            if "rnn" in str(self._model_dump_path):
                a = torch.tensor(x_scaled, dtype=torch.float32).unsqueeze(1)
                h0 = self._model.init_hidden(1)
                y_scaled, _ = self._model(a, h0)
                y_scaled = y_scaled.detach().numpy().reshape(-1, 1)
            elif "mlp" in str(self._model_dump_path):
                y_scaled = self._model(torch.tensor(x_scaled, dtype=torch.float32).T)
                y_scaled = y_scaled.detach().numpy().reshape(-1, 1)
        elif self._model_dump_path.suffix == ".sm":
            y_scaled = self._model.apply(x_scaled).forecast(steps)[-1].reshape(-1, 1)
        else:
            # TODO: drop assumptions on underlying model input shape.
            # Currently assuming the underlying model is an LSTM expecting 3D
            # inputs.
            x_scaled = x_scaled.reshape(
                -1,
                *x_scaled.shape,
            )

            y_scaled = self._model.predict(x_scaled)

        log.debug("y_scaled (shape=%s): %s", str(y_scaled.shape), str(y_scaled))
        log.debug("scaler input shape: %s", str(self._scaler.scale_.shape))

        # NOTE: assuming the expected output of the model is a single value,
        # that is the last feature to be provided to the scaler.
        scaler_input_length = len(self._scaler.scale_)
        if y_scaled.shape[1] < scaler_input_length:
            y_scaled_temp = np.zeros((1, scaler_input_length))
            y_scaled_temp[0, -1] = y_scaled[0, -1]

            y = self._scaler.inverse_transform(y_scaled_temp)
            return float(y.flatten()[-1])

        return float(self._scaler.inverse_transform(y_scaled).flatten())

    class RNN(nn.Module):
        def __init__(self, in_size, hidden_size, out_size, layers):
            super(Model.RNN, self).__init__()
            self.input_size = in_size
            self.hidden_size = hidden_size
            self.output_size = out_size
            self.layers = layers
            self.rnn = nn.RNN(
                input_size=self.input_size,
                hidden_size=self.hidden_size,
                num_layers=self.layers,
                batch_first=False,
                nonlinearity="relu",
            )
            self.lin = nn.Linear(self.hidden_size, self.output_size)

        def forward(self, seq, hidden):
            output, _ = self.rnn(seq, hidden)
            output = self.lin(output[-1:])
            return output, hidden

        def init_hidden(self, batch_size):
            return torch.zeros(self.layers, batch_size, self.hidden_size)

    class MLP(nn.Module):
        def __init__(self, in_size: int, hidden_size: list, output_size: int):
            super(Model.MLP, self).__init__()
            self.input_size = in_size
            self.hidden_size = hidden_size
            self.output_size = output_size
            self.dimensions = [self.input_size] + self.hidden_size + [self.output_size]
            self.stack = []
            for idx in range(len(self.dimensions) - 1):
                self.stack.append(
                    nn.Linear(self.dimensions[idx], self.dimensions[idx + 1])
                )
                self.stack.append(nn.LeakyReLU())
            self.stack = nn.ModuleList(self.stack)

        def forward(self, x):
            signal = x
            for idx, processing in enumerate(self.stack):
                signal = processing(signal)
            return signal


class LinearModel(Model):
    def __init__(self):
        super().__init__()
        log.debug("Loaded model of type '%s'.", LinearRegression)

    def predict(self, x, steps=None):
        if not isinstance(x, np.ndarray):
            log.debug("Input is of type '%s', converting to 'numpy.ndarray'.", type(x))
            x = np.array(x)

        # fit a linear model on input samples to get the trend
        time_steps = np.arange(0, len(x))
        self._model = LinearRegression().fit(time_steps.reshape(-1, 1), x)

        y = self._model.predict(np.array([[time_steps[-1] + steps]]))

        log.debug("y (shape=%s):\n%s", str(y.shape), str(y))

        # NOTE: assuming the expected output of the model is a single value
        return float(y.flatten())

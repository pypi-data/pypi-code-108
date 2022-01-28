import numpy as np
import sklearn.base

from tensorflow.compat.v1.keras.models import Model
from tensorflow.compat.v1.keras.layers import Input, Dense, Reshape, LSTM
from tensorflow.compat.v1.keras.optimizers import Adam
from tensorflow.compat.v1.keras.callbacks import EarlyStopping

_DTYPE = 'float32'
_MAX_LAYER_SIZE = 64
_MIN_LAYER_SIZE = 4


class TimeSeriesLSTM(sklearn.base.BaseEstimator):
    def __init__(self, learning_rate=1e-4, num_epochs=100, random_state=1234, verbose=False):
        self._params = dict(
            learning_rate=learning_rate,
            num_epochs=num_epochs,
            random_state=random_state
        )
        self.verbose = 2 if verbose else 0
        # 0 = silent, 1 = progress bar, 2 = one line per epoch
        self._model = None

    def get_params(self, deep=False):
        return self._params

    @staticmethod
    def __to_ndarray(src):
        src = np.asarray(src, dtype=np.float64)
        if src.ndim == 1:
            src = np.expand_dims(src, axis=1)
        return src

    def __convert_to_fit(self, x, y):
        if isinstance(x, tuple):
            x, y = x
        y = self.__to_ndarray(y)
        if hasattr(x, 'shape'):
            x = self.__to_ndarray(x)
            x = np.concatenate(
                (x[:-1,...], y[:-1,...]), axis=1)
        else:
            x = y[:-1,...]
        y = y[1:, ...]
        return x, y

    def __convert_to_predict(self, x):
        if isinstance(x, tuple):
            x, y, _ = x
            x = self.__to_ndarray(x)
            y = self.__to_ndarray(y)
            x = np.concatenate((x, y), axis=1)
        else:
            x = self.__to_ndarray(x)
        return x

    @staticmethod
    def __get_sizes(data):
        input_size = data.shape[1]
        layer_sizes = min(
            int(np.exp(data.shape[1]) + 1),
            _MAX_LAYER_SIZE
        )
        layer_sizes = max(layer_sizes, _MIN_LAYER_SIZE)
        return input_size, layer_sizes

    def fit(self, x, y):
        np.random.seed(88)

        x, y = self.__convert_to_fit(x, y)
        model = self._build_model(*self.__get_sizes(x))

        model, early_stopper = self._add_trainers(model)

        model.fit(x, y, batch_size=1, shuffle=False, verbose=self.verbose,
                  epochs=self._params['num_epochs'], callbacks=[early_stopper])
        self._model = model
        return self

    def predict(self, x):
        x = self.__convert_to_predict(x)
        return self._model.predict(x)[:, 0]

    @staticmethod
    def _build_model(input_size, layer_sizes):
        inputs = Input(shape=(input_size,), dtype=_DTYPE)
        initializer = 'lecun_uniform'
        # 'lecun_uniform' 'glorot_uniform' 'he_uniform'
        through = Dense(layer_sizes, activation='elu', dtype=_DTYPE,
                        kernel_initializer=initializer)(inputs)
        through = Reshape((1, layer_sizes))(through)
        through = LSTM(layer_sizes, activation='elu', dtype=_DTYPE,
                       input_shape=(1, layer_sizes),
                       kernel_initializer=initializer)(through)
        outputs = Dense(1, activation='linear', dtype=_DTYPE)(through)

        model = Model(inputs=inputs, outputs=outputs)
        # model.summary()
        return model

    def _add_trainers(self, model):
        optimizer = Adam(lr=self._params['learning_rate'])
        # 'mse' 'mae' 'mape' 'msle'
        model.compile(loss='mae', optimizer=optimizer)
        early_stopper = EarlyStopping(monitor='loss', patience=2, verbose=self.verbose,
                                      restore_best_weights=True)
        return model, early_stopper

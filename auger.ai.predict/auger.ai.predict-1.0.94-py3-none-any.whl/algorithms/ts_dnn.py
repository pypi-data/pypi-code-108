import numpy as np
import sklearn.base

from tensorflow.compat.v1.keras.engine.input_layer import Input
from tensorflow.compat.v1.keras.models import Model
from tensorflow.compat.v1.keras import backend as K
from tensorflow.compat.v1.keras.layers import Conv2D, PReLU, Lambda, Add
from tensorflow.compat.v1.keras import regularizers
from tensorflow.compat.v1.keras.optimizers import Adam
from tensorflow.compat.v1.keras.callbacks import EarlyStopping, ReduceLROnPlateau

_DTYPE = np.float64

#############################################################
#                   DEFINE THE LAYERS
#############################################################

class DilatedConv1D(object):
    """ Creates a dilated convolutional layer
        Args:
            x: input
            rnd: a random number generator used to initialize weights
            dilation: the dilation factor for each layer
            filter_height: the samples that are included in each convolution, after dilating through height
            filter_width: the samples that are included in each convolution, after dilating through width
            n_filters: how many filters to learn for the dilated convolution
            n_channels: number of channels in input data
            apply_bias: boolean, it is set to True to use bias term by default
            activation: the activation function, `linear` by default
    """
    def __init__(self, x, rnd, dilation, filter_height, filter_width, n_filters, n_channels, apply_bias=True,
                 activation='linear', reg_rate=1e-3):
        self.input = x
        self.dilation = dilation
        self.filterHeight = filter_height
        self.filterWidth = filter_width
        self.nFilters = n_filters
        self.nChannels = n_channels

        # Initialization of filter for each layer of size:
        # (n_filters, n_channels in input, filter_height, filter_width)
        if activation == 'tanh':
            def initializer(shape, dtype=None):
                return K.random_uniform(minval=-np.sqrt(6) / np.sqrt(2 * filter_width * n_filters),
                                        maxval=np.sqrt(6) / np.sqrt(2 * filter_width * n_filters),
                                        shape=shape, dtype=dtype, seed=rnd)
        elif activation == 'sigmoid':
            def initializer(shape, dtype=None):
                return K.random_uniform(minval=-4 * np.sqrt(6) / np.sqrt(2 * filter_width * n_filters),
                                        maxval=4 * np.sqrt(6) / np.sqrt(2 * filter_width * n_filters),
                                        shape=shape, dtype=dtype, seed=rnd)
        elif activation == 'relu':
            def initializer(shape, dtype=None):
                return K.random_normal(mean=0.0,
                                       stddev=np.sqrt(2) / np.sqrt(filter_width * n_filters),
                                       shape=shape, dtype=dtype, seed=rnd)
        else:
            def initializer(shape, dtype=None):
                return K.random_uniform(minval=-np.sqrt(6) / np.sqrt(filter_width * n_filters),
                                        maxval=np.sqrt(6) / np.sqrt(filter_width * n_filters),
                                        shape=shape, dtype=dtype, seed=rnd)

        result = Conv2D(n_filters, (filter_height, filter_width), dilation_rate=(1, dilation),
                        kernel_initializer=initializer, use_bias=apply_bias,
                        activity_regularizer=regularizers.l2(reg_rate),
                        data_format = "channels_first")(x)

        self.output = result

#############################################################
#                    BUILD THE MODEL
#############################################################

class WaveNetCond(object):
    def __init__(self, input_x, rnd, n_cond, n_stacks, dilations, n_filters, filter_width, n_channels,
                 reg_rate):
        # Input shape is (n_batches = 1, n_channels, 1, N)
        self.result = input_x
        self.L2 = 0

        # Define apply_bias and activation used in DilatedConv1D layer
        apply_bias = True
        activation = 'relu'

        for s in range(n_stacks):
            for i in range(len(dilations)):
                original_x = self.result

                output = DilatedConv1D(self.result, rnd, dilations[i], 1, filter_width, n_filters, n_channels,
                                       apply_bias, activation, reg_rate)
                self.result = PReLU(shared_axes=[2, 3])(output.output)

                # Add a residual connection from original_x to output
                output = DilatedConv1D(original_x, rnd, 1, 1, 1, n_filters, n_channels,
                                       apply_bias, activation, reg_rate)
                original_x = output.output

                n_channels = n_filters
                if filter_width == 1:
                    lam = Lambda(lambda x: x[..., :])(original_x)
                    self.result = Add()([self.result, lam])
                else:
                    lam = Lambda(lambda x: x[..., dilations[i]:])(original_x)
                    self.result = Add()([self.result, lam])

        # End with a 1x1 convolution, to reduce n_channels back to n_cond
        output = DilatedConv1D(self.result, rnd, 1, 1, 1, n_cond, n_channels, apply_bias, reg_rate)

        self.resultFull = output.output
        self.result = Lambda(lambda x: x[..., 0:-1])(output.output)


class DeepTimeSeriesRegressor(sklearn.base.BaseEstimator):
    def __init__(self, n_stacks=1, normalize=True, learning_rate=1e-2, reg_rate=1e-3,
                 train_iters=20000, random_state=1234, verbose=False):
        self._params = dict(
            n_stacks=n_stacks,
            normalize=normalize,
            learning_rate=learning_rate,
            reg_rate=reg_rate,
            train_iters=train_iters,
            random_state=random_state
        )
        self._predict_fn = None
        self._train_data_tail = None
        self._rec_field = None
        self._n_cond = None

        self._train_mean = None
        self._train_std = None
        self.verbose = verbose
        self._model = None

    def get_params(self, deep=False):
        return self._params

    @staticmethod
    def __to_ndarray(src):
        src = np.asarray(src, dtype=_DTYPE)
        if src.ndim == 1:
            src = np.expand_dims(src, axis=1)
        return src

    def __convert_to_fit(self, x, y):
        if isinstance(x, tuple):
            x, y = x
        y = self.__to_ndarray(y)
        if hasattr(x, 'shape'):
            x = self.__to_ndarray(x)

        data = y
        if hasattr(x, 'shape'):
            data = np.concatenate((data, x), axis=1)
        return data

    def _to_norm(self, data, store_moments=False):
        if store_moments:
            self._train_mean = np.mean(data)
            self._train_std = np.std(data)
            if self._train_std < 1e-8:
                self._train_std = 1e-8
        return (data - self._train_mean) / self._train_std

    def _from_norm(self, data):
        if self._train_std is None:
            raise Exception("Mean & std wasn't stored at training stage!")
        return data * self._train_std + self._train_mean

    def _to_data_transform(self, data):
        n_samples = data.shape[0]
        data = np.swapaxes(data, 0, 1)
        data = data.reshape((1, self._n_cond, 1, n_samples))

        return np.append(np.zeros(shape=(data.shape[:-1] + (self._rec_field,)), dtype=_DTYPE), data, axis=-1)

    def fit(self, x, y):
        data = self.__convert_to_fit(x, y)
        self._n_cond = data.shape[1]

        model, callbacks = self._build_model()

        self._train_data_tail = data[-self._rec_field:, ...]

        if self._params['normalize']:
            data = self._to_norm(data, store_moments=True)

        data = self._to_data_transform(data)

        model.fit(data, data, batch_size=1, shuffle=False, verbose=self.verbose,
                  epochs=self._params['train_iters'], callbacks=callbacks)

        self._model = model
        return self

    def __convert_to_predict(self, x):
        cut = True
        if isinstance(x, tuple):
            x, y, cut = x
            x = self.__to_ndarray(x)
            y = self.__to_ndarray(y)
            x = np.concatenate((y, x), axis=1)
        else:
            x = self.__to_ndarray(x)
        return np.concatenate((self._train_data_tail, x)), cut

    def _from_data_transform(self, data):
        data = np.reshape(data, (self._n_cond, data.shape[-1]))
        return np.swapaxes(data, 0, 1)

    def predict(self, x):
        data, cut = self.__convert_to_predict(x)

        if self._params['normalize']:
            data = self._to_norm(data)
        data = self._to_data_transform(data)

        predicts = self._model.predict(data)[..., self._train_data_tail.shape[0]:]
        if cut:
            predicts = predicts[..., :-1]

        predicts = self._from_data_transform(predicts)
        if self._params['normalize']:
            predicts = self._from_norm(predicts)

        if predicts.ndim == 2:
            predicts = predicts[:, 0]
        elif predicts.ndim > 2:
            raise ValueError("Dimension ERROR, predictions should have 1D or 2D shape")

        return np.asarray(predicts)

    @staticmethod
    def _compute_receptive_field(n_stacks, dilation, filter_width):
        """ Helper function to compute receptive field """
        if filter_width > 1:
            receptive_field = n_stacks * (dilation * filter_width) - (n_stacks - 1)
        else:
            receptive_field = 1
        return receptive_field

    def _build_model(self):
        # Set intermediate parameters
        rnd = self._params['random_state']
        n_stacks = self._params['n_stacks']
        reg_rate = self._params['reg_rate']
        lr = self._params['learning_rate']
        n_filters = n_channels = n_cond = self._n_cond
        dilations = [1, 2, 4]
        filter_width = 2
        np.random.seed(rnd)

        # Define receptive filed to correct the input from the left
        self._rec_field = rc = self._compute_receptive_field(n_stacks, dilations[-1], filter_width)

        # Define inputs and the model
        input_x = Input(batch_shape=(1, n_cond, 1, None))
        model = WaveNetCond(input_x, rnd, n_cond, n_stacks, dilations, n_filters, filter_width, n_channels,
                            reg_rate)

        nn = Model(inputs=input_x, outputs=model.resultFull)
        optimizer = Adam(lr=lr)
        def loss(y_true, y_pred):
            return K.sum(K.abs(input_x[..., rc:] - model.result))
        nn.compile(loss=loss, optimizer=optimizer)
        early_stopper = EarlyStopping(monitor='loss', patience=200, verbose=self.verbose,
                                      restore_best_weights=True)
        lr_reducer = ReduceLROnPlateau(
            monitor='loss', factor=0.5, patience=50,
            verbose=self.verbose, mode='auto', cooldown=0, min_lr=0)
        return nn, [early_stopper, lr_reducer]

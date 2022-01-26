import sys
import numpy as np
import sklearn.base
import theano as th
import theano.tensor as tns
from auger_ml.algorithms.utils import adam


sys.setrecursionlimit(100000)
_DTYPE = np.float64


#############################################################
#                   DEFINE THE LAYERS
#############################################################

class PReLU(object):
    """ PReLU activation """
    def __init__(self, x):
        i_alpha = 0
        self.alpha = th.shared(value=i_alpha, borrow=True)
        self.result = tns.switch(x < 0, self.alpha * x, x)
        self.params = [self.alpha]


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
                 activation='linear'):
        self.input = x
        self.dilation = dilation
        self.filterHeight = filter_height
        self.filterWidth = filter_width
        self.nFilters = n_filters
        self.nChannels = n_channels

        # Initialization of filter for each layer of size:
        # (n_filters, n_channels in input, filter_height, filter_width)
        if activation == 'tanh':
            i_filters = rnd.uniform(-np.sqrt(6) / np.sqrt(2 * filter_width * n_filters),
                                    np.sqrt(6) / np.sqrt(2 * filter_width * n_filters),
                                    [n_filters, n_channels, filter_height, filter_width]).astype(_DTYPE)
        elif activation == 'sigmoid':
            i_filters = rnd.uniform(-4 * np.sqrt(6) / np.sqrt(2 * filter_width * n_filters),
                                    4 * np.sqrt(6) / np.sqrt(2 * filter_width * n_filters),
                                    [n_filters, n_channels, filter_height, filter_width]).astype(_DTYPE)
        elif activation == 'relu':
            i_filters = rnd.normal(0, np.sqrt(2) / np.sqrt(filter_width * n_filters),
                                   [n_filters, n_channels, filter_height, filter_width]).astype(_DTYPE)
        else:
            i_filters = rnd.uniform(-np.sqrt(6) / np.sqrt(filter_width * n_filters),
                                    np.sqrt(6) / np.sqrt(filter_width * n_filters),
                                    [n_filters, n_channels, filter_height, filter_width]).astype(_DTYPE)

        self.filters = th.shared(value=i_filters, borrow=True)
        # Convolve input feature map with filters
        result = tns.nnet.conv2d(self.input, self.filters, border_mode='valid',
                                 filter_dilation=(1, self.dilation))
        # Check for bias
        if apply_bias:
            # Define bias
            i_bias = np.zeros([n_filters], dtype=_DTYPE)
            self.bias = th.shared(value=i_bias, borrow=True)
            # Store parameters of this layer
            self.params = [self.filters, self.bias]
            # Apply bias
            result += self.bias[None, :, None, None]
        else:
            self.params = [self.filters]

        self.output = result


#############################################################
#                    BUILD THE MODEL
#############################################################

class WaveNetCond(object):
    def __init__(self, input_x, rnd, n_cond, n_stacks, dilations, n_filters, filter_width, n_channels):
        # Input shape is (n_batches = 1, n_channels, 1, N)
        self.result = input_x
        self.params = []
        self.L2 = 0

        # Define apply_bias and activation used in DilatedConv1D layer
        apply_bias = True
        activation = 'relu'

        for s in range(n_stacks):
            for i in range(len(dilations)):
                original_x = self.result

                # Input will have n_channels channels, output will have n_filters channels
                output = DilatedConv1D(self.result, rnd, dilations[i], 1, filter_width, n_filters, n_channels,
                                       apply_bias, activation)
                self.params += output.params
                # Use regularization -> L2
                self.L2 += 0.5 * tns.sum(tns.sqr(output.params[0]))

                output_prelu = PReLU(output.output)
                self.result = output_prelu.result

                # Add a residual connection from original_x to output
                output = DilatedConv1D(original_x, rnd, 1, 1, 1, n_filters, n_channels,
                                       apply_bias, activation)
                self.params += output.params
                # Use regularization -> L2
                self.L2 += 0.5 * tns.sum(tns.sqr(output.params[0]))

                original_x = output.output
                n_channels = n_filters

                if filter_width == 1:
                    self.result += original_x[..., :]
                else:
                    self.result += original_x[..., dilations[i]:]

        # End with a 1x1 convolution, to reduce n_channels back to n_cond
        output = DilatedConv1D(self.result, rnd, 1, 1, 1, n_cond, n_channels, apply_bias)
        self.params += output.params
        # Use regularization -> L2
        self.L2 += 0.5 * tns.sum(tns.sqr(output.params[0]))

        self.resultFull = output.output
        self.result = self.resultFull[..., 0:-1]


class DeepTimeSeriesRegressor(sklearn.base.BaseEstimator):
    def __init__(self, n_stacks=1, normalize=True, use_lag=False, learning_rate=1e-3, reg_rate=1e-3,
                 train_iters=20000, random_state=1234, verbose=False):
        self._params = dict(
            n_stacks=n_stacks,
            normalize=normalize,
            use_lag=use_lag,
            learning_rate=learning_rate,
            reg_rate=reg_rate,
            train_iters=train_iters,
            random_state=random_state
        )
        self._predict_fn = None
        self._train_data_tail = None
        self._rec_field = None
        self._n_cond = None

        self._lag_init_values = None
        self._train_mean = None
        self._train_std = None
        self.verbose = verbose

    def fit(self, x, y):
        if isinstance(x, tuple):
            x, y = x

        if hasattr(x, 'shape'):     # assume that it is `pandas df` or `np ndarray`
            x = np.asarray(x, dtype=_DTYPE)
            if x.ndim == 1:
                x = np.expand_dims(x, axis=1)

        y = np.asarray(y, dtype=_DTYPE)
        if y.ndim == 1:
            y = np.expand_dims(y, axis=1)

        data = y
        if hasattr(x, 'shape'):
            data = np.concatenate((data, x), axis=1)

        self._n_cond = data.shape[1]

        train_fn = self._build_model()
        self._train_data_tail = data[-self._rec_field:, ...]

        if self._params['use_lag']:
            data = self._to_lag(data)

        if self._params['normalize']:
            data = self._to_norm(data, store_moments=True)

        data = self._to_data_transform(data)
        for j in range(0, self._params['train_iters']):
            cost = train_fn(data)
            if self.verbose and j % 1000 == 0:
                print(j, cost)

        return self

    @staticmethod
    def __to_ndarray(src):
        src = np.asarray(src, dtype=_DTYPE)
        if src.ndim == 1:
            src = np.expand_dims(src, axis=1)
        return src

    def predict(self, x):
        cut = True
        if isinstance(x, tuple):
            x, y, cut = x
            x = self.__to_ndarray(x)
            y = self.__to_ndarray(y)
            data = np.concatenate((y, x), axis=1)
        else:
            data = self.__to_ndarray(x)
        data = np.concatenate((self._train_data_tail, data))

        if self._params['use_lag']:
            data = self._to_lag(data)

        if self._params['normalize']:
            data = self._to_norm(data)

        data = self._to_data_transform(data)

        predicts = self._predict_fn(data)[..., self._train_data_tail.shape[0]:]
        if cut:
            predicts = predicts[..., :-1]

        predicts = self._from_data_transform(predicts)

        if self._params['normalize']:
            predicts = self._from_norm(predicts)

        if self._params['use_lag']:
            predicts = self._from_lag(predicts)

        if predicts.ndim == 2:
            predicts = predicts[:, 0]
        elif predicts.ndim > 2:
            raise ValueError("Dimension ERROR, predictions should have 1D or 2D shape")

        return np.asarray(predicts)

    def get_params(self, deep=False):
        return self._params

    @staticmethod
    def _compute_receptive_field(n_stacks, dilation, filter_width):
        """ Helper function to compute receptive field """
        if filter_width > 1:
            receptive_field = n_stacks * (dilation * filter_width) - (n_stacks - 1)
        else:
            receptive_field = 1
        return receptive_field

    def _to_data_transform(self, data):
        n_samples = data.shape[0]
        data = np.swapaxes(data, 0, 1)
        data = data.reshape((1, self._n_cond, 1, n_samples))

        return np.append(np.zeros(shape=(data.shape[:-1] + (self._rec_field,)), dtype=_DTYPE), data, axis=-1)

    def _from_data_transform(self, data):
        data = np.reshape(data, (self._n_cond, data.shape[-1]))
        return np.swapaxes(data, 0, 1)

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

    def _to_lag(self, data):
        out_data = np.zeros_like(data, dtype=_DTYPE)
        self._lag_init_values = data[0, ...]

        for row in range(1, data.shape[0]):
            prev_values = data[row - 1, ...]
            denominator = np.copy(prev_values)
            denominator[np.abs(denominator) < 1e-8] = 1.
            out_data[row, ...] = (data[row, ...] - prev_values) / denominator

        return out_data

    def _from_lag(self, data):
        out_data = np.zeros_like(data, dtype=_DTYPE)
        out_data[0, ...] = self._lag_init_values

        for row in range(1, data.shape[0]):
            out_data[row, ...] = (data[row, ...] + 1.) * out_data[row - 1, ...]

        return out_data

    def _build_model(self):
        # Set intermediate parameters
        rnd = np.random.RandomState(self._params['random_state'])
        n_stacks = self._params['n_stacks']
        reg_rate = self._params['reg_rate']
        lr = self._params['learning_rate']
        n_filters = n_channels = n_cond = self._n_cond
        dilations = [1, 2, 4]
        filter_width = 2

        # Define receptive filed to correct the input from the left
        self._rec_field = self._compute_receptive_field(n_stacks, dilations[-1], filter_width)

        # Define inputs and the model
        input_x = tns.tensor4('input', dtype='float64')
        model = WaveNetCond(input_x, rnd, n_cond, n_stacks, dilations, n_filters, filter_width, n_channels)

        # Define cost function and updates procedure
        cost = tns.sum(tns.abs_(input_x[..., self._rec_field:] - model.result)) + reg_rate * model.L2
        grads = tns.grad(cost, model.params)
        updates = adam(grads, model.params, learning_rate=lr)

        # Define the test and train functions
        train_fn = th.function(
            [input_x],
            cost,
            updates=updates,
            on_unused_input='warn'
        )

        self._predict_fn = th.function(
            [input_x],
            model.resultFull,
            # updates=updates,
            on_unused_input='warn'
        )
        return train_fn

from celery.utils.log import get_task_logger
logging = get_task_logger(__name__)

from auger_ml.algorithms.dnn_base import DeepNeuralNetworkBase, DeepNeuralNetworkClassifier, DeepNeuralNetworkRegressor


class ShapedDeepNeuralNetworkBase(DeepNeuralNetworkBase):
    def __init__(self, **kwargs):
        # Fill specific shaped NN params
        self.num_layers = kwargs.get('num_layers', 0)
        self.shape = kwargs.get('shape', 'funnel')
        self.max_neurons = kwargs.get('max_neurons', 32)
        self.dropout_rate = kwargs.get('dropout_rate', '0.05')
        self.activation = kwargs.get('activation', 'relu')
        self.layer_initializer = kwargs.get('layer_initializer', 'glorot_uniform')

        # Fill parent params, some will be empty
        super(ShapedDeepNeuralNetworkBase, self).__init__(**kwargs)

    def get_params(self, deep=True):
        params = super(ShapedDeepNeuralNetworkBase, self)._get_shared_params()
        params['num_layers'] = self.num_layers
        params['shape'] = self.shape
        params['max_neurons'] = self.max_neurons
        params['dropout_rate'] = self.dropout_rate
        params['activation'] = self.activation
        params['layer_initializer'] = self.layer_initializer

        return params

    def _infer_last_layer(self, X, y):
        # We need to know the number of categories before building shapes of other layers
        super(ShapedDeepNeuralNetworkBase, self)._infer_last_layer(X, y)

        # Now we fill per-layer parameters that will be used later by _build_model()
        # So far we have:
        #     self.num_inpouts_
        #     self.last_layer_size_
        #     self.max_neurons
        # We need to populate:
        #     self.layer_sizes
        #     self.layer_acts
        #     self.layer_drops
        #     self.layer_initializers

        if self.shape == 'funnel':
            self.layer_sizes += get_funnel(first=self.max_neurons, last=self.last_layer_size_, k=self.num_layers)

        elif self.shape == 'long_funnel':
            if self.num_layers % 2 == 1:
                self.layer_sizes.append(self.max_neurons)

            for i in range(self.num_layers // 2):
                self.layer_sizes.append(self.max_neurons)

            self.layer_sizes += get_funnel(first=self.max_neurons, last=self.last_layer_size_, k=self.num_layers)[1:]

        elif self.shape == 'brick':
            for i in range(self.num_layers):
                self.layer_sizes.append(self.max_neurons)

        elif self.shape == 'triangle':
            self.layer_sizes.append(1)
            self.layer_sizes += reversed(get_funnel(first=self.max_neurons,
                                                    last=self.last_layer_size_,
                                                    k=self.num_layers)[:-1])

        elif self.shape == 'rhombus':
            k = self.num_layers // 2
            if self.num_layers % 2 == 1:
                k += 1

            l1 = get_linear_funnel(first=1,
                                   last=self.max_neurons,
                                   k=k)
            l2 = l1[:]
            if self.num_layers % 2 == 1:
                l2.pop()
            l2.reverse()

            self.layer_sizes += l1 + l2

        elif self.shape == 'diamond':
            for i in range(self.num_layers // 2):
                self.layer_sizes.append(self.max_neurons * self.num_layers // (self.num_layers - 1))
            if self.num_layers % 2 == 1:
                self.layer_sizes.append(self.max_neurons)
            self.layer_sizes += get_funnel(first=self.max_neurons,
                                           last=self.last_layer_size_,
                                           k=self.num_layers // 2)
        elif self.shape == 'stairs':
            if self.num_layers < 2:
                self.layer_sizes.append(self.max_neurons)
            else:
                if self.num_layers % 2 == 1:
                    self.layer_sizes.append(self.max_neurons)
                l = [i for i in range(self.max_neurons, self.max_neurons - self.num_layers // 2 - 2, -2) for _ in range(2)]
                self.layer_sizes += l
        else:
            logging.error("Unsupported DNN shape: {}.".format(self.shape))

        for _ in self.layer_sizes:
            self.layer_acts.append(self.activation)
            self.layer_initializers.append(self.layer_initializer)
            self.layer_drops.append(self.dropout_rate)

        logging.info("shape: {}, layer_sizes: {}".format(self.shape, self.layer_sizes))


def get_funnel(first, last, k, q=2):
    # Parameterized funnel shape with exponential decrease.
    # Use power for simplicity, since k will be small.
    return [int((first - last) // (q**n)) + last for n in range(k)]


def get_linear_funnel(first, last, k):
    # Parameterized funnel shape with linear decrease.
    return [first - int(n * (first - last) // (k-1)) for n in range(k)]


class ShapedDeepNeuralNetworkClassifier(ShapedDeepNeuralNetworkBase, DeepNeuralNetworkClassifier):
    pass


class ShapedDeepNeuralNetworkRegressor(ShapedDeepNeuralNetworkBase, DeepNeuralNetworkRegressor):
    pass

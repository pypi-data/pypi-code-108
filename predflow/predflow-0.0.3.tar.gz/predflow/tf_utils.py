'''
General tensorflow utilities.

- Custom tensorflow modules
- Simple general tensorflow operations (e.g. :py:func:`reduced_batched_outer_product`)
- tensorboard utilities
'''


import tensorflow as tf

class Dense(tf.Module):
    """Unbiased dense layer, :code:`y = W * f(x)`

    :param input_dim: dimension of the layer's input
    :type input_dim: int
    :param output_size: dimension of the layer's output
    :type output_size: int
    :param name: custom name for the layer, defaults to None
    :type name: str, optional
    :param activation: activation function, defaults to tf.nn.relu
    :type activation: function, optional
    :param stddev: standard deviation of the normal initialization, defaults to .001
    :type stddev: float, optional
    """

    def __init__(self, input_dim, output_size, name=None, activation=tf.nn.relu, stddev=.001):
        super(Dense, self).__init__(name=name)
        self.w = tf.Variable(tf.random.normal([output_size, input_dim], stddev=stddev), name='w')
        self.activation = activation
        
    def __call__(self, x):
        """Path through layer

        :param x: input
        :type x: 3d tf.Tensor of float32
        :return: output
        :rtype: 3d tf.Tensor of float32
        """
        
        return tf.matmul(self.w, self.activation(x)) 
    
class PrecisionModulatedDense(tf.Module):

    def __init__(self, input_dim, output_size, name=None, activation=tf.nn.relu, stddev=.001):
        super(PrecisionModulatedDense, self).__init__(name=name)
        self.w = tf.Variable(tf.random.normal([output_size, input_dim], mean=0.05, stddev=stddev), name='w')
        self.P = tf.Variable(tf.eye(output_size), name='P')
        self.activation = activation
        
    def __call__(self, x):
        return tf.matmul(self.w, self.activation(x)) 
    
class BiasedDense(tf.Module):
    """Biased dense layer, :code:`y = W * f(x) + b`

    :param input_dim: dimension of the layer's input
    :type input_dim: int
    :param output_size: dimension of the layer's output
    :type output_size: int
    :param name: custom name for the layer, defaults to None
    :type name: str, optional
    :param activation: activation function, defaults to tf.nn.relu
    :type activation: function, optional
    :param stddev: standard deviation of the normal initialization, defaults to .001
    :type stddev: float, optional
    """
        
    def __init__(self, input_dim, output_size, name=None, activation=tf.nn.relu, stddev=.001):
        super(BiasedDense, self).__init__(name=name)
        self.w = tf.Variable(tf.random.normal([output_size, input_dim], stddev=stddev), name='w')
        self.b = tf.Variable(tf.zeros([output_size,1]), name='b')
        self.activation = activation
        
    def __call__(self, x):
        """Path through layer

        :param x: input
        :type x: 3d tf.Tensor of float32
        :return: output
        :rtype: 3d tf.Tensor of float32
        """
        
        return tf.matmul(self.w, self.activation(x)) + self.b

def load_tensorboard_graph(logdir, func, args, name, step=0, kwargs={}):
    """Log the tensorboard graph trace of :code:`func(*args, **kwargs)`

    :param logdir: log folder path
    :type logdir: str
    :param func: function to analyze
    :type func: function
    :param args: arguments of func
    :type args: list
    :param name: name of the tensorboard trace
    :type name: str
    :param step: tensorboard step, defaults to 0
    :type step: int, optional
    :param kwargs: kwargs of func, defaults to {}
    :type kwargs: dict, optional
    """
    
    writer = tf.summary.create_file_writer(logdir)
    tf.summary.trace_on()
    func(*args, **kwargs)
    with writer.as_default():
        tf.summary.trace_export(
            name=name,
            step=step,
            profiler_outdir=logdir)

def reduced_batched_outer_product(x, y):
    """Compute the outer product of :code:`x` and :code:`y` summed over batch dimesion 

    :param x: first tensor
    :type x: 3d tf.Tensor
    :param y: second tensor
    :type y: 3d tf.Tensor
    :return: outer product summed over batch dimesion 
    :rtype: 2d tf.Tensor
    """
    
    with tf.name_scope("ReducedBatchedOuterProduct"):
        return tf.reduce_sum(tf.einsum('nx,ny->nxy', tf.squeeze(x), tf.squeeze(y)), 0)

def relu_derivate(x):
    """Derivate of the ReLU activation function

    :param x: input
    :type x: tf.Tensor
    :return: output
    :rtype: tf.Tensor
    """
    
    with tf.name_scope("ReLUDerivate"):
        return tf.cast(tf.greater(x, tf.constant(0.)), tf.float32)
    
def tanh_derivate(x):
    """Derivate of the ReLU activation function

    :param x: input
    :type x: tf.Tensor
    :return: output
    :rtype: tf.Tensor
    """
    
    with tf.name_scope("tanhDerivate"):
        return tf.cast(1.0-tf.square(tf.nn.tanh(x)), tf.float32)

def mlp(*args, biased=False, reversed_flow=False, activation=tf.nn.relu, stddev=0.01, only_return_variables=False, precision_modulated=False):
    """Create a multi-layer perceptron

    :param args: sequence of int representing layer sizes
    :param biased: controls weither we use bias in layers, defaults to False
    :type biased: bool, optional
    :param reversed_flow: controls weither we reverse the flow of activation (default is bottom-up), defaults to False
    :type reversed_flow: bool, optional
    :param activation: activation function, defaults to tf.nn.relu
    :type activation: function, optional
    :param stddev: standard deviation of the normal initialization, defaults to 0.01
    :type stddev: float, optional
    :param only_return_weights: controls weither we return a list of tf.Module or 2d variable weight matrices, defaults to False
    :type only_return_weights: bool, optional
    :return: model
    :rtype: list of :py:class:`tf_utils.Dense` or :py:class:`tf_utils.BiasedDense` or 2d variable tf.Tensor of float32
    """
    
    if precision_modulated:
        Layer = PrecisionModulatedDense
    elif biased:
        Layer = BiasedDense
    else:
        Layer=Dense
    if only_return_variables:
        if not reversed_flow:
            if not precision_modulated:
                return [tf.Variable(tf.random.normal([s2, s1], stddev=stddev)) for (s1, s2) in zip(list(args)[:-1], list(args)[1:])]
            else:
                return ([tf.Variable(tf.random.normal([s2, s1], stddev=stddev)) for (s1, s2) in zip(list(args)[:-1], list(args)[1:])], 
                        [tf.Variable(tf.eye(s2)) for s2 in list(args)[1:]])
        else:
            if not precision_modulated:
                return [tf.Variable(tf.random.normal([s1, s2], stddev=stddev)) for (s1, s2) in zip(list(args)[:-1], list(args)[1:])]
            else:
                return ([tf.Variable(tf.random.normal([s1, s2], stddev=stddev)) for (s1, s2) in zip(list(args)[:-1], list(args)[1:])], 
                        [tf.Variable(tf.eye(s1)) for s1 in list(args)[:-1]])
    else:
        if not reversed_flow:
            return [Layer(s1, s2, activation=activation, stddev=stddev) for (s1, s2) in zip(list(args)[:-1], list(args)[1:])]
        else:
            return [Layer(s2, s1, activation=activation, stddev=stddev) for (s1, s2) in zip(list(args)[:-1], list(args)[1:])]


def one_hot_pred_accuracy(p, t, axis=1):
    """Compute the accuracy of a prediction :code:`p` with respect to target :code:`t` as the proportion of time :code:`argmax(p) == argmax(t)`

    :param p: network prediction
    :type p: 3d tf.Tensor
    :param t: ground truth target
    :type t: 3d tf.Tensor
    :param axis: argmax axis, defaults to 1
    :type axis: int, optional
    :return: accuracy
    :rtype: float32
    """
    
    with tf.name_scope("AccuracyComputation"):
        return tf.cast(tf.math.count_nonzero(tf.argmax(p, axis=axis) == tf.argmax(t, axis=axis)), tf.int32)/tf.shape(p)[0]
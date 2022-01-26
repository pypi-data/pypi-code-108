'''
Utilities for predictive coding specifically.

- Energy computation and autodifferentiated gradients of energy wrt to representations and learnable parameters  
- Explicit computation of gradients expressed with prediction errors in the nonlinear fully-connected strictly hierarchical case
- Stochastic gradient descent steps on representations and learnable parameters
- Representations initializers (first pass)
'''


import tensorflow as tf 
from tf_utils import reduced_batched_outer_product

def inference_SGD_step(r, ir, g, update_last=True):
    """Stochastic gradient descent step on represnetations (inference) using autodifferentiated gradients

    :param r: representations
    :type r: list of 3d tf.Tensor of float32
    :param ir: inference rate
    :type ir: float32
    :param g: autodiff gradient tape
    :type g: tf.GradientTape
    :param update_last: controls weither representations in the last layer are updated, defaults to True
    :type update_last: bool, optional
    """
    
    N = len(r) - 1
    with tf.name_scope("RepresentationUpdate"):
        for i in range(1, N):
            r[i] -= tf.scalar_mul(ir, g[i]+ 0.00 * r[i])
        if update_last:
            r[N] -= tf.scalar_mul(ir, g[N]+ 0.00 * r[N] )
    
def parameters_SGD_step(theta, lr, g):
    """Stochastic gradient descent step on learnable parameters (learning) using autodifferentiated gradients

    :param theta: learnable parameters
    :type theta: list of variable tf.Tensor of float32
    :param lr: learning rate
    :type lr: float32
    :param g: autodiff gradient tape
    :type g: tf.GradientTape
    """
    
    with tf.name_scope("ParametersUpdate"):
        for i in range(len(theta)):
            theta[i].assign_add(tf.scalar_mul(lr, -g[i]- 0.00 * theta[i]))
    
def energy_and_error(model, r, theta=[], predictions_flow_upward=False):
    """Energy (total squared L2 norm of errors) computation and autodifferentiation with respect to representations and learnable parameters

    :param model: description of a sequential network by a list of layers, can be generated e.g. using :py:func:`tf_utils.mlp`
    :type model: list of :py:class:`tf_utils.Dense` or :py:class:`tf_utils.BiasedDense`
    :param r: representations
    :type r: list of 3d tf.Tensor of float32
    :param theta: learnable parameters, defaults to []
    :type theta: list of variable tf.Tensor of float32, optional
    :param predictions_flow_upward: direction of prediction flow, defaults to False
    :type predictions_flow_upward: bool, optional
    :return: energy, autodiff gradient tape
    :rtype: float32, tf.GradientTape
    """
    
    with tf.name_scope("EnergyComputation"):
        F = tf.zeros(())
        with tf.GradientTape(persistent=True, watch_accessed_variables=False) as tape:
            tape.watch(r+theta)
            for i in range(len(model)):
                if predictions_flow_upward:
                    F += 0.5 * tf.reduce_sum(tf.square(tf.subtract(r[i+1], model[i](r[i]))), 1)
                else:
                    F += 0.5 * tf.reduce_sum(tf.square(tf.subtract(r[i], model[i](r[i+1]))), 1)
        return F, tape
    
def forward_initialize_representations(model, data, target=None):
    """Initial representations with a forward sweep through the model

    :param model: description of a sequential network by a list of layers, can be generated e.g. using :py:func:`tf_utils.mlp`
    :type model: list of :py:class:`tf_utils.Dense` or :py:class:`tf_utils.BiasedDense`
    :param data: inuput data batch
    :type data: 3d tf.Tensor of float32
    :param target: output target batch, defaults to None
    :type target: 3d tf.Tensor of float32, optional
    :return: representations
    :rtype: list of 3d tf.Tensor of float32
    """
    
    with tf.name_scope("Initialization"):
        N = len(model)
        representations = [data,]
        for i in range(N-1):
            representations.append(model[i](representations[-1]))
        if target is not None:
            representations.append(target)
        else:
            representations.append(model[-1](representations[-1]))
        return representations
    
def backward_initialize_representations(model, target, data=None):
    """Initial representations with a backward sweep through the model

    :param model: description of a sequential network by a list of layers, can be generated e.g. using :py:func:`tf_utils.mlp`
    :type model: list of :py:class:`tf_utils.Dense` or :py:class:`tf_utils.BiasedDense`
    :param target: output target batch
    :type target: 3d tf.Tensor of float32
    :param data: inuput data batch, defaults to None
    :type data: 3d tf.Tensor of float32, optional
    :return: representations
    :rtype: list of 3d tf.Tensor of float32
    """
    
    with tf.name_scope("Initialization"):
        N = len(model)
        representations = [target,]
        for i in reversed(range(1, N)):
            representations.insert(0, model[i](representations[0]))
        if data is not None:
            representations.insert(0, data)
        else:
            representations.insert(0, model[0](representations[0]))
        return representations
    
def random_initialize_representations(model, data, stddev=0.001, predictions_flow_upward=False, target_shape=None):
    """Randomly initialize latent representations 

    :param model: description of a sequential network by a list of layers, can be generated e.g. using :py:func:`tf_utils.mlp`
    :type model: list of :py:class:`tf_utils.Dense` or :py:class:`tf_utils.BiasedDense`
    :param data: inuput data batch
    :type data: 3d tf.Tensor of float32
    :param stddev: standard deviation of the normal initialization, defaults to 0.001
    :type stddev: float, optional
    :param predictions_flow_upward: direction of prediction flow, defaults to False
    :type predictions_flow_upward: bool, optional
    :param target_shape: shape of target minibatch, defaults to None
    :type target_shape: 1d tf.Tensor of int32, optional
    :return: representations
    :rtype: list of 3d tf.Tensor of float32
    """
    
    with tf.name_scope("Initialization"):
        N = len(model)
        if predictions_flow_upward:
            representations = [data,]
            for i in range(N):
                representations.append(tf.random.normal(tf.shape(model[i](representations[-1])), stddev=stddev))
        else:
            representations = [tf.random.normal(target_shape, stddev=stddev),]
            for i in reversed(range(1, N)):
                representations.insert(0, tf.random.normal(tf.shape(model[i](representations[0])),stddev=stddev))
            representations.insert(0, data)
        return representations
    
def zero_initialize_representations(model, data, predictions_flow_upward=False, target_shape=None, bias=tf.constant(0.)):
    """Initialize representations at zero (or a constant)

    :param model: description of a sequential network by a list of layers, can be generated e.g. using :py:func:`tf_utils.mlp`
    :type model: list of :py:class:`tf_utils.Dense` or :py:class:`tf_utils.BiasedDense`
    :param data: inuput data batch
    :type data: 3d tf.Tensor of float32
    :param predictions_flow_upward: direction of prediction flow, defaults to False
    :type predictions_flow_upward: bool, optional
    :param target_shape: shape of target minibatch, defaults to None
    :type target_shape: 1d tf.Tensor of int32, optional
    :param bias: initialize representation with bias rather than 0., defaults to tf.constant(0.)
    :type bias: float32, optional
    :return: representations
    :rtype: list of 3d tf.Tensor of float32
    """
    
    with tf.name_scope("Initialization"):
        N = len(model)
        if predictions_flow_upward:
            representations = [data,]
            for i in range(N):
                representations.append(bias+tf.zeros(tf.shape(model[i](representations[-1]))))
        else:
            representations = [tf.zeros(target_shape)+bias,]
            for i in reversed(range(1, N)):
                representations.insert(0, tf.zeros(tf.shape(model[i](representations[0])))+bias)
            representations.insert(0, data)
        return representations
    
def inference_step_backward_predictions(e, r, w, ir, f, df, update_last=True, update_first=False):
    """Representations update using stochastic gradient descent with analytic expressions
    of the gradients of energy wrt representations, only applicable to an
    unbiased MLP with reversed flow (predictions come from higher layer)

    :param e: prediction errors
    :type e: list of 3d tf.Tensor of float32
    :param r: representations
    :type r: list of 3d tf.Tensor of float32
    :param w: list of weight matrices, can be generated e.g. using :py:func:`tf_utils.mlp`
    :type w: list of 2d tf.Tensor of float32
    :param ir: inference rate
    :type ir: float32
    :param f: activation function
    :type f: function
    :param df: derivate of the activation function
    :type df: function
    :param update_last: controls weither representations in the last layer are updated, defaults to True
    :type update_last: bool, optional
    """
    
    N = len(w)
    with tf.name_scope("PredictionErrorComputation"):
        for i in range(N):
            e[i] = tf.subtract(r[i], tf.matmul(w[i], f(r[i+1])))
    with tf.name_scope("RepresentationUpdate"):
        for i in range(1, N):
            r[i] += tf.scalar_mul(ir, tf.subtract(tf.matmul(w[i-1], e[i-1], transpose_a=True) * df(r[i]), e[i]))
        if update_last:
            r[N] += tf.scalar_mul(ir, tf.matmul(w[N-1], e[N-1], transpose_a=True) * df(r[N]))
        if update_first:
            r[0] += tf.scalar_mul(ir, -e[0])
            
def weight_update_backward_predictions(w, e, r, lr, f):
    """Weight update using stochastic gradient descent with analytic expressions
    of the gradients of energy wrt weights, only applicable to an
    unbiased MLP with reversed flow (predictions come from higher layer)

    :param w: list of weight matrices, can be generated e.g. using :py:func:`tf_utils.mlp`
    :type w: list of 2d tf.Tensor of float32
    :param e: prediction errors
    :type e: list of 3d tf.Tensor of float32
    :param r: representations
    :type r: list of 3d tf.Tensor of float32
    :param lr: learning rate
    :type lr: float32
    :param f: activation function
    :type f: function
    """
    
    with tf.name_scope("WeightUpdate"):
        for i in range(len(w)):
            w[i].assign_add(tf.scalar_mul(lr, reduced_batched_outer_product(e[i], f(r[i+1]))))

def inference_step_forward_predictions(e, r, w, ir, f, df, update_last=True):
    """Representations update using stochastic gradient descent with analytic expressions
    of the gradients of energy wrt representations, only applicable to an
    unbiased MLP (predictions come from lower layer)

    :param e: prediction errors
    :type e: list of 3d tf.Tensor of float32
    :param r: representations
    :type r: list of 3d tf.Tensor of float32
    :param w: list of weight matrices, can be generated e.g. using :py:func:`tf_utils.mlp`
    :type w: list of 2d tf.Tensor of float32
    :param ir: inference rate
    :type ir: float32
    :param f: activation function
    :type f: float32
    :param df: derivate of the activation function
    :type df: function
    :param update_last: controls weither representations in the last layer are updated, defaults to True
    :type update_last: bool, optional
    """
    
    N = len(w)
    with tf.name_scope("PredictionErrorComputation"):
        for i in range(N):
            e[i] = tf.subtract(r[i+1], tf.matmul(w[i], f(r[i])))
    with tf.name_scope("RepresentationUpdate"):
        for i in range(1,N):
            r[i] += tf.scalar_mul(ir, tf.subtract(tf.matmul(w[i], e[i], transpose_a=True) * df(r[i]), e[i-1]))
        if update_last:
            r[N] -= tf.scalar_mul(ir, e[N-1])
            
def weight_update_forward_predictions(w, e, r, lr, f):
    """Weight update using stochastic gradient descent with analytic expressions
    of the gradients of energy wrt weights, only applicable to an
    unbiased MLP (predictions come from lower layer)

    :param w: list of weight matrices, can be generated e.g. using :py:func:`tf_utils.mlp`
    :type w: list of 2d tf.Tensor of float32
    :param e: prediction errors
    :type e: list of 3d tf.Tensor of float32
    :param r: representations
    :type r: list of 3d tf.Tensor of float32
    :param lr: learning rate
    :type lr: float32
    :param f: activation function
    :type f: function
    """
    
    with tf.name_scope("WeightUpdate"):
        for i in range(len(w)):
            w[i].assign_add(tf.scalar_mul(lr, reduced_batched_outer_product(e[i], f(r[i]))))

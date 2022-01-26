import tensorflow as tf
from tf_utils import reduced_batched_outer_product

def set_noisy_sensory(representations, data, noise):
    b = tf.shape(representations[0])[0]
    representations[0] = tf.clip_by_value(tf.concat([tf.random.normal(tf.shape(data[:,:196,:]),0.,noise),
                                                     data[:,196:392,:],
                                                     tf.random.normal(tf.shape(data[:,392:,:]),0.,noise)],1), -10, 10)

def precision_modulated_energy(model, r, theta=[], predictions_flow_upward=False, gamma=tf.constant(.5)):
    """Energy (total squared L2 norm of precision-weighted errors + regularizer) computation and autodifferentiation with respect to representations and learnable parameters

    :param model: description of a sequential network by a list of layers, can be generated e.g. using :py:func:`tf_utils.mlp`
    :type model: list of :py:class:`tf_utils.Dense` or :py:class:`tf_utils.BiasedDense`
    :param r: representations
    :type r: list of 3d tf.Tensor of float32
    :param theta: learnable parameters, defaults to []
    :type theta: list of variable tf.Tensor of float32, optional
    :param predictions_flow_upward: direction of prediction flow, defaults to False
    :type predictions_flow_upward: bool, optional
    :param gamma: Regularization scalar, defaults to .5
    :type gamma: float32, optional
    :return: energy, autodiff gradient tape
    :rtype: float32, tf.GradientTape
    """
    
    with tf.name_scope("EnergyComputation"):
        F = tf.zeros(())
        with tf.GradientTape(persistent=True, watch_accessed_variables=False) as tape:
            tape.watch(r+theta)
            for i in range(len(model)):
                if predictions_flow_upward:
                    e = tf.subtract(r[i+1], model[i](r[i]))
                else:
                    e = tf.subtract(r[i], model[i](r[i+1]))
                F += 0.5 * tf.matmul(tf.matmul(e, model[i].P, transpose_a=True), e) - gamma*tf.math.log(tf.linalg.det(model[i].P))
        return F, tape

def precision_modulated_inference_step_forward_predictions(e, r, w, P, ir, f, df, update_last=True):
    """Representations update using stochastic gradient descent with analytic expressions
    of the gradients of energy wrt representations, only applicable to an
    unbiased MLP (predictions come from lower layer)

    :param e: prediction errors
    :type e: list of 3d tf.Tensor of float32
    :param r: representations
    :type r: list of 3d tf.Tensor of float32
    :param w: list of weight matrices, can be generated e.g. using :py:func:`tf_utils.mlp`
    :type w: list of 2d tf.Tensor of float32
    :param P: list of precision matrices
    :type P: list of 2d tf.Tensor of float32
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
            r[i] += tf.scalar_mul(ir, tf.subtract(tf.matmul(w[i], tf.matmul(P[i], e[i]), transpose_a=True) * df(r[i]), tf.matmul(P[i-1], e[i-1])))
        if update_last:
            r[N] -= tf.scalar_mul(ir, tf.matmul(P[N-1], e[N-1]))
            
def precision_modulated_weight_update_forward_predictions(w, e, r, P, lr, f):
    """Weight update using stochastic gradient descent with analytic expressions
    of the gradients of energy wrt weights, only applicable to an
    unbiased MLP (predictions come from lower layer)

    :param w: list of weight matrices, can be generated e.g. using :py:func:`tf_utils.mlp`
    :type w: list of 2d tf.Tensor of float32
    :param e: prediction errors
    :type e: list of 3d tf.Tensor of float32
    :param r: representations
    :type r: list of 3d tf.Tensor of float32
    :param P: list of precision matrices
    :type P: list of 2d tf.Tensor of float32
    :param lr: learning rate
    :type lr: float32
    :param f: activation function
    :type f: function
    """
    
    with tf.name_scope("WeightUpdate"):
        for i in range(len(w)):
            w[i].assign_add(tf.scalar_mul(lr, reduced_batched_outer_product(tf.matmul(P[i], e[i]), f(r[i]))))


def precision_modulated_inference_step_backward_predictions(e, r, w, P, ir, f, df, update_last=True, sensory_noise=0.0):
    """Representations update using stochastic gradient descent with analytic expressions
    of the gradients of energy wrt representations, only applicable to an
    unbiased MLP with reversed flow (predictions come from higher layer)

    :param e: prediction errors
    :type e: list of 3d tf.Tensor of float32
    :param r: representations
    :type r: list of 3d tf.Tensor of float32
    :param w: list of weight matrices, can be generated e.g. using :py:func:`tf_utils.mlp`
    :type w: list of 2d tf.Tensor of float32
    :param P: list of precision matrices
    :type P: list of 2d tf.Tensor of float32
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
            r[i] += tf.scalar_mul(ir, tf.subtract(tf.matmul(w[i-1], tf.matmul(P[i-1],e[i-1]), transpose_a=True) * df(r[i]), tf.matmul(P[i],e[i])))
        if update_last:
            r[N] += tf.scalar_mul(ir, tf.matmul(w[N-1], tf.matmul(P[N-1], e[N-1]), transpose_a=True) * df(r[N]))
    if sensory_noise != 0.0:     
        set_noisy_sensory(r, r[0], sensory_noise)
            
def precision_modulated_weight_update_backward_predictions(w, e, r, P, lr, f):
    """Weight update using stochastic gradient descent with analytic expressions
    of the gradients of energy wrt weights, only applicable to an
    unbiased MLP with reversed flow (predictions come from higher layer)

    :param w: list of weight matrices, can be generated e.g. using :py:func:`tf_utils.mlp`
    :type w: list of 2d tf.Tensor of float32
    :param e: prediction errors
    :type e: list of 3d tf.Tensor of float32
    :param r: representations
    :type r: list of 3d tf.Tensor of float32
    :param P: list of precision matrices
    :type P: list of 2d tf.Tensor of float32
    :param lr: learning rate
    :type lr: float32
    :param f: activation function
    :type f: function
    """
    
    with tf.name_scope("WeightUpdate"):
        for i in range(len(w)):
            w[i].assign_add(tf.scalar_mul(lr, reduced_batched_outer_product(tf.matmul(P[i],e[i]), f(r[i+1]))))
                
def precisions_update_backward_predictions(e, P, lr, diagonal=False, only_update_layer_indices=None):
    """Precision update using stochastic gradient descent with analytic expressions
    of the gradients of energy wrt precision, only applicable to an
    unbiased MLP (predictions come from higher layer)

    :param e: prediction errors
    :type e: list of 3d tf.Tensor of float32
    :param P: list of precision matrices
    :type P: list of 2d tf.Tensor of float32
    :param lr: learning rate
    :type lr: float32
    :param diagonal: controls weither we use a diagonal approximation of the precision
    :type diagonal: bool
    :param only_update_layer_indices: 
    """
    
    with tf.name_scope("PrecisionUpdate"):
        b = tf.cast(tf.shape(e[0])[0], tf.float32)
        for i in range(1):
            Peet = reduced_batched_outer_product(tf.matmul(P[i], e[i]), e[i])
            I = tf.eye(tf.shape(P[i])[0])
            P[i].assign_add(tf.scalar_mul(lr, 0.05*I - Peet/b))
            
def precisions_update_forward_predictions(e, P, lr, diagonal=False):
    """Precision update using stochastic gradient descent with analytic expressions
    of the gradients of energy wrt precision, only applicable to an
    unbiased MLP (predictions come from lower layer)

    :param e: prediction errors
    :type e: list of 3d tf.Tensor of float32
    :param P: list of precision matrices
    :type P: list of 2d tf.Tensor of float32
    :param lr: learning rate
    :type lr: float32
    """
    
    b = tf.cast(tf.shape(e[0])[0], tf.float32)
    
    with tf.name_scope("PrecisionUpdate"):
        for i in range(len(P)):
            if diagonal:
                P[i].assign_add(tf.scalar_mul(lr, tf.linalg.diag(tf.linalg.diag_part(0.05*tf.eye(tf.shape(P[i])[0]) - reduced_batched_outer_product(tf.matmul(P[i], e[i]), e[i])/b))))
            else:
                P[i].assign_add(tf.scalar_mul(lr, 0.05*tf.eye(tf.shape(P[i])[0]) - reduced_batched_outer_product(tf.matmul(P[i], e[i]), e[i])/b))
            
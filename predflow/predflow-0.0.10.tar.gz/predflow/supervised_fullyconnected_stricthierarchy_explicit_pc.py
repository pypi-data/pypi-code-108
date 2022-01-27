'''
Supervised predictive coding with analytic expressions of the gradients of the 
energy with respect to representations and learnable parameters.
'''


import tensorflow as tf
from .pc_utils import *
from .tf_utils import relu_derivate

@tf.function
def learn(weights, data, target, ir=0.05, lr=0.001, T=40, f=tf.nn.relu, df=relu_derivate,
          predictions_flow_upward=False):
    """Implements the following logic::
    
        Initialize representations
        do T times
            e = r - W * r
            r += ir * (-e + tranpose(W) * e)
        W += lr * (e * tranpose(r))

    :param weights: list of weight matrices, can be generated e.g. using :py:func:`tf_utils.mlp`
    :type weights: list of 2d variable tf.Tensor of float32
    :param data: inuput data batch
    :type data: 3d tf.Tensor of float32
    :param target: output target batch
    :type target: 3d tf.Tensor of float32
    :param ir: inference rate, defaults to 0.05
    :type ir: float, optional
    :param lr: learning rate, defaults to 0.001
    :type lr: float, optional
    :param T: number of inference steps, defaults to 40
    :type T: int, optional
    :param f: activation function, defaults to tf.nn.relu
    :type f: function, optional
    :param df: derivate of the activation function, defaults to tf_utils.relu_derivate
    :type df: function, optional
    :param predictions_flow_upward: direction of prediction flow, defaults to False
    :type predictions_flow_upward: bool, optional
    """
    
    with tf.name_scope("Initialization"):
        if predictions_flow_upward:
            representations, errors = forward_initialize_representations_explicit(weights, f, data, target)
            inference_step = inference_step_forward_predictions
            weight_update = weight_update_forward_predictions
        else:
            representations, errors = backward_initialize_representations_explicit(weights, f, target, data)
            inference_step = inference_step_backward_predictions
            weight_update = weight_update_backward_predictions
        
    with tf.name_scope("InferenceLoop"):
        for _ in range(T):
            inference_step(errors, representations, weights, ir, f, df, update_last=False)
                    
    weight_update(weights, errors, representations, lr, f)
        
@tf.function
def infer(weights, data, ir=0.05, T=40, f=tf.nn.relu, df=relu_derivate,
          predictions_flow_upward=False, target_shape=None):
    """Implements the following logic::
    
        Initialize representations and clamp representations in the sensory layer
        do T times
            e = r - W * r
            r += ir * (-e + tranpose(W) * e)
        return r

    :param weights: list of weight matrices, can be generated e.g. using :py:func:`tf_utils.mlp`
    :type weights: list of 2d tf.Tensor of float32
    :param data: inuput data batch
    :type data: 3d tf.Tensor of float32
    :param ir: inference rate, defaults to 0.05
    :type ir: float, optional
    :param T: number of inference steps, defaults to 40
    :type T: int, optional
    :param f: activation function, defaults to tf.nn.relu
    :type f: function, optional
    :param df: derivate of the activation function, defaults to relu_derivate
    :type df: function, optional
    :param predictions_flow_upward: direction of prediction flow, defaults to False
    :type predictions_flow_upward: bool, optional
    :param target_shape: shape of target minibatch, defaults to None
    :type target_shape: 1d tf.Tensor of int32, optional
    :return: latent representations
    :rtype: list of 3d tf.Tensor of float32
    """
    
    with tf.name_scope("Initialization"):
        if predictions_flow_upward:
            representations, errors = forward_initialize_representations_explicit(weights, f, data)
            inference_step = inference_step_forward_predictions
        else:
            representations, errors = backward_zero_initialize_representations_explicit(weights, f,
                                                                                        target_shape, data=data)
            inference_step = inference_step_backward_predictions
        
    with tf.name_scope("InferenceLoop"):
        for _ in range(T):
            with tf.name_scope("InferenceStep"):
                inference_step(errors, representations, weights, ir, f, df)
                    
    return representations[1:]

@tf.function
def generate(weights,target, ir=0.05, T=40, f=tf.nn.relu, df=relu_derivate, predictions_flow_upward=False):
    """Implements the following logic::
    
        Initialize representations and clamp representations in the top layer
        do T times
            e = r - W * r
            r += ir * (-e + tranpose(W) * e)
        return r

    :param weights: list of weight matrices, can be generated e.g. using :py:func:`tf_utils.mlp`
    :type weights: list of 2d tf.Tensor of float32
    :param target: inuput data batch (one-hot encoded labels for generation)
    :type target: 3d tf.Tensor of float32
    :param ir: inference rate, defaults to 0.05
    :type ir: float, optional
    :param T: number of inference steps, defaults to 40
    :type T: int, optional
    :param f: activation function, defaults to tf.nn.relu
    :type f: function, optional
    :param df: derivate of the activation function, defaults to relu_derivate
    :type df: function, optional
    :param predictions_flow_upward: direction of prediction flow, defaults to False
    :type predictions_flow_upward: bool, optional
    :return: latent representations
    :rtype: list of 3d tf.Tensor of float32
    """
    
    if predictions_flow_upward:
        raise NotImplementedError("Generation is not implemented for reversed dynamics")
    
    N = len(weights)
    with tf.name_scope("Initialization"):
        representations, errors = backward_initialize_representations_explicit(weights, f, target)
        
    with tf.name_scope("InferenceLoop"):
        for _ in range(T):
            with tf.name_scope("InferenceStep"):
                inference_step_backward_predictions(errors, representations, weights, ir, f, df,
                                                    update_first=True, update_last=False)
                    
    return representations[:-1]
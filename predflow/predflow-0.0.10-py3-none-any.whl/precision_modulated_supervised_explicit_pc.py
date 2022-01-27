'''
Supervised predictive coding with analytic expressions of the gradients of the 
energy with respect to representations and learnable parameters, including
precision weighting of prediction errors.
'''


import tensorflow as tf
from .pc_utils import *
from .precisions_utils import *
from .tf_utils import relu_derivate

@tf.function
def learn(weights, precisions, data, target, ir=0.05, lr=0.001, pr=0.001, T=40, f=tf.nn.relu, df=relu_derivate, 
          predictions_flow_upward=False, diagonal=False, noise=0., learn_precision_indices=None, 
          gamma=tf.constant(0.05)):
    """Implements the following logic::
    
        Initialize representations
        do T times
            e = r - W * r
            r += ir * (- P * e + tranpose(W) * P * e)
        W += lr * (P * e * tranpose(r))
        P += pr * (I - P * e * transpose(e))

    :param weights: list of weight matrices, can be generated e.g. using :py:func:`tf_utils.mlp`
    :type weights: list of 2d variable tf.Tensor of float32
    :param precisions: list of precision matrices, can be generated e.g. using :py:func:`tf_utils.mlp`
    :type preciions: list of 2d variable tf.Tensor of float32
    :param data: inuput data batch
    :type data: 3d tf.Tensor of float32
    :param target: output target batch
    :type target: 3d tf.Tensor of float32
    :param ir: inference rate, defaults to 0.05
    :type ir: float, optional
    :param lr: learning rate for weights, defaults to 0.001
    :type lr: float, optional
    :param pr: learning rate for precision, defaults to 0.001
    :type pr: float, optional
    :param T: number of inference steps, defaults to 40
    :type T: int, optional
    :param f: activation function, defaults to tf.nn.relu
    :type f: function, optional
    :param df: derivate of the activation function, defaults to tf_utils.relu_derivate
    :type df: function, optional
    :param predictions_flow_upward: direction of prediction flow, defaults to False
    :type predictions_flow_upward: bool, optional
    :param diagonal: controls weither we use a diagonal approximation of the precision, defaults to False
    :type diagonal: bool, optional
    :param noise: standard deviation of an eventual noise mask in the sensory layer, defaults to 0 (no noise mask)
    :type noise: float, optional
    :param learn_precision_indices: list of indices of layers in which we want to learn precision matrices,
                                    defaults to None (all layers)
    :type learn_precision_indices: list of int, optional 
    """
    
    N = len(weights)
    with tf.name_scope("Initialization"):
        if predictions_flow_upward:
            representations, errors = forward_initialize_representations_explicit(weights, f, data, target)
            inference_step = precision_modulated_inference_step_forward_predictions
            weight_update = precision_modulated_weight_update_forward_predictions
            precision_update = precisions_update_forward_predictions
        else:
            representations, errors = backward_initialize_representations_explicit(weights, f, target, data)
            inference_step = precision_modulated_inference_step_backward_predictions
            weight_update = precision_modulated_weight_update_backward_predictions
            precision_update = precisions_update_backward_predictions
            
    with tf.name_scope("InferenceLoop"):
        for _ in range(T):
            inference_step(errors, representations, weights, precisions, ir, f, df,
                           update_last=False, sensory_noise=noise)
    weight_update(weights, errors, representations, precisions, lr, f)
    precision_update(errors, precisions, pr, diagonal=diagonal,
                     update_layer_indices=learn_precision_indices, gamma=gamma)
        
        
@tf.function
def infer(weights, precisions, data, ir=0.05, T=40, f=tf.nn.relu, df=relu_derivate, predictions_flow_upward=False,
          target_shape=None, noise=0., forward_pass_initialize=True, initialization_bias=tf.constant(0.)):
    """Implements the following logic::
    
        Initialize representations
        do T times
            e = r - W * r
            r += ir * (-P * e + tranpose(W) * P * e)
        return r

    :param weights: list of weight matrices, can be generated e.g. using :py:func:`tf_utils.mlp`
    :type weights: list of 2d tf.Tensor of float32
    :param precisions: list of precision matrices, can be generated e.g. using :py:func:`tf_utils.mlp`
    :type preciions: list of 2d variable tf.Tensor of float32
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
    :param noise: standard deviation of an eventual noise mask in the sensory layer, defaults to 0 (no noise mask)
    :type noise: float, optional
    :param forward_pass_initialize: controls weither we initialize the hidden and top representations to 
                                    the predictions or zero for models with predictions flowing upwards, 
                                    defaults to True (intiialize to predictions)
    :type forward_pass_initialize: bool, optional
    :param initialization_bias: If `forward_pass_initialize` is False, controls the value at which 
                                representations are initialized, defaults to 0.
    :type initialization_bias: float
    :return: latent representations
    :rtype: list of 3d tf.Tensor of float32
    """
    
    N = len(weights)
    with tf.name_scope("Initialization"):
        if predictions_flow_upward:
            if forward_pass_initialize:
                representations, errors = forward_initialize_representations_explicit(weights, f, data)
            else:
                representations, errors = forward_zero_initialize_representations_explicit(weights, f, data, 
                                                                                           bias=initialization_bias)
            inference_step = precision_modulated_inference_step_forward_predictions
        else:
            representations, errors = backward_zero_initialize_representations_explicit(weights, f, target_shape, data)
            inference_step = precision_modulated_inference_step_backward_predictions
    
    with tf.name_scope("InferenceLoop"):
        for _ in range(T):
            with tf.name_scope("InferenceStep"):
                inference_step(errors, representations, weights, precisions, ir, f, df, sensory_noise=noise)
    
    return representations[1:]
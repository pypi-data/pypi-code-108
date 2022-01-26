'''
Supervised predictive coding with implicit gradients using tensorflow's 
autodifferentiation of the energy with respect to representations and 
learnable parameters.
'''

import tensorflow as tf
from pc_utils import *

@tf.function
def learn(model, data, target, ir=0.1, lr=0.001, T=40, predictions_flow_upward=False):
    """Implements the following logic::
    
        Initialize representations
        do T times
            E = 0.5 * norm(r - model(r)) ^ 2
            r -= ir * dE/dr
        W -= lr * dE/dW

    :param model: description of a sequential network by a list of layers, can be generated e.g. using :py:func:`tf_utils.mlp`
    :type model: list of :py:class:`tf_utils.Dense` or :py:class:`tf_utils.BiasedDense`
    :param data: inuput data batch
    :type data: 3d tf.Tensor of float32
    :param target: output target batch
    :type target: 3d tf.Tensor of float32
    :param ir: inference rate, defaults to 0.1
    :type ir: float, optional
    :param lr: learning rate, defaults to 0.001
    :type lr: float, optional
    :param T: number of inference steps, defaults to 40
    :type T: int, optional
    :param predictions_flow_upward: direction of prediction flow, defaults to False
    :type predictions_flow_upward: bool, optional
    """
    
    if predictions_flow_upward:
        representations = forward_initialize_representations(model, data, target)
    else:
        representations = backward_initialize_representations(model, target, data)
    parameters = [param for layer in model for param in layer.trainable_variables]
    
    with tf.name_scope("InferenceLoop"):
        for _ in range(T):
            with tf.name_scope("InferenceStep"):
                energy, autodiff = energy_and_error(model, representations, parameters, predictions_flow_upward=predictions_flow_upward)
                inference_SGD_step(representations, ir, autodiff.gradient(energy, representations), update_last=False)
            
    parameters_SGD_step(parameters, lr, autodiff.gradient(energy, parameters))
    
    del autodiff

@tf.function
def infer(model, data, ir=0.025, T=200, predictions_flow_upward=False, target_shape=None):
    """Implements the following logic::
    
        Initialize representations
        do T times
            E = 0.5 * norm(r - model(r)) ^ 2
            r -= ir * dE/dr
        return r

    :param model: description of a sequential network by a list of layers, can be generated e.g. using :py:func:`tf_utils.mlp`
    :type model: list of :py:class:`tf_utils.Dense` or :py:class:`tf_utils.BiasedDense`
    :param data: inuput data batch
    :type data: 3d `tf.Tensor` of float32
    :param ir: inference rate, defaults to 0.025
    :type ir: float, optional
    :param T: number of inference steps, defaults to 200
    :type T: int, optional
    :param predictions_flow_upward: direction of prediction flow, defaults to False
    :type predictions_flow_upward: bool, optional
    :param target_shape: shape of target minibatch, defaults to None
    :type target_shape: 1d tf.Tensor of int32, optional
    :return: latent representations
    :rtype: list of 3d tf.Tensor of float32
    """
    
    if predictions_flow_upward:
        representations = forward_initialize_representations(model, data)
    else:
        representations = zero_initialize_representations(model, data, predictions_flow_upward=predictions_flow_upward, target_shape=target_shape, bias=tf.constant(.0001))
        
    with tf.name_scope("InferenceLoop"):
        for _ in range(T):
            with tf.name_scope("InferenceStep"):
                energy, autodiff = energy_and_error(model, representations, predictions_flow_upward=predictions_flow_upward)
                inference_SGD_step(representations, ir, autodiff.gradient(energy, representations))
                
    del autodiff
    
    return representations[1:]
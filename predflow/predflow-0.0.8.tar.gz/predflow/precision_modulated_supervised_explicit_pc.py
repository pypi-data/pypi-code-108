'''
Supervised predictive coding with analytic expressions of the gradients of the 
energy with respect to representations and learnable parameters.
'''


import tensorflow as tf
from pc_utils import *
from precisions_utils import *
from tf_utils import relu_derivate

@tf.function
def learn(weights, precisions, data, target, ir=0.1, lr=0.001, pr=0.001, T=20, 
          f=tf.nn.relu, df=relu_derivate, predictions_flow_upward=False, 
          diagonal=False, noise=0.0, clamp_w=None, defective_error_ratio=0.):
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
    :param ir: inference rate, defaults to 0.1
    :type ir: float, optional
    :param lr: learning rate for weights, defaults to 0.001
    :type lr: float, optional
    :param pr: learning rate for precision, defaults to 0.001
    :type pr: float, optional
    :param T: number of inference steps, defaults to 20
    :type T: int, optional
    :param f: activation function, defaults to tf.nn.relu
    :type f: function, optional
    :param df: derivate of the activation function, defaults to tf_utils.relu_derivate
    :type df: function, optional
    :param predictions_flow_upward: direction of prediction flow, defaults to False
    :type predictions_flow_upward: bool, optional
    """
    
    N = len(weights)
    with tf.name_scope("Init"):
        if predictions_flow_upward:
            representations = [data, ]
            for i in range(N-1):
                representations.append(tf.matmul(weights[i], f(representations[-1])))
            representations.append(target)
            errors = [tf.zeros(tf.shape(representations[i+1])) for i in range(N)]
        else:
            representations = [target, ]
            for i in reversed(range(1, N)):
                representations.insert(0, tf.matmul(weights[i], f(representations[0])))
            representations.insert(0, data )
            errors = [tf.zeros(tf.shape(representations[i])) for i in range(N)]
    with tf.name_scope("InferenceLoop"):
        for _ in range(T):
            if predictions_flow_upward:
                precision_modulated_inference_step_forward_predictions(errors, representations, weights, precisions, ir, f, df, update_last=False, defective_error_ratio=defective_error_ratio)
            else:
                precision_modulated_inference_step_backward_predictions(errors, representations, weights, precisions, ir, f, df, update_last=False, sensory_noise=noise)
    if predictions_flow_upward:
        precision_modulated_weight_update_forward_predictions(weights, errors, representations, precisions, lr, f, clamp_w=clamp_w)
        precisions_update_forward_predictions(errors, precisions, pr, diagonal=diagonal)
    else:
        precision_modulated_weight_update_backward_predictions(weights, errors, representations, precisions, lr, f)
        precisions_update_backward_predictions(errors, precisions, pr)
        
        
@tf.function
def infer(weights, precisions, data, ir=0.025, T=200, f=tf.nn.relu, df=relu_derivate, predictions_flow_upward=False, target_shape=None, noise=0.0, initialize=True, defective_error_ratio=0.):
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
    :param ir: inference rate, defaults to 0.025
    :type ir: float, optional
    :param T: number of inference steps, defaults to 200
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
    
    N = len(weights)
    with tf.name_scope("Initialization"):
        if predictions_flow_upward:
            representations = [data, ]
            for i in range(N):
                if initialize:
                    representations.append(tf.matmul(weights[i], f(representations[-1])))
                else:
                    representations.append(tf.zeros(tf.shape(tf.matmul(weights[i], f(representations[-1]))))+0.01)
        else:
            representations = [tf.zeros(target_shape)+tf.constant(.0001),]
            for i in reversed(range(1,N)):
                representations.insert(0, tf.zeros(tf.shape(tf.matmul(weights[i], representations[0])))+tf.constant(.0001))
            representations.insert(0, data)
            
        errors = [tf.zeros(tf.shape(representations[i])) for i in range(N)]
    
    with tf.name_scope("InferenceLoop"):
        for _ in range(T):
            with tf.name_scope("InferenceStep"):
                if predictions_flow_upward:
                    precision_modulated_inference_step_forward_predictions(errors, representations, weights, precisions, ir, f, df, defective_error_ratio=defective_error_ratio)
                else:
                    precision_modulated_inference_step_backward_predictions(errors, representations, weights, precisions, ir, f, df, sensory_noise=noise)
    
    return representations[1:]
"""C converter for deep neural network pytorch models

This script provides a toolkit to convert pytorch deepl learning models to c.

This file can also be imported as a module and contains the following
functions:

    * transform - transforms a (trained) pytorch module to _C_ source code.


"""

import torch.nn as nn

import bitgeist.transform as gs
from bitgeist.layers import DenseBlock


def transform(
    model: nn.Module, template: str = "./bitgeist/resources/ctemplate.tpl.c"
):
    """Initializes the deep neural net layer builder

    Parameters
    ----------
    model : nn.Module
        The root pytorch module to be transformed

    template : str
        _C_ text template

    Returns
    -------
    str
        the transformed c source code.
    """
    layers = gs.entry(28 * 28)
    for layer in model.children():
        if type(layer) == DenseBlock:
            values = layer.lin.binary_weights.numpy()
            m, n = values.shape
            layers += [gs.activation_binarization(), gs.dense(m, list(values[0]))]
        if type(layer) == nn.PReLU:
            layers += [gs.relu()]
    layers += [gs.argmax()]

    return gs.model_transform(layers, template)

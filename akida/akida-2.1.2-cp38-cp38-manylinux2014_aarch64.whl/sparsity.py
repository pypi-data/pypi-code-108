import numpy as np
from .core import LayerType
from .model import Model


def evaluate_sparsity(model, inputs):
    """Evaluate the sparsity of a Model on a set of inputs

    Args:
        model (:obj:`Model`): the model to evaluate
        inputs (:obj:`numpy.ndarray`): a numpy.ndarray

    Returns:
        a dictionary of float sparsity values indexed by layers

    """
    sparsities = {}
    current_inputs = inputs
    for layer in model.layers:
        params = layer.parameters
        if params.layer_type != LayerType.InputData and layer.parameters.activation:
            sub_model = Model(layers=[layer])
            current_inputs = sub_model.forward(current_inputs)
            output_size = np.prod(current_inputs.shape)
            activations = np.count_nonzero(current_inputs)
            sparsities[layer] = 1 - activations / output_size
        else:
            sparsities[layer] = None
    return sparsities

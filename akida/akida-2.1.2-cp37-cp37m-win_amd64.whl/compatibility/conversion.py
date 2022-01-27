import copy
import numpy as np
import akida


def _get_weights_params_identity(layer):
    """
    Creates an 'identity' convolutional layer parameters and its weights.
    """
    out_dims = layer.output_dims
    nb_chan = out_dims[2]
    dw_weights = np.zeros((3, 3, nb_chan, 1), dtype=np.int8)
    pw_weights = np.zeros((1, 1, nb_chan, nb_chan), dtype=np.int8)
    for i in range(nb_chan):
        dw_weights[1, 1, i, 0] = 1
        pw_weights[0, 0, i, i] = 1

    # create a layer to have default parameters
    identity_layer = akida.SeparableConvolutional(
        name=f"{layer.name}_pooling",
        kernel_size=(3, 3),
        filters=nb_chan,
        threshold=0,
        act_bits=layer.parameters.act_bits,
        act_step=2**layer.parameters.act_bits / 16)
    return copy.copy(identity_layer.parameters), dw_weights, pw_weights


def _copy_layer_variables(layer, copied_layer):
    for var in copied_layer.get_variable_names():
        layer.set_variable(var, copied_layer.get_variable(var))


def _copy_layer(model, layer):
    new_layer = akida.Layer(layer.parameters, layer.name)
    model.add(new_layer)
    if layer.learning:
        # Recompile model with layer parameters
        learn_params = {
            attr: getattr(layer.learning, attr)
            for attr in dir(layer.learning)
            if '__' not in attr and 'learning_type' not in attr
        }
        model.compile(**learn_params)
    _copy_layer_variables(new_layer, layer)


def _add_identity_cnp_after_max_pooling(model, layer):
    """
    Adds the layer and an identity CNP to the model
    """
    ident_params, ident_dw_weights, ident_pw_weights = _get_weights_params_identity(
        layer)
    identity_layer = akida.Layer(ident_params, f"{layer.name}_identity")
    model.add(identity_layer)
    identity_layer.set_variable("weights", ident_dw_weights)
    identity_layer.set_variable("weights_pw", ident_pw_weights)


def _cnp_max_pooling(layer):
    return layer.parameters.layer_type in [
        akida.LayerType.Convolutional, akida.LayerType.SeparableConvolutional
    ] and layer.parameters.pool_type == akida.PoolType.Max


def _cnp_pooling_needs_identity_cnp(model, layer_index):
    """
    Returns True if the layer is CNP with max pooling not followed by another
    CNP, and we can add an identity CNP layer after it without altering result
    """
    result = False
    layer = model.get_layer(layer_index)
    if _cnp_max_pooling(layer):
        # if it is not the last layer, check the layer is not followed by
        # another cnp
        if layer_index != model.get_layer_count() - 1:
            next_layer = model.get_layer(layer_index + 1)
            if next_layer.parameters.layer_type not in [
                    akida.LayerType.Convolutional,
                    akida.LayerType.SeparableConvolutional
            ]:
                result = True
        # if it is the last layer, we can add an identity layer only if it has
        # activations enabled
        elif layer.parameters.activation:
            result = True
    return result


def _cnp_max_pooling_split(model, layer):
    """
    Splits a CNP with max pooling into 2 CNPs:
        - one performing the convolution
        - the other one performing the pooling
    """
    # 1st layer is the conv without pooling
    conv_params = copy.copy(layer.parameters)
    conv_params.pool_type = akida.PoolType.NoPooling
    conv_params.pool_size = (-1, -1)
    conv_params.pool_stride = (-1, -1)
    layer_conv = akida.Layer(conv_params, f"{layer.name}_conv")
    model.add(layer_conv)
    _copy_layer_variables(layer_conv, layer)
    # 2nd layer is an identity conv with pooling
    pool_params, pool_dw_weights, pool_pw_weights = _get_weights_params_identity(
        layer)
    pool_params.pool_type = akida.PoolType.Max
    pool_params.pool_size = layer.parameters.pool_size
    pool_params.pool_stride = layer.parameters.pool_stride
    pool_layer = akida.Layer(pool_params, f"{layer.name}_pooling")
    model.add(pool_layer)
    pool_layer.set_variable("weights", pool_dw_weights)
    pool_layer.set_variable("weights_pw", pool_pw_weights)


def create_from_model(model):
    """Tries to create a HW compatible model from an incompatible one

    Tries to create a HW compatible model from an incompatible one, using SW
    workarounds for known limitations. It returns a converted model that is not
    guaranteed to be HW compatible, depending if workaround have been found.

    Args:
        model (:obj:`Model`): a Model object to convert

    Returns:
        :obj:`Model`: a new Model with no guarantee that it is HW compatible.
    """
    new_model = akida.Model()
    nb_layers = model.get_layer_count()
    for i in range(nb_layers):
        layer = model.get_layer(i)
        if _cnp_max_pooling(layer):
            # On hardware, any CNP with max pooling must be followed by a CNP
            # (to perform vertical pooling). If not, an identity CNP layer is
            # then added.
            _copy_layer(new_model, layer)
            # If CNP has max pooling and is not followed by another CNP, we can
            # add an identity CNP layer
            if _cnp_pooling_needs_identity_cnp(model, i):
                _add_identity_cnp_after_max_pooling(new_model, layer)
            continue

        # if no particular case is found, copy the layer into the new model
        _copy_layer(new_model, layer)

    return new_model

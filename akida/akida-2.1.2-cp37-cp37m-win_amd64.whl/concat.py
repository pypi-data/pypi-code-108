from akida.core import (Layer, ConcatParams, ActivationsParams)


class Concat(Layer):
    """Concatenates its inputs along the last dimension

    It takes as input a list of tensors, all of the same shape except for the
    last dimension, and returns a single tensor that is the concatenation
    of all inputs.

    It accepts as inputs either potentials or activations.

    It can perform an activation on the concatenated output with its own set of
    activation parameters and variables.

    Args:
        name (str, optional): name of the layer.
        activation (bool, optional): enable or disable activation
            function.
        threshold (int, optional): threshold for neurons to fire or
            generate an event.
        act_step (float, optional): length of the potential
            quantization intervals.
        act_bits (int, optional): number of bits used to
            quantize the neuron response.

    """

    def __init__(self,
                 name="",
                 activation=True,
                 threshold=0,
                 act_step=1,
                 act_bits=1):
        try:
            params = ConcatParams(
                ActivationsParams(activation, threshold, act_step, act_bits))

            # Call parent constructor to initialize C++ bindings
            # Note that we invoke directly __init__ instead of using super, as
            # specified in pybind documentation
            Layer.__init__(self, params, name)
        except:
            self = None
            raise

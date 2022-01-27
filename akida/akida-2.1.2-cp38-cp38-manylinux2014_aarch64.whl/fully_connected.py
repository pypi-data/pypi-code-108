from akida.core import (Layer, FullyConnectedParams, DataProcessingParams,
                        NumNeuronsParams, WeightBitsParams, LearningParams,
                        ActivationsParams)


class FullyConnected(Layer):
    """This is used for most processing purposes, since any neuron in the layer
    can be connected to any input channel.

    Outputs are returned from FullyConnected layers as a list of events, that
    is, as a triplet of x, y and feature values. However, FullyConnected
    models by definition have no intrinsic spatial organization. Thus, all
    output events have x and y values of zero with only the f value being
    meaningful – corresponding to the index of the event-generating neuron.
    Note that each neuron can only generate a single event for each packet of
    inputs processed.

    Args:
        units (int): number of units.
        name (str, optional): name of the layer.
        weights_bits (int, optional): number of bits used to quantize weights.
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
                 units,
                 name="",
                 weights_bits=1,
                 activation=True,
                 threshold=0,
                 act_step=1,
                 act_bits=1):
        try:
            params = FullyConnectedParams(
                DataProcessingParams(
                    NumNeuronsParams(units), WeightBitsParams(weights_bits),
                    LearningParams(),
                    ActivationsParams(activation, threshold, act_step,
                                      act_bits)))

            # Call parent constructor to initialize C++ bindings
            # Note that we invoke directly __init__ instead of using super, as
            # specified in pybind documentation
            Layer.__init__(self, params, name)
        except:
            self = None
            raise

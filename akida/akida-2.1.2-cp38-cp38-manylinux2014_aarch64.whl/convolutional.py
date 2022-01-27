from akida.core import (Layer, ConvolutionalParams, Padding, PoolType,
                        ConvolutionKernelParams, NumNeuronsParams, StrideParams,
                        WeightBitsParams, PoolingParams, ActivationsParams,
                        DataProcessingParams, LearningParams)


class Convolutional(Layer):
    """Convolutional or "weight-sharing" layers are commonly used in visual
    processing. However, the convolution operation is extremely useful in any
    domain where translational invariance is required – that is, where localized
    patterns may be of interest regardless of absolute position within the
    input. The convolution implemented here is typical of that used in visual
    processing, i.e., it is a 2D convolution (across the x- and y-dimensions),
    but a 3D input with a 3D filter. No convolution occurs across the third
    dimension; events from input feature 1 only interact with connections to
    input feature 1 – likewise for input feature 2 and so on. Typically,
    the input feature is the identity of the event-emitting neuron in the
    previous layer.

    Outputs are returned from convolutional layers as a list of events, that is,
    as a triplet of x, y and feature (neuron index) values. Note that for a
    single packet processed, each neuron can only generate a single event at a
    given location, but can generate events at multiple different locations and
    that multiple neurons may all generate events at a single location.

    Args:
        kernel_size (list): list of 2 integer representing the spatial
            dimensions of the convolutional kernel.
        filters (int): number of filters.
        name (str, optional): name of the layer.
        padding (:obj:`Padding`, optional): type of convolution.
        kernel_stride (list, optional): list of 2 integer representing the
            convolution stride (X, Y).
        weights_bits (int, optional): number of bits used to quantize weights.
        pool_size (list, optional): list of 2 integers, representing the window
            size over which to take the maximum or the average (depending on
            pool_type parameter).
        pool_type (:obj:`PoolType`, optional): pooling type
            (None, Max or Average).
        pool_stride (list, optional): list of 2 integers representing
            the stride dimensions.
        activation (bool, optional): enable or disable activation
            function.
        threshold (int, optional): threshold for neurons to fire or
            generate an event.
        act_step (float, optional): length of the potential
            quantization intervals.
        act_bits (int, optional): number of bits used to quantize
            the neuron response.

    """

    def __init__(self,
                 kernel_size,
                 filters,
                 name="",
                 padding=Padding.Same,
                 kernel_stride=(1, 1),
                 weights_bits=1,
                 pool_size=(-1, -1),
                 pool_type=PoolType.NoPooling,
                 pool_stride=(-1, -1),
                 activation=True,
                 threshold=0,
                 act_step=1,
                 act_bits=1):
        try:
            params = ConvolutionalParams(
                DataProcessingParams(
                    NumNeuronsParams(filters), WeightBitsParams(weights_bits),
                    LearningParams(),
                    ActivationsParams(activation, threshold, act_step,
                                      act_bits)),
                ConvolutionKernelParams(kernel_size, padding),
                PoolingParams(pool_size, pool_type, pool_stride),
                StrideParams(kernel_stride))

            # Call parent constructor to initialize C++ bindings
            # Note that we invoke directly __init__ instead of using super, as
            # specified in pybind documentation
            Layer.__init__(self, params, name)
        except:
            self = None
            raise

from akida.core import (Layer, SeparableConvolutionalParams, Padding, PoolType,
                        ConvolutionalParams, DataProcessingParams,
                        NumNeuronsParams, WeightBitsParams, LearningParams,
                        ActivationsParams, ConvolutionKernelParams,
                        PoolingParams, StrideParams)


class SeparableConvolutional(Layer):
    """Separable convolutions consist in first performing a depthwise spatial
    convolution (which acts on each input channel separately) followed by a
    pointwise convolution which mixes together the resulting output channels.
    Intuitively, separable convolutions can be understood as a way to factorize
    a convolution kernel into two smaller kernels, thus decreasing the number of
    computations required to evaluate the output potentials. The
    ``SeparableConvolutional`` layer can also integrate a final pooling
    operation to reduce its spatial output dimensions.

    Args:
        kernel_size (list): list of 2 integer representing the spatial
            dimensions of the convolutional kernel.
        filters (int): number of pointwise filters.
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
                 weights_bits=2,
                 pool_size=(-1, -1),
                 pool_type=PoolType.NoPooling,
                 pool_stride=(-1, -1),
                 activation=True,
                 threshold=0,
                 act_step=1,
                 act_bits=1):
        try:
            params = SeparableConvolutionalParams(
                ConvolutionalParams(
                    DataProcessingParams(
                        NumNeuronsParams(filters),
                        WeightBitsParams(weights_bits), LearningParams(),
                        ActivationsParams(activation, threshold, act_step,
                                          act_bits)),
                    ConvolutionKernelParams(kernel_size, padding),
                    PoolingParams(pool_size, pool_type, pool_stride),
                    StrideParams(kernel_stride)))

            # Call parent constructor to initialize C++ bindings
            # Note that we invoke directly __init__ instead of using super, as
            # specified in pybind documentation
            Layer.__init__(self, params, name)
        except:
            self = None
            raise

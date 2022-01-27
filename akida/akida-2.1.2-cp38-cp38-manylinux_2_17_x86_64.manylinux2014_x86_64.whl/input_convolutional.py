from akida.core import (Layer, InputLayerParams, NumNeuronsParams,
                        ConvolutionKernelParams, StrideParams,
                        ActivationsParams, WeightBitsParams, PoolingParams,
                        InputParams, InputConvolutionalParams, Padding,
                        PoolType)


class InputConvolutional(Layer):
    """The ``InputConvolutional`` layer is an image-specific input layer.

    It is used if images are sent directly to AEE without using the
    event-generating method. If the User applies their own event-generating
    method, the resulting events should be sent to an InputData type layer
    instead.

    The InputConvolutional layer accepts images in 8-bit pixels, either
    grayscale or RGB. Images are converted to events using a combination of
    convolution kernels, activation thresholds and winner-take-all (WTA)
    policies. Note that since the layer input is dense, expect approximately one
    event per pixel – fewer if there are large contrast-free regions in the
    image, such as with the MNIST dataset.

    Note that this format is not appropriate for neuromorphic camera type input
    which data is natively event-based and should be sent to an InputData type
    input layer.

    Args:
        input_shape (tuple): the 3D input shape.
        kernel_size (list): list of 2 integer representing the spatial
            dimensions of the convolutional kernel.
        filters (int): number of filters.
        name (str, optional): name of the layer.
        padding (:obj:`Padding`, optional): type of
            convolution.
        kernel_stride (tuple, optional): tuple of integer representing the
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
        padding_value (int, optional): value used when padding.

    """

    def __init__(self,
                 input_shape,
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
                 act_bits=1,
                 padding_value=0):
        try:
            params = InputConvolutionalParams(
                InputLayerParams(InputParams(input_shape)),
                ConvolutionKernelParams(kernel_size, padding),
                NumNeuronsParams(filters), StrideParams(kernel_stride),
                WeightBitsParams(weights_bits),
                PoolingParams(pool_size, pool_type, pool_stride),
                ActivationsParams(activation, threshold, act_step, act_bits),
                padding_value)

            # Call parent constructor to initialize C++ bindings
            # Note that we invoke directly __init__ instead of using super, as
            # specified in pybind documentation
            Layer.__init__(self, params, name)
        except:
            self = None
            raise

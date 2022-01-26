import json
import tensorflow as tf
import tf2onnx
from tf2onnx import optimizer
from brevettiai.utils.profiling import profile_graph
from tensorflow.python.keras.saving import saving_utils as _saving_utils
from tensorflow.python.framework.convert_to_constants import convert_variables_to_constants_v2


def input_output_quantization(function, dtype=tf.uint8, output_scaling=255):
    @tf.function(input_signature=[tf.TensorSpec(shape=s.shape, dtype=dtype, name=s.name) for s in
                                  function.input_signature])
    def _input_output_quant_wrapper(x):
        x = tf.cast(x, tf.float32)
        yhat = function(x)
        return {k: tf.transpose(tf.cast(v * output_scaling, dtype=dtype), [0, 3, 1, 2]) for k, v in yhat.items()}
    return _input_output_quant_wrapper


def input_as_nchw(function):
    @tf.function(input_signature=[tf.TensorSpec(shape=tuple(s.shape[x] for x in [0, 3, 1, 2]), dtype=s.dtype, name=s.name)
                                  for s in function.input_signature])
    def _input_output_wrapper(x):
        x_nhwc = tf.transpose(x, [0, 2, 3, 1])
        yhat = function(x_nhwc)
        yhat = {k: tf.transpose(v, [0, 3, 1, 2]) for k, v in yhat.items()}
        return yhat
    return _input_output_wrapper


def export_model(model, output_file=None, inputs_as_nchw: (list, bool) = None, shape_override=None,
                 meta_data: dict = None):
    inputs_as_nchw = inputs_as_nchw or []
    shape_override = shape_override or {}
    meta_data = meta_data or {}

    # Create graph representation
    if shape_override:
        input_signature = [tf.TensorSpec(sh, dtype=spec.dtype or tf.float32, name=spec.name)
                           for sh, spec in zip(shape_override, model.input_spec)]
    else:
        input_signature = None

    function = _saving_utils.trace_model_call(model, input_signature)

    # Quantize input
    #function = input_output_quantization(function, dtype=tf.uint8, output_scaling=255)
    if inputs_as_nchw:
       function = input_as_nchw(function)

    # Get concrete function
    concrete_func = function.get_concrete_function()
    concrete_func = convert_variables_to_constants_v2(concrete_func,
                                                      lower_control_flow=False,
                                                      aggressive_inlining=True)

    # allow to pass inputs and outputs from caller if we don't want all of them
    input_names = [input_tensor.name for input_tensor in concrete_func.inputs
                   if input_tensor.dtype != tf.dtypes.resource]
    output_names = [output_tensor.name for output_tensor in concrete_func.outputs
                    if output_tensor.dtype != tf.dtypes.resource]

    frozen_graph = tf2onnx.tf_loader.from_function(concrete_func, input_names, output_names)

    if not isinstance(shape_override, dict):
        shape_override = {n: v for n, v in zip(input_names, shape_override)}

    if inputs_as_nchw is True:
        inputs_as_nchw = input_names

    # Convert graph to ONNX
    graph_def = frozen_graph

    if graph_def is not None:
        with tf.Graph().as_default() as tf_graph:
            tf.import_graph_def(graph_def, name='')

            flops = profile_graph(tf_graph)
            meta_data["total_float_ops"] = flops.total_float_ops

            with tf2onnx.tf_loader.tf_session(graph=tf_graph):
                g = tf2onnx.tfonnx.process_tf_graph(tf_graph,
                                                    opset=11,
                                     #shape_override=shape_override,
                                     input_names=input_names,
                                     output_names=output_names,
                                     #inputs_as_nchw=inputs_as_nchw,
                                     const_node_values=None,
                                     initialized_tables=None)

    onnx_graph = optimizer.optimize_graph(g)
    model_proto = onnx_graph.make_model("converted from {}".format(model.name), external_tensor_storage=None)

    for kk, vv in meta_data.items():
        meta = model_proto.metadata_props.add()
        meta.key = kk
        if not isinstance(vv, str):
            vv = json.dumps(vv)
        meta.value = vv

    # Export graph
    if output_file:
        tf2onnx.utils.save_protobuf(output_file, model_proto)
        return output_file
    else:
        return model_proto

import tensorflow as tf

from distutils.version import LooseVersion
from tensorflow.python.keras.saving import saving_utils as _saving_utils
from tensorflow.python.framework.convert_to_constants import convert_variables_to_constants_v2


def profile_keras_model(model, batch_size=1, shape_override=None):
    """
    shape override takes precedence over batch_size
    :param model:
    :param batch_size:
    :param shape_override:
    :return:
    """
    if shape_override:
        input_signature = [tf.TensorSpec(sh, dtype=spec.dtype or tf.float32, name=spec.name)
                           for sh, spec in zip(shape_override, model.input_spec)]
    else:
        input_signature = [tf.TensorSpec([batch_size] + inp.shape[1:], inp.dtype) for inp in model.inputs]

    function = _saving_utils.trace_model_call(model, input_signature)
    concrete_func = function.get_concrete_function()

    if LooseVersion(tf.__version__) < LooseVersion("2.2"):
        frozen_func = convert_variables_to_constants_v2(concrete_func, lower_control_flow=False)
    else:
        frozen_func = convert_variables_to_constants_v2(concrete_func, lower_control_flow=False,
                                                        aggressive_inlining=True)

    return profile_graph(frozen_func.graph)


def profile_graph_def(graph_def):
    with tf.Graph().as_default() as graph:
        tf.import_graph_def(graph_def, name="")
        return profile_graph(graph)


def profile_graph(graph):
    run_meta = tf.compat.v1.RunMetadata()
    opts = tf.compat.v1.profiler.ProfileOptionBuilder.float_operation()
    flops = tf.compat.v1.profiler.profile(graph=graph, run_meta=run_meta, cmd="scope", options=opts)
    return flops

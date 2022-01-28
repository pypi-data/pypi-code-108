import os
import json
import tempfile

import tensorflow as tf
from tensorflow.python.framework.convert_to_constants import convert_variables_to_constants_v2
from tensorflow.python.keras.saving import saving_utils as _saving_utils

from mo.main import driver
from mo.utils.cli_parser import get_all_cli_parser
import telemetry.telemetry as tm


def export_model(model, output_dir=None, shape_override=None, meta_data: dict = None):
    # Create graph representation
    if shape_override:
        input_signature = [tf.TensorSpec(sh, dtype=spec.dtype or tf.float32, name=spec.name)
                           for sh, spec in zip(shape_override, model.input_spec)]
    else:
        input_signature = None

    function = _saving_utils.trace_model_call(model, input_signature)

    # Get concrete function
    concrete_func = function.get_concrete_function()

    # allow to pass inputs and outputs from caller if we don't want all of them
    input_names = [input_tensor.name for input_tensor in concrete_func.inputs
                   if input_tensor.dtype != tf.dtypes.resource]
    output_names = [output_tensor.name for output_tensor in concrete_func.outputs
                    if output_tensor.dtype != tf.dtypes.resource]

    frozen_func = convert_variables_to_constants_v2(concrete_func, lower_control_flow=False, aggressive_inlining=True)

    with tempfile.TemporaryDirectory() as tmpdir:
        pb_file = tf.io.write_graph(frozen_func.graph.as_graph_def(add_shapes=True),
                                    tmpdir, "model.pb", as_text=False)

        telemetry = tm.Telemetry(app_name='Model Optimizer', app_version="0")
        args = get_all_cli_parser().parse_args([
            "--framework", "tf",
            "--input_model", pb_file,
            "--output_dir", output_dir,
            "--output", ",".join([n.split(":")[0] for n in output_names]),
            "--input", ",".join([n.split(":")[0] for n in input_names]),
            "--data_type", "FP32",
            "--enable_concat_optimization"
        ])
        driver(args)

        # Save metadata
        meta_data = {} if meta_data is None else meta_data
        with open(os.path.join(output_dir, "model.meta.json"), "w") as fp:
            json.dump(meta_data, fp, indent=2)

        # Check export
        assert set(os.listdir(output_dir)).issuperset({"model." + x for x in ("bin", "mapping", "xml", "meta.json")})


def predict(tmpdir):
    from openvino.inference_engine import IECore
    ie_core_handler = IECore()
    network = ie_core_handler.read_network(model=os.path.join(tmpdir, "model.xml"),
                                           weights=os.path.join(tmpdir, "model.bin"))
    executable_network = ie_core_handler.load_network(network, device_name='CPU', num_requests=1)
    inference_request = executable_network.requests[0]

    import numpy as np
    from openvino.inference_engine import IECore, Blob, TensorDesc
    input_blob_name = next(iter(inference_request.input_blobs))
    output_blob_name = next(iter(inference_request.output_blobs))
    inp_ = inference_request.input_blobs[input_blob_name]
    input_blob = Blob(inp_.tensor_desc, np.random.rand(*inp_.tensor_desc.dims).astype(np.float32))
    inference_request.set_blob(blob_name=input_blob_name, blob=input_blob)
    inference_request.infer()
    output = inference_request.output_blobs[output_blob_name].buffer
    print(f"{inference_request.latency} ms")
    import matplotlib.pyplot as plt
    plt.imshow(output[0, 0])
from typing import Union


def create_onnx_from_keras(model,
                           name: str = 'model',
                           file_pfx: Union[None, str] = None,
                           is_flattened: bool = True,
                           has_timestep: bool = True,
                           has_channel: bool = False,
                           is_mutex: bool = True,
                           feature: str = ''):
    # Create onnx model from keras model and write onnx model file if file_pfx provided.
    #   model           keras model
    #   name            model name
    #   file_pfx        filename prefix to save onnx model (do not save if empty)
    #   is_flattened    model feature data is flattened
    #   has_timestep    model has timestep dimension
    #   has_channel     model has channel dimension
    #   is_mutex        model label output is mutually exclusive
    #   feature         model feature type
    # import tf2onnx
    import keras2onnx
    from tensorflow.keras.layers import GRU

    msg = ''

    # convert to onnx model
    # spec = (tf.TensorSpec((None, 224, 224, 3), tf.float32, name="input"),)
    # onnx_model, _ = tf2onnx.convert.from_keras(model)
    onnx_model = keras2onnx.convert_keras(model, name, debug_mode=True)

    # Replace stateful GRUs with custom layers
    stateful_gru_names = []
    for i in range(len(model.layers)):
        layer = model.layers[i]
        if isinstance(layer, GRU):
            if layer.stateful:
                stateful_gru_names.append(layer.name)

    for i in range(len(onnx_model.graph.node)):
        node = onnx_model.graph.node[i]
        if node.name in stateful_gru_names:
            node.op_type = 'SGRU'

    # Add metadata to model
    f_flag = onnx_model.metadata_props.add()
    f_flag.key = 'is_flattened'
    f_flag.value = str(is_flattened)

    t_flag = onnx_model.metadata_props.add()
    t_flag.key = 'has_timestep'
    t_flag.value = str(has_timestep)

    c_flag = onnx_model.metadata_props.add()
    c_flag.key = 'has_channel'
    c_flag.value = str(has_channel)

    m_flag = onnx_model.metadata_props.add()
    m_flag.key = 'is_mutex'
    m_flag.value = str(is_mutex)

    feature_flag = onnx_model.metadata_props.add()
    feature_flag.key = 'feature'
    feature_flag.value = str(feature)

    # save the model in ONNX format
    if file_pfx is not None:
        file_name = file_pfx + '.onnx'
        msg = 'onnx model saved to {}'.format(file_name)
        keras2onnx.save_model(onnx_model, file_name)

    return onnx_model, msg

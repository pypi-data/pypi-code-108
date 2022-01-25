import json
import pickle
import io
import sys

import base64
from pprint import pprint

# This is a UUID we use to demarcate JSON data that needs specialized
# deserialization logic.  Because it's a UUID, we can expect it not to
# be present in user objects.
DMN_JSON = "47ce6720-cd47-44c5-a46f-86e346fc384f"

# TODO: all other possible types

def gm(name):
    mod = sys.modules.get(name, None)
    if mod is None:
        raise RuntimeError(f"Module {name} is not available")
    return mod

def binary_serialize(f):
    def inner(obj):
        tmp_io = io.BytesIO()
        res = f(obj, tmp_io)
        tmp_io.seek(0)
        return {
            'metadata': res,
            'b64': base64.b64encode(tmp_io.read()).decode('utf-8'),
        }
    return inner

def binary_deserialize(f):
    def inner(obj):
        tmp_io = io.BytesIO(base64.b64decode(obj['b64'].encode('utf-8')))
        return f(tmp_io, obj['metadata'])
    return inner

@binary_serialize
def serialize_numpy_ndarray(obj, io_out):
    gm('numpy').savez_compressed(io_out, array=obj)

@binary_deserialize
def deserialize_numpy_ndarray(io_in, _):
    return gm('numpy').load(io_in)["array"]

@binary_serialize
def serialize_torch(obj, io_out):
    gm('torch').save(obj, io_out)

@binary_deserialize
def deserialize_torch(io_in, _):
    return gm('torch').load(io_in)

@binary_serialize
def serialize_tensorflow_tensor(obj, io_out):
    tf = gm('tensorflow')
    if not hasattr(tf, "Session"):
        tf = tf.compat.v1
    sess = tf.get_default_session()
    if sess is None:
        sess = tf.Session()

    io_out.write(tf.serialize_tensor(obj).eval(session=sess))

    return {'out_type': obj.dtype.name}

@binary_deserialize
def deserialize_tensorflow_tensor(io_in, metadata):
    tf = gm('tensorflow')
    if not hasattr(tf, "Session"):
        tf = tf.compat.v1
    return tf.io.parse_tensor(io_in.read(), **metadata)

@binary_serialize
def serialize_tensorflow_eager_tensor(obj, io_out):
    tf = gm('tensorflow')
    if not hasattr(tf, "Session"):
        tf = tf.compat.v1
    io_out.write(tf.serialize_tensor(obj).numpy())
    return {'out_type': obj.dtype.name}

@binary_deserialize
def deserialize_tensorflow_eager_tensor(io_in, metadata):
    tf = gm('tensorflow')
    if not hasattr(tf, "Session"):
        tf = tf.compat.v1
    return tf.io.parse_tensor(io_in.read(), **metadata)

def serialize_bytes(obj):
    return base64.b64encode(obj).decode('utf-8')

def deserialize_bytes(s):
    return base64.b64decode(s)

def serialize_pandas_df(obj):
    # This will preserve wonky indexes
    return obj.to_json(orient='split')

def deserialize_pandas_df(s):
    return gm('pandas').read_json(s, orient='split')

FORMAT_MAP = {
    'numpy.ndarray': [serialize_numpy_ndarray, deserialize_numpy_ndarray],
    'torch.Tensor': [serialize_torch, deserialize_torch],
    'tensorflow.python.framework.ops.Tensor': [
        serialize_tensorflow_tensor, deserialize_tensorflow_tensor],
    'tensorflow.python.framework.ops.EagerTensor': [
        serialize_tensorflow_eager_tensor, deserialize_tensorflow_eager_tensor],
    'pandas.core.frame.DataFrame': [serialize_pandas_df, deserialize_pandas_df],
    'builtins.bytes': [serialize_bytes, deserialize_bytes]
}

def custom_attempt_deserialize(obj):
    if DMN_JSON in obj:
        qualname = obj[DMN_JSON][0]
        json = obj[DMN_JSON][1]

        if isinstance(qualname, str):
            func = FORMAT_MAP[qualname][1]
            return func(json)
        elif qualname is None:
            # Fallback case we're potentially loading pickled data
            return pickle.loads(base64.b64decode(json.encode('utf-8')))
        else:
            raise RuntimeError("Somehow qualname was neither a str nor None")
    return obj

def pickle_unsafe(obj):
    obj_data = gm('cloudpickle').dumps(obj)
    return {
        DMN_JSON: [None, base64.b64encode(obj_data).decode('utf-8')],
    }

def dumps(obj, serialization_fallback=None):
    def custom_attempt_serialize(obj):
        qualname = f"{obj.__class__.__module__}.{obj.__class__.__qualname__}"
        # This is only called if we failed the default deserializer
        if qualname in FORMAT_MAP:
            return {
                DMN_JSON: [qualname, FORMAT_MAP[qualname][0](obj)],
            }
        else:
            if serialization_fallback is not None:
                return serialization_fallback(obj)
            else:
                raise RuntimeError(f'Unable to serialize `{qualname}`.  Please specify a `serialization_fallback`, such as `dmn.json_utils.pickle_unsafe`.')

    return json.dumps(obj, default=custom_attempt_serialize)

def loads(s):
    # handle custom objects
    return json.loads(s, object_hook=custom_attempt_deserialize)

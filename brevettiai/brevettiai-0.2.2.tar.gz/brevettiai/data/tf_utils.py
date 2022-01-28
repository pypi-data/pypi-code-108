import json
import tensorflow as tf
import numpy as np
from tensorflow.python.data.util import nest


class TfEncoder(json.JSONEncoder):
    def default(self, obj):
        if tf.is_tensor(obj):
            return obj.numpy()
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, bytes):
            return obj.decode()
        elif isinstance(obj, np.generic):
            return obj.item()
        return json.JSONEncoder.default(self, obj)


def unpack(obj):
    if tf.is_tensor(obj):
        return unpack(obj.numpy())
    elif isinstance(obj, np.ndarray):
        return tuple(unpack(x) for x in obj)
    elif isinstance(obj, list):
        return tuple(unpack(x) for x in obj)
    elif isinstance(obj, bytes):
        return unpack(obj.decode())
    elif isinstance(obj, np.generic):
        return unpack(obj.item())
    elif isinstance(obj, tf.RaggedTensor):
        return unpack(obj.to_list())
    return obj


class NumpyStringIterator:
    """Iterator over a dataset with elements converted to numpy. and strings decoded"""

    def __init__(self, dataset):
        self._iterator = iter(dataset)

    def __iter__(self):
        return self

    @staticmethod
    def parser(x):
        try:
            v = x.numpy()
            if x.dtype == tf.string:
                try:
                    return v.astype(str, copy=False)
                except AttributeError:
                    return v.decode()
                except UnicodeDecodeError:
                    return v
            else:
                return v
        except Exception:
            return unpack(x)

    def __next__(self):
        return nest.map_structure(self.parser, next(self._iterator))


def dataset_from_pandas(df):
    """
    Build a tensorflow generator dataset from a pandas dataframe allowing tuples of different sizes in each sample
    :param df:
    :return:
    """
    df = df.copy()

    def sampler():
        for k, row in df.iterrows():
            yield {**row}

    ds = tf.data.Dataset.from_generator(sampler, **tf_dataset_metadata(df))
    return ds


def tf_dataset_metadata(df):
    """
    Generate tf dataset metadata-object from pandas dataframe
    :param df:
    :return:
    """
    tftypes = (tf.float16, tf.float32, tf.float64,
               tf.int8, tf.int16, tf.int32, tf.int64,
               tf.uint8, tf.uint16, tf.uint32, tf.uint64)
    dtypes = {}
    shapes = {}
    for c in df:
        col = df[c]

        # Direct dtype/shape assignment via pandas
        dtype = col.dtype.type
        for tftype in tftypes:
            if dtype == tftype:
                dtypes[c] = tftype
                shapes[c] = ()

        first = col.values[0]
        # Numpy nd array dtype/shape inference
        if isinstance(first, np.ndarray):
            tpold = None
            for tp in set(v.dtype for v in col.values):
                tpold = tpold or tp
                if np.can_cast(tp, tpold):
                    continue
                elif np.can_cast(tpold, tp):
                    tpold = tp
                else:
                    raise AssertionError("dtypes do not match %s; %s, %s" % (c, tp, tpold))

            for tftype in tftypes:
                if tpold == tftype.as_numpy_dtype:
                    dtypes[c] = tftype

            for shape in set(v.shape for v in col.values):
                shold = shapes.setdefault(c, shape)
                if shold != shape:
                    assert len(shape) == len(shold), \
                        "Shapes in input generator [%s] does not match; %s, %s" % (c, shape, shold)
                shapes[c] = tuple(x if x == y else None for x, y in zip(shold, shape))

        # Tuple shape/dtype inference
        if isinstance(first, tuple):
            for shape in set(len(v) for v in col.values):
                shold = shapes.setdefault(c, (shape,))
                shapes[c] = (shold,) if shold == shape else (None,)

            tpold = None
            for tp in set(np.dtype(type(v[0])) if len(v) != 0 else None for v in col.values):
                tpold = tpold or tp
                if tpold is not None and tp is not None:
                    if np.can_cast(tp, tpold):
                        continue
                    elif np.can_cast(tpold, tp):
                        tpold = tp
                    else:
                        raise AssertionError("dtypes do not match %s; %s, %s" % (c, tp, tpold))

            for tftype in tftypes:
                if tpold == tftype.as_numpy_dtype:
                    dtypes[c] = tftype

        # Fallback
        if c not in dtypes:
            dtypes[c] = tf.string

        if c not in shapes:
            shapes[c] = ()

    return dict(output_types=dtypes, output_shapes=shapes)


def fill_empty(df):
    set_empty_list = {
        bool: -1,
        int: -1,
        str: "N/A",
        float: np.nan,
        np.int32: -1,
        np.int64: -1,
        np.float64: np.float64(np.nan),
        np.float32: np.float32(np.nan)
    }
    df_out = df.copy()
    replace_summary = df.copy()
    for col_name in df_out.columns:
        col = df_out[col_name]
        valid_col = col[~col.isna()]
        first = valid_col.values[0] if len(valid_col) else col.values[0]
        dtype = type(first)
        if dtype in [tuple, list]:
            elem_dtype = str
            for elem in first:
                if elem:
                    elem_dtype = type(elem)
            shape = len(first)
            prototype = dtype([set_empty_list[elem_dtype]] * shape)
        elif dtype is np.ndarray:
            fill_val = set_empty_list[first.dtype.type]
            prototype = (np.ones_like(first) * fill_val).astype(first.dtype)
        else:
            elem_dtype = valid_col.apply(type).iloc[0] if len(valid_col) else col.apply(type).iloc[0]
            prototype = set_empty_list.get(elem_dtype, "Unknown Type")
        df_out[col_name] = col.apply(lambda c: c if isinstance(c, type(prototype)) else prototype)
        replace_summary[col_name] = col.apply(lambda c: not isinstance(c, type(prototype)))
        if replace_summary[col_name].sum() > 0:
            print("Replacing: ", col_name, replace_summary[col_name].sum())

    return df_out, replace_summary
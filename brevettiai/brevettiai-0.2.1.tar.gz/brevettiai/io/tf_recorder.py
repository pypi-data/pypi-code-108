import tensorflow as tf
from brevettiai import Module

def _bytes_feature(value):
    """Returns a bytes_list from a string / byte."""
    if isinstance(value, type(tf.constant(0))):
        value = value.numpy()  # BytesList won't unpack a string from an EagerTensor.
    return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))


def _float_feature(value):
    """Returns a float_list from a float / double."""
    return tf.train.Feature(float_list=tf.train.FloatList(value=[value]))


def _int64_feature(value):
    """Returns an int64_list from a bool / enum / int / uint."""
    return tf.train.Feature(int64_list=tf.train.Int64List(value=[value]))


def serialize_composite_structure(value):
    try:
        return _bytes_feature(tf.io.serialize_tensor(value))
    except ValueError:
        if isinstance(value, dict):
            return tf.train.Features(feature={k: serialize_composite_structure(v) for k, v in value.items()})


def generate_dtype_structure(value):
    if isinstance(value, type(tf.constant(0))):
        return value.dtype
    if isinstance(value, dict):
        return {k: generate_dtype_structure(v) for k, v in value.items()}
    else:
        return tf.constant(value).dtype


class TfRecorder(Module):
    def __init__(self, filenames, structure=None, compression_type="GZIP"):
        self.filenames = filenames
        self.structure = structure
        self.compression_type = compression_type

        self.writer = None

    def set_structure_from_example(self, value):
        self.structure = generate_dtype_structure(value)
        return self.structure

    @property
    def feature_description(self):
        return tf.nest.pack_sequence_as(
            flat_sequence=[tf.io.FixedLenFeature((), tf.string)] * len(tf.nest.flatten(self.structure)),
            structure=self.structure)

    def __enter__(self):
        options = tf.io.TFRecordOptions(compression_type=self.compression_type)
        self.writer = tf.io.TFRecordWriter(self.filenames, options)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.writer.__exit__(exc_type, exc_val, exc_tb)
        self.writer = None

    def write(self, value):
        if self.writer is None:
            raise ValueError("writer not open, use context manager or __enter__ / __exit__ functions")
        self.writer.write(self.serialize(value).SerializeToString())

    def serialize(self, value):
        if self.structure is None:
            self.set_structure_from_example(value)
        return tf.train.Example(features=serialize_composite_structure(value))

    def get_dataset(self, *args, **kwargs):
        if self.structure is None:
            raise ValueError("Structure not known, set before loading dataset")

        ds = tf.data.TFRecordDataset(filenames=self.filenames, compression_type=self.compression_type, *args, **kwargs)
        return ds.map(self.parse_dataset)

    def parse_dataset(self, x):
        x = tf.io.parse_single_example(x, self.feature_description)
        parsed = [tf.io.parse_tensor(x, dtype) for dtype, x in zip(tf.nest.flatten(self.structure), tf.nest.flatten(x))]
        return tf.nest.pack_sequence_as(flat_sequence=parsed, structure=x)

    def get_config(self):
        cfg = super().get_config()
        cfg["structure"] = tf.nest.map_structure(lambda x: x.name, cfg["structure"])
        return cfg

    @classmethod
    def from_config(cls, config):
        config["structure"] = tf.nest.map_structure(tf.dtypes.as_dtype, config["structure"])
        return super().from_config(config)

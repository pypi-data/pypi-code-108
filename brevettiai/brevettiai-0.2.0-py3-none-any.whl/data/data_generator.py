import logging
import inspect
from collections import OrderedDict
import copy

import numpy as np
import pandas as pd

from pandas.core.dtypes.common import is_signed_integer_dtype, is_unsigned_integer_dtype
from tqdm import tqdm

from brevettiai.interfaces import vue_schema_utils as vue

log = logging.getLogger(__name__)

try:
    import tensorflow as tf
    from brevettiai.data.image import ImagePipeline
    from brevettiai.data.tf_utils import NumpyStringIterator
except ImportError as ex:
    log.warn("Tensorflow not installed; Some data loading functionality may not work")
    from unittest.mock import MagicMock
    tf = MagicMock()


weighing_presets = OrderedDict([
    ("uniform", lambda x: 1),
    ("count", lambda x: x),
    ("square root", np.sqrt),
    ("log", np.log),
    ("logx+1", lambda x: np.log(x) + 1)])


def parse_weighing(weighing):
    if isinstance(weighing, str):
        weighing = weighing_presets[weighing]

    def _get_weights_safe(count, group):
        try:
            return weighing(count, group)
        except TypeError:
            return weighing(count)

    return _get_weights_safe


sampling_groupby_presets = OrderedDict([
    ("", None),
    ("None", None),
    ("Class", ["category"]),
    ("Dataset / Class", ["dataset_id", "category"]),
    ("Dataset / Folder", ["dataset_id", "folder"]),
])


def weighted_dataset_selector(weight):
    def selector_gen():
        cweight = np.cumsum(weight)
        step = weight.min() / 2
        state = 0
        while True:
            state += step
            yield np.sum(cweight < state % 1.0)

    return selector_gen


def item_mapping(df):
    mapping = {}
    for name in df.columns:
        col = df[name]
        mapping_name = f"_{name}_mapping"
        if col.dtype.name == "category":
            df.loc[:, mapping_name] = col.cat.codes
            lookup_tbl = tf.ragged.constant(col.cat.categories.values, name=f"{name}lookup")
            mapping[mapping_name] = name, lambda x, tbl=lookup_tbl: tbl[tf.cast(x, tf.int32)]
        if col.apply(pd.api.types.is_list_like).any():
            if col.apply(pd.api.types.is_hashable).all():
                grp = df.groupby(name)
                df.loc[:, mapping_name] = grp.ngroup()
                lookup_tbl = tf.ragged.constant([k for k, v in grp], name=f"{name}lookup")
            else:
                df.loc[:, mapping_name] = np.arange(col.size)
                try:
                    lookup_tbl = tf.constant(col.values.tolist())
                except ValueError:
                    lookup_tbl = tf.ragged.constant(col.values.tolist())
            mapping[mapping_name] = name, lambda x, tbl=lookup_tbl: tbl[tf.cast(x, tf.int32)]
        else:
            mapping[name] = name, lambda x: x

    return df[mapping.keys()], mapping


def _downcast(s):
    if is_signed_integer_dtype(s.dtype):
        return pd.to_numeric(s, downcast="integer")
    elif is_unsigned_integer_dtype(s.dtype):
        return pd.to_numeric(s, downcast="unsigned")
    return s


def get_dataset(df, shuffle, repeat, seed=None):
    """
    Build simple tensorflow dataset from pandas dataframe
    :param df:
    :param shuffle:
    :param repeat:
    :param seed: seed or np.random.RandomState
    :return:
    """
    rand = seed if isinstance(seed, np.random.RandomState) else np.random.RandomState(seed=seed)

    if shuffle:
        df = df.iloc[rand.permutation(np.arange(len(df)))]

    ds = tf.data.Dataset.from_tensor_slices({c: df[c].values for c in df.columns})

    if repeat:
        ds = ds.repeat(-1 if repeat is True else repeat)

    if shuffle:
        ds = ds.shuffle(min(len(df), 1024),
                        seed=np.frombuffer(rand.bytes(8), dtype=np.int64)[0],
                        reshuffle_each_iteration=False)
    return ds


def build_dataset_from_samples(samples, groupby="category", weighing="uniform", shuffle=True, repeat=True, seed=None):
    """
    Build tensorflow dataset from pandas dataframe with oversampling of groups
    :param samples:
    :param groupby:
    :param weighing:
    :param shuffle:
    :param repeat:
    :param seed: seed or np.random.RandomState
    :return:
    """
    rand = seed if isinstance(seed, np.random.RandomState) else np.random.RandomState(seed=seed)
    ds_metadata = {}

    if not isinstance(samples, pd.DataFrame):
        samples = pd.DataFrame(samples)
    else:
        samples = samples.copy()

    samples = samples.apply(_downcast, axis=0)

    if isinstance(groupby, str):
        groupby = sampling_groupby_presets.get(groupby, [groupby])

    sample_grouper, weight = None, None
    if groupby is not None:
        sampling_group_col_name = "_sampling_group"
        sample_grouper = samples.groupby(groupby)
        samples[sampling_group_col_name] = sample_grouper.ngroup()

        weighing_fn = parse_weighing(weighing)
        weight = np.array([weighing_fn(len(i), x) for x, i in sample_grouper.groups.items()])
        weight = weight / weight.sum()

    # Perform mapping of ragged tuple elements and categoricals before input to tensorflow dataset
    samples, colmapping = item_mapping(samples)

    # Perform oversampling of datasets
    if groupby is not None:
        datasets = [get_dataset(v[colmapping.keys()], shuffle=shuffle, repeat=repeat, seed=rand)
                    for key, v in sample_grouper]
        if shuffle:
            ds = tf.data.experimental.sample_from_datasets(datasets, weights=weight,
                                                           seed=np.frombuffer(rand.bytes(8), dtype=np.int64)[0])
        else:
            selector = tf.data.Dataset.from_generator(weighted_dataset_selector(weight), tf.int64)
            ds = tf.data.experimental.choose_from_datasets(datasets, selector)

        ds_metadata["sample_weight"] = dict(zip(sample_grouper.groups.keys(), weight))
    else:
        ds = get_dataset(samples[colmapping.keys()], shuffle=shuffle, repeat=repeat, seed=rand)

    # Reverse map indexes
    ds = ds.map(lambda x: {name: func(x[k]) for k, (name, func) in colmapping.items()})
    ds._ds_metadata = ds_metadata
    return ds


def map_output_structure(x, structure):
    keys = tf.nest.flatten(structure)
    return tf.nest.pack_sequence_as(structure, [x[k] for k in keys])


class DataGenerator:
    def __init__(self, samples, batch_size: int = 32, shuffle: bool = False, repeat: bool = False,
                 sampling_groupby: str = None,
                 sampling_group_weighing: str = "uniform", seed: int = None,
                 output_structure: tuple = None, max_epoch_samples: int = np.inf):
        """

        Dataset helper based on Tensorflow datasets, capable of seeding, weighted sampling, and tracking datasets for
        logs.
        :param samples: Pandas dataframe with inputs
        :param batch_size: Number of samples per batch
        :param shuffle: Shuffle items in dataset
        :param repeat: Repeat samples from dataset
        :param sampling_groupby: Stratified sample columns to group by when weighing each sample group for sampling
        :param sampling_group_weighing: Stratfied sampling weighing function to use for weighing the sample groups supply function or select from ["uniform", "count", "square root", "log"]
        :param seed: Seeding of dataset
        :param output_structure: default output structure (tuples with keys) of dataset or None for full dictionary
        :param max_epoch_samples: Max number of samples per epoch
        """
        self.random = seed if isinstance(seed, np.random.RandomState) else np.random.RandomState(seed=seed)
        self.output_structure = output_structure
        self._tfds_actions = []

        if not isinstance(samples, pd.DataFrame):
            samples = pd.DataFrame(list(samples) if isinstance(samples, np.ndarray) else samples)

        self.total_sample_count = len(samples)
        self.epoch_samples = min(max_epoch_samples, self.total_sample_count)
        self.batch_size = batch_size

        self._dataset = self.dataset = build_dataset_from_samples(
            samples=samples, groupby=sampling_groupby, weighing=sampling_group_weighing,
            shuffle=shuffle, repeat=repeat, seed=self.random)

    def get_samples(self, batch=True, structure=None) -> tf.data.Dataset:
        """
        Get tensorflow samples as tensorflow dataset without applying maps for e.g. loading data
        :param batch: output batched
        :param structure: Structure of output, (None, "__default__" or structure of keys)
        :return:
        """
        ds = self.dataset.batch(self.batch_size) if batch else self.dataset

        structure = self.output_structure if structure is "__default__" else structure
        if structure is not None:
            ds = ds.map(lambda x: map_output_structure(x, structure))
        return ds

    def get_samples_numpy(self, *args, **kwargs):
        """
        Get numpy iterator of samples in dataset, similar interface as .get_samples()
        :return:
        """
        return NumpyStringIterator(self.get_samples(*args, **kwargs))

    def get_dataset(self, batch=True, structure="__default__") -> tf.data.Dataset:
        """
        Get tensorflow dataset
        :param batch: output batched
        :param structure: Structure of output, (None, "__default__" or structure of keys)
        :return:
        """
        ds = self.dataset.batch(self.batch_size)
        ds = self.build_dataset(ds)
        assert isinstance(ds, tf.data.Dataset), "Return value of build_dataset must be tensorflow dataset"
        ds = self.apply_tfds_actions(ds)
        ds = ds if batch else ds.unbatch()

        structure = self.output_structure if structure is "__default__" else structure
        if structure is not None:
            ds = ds.map(lambda x: map_output_structure(x, structure))
        return ds.prefetch(tf.data.experimental.AUTOTUNE)

    def get_dataset_numpy(self, *args, **kwargs):
        """
        Get numpy iterator of Dataset, similar interface as .get_dataset()
        :return:
        """
        return NumpyStringIterator(self.get_dataset(*args, **kwargs))

    def build_dataset(self, ds: tf.data.Dataset) -> tf.data.Dataset:
        """Extend this function to apply special functions to the dataset"""
        return ds

    def apply_tfds_actions(self, tfds):
        for action, func_kwargs, kwargs in self._tfds_actions:
            apply_unbatched = hasattr(action, "apply_unbatched") and action.apply_unbatched
            if apply_unbatched:
                tfds = tfds.unbatch()
            tfds = tfds.map(lambda x: action(x, **func_kwargs), **kwargs)
            if apply_unbatched:
                tfds = tfds.batch(self.batch_size)
        return tfds

    def get_dataset_actions(self):
        """
        Get variable actions performed on datasets.

        :return: list of actions, each action consisting of (callable,
        args for callable, and args for tensorflow dataset map)
        """
        return self._tfds_actions

    def map(self, map_func, num_parallel_calls=tf.data.experimental.AUTOTUNE, **kwargs):
        """
        :param map_func: an action or a list of actions, for lists None items are skipped
        """
        if isinstance(map_func, list):
            generator = self
            for map_func in map_func:
                if map_func is not None:
                    generator = generator.map(map_func, **kwargs)
            return generator
        else:
            func_kwargs = dict(
                seed=int(self.random.randint(1 << 32, dtype=np.uint64))
            )
            # Check function signature for extra kwargs
            allowed = inspect.signature(map_func).parameters
            if not any(k for k, v in reversed(allowed.items()) if v.kind == v.VAR_KEYWORD):
                func_kwargs = {k: v for k, v in func_kwargs.items() if k in allowed or "kwargs" in allowed}

            output = copy.copy(self)
            output._tfds_actions = [*output._tfds_actions,
                                    (map_func, func_kwargs, dict(num_parallel_calls=num_parallel_calls, **kwargs))]

            return output

    def get_debug_info(self):
        try:
            return self._dataset._ds_metadata
        except Exception:
            return {}

    def __len__(self):
        """The number of batches per epoch"""
        return int(np.ceil(self.epoch_samples / self.batch_size))

    def __iter__(self):
        return iter(self.get_dataset())


class StratifiedSampler(vue.VueSettingsModule):
    def __init__(self, batch_size: int = 32, groupby: list = None,
                 group_weighing: str = "uniform", max_epoch_samples: int = 10**9,
                 seed: int = -1):
        """
        https://en.wikipedia.org/wiki/Stratified_sampling
        :param batch_size: Number of samples per batch
        :param groupby: Stratified sample columns to group by when weighing each sample group for sampling
        :param group_weighing: Stratfied sampling weighing function to use for weighing the sample groups supply function or select from ["uniform", "count", "square root", "log"]
        :param seed: Seeding of dataset
        """
        self.batch_size = batch_size
        self.groupby = groupby or None
        self.group_weighing = group_weighing
        self.max_epoch_samples = max_epoch_samples
        self.seed = seed

    def get(self, samples, shuffle: bool = False, repeat: bool = False, **kwargs) -> DataGenerator:
        """
        :param samples: Pandas dataframe with inputs
        :param shuffle: Shuffle items in dataset
        :param repeat: Repeat samples from dataset
        :param max_epoch_samples: Max number of samples per epoch
        """
        kwargs["batch_size"] = kwargs.get("batch_size", self.batch_size)
        kwargs["max_epoch_samples"] = kwargs.get("max_epoch_samples", self.max_epoch_samples)
        kwargs["seed"] = kwargs.get("seed", None if self.seed < 0 else self.seed)

        return DataGenerator(samples, shuffle=shuffle, repeat=repeat,
                             sampling_groupby=self.groupby, sampling_group_weighing=self.group_weighing,
                             **kwargs)

    @classmethod
    def to_schema(cls, builder, name, ptype, default, **kwargs):
        if name == "group_weighing":
            builder.add_field(vue.select("Sampling Group Weighing", model=name, default=ptype(default), **kwargs,
                                         values=list(weighing_presets.keys())))
        else:
            return super().to_schema(builder=builder, name=name, ptype=ptype, default=default, **kwargs)


def predict_dataset(model, dataset, map_output=None):
    """
    Predict results of model given dataset
    :param model:
    :param dataset:
    :param map_output:
    :return:
    """
    prediction_func = model.predict_on_batch if isinstance(model, tf.keras.Model) else model

    ds = tf.data.Dataset.zip((dataset.get_samples(batch=True), dataset.get_dataset()))
    for samples, (x, y) in tqdm(ds.take(len(dataset)), total=len(dataset), mininterval=2):
        if isinstance(x, dict):
            yhat = prediction_func(**x)
        else:
            yhat = prediction_func(x)

        if not isinstance(yhat, dict):
            outputs = tuple(x.name.split("/")[0] for x in model.outputs)
            if len(outputs) == 1:
                yhat = {outputs[0]: yhat}
            else:
                yhat = {k: v for k, v in zip(outputs, yhat)}

        if map_output is not None:
            yhat = map_output(yhat)
        yield {**samples, **yhat}


class OneHotEncoder(vue.VueSettingsModule):
    def __init__(self, classes, input_key="category", output_key="onehot"):
        self.classes = classes
        self.input_key = input_key
        self.output_key = output_key

        items = len(classes)
        assert items > 0, "Number of classes should be larger than zero"

        # Build mapping table to indices
        self.class_table = tf.lookup.StaticHashTable(
            initializer=tf.lookup.KeyValueTensorInitializer(
                keys=tf.constant(classes),
                values=tf.range(items),
            ),
            default_value=tf.constant(items),
            name="class_weight"
        )

        # Build encoding table from indices to encoding
        self.encoding = tf.eye(items + 1, items)

    @classmethod
    def to_schema(cls, builder, name, ptype, default, **kwargs):
        if name in {"input_key", "output_key"}:
            return
        else:
            return super().to_schema(builder=builder, name=name, ptype=ptype, default=default, **kwargs)

    def encode(self, item):
        class_idx = self.class_table.lookup(item)
        enc = tf.gather(self.encoding, class_idx)
        return enc

    def __call__(self, x, *args, **kwargs):
        x[self.output_key] = self.encode(x[self.input_key])
        return x


def build_image_data_generator(samples, classes=None, image=None, augmentation=None, *args, **kwargs):
    """
    Utility function for building a default image dataset with images at "path" and class definitions at "category"
    outputting image and onehot encoded class
    :param samples: Pandas dataframe of samples, with at least columns (path, category)
    :param classes: list of classes or none to autodetect from samples
    :param image: kwargs for ImageLoader
    :param augmentation: kwargs for ImageAugmenter
    :param args: args for TfDataset
    :param kwargs: args for TfDataset
    :return: (image, onehot)
    """
    if classes is None:
        class_space = set(samples.category.unique())
        classes = set(item for sublist in class_space for item in sublist if item != "__UNLABELED__")
        classes = list(sorted(classes))

    image = image or {}
    image = ImagePipeline(**image) if isinstance(image, dict) else image
    ds = DataGenerator(samples, output_structure=("img", "onehot"), *args, **kwargs) \
        .map(image)

    if augmentation is not None:
        from brevettiai.data.image.image_augmenter import ImageAugmenter
        augmentation = ImageAugmenter(**augmentation) if isinstance(augmentation, dict) else augmentation
        ds = ds.map(augmentation)

    ds = ds.map(OneHotEncoder(classes=classes))

    return ds

"""Tensorflow Data Transformer for Tables"""
import json
from ast import literal_eval
from datatransformer.abstractobject import DataTransformer

import vaex as vx
import pandas as pd
import tensorflow as tf
#pylint: disable=unnecessary-lambda
class TensorflowDataTransformer(DataTransformer):
    """Tensorflow Data Transformer for Tables"""
    #pylint: disable=R0913
    #pylint: disable=R0902
    def __init__(
        self,
        data_spec: dict,
        feature_column_config: dict,
        data=None,
        shuffle: bool =False,
        batch_size: int =1
    ):
        """Creates a DataTransformer object.
        Args:
          data_spec: A dictionary that represents the dataset about to be transformed.
          data: if using small sample of data, feed it into the data dictionary to transform it.
          feature_column_config: a dictionary that defines the categories of feature columns

          ```python
          data_spec = {
              'foo': {
                  'type': 'non_sequential',
                  'file_path': ["/path/to/data/foo.csv"],
                        # if not set you can also feed data with §data§ arg
                  'dense_feature': ['foo'],
                  'sparse_feature': ['bar'],
                  'exclude_columns': ['a','b'],
                  'orient': 'records',
                  'dtype': {'column': type},
              }
              'bar': {
                  'type': 'sequential',
                  'file_path': ["/path/to/data/bar.csv"],
                  'dense_feature': ['foo'],
                  'sparse_feature': ['bar'],
                  'exclude_columns': ['b','c'],
                  'orient': 'records',
                  'dtype': {'column': type},
              }
              'labels': {
                  'type': 'classification', # §classification§ or §regression§
                  'file_path': [/path/to/data/label.csv]
                  'label': ['label']
              }
          }
          feature_column_config = {
              'foo': {
                  'column': ['category1', 'category2' ...]
              }
              'bar':{
                  'column': ['category3', 'category4' ...]
              }
          }
          TensorflowDataTransformer(data_spec=data_spec)
          ```
        """
        self._data_spec = data_spec
        self._data = data
        self._feature_column_config = feature_column_config
        self._feature_columns = {}
        self._labels= None
        self._preserve_columns={}
        self.shuffle = shuffle
        self.batch_size = batch_size

        if not data:
            #pylint: disable=W0612
            for dim, spec in data_spec.items():
                if 'file_path' not in spec:
                    raise ValueError("Please specify file_path in data_spec if data is not set.")
            #pylint: enable=W0612
        else:
            #parse different type of Input Data
            self._data = self._input_parser(data)
            #parse dims exclude columns
            for dim in self.dimensions:
                self._dim_parser(dim)

            self._data_reshape()
        self._load()

    @property
    def dimensions(self):
        return [dim for dim in self._data_spec.keys() if dim != 'labels']

    @property
    def dense_features(self):
        return {dim: spec['dense_feature'] for dim, spec in self._data_spec.items()}

    @property
    def sparse_features(self):
        return {dim: spec['sparse_feature'] for dim, spec in self._data_spec.items()}

    @property
    def feature_columns(self):
        for dim in self.dimensions:
            if self._data_spec[dim]['type'] == 'non_sequential':
                self._feature_columns['non_sequential'] = {
                    dim: {
                        'dense': [
                            tf.feature_column.numeric_column(feat)
                            for feat in self._data_spec[dim]['dense_feature']
                        ],
                        'sparse': [
                            tf.feature_column.categorical_column_with_vocabulary_list(
                                feat, self._feature_column_config[dim][feat]
                            )
                            for feat in self._data_spec[dim]['sparse_feature']
                        ]
                    }
                }
            elif self._data_spec[dim]['type'] == 'sequential':
                self._feature_columns['sequential'] = {
                    dim: {
                        'dense': [
                            tf.feature_column.sequence_numeric_column(feat)
                            for feat in self._data_spec[dim]['dense_feature']
                        ],
                        'sparse': [
                            tf.feature_column.sequence_categorical_column_with_vocabulary_list(
                                feat, self._feature_column_config[dim][feat]
                            )
                            for feat in self._data_spec[dim]['sparse_feature']
                        ]
                    }
                }
            else:
                raise ValueError(f"Unsupported type {self._data_spec[dim]['type']}")
        return self._feature_columns

    @property
    def labels(self):
        return self._labels if hasattr(self, '_labels') else None

    @property
    def buffer_size(self):
        """Get buffer size"""
        den = iter(self.dense_features)
        len_den = len(next(den))
        if not all(len(l) == len_den for l in den):
            raise ValueError('not all dense feature in same length.')
        return len_den

    def _input_parser(self, data):
        """Parse Different Inputs to Dataframe"""
        #Data Input Json String to DataFrame
        if isinstance(data, str):
            #check json serializable
            try:
                json.dumps(data)
            except Exception as error:
                raise error
            data = json.loads(data)
            data = {
                dim: pd.read_json(
                    instances, orient=self._data_spec[dim]['orient'],
                    dtype=self._data_spec[dim]['dtype']
                ) for dim, instances in data.items()
            }

        return data

    def _dim_parser(self, dim):
        """Dimensions Parsing"""
        #save exclude columns
        self._preserve_columns[dim] = self._data[dim][self._data_spec[dim]['exclude_columns']]
        #drop exclude columns
        self._data[dim] = self._data[dim].drop(self._data_spec[dim]['exclude_columns'], axis=1)

    def _data_reshape(self):
        """Reshape Sequential Data"""
        for dim in self.dimensions:
            if self._data_spec[dim]['type'] == 'sequential':
                group = self._data[dim].set_index('trans_id').groupby('trans_id')
                #這裡的group 可能要根據data客製化
                #pylint: disable=W0612
                for index, group_ele in group:
                    reshape_dataframe = group.agg(
                        {
                            col: lambda x: x.tolist() for col in group_ele.columns
                        },
                        axis=1
                    ).reset_index()
                    break
                self._data[dim] = reshape_dataframe
                #pylint: enable=W0612

    def _load(self):
        """Load Data"""
        if self._data:
            self._data_parser()
        else:
            self._file_parser()

    def _data_parser(self):
        """Parse Data from data input format"""
        if 'labels' in self._data:
            self._labels = tf.data.Dataset.from_tensor_slices(
                dict(self._data.pop('labels'))
            )
            self._data_spec.pop('labels')
        else:
            self._labels = None

        for dim, val in self._data.items():
            if self._data_spec[dim]['type'] == 'non_sequential':
                self._data_spec[dim]['data'] = tf.data.Dataset.from_tensor_slices(
                    dict(val[self.sparse_features[dim]+self.dense_features[dim]])
                )
            else:
                self._data_spec[dim]['data'] = tf.data.Dataset.from_tensor_slices({
                    feature: tf.ragged.constant(val[[feature]].values)
                    for feature in self.sparse_features[dim] + self.dense_features[dim]
                })

    def _file_parser(self):
        """Parse Data from file input format"""
        if 'labels' in self._data_spec:
            self._labels = tf.data.Dataset.from_tensor_slices(
                dict(vx.open(self._data_spec['labels']['file_path']).to_pandas_df())
            )
            self._data_spec.pop('labels')
        else:
            self._labels = None

        for dim, spec in self._data_spec.items():
            if spec['type'] == 'sequential':
                converter_dict =dict.fromkeys(
                    spec['dense_feature']+spec['sparse_feature'], lambda x: literal_eval(x)
                )
                vx_frame = vx.open(
                    path=spec['file_path'], converters=converter_dict
                )
                self._data_spec[dim]['data'] = tf.data.Dataset.from_tensor_slices({
                    x: (lambda x : tf.ragged.constant(vx_frame[x].to_numpy()))(x)
                    for x in spec['dense_feature']+spec['sparse_feature']
                })
            elif spec['type'] == 'non_sequential':
                self._data_spec[dim]['data'] = tf.data.experimental.make_csv_dataset(
                    file_pattern=spec['file_path'],
                    select_columns=spec['dense_feature']+spec['sparse_feature'],
                    header=True, batch_size=1
                )
            else:
                raise ValueError(
                    "the dimension type should be either sequential or non_sequential."
                )

    def list_files(self):
        """List of used file"""
        return {dim: spec['file_path'] for dim, spec in self._data_spec.items()}

    def to_dataset(self):
        """Transform data to tensroflow dataset"""
        features = tf.data.Dataset.zip(
            tuple(spec['data'] for dim, spec in self._data_spec.items())
        )

        if self._labels is not None:
            dataset = tf.data.Dataset.zip((features, self._labels))
        else:
            dataset = features

        if self.shuffle is True:
            dataset = dataset.shuffle(buffer_size=self.buffer_size)
        if self.batch_size:
            dataset = dataset.batch(self.batch_size)
        return dataset

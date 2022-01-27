"""Create Custom Layers."""
import tensorflow as tf

class TransformLayer(tf.keras.layers.Layer):
    """Creates Transform Layers."""
    def __init__(self, features_columns, dim_type):
        """Creates Transform Layers.
        Args:
          features_columns: A dictionary that store tensorflow features columns
                           (like numeric_column or categorical_column_with_vocabulary_list)
          dim_type: A dictionary to show which dim is non_sequential or sequential
          ```python
          dim_type = {0: 'non_sequential', 1:'sequential'}
          features_columns = {
              'foo': [tf.feature_column.categorical_column_with_vocabulary_list],
              'bar': [feature_column.numeric_column],
          }
        """
        super().__init__()
        self.dim_type = dim_type

        self.features_layers = {}
        for dim in features_columns['non_sequential'].keys():
            for dcat in features_columns['non_sequential'][dim].keys():
                if dcat =='sparse':
                    for col in range(len(features_columns['non_sequential'][dim][dcat])):
                        key = features_columns['non_sequential'][dim][dcat][col].name
                        embedded = tf.feature_column.embedding_column(
                            features_columns['non_sequential'][dim][dcat][col], dimension=4
                        )
                        self.features_layers[key] = tf.keras.layers.DenseFeatures(
                            embedded, trainable=True
                        )
                else:
                    for col in range(len(features_columns['non_sequential'][dim][dcat])):
                        key = features_columns['non_sequential'][dim][dcat][col].name
                        self.features_layers[key] = tf.keras.layers.DenseFeatures(
                            features_columns['non_sequential'][dim][dcat][col], trainable=True
                        )

        for dim in features_columns['sequential'].keys():
            for dcat in features_columns['sequential'][dim].keys():
                if dcat =='sparse':
                    for col in range(len(features_columns['sequential'][dim][dcat])):
                        key = features_columns['sequential'][dim][dcat][col].name
                        embedded = tf.feature_column.embedding_column(
                            features_columns['sequential'][dim][dcat][col], dimension=4
                        )
                        self.features_layers[key] = tf.keras.experimental.SequenceFeatures(
                            embedded, trainable=True
                        )
                else:
                    for col in range(len(features_columns['sequential'][dim][dcat])):
                        key = features_columns['sequential'][dim][dcat][col].name
                        self.features_layers[key] = tf.keras.experimental.SequenceFeatures(
                            features_columns['sequential'][dim][dcat][col], trainable=True
                        )

    def get_config(self):
        """Overwirte original get_config function to get config of custom objects
        """
        config = super().get_config().copy()
        config.update({
            'features_layers': self.features_layers,
            'dim_type': self.dim_type,
        })

        return config

    def call(self, inputs):
        """Define data flow for TransformLayer
        Args:
            inputs: A tuple for inputs (dim1,dim2)
        """

        trainable_dic = {}
        for dim_type in self.dim_type.keys():
            if self.dim_type[dim_type] == 'non_sequential':
                fea_ten_dic = {
                    key: self.features_layers[key]({key: inputs[dim_type][key]})
                    for key in sorted(inputs[dim_type].keys())
                }
                trainable_dic[dim_type] = tf.concat(
                    [fea_ten_dic[key] for key in sorted(fea_ten_dic.keys())], 1,
                    name='non_seq_concat'
                )
            else:
                fea_ten_dic = {
                    key: tf.reduce_mean(
                        self.features_layers[key]({key: inputs[dim_type][key].to_sparse()})[0],
                        1
                    )
                    for key in sorted(inputs[dim_type].keys())
                }
                trainable_dic[dim_type] = tf.concat(
                    [fea_ten_dic[key] for key in sorted(fea_ten_dic.keys())], 1,
                    name='seq_concat'
                )

        trainable = tf.concat([trainable_dic[key] for key in sorted(trainable_dic.keys())], 1)

        return trainable

"""Create Tensorflow based Model."""
import tensorflow as tf
from modelbricks.layers.layers import TransformLayer
from modelbricks.metrics.metrics import F1Score

class RucModel(tf.keras.models.Model):
    """Creates a RiskUserClassification Model.
    Usage:
        fit: train model with data,
             this will call train_step function,
             You can overwrite it for your custom logics.
        evaluate: test model metrics with untrained data,
             this will call test_step function,
             You can overwrite it for your custom logics.
        predict: generate prediction for unseen data,
             this will call predict_step function,
             You can overwrite it for your custom logics.

    ```python
    model.fit(train_data, epoch, ...)

    model.evaluate(test_data)

    prediction = model.predict(test_data)
    ```
    """
    def __init__(self, features_columns, dim_type, label):
        """Creates a RiskUserClassification Model.
        Args:
          features_columns: A dictionary that store tensorflow features columns
                           (like numeric_column or categorical_column_with_vocabulary_list)
          dim_type: A dictionary to show which dim is non_sequential or sequential
          label: The label column name in our data

        '''python
        dim_type = {0: 'non_sequential', 1:'sequential'}
        features_columns = {
              'foo': [tf.feature_column.categorical_column_with_vocabulary_list],
              'bar': [feature_column.numeric_column],
        }
        label = 'label'

        ruc = RucModel(features_columns, dim_type, label)
        ```
        """
        super().__init__()
        self.trans_layer = TransformLayer(features_columns, dim_type)
        self.dense_layer = tf.keras.layers.Dense(34, activation='relu')
        self.dense_layer2 = tf.keras.layers.Dense(15, activation='relu')
        self.output_layer = tf.keras.layers.Dense(1, activation='sigmoid')
        self.label = label

    @tf.function
    def train_step(self, data):
        """Define Train step for Model
        Args:
            data: A tuple for inputs data ((dim1,dim2),label)
        """
        #pylint:disable=C0103
        x, y = data
        #label is dictionary but our prediction is only a value,
        #so we need to select the value from label dictionary
        y = y[self.label]

        with tf.GradientTape() as tape:
            y_pred = self(x, training=True)
            loss = self.compiled_loss(y, y_pred, regularization_losses=self.losses)

        trainable_vars = self.trainable_variables
        gradients = tape.gradient(loss, trainable_vars)

        self.optimizer.apply_gradients(zip(gradients, trainable_vars))
        self.compiled_metrics.update_state(y, y_pred)
        #pylint:enable=C0103
        return {m.name: m.result() for m in self.metrics}

    @tf.function
    def test_step(self, data):
        """Define Test step for Model
        Args:
            data: A tuple for inputs data ((dim1,dim2),label)
        """
        #pylint:disable=C0103
        x, y = data
        #label is dictionary but our prediction is only a value,
        #so we need to select the value from label dictionary
        y = y[self.label]

        y_pred = self(x, training=False)
        #pylint:disable=W0612
        loss = self.compiled_loss(y, y_pred, regularization_losses=self.losses)
        #pylint:enable=W0612
        self.compiled_metrics.update_state(y, y_pred)
        #pylint:enable=C0103
        return {m.name: m.result() for m in self.metrics}

    def get_config(self):
        """Overwirte original get_config function to get config of custom objects
        """
        config = super().get_config().copy()
        config.update({
            'accuracy': tf.keras.metrics.Accuracy(),
            'Recall': tf.keras.metrics.Recall(),
            'Precision': tf.keras.metrics.Precision(),
            'TP': tf.keras.metrics.TruePositives(),
            'F1_Score': F1Score(),
        })

        return config

#     @classmethod
#     def from_config(cls, config):
#         return cls(**config)

    def call(self, inputs):
        """Define data flow for Model to get prediction from Model
        Args:
            inputs: A tuple for inputs (dim1,dim2)
        """
        trainable = self.trans_layer(inputs)
        dly1_out = self.dense_layer(trainable)
        dly2_out = self.dense_layer2(dly1_out)
        out = self.output_layer(dly2_out)

        return out

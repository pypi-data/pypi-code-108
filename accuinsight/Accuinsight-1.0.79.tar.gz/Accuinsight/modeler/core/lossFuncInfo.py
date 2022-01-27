'''
<2020.05.13>
Classify available loss functions to regression and classification.

reference: https://www.tensorflow.org/api_docs/python/tf/keras/losses
total: 34
'''

REGRESSION = ['MeanAbsoluteError', 'MeanAbsolutePercentageError', 'MeanSquaredError', 'MeanSquaredError', 'MAE', 'mae', 'MAPE', 'mape', 'MSE', 'mse', 'MSLE', 'msle', 'Huber', 'huber', 'LogCosh','logcosh', 'Poisson', 'poisson']
CLASSIFICATION = ['Hinge', 'hinge', 'SquaredHinge', 'squared_hinge', 'KLD', 'KLDivergence', 'BinaryCrossentropy', 'binary_crossentropy', 'CategoricalCrossentropy', 'CategoricalHinge', 'categorical_crossentropy', 'categorical_hinge', 'SparseCategoricalCrossentropy', 'sparse_categorical_crossentropy']

# poisson: regression for count data

# These are not loss functions.
# (Reduction / serialize / deserialize / get / Loss)

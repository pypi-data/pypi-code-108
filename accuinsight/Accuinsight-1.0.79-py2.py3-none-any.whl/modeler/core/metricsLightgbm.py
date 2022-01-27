# metrics in lightgbm

REGRESSION = ['l1', 'mean_absolute_error', 'mae', 'regression_l1',
             'l2', 'mean_squared_error', 'mse', 'regression_l2', 'regression',
             'rmse', 'root_mean_squared_error', 'l2_root',
             'mape', 'mean_absolute_percentage_error',
             'huber',
             'fair',
             'poisson',                    # Poisson regression
             'gamma', 'gamma_deviance',    # Gamma regression
             'tweedie',                    # Tweedie regression
             'quantile'                    # Quantile regression
             ]

CLASSIFICATION = ['map', 'mean_average_precision',
              'auc',
              'average_precision',
              'binary_logloss', 'binary',
              'binary_error',
              'auc_mu',
              'multi_logloss', 'multiclass', 'softmax',
              'multiclassova', 'multiclass_ova', 'ova', 'ovr',
              'multi_error',
              'cross_entropy', 'xentropy',
              'cross_entropy_lambda', 'xentlambda',
              'kullback_leibler', 'kldiv']
              
no_metrics = ['"None"', 'na', 'null', '']


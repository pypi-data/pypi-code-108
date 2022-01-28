regressor_space = {
    'auger_ml.ensembles.algorithms.SuperLearnerAlgorithmRegressor': {
        'method': 'nnls',
        'opt_trials': 3
    },
    'auger_ml.ensembles.algorithms.AveragingAlgorithmRegressor': {
        'weights': None,
        'n_best': 3
    }
}

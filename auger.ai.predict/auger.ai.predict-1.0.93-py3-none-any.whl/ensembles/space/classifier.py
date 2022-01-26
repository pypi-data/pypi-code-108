classifier_space = {
    'auger_ml.ensembles.algorithms.SuperLearnerAlgorithmClassifier': {
        'method': 'slsqp',
        'opt_trials': 3
    },
    #TODO: reimplement using trials
    # 'auger_ml.ensembles.algorithms.DeepSuperLearnerAlgorithm': {
    #     'method': 'slsqp',
    #     'k_folds': 3,
    #     'opt_trials': 3,
    #     'max_iters': 12,
    #     'classification': True
    # },
    'auger_ml.ensembles.algorithms.GreedySelectionAlgorithm': {
        'improve_eps': False,
        'random_state': 42,
        'prune_fraction': 0.0,
        'n_best': 1,
        'n_bags': 3,
        'bag_fraction': 0.5,
        'max_bag_pipelines': 3
    },
    'auger_ml.ensembles.algorithms.VotingAlgorithm': {
        'weights': None,
        'n_best': 3,
        'voting': 'soft'
    },
    'auger_ml.ensembles.algorithms.AveragingAlgorithmClassifier': {
        'weights': None,
        'n_best': 3
    }
}

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Permet de vérifier si on accède a l'__init__.py via le setup.
try:
    __SETUP__
except NameError:
    __SETUP__ = False

# teste si pytorch est installé si ce n'est pas via le setup qu'on passe par 
# le __init__.py !
if __SETUP__:
    pass
else :
    try:
        import torch
    except ModuleNotFoundError:
        raise ModuleNotFoundError(
            "Le module PyTorch n'est pas installé : l'instruction import torch "
            "renvoit une erreur ModuleNotFoundError. Visitez la page du projet "
            "PyTorch pour savoir comment l'installer."
        )

    from dstk.pytorch._utils import (check_tensor, check_tensor_dict, detach,
                                     collate_zeros_padding, make_mask)
    from dstk.pytorch._callback import (CallbackInterface, CallbackHandler,
                                        FitState, FitControl, PrintCallback,
                                        ProgressBarCallback,
                                        LRSchedulerCallback,
                                        EarlyStoppingCallback, Supervision,
                                        DEFAULT_CALLBACKS)
    from dstk.pytorch._swa import StochasticWeightAveraging, cut_dataset
    from dstk.pytorch._random_search import RandomizedSearchOnline
    from dstk.pytorch._classifier import BaseClassifier, BaseClassifierOnline
    from dstk.pytorch._regressor import BaseRegressor, BaseRegressorOnline
    
    __all__ = (
        'BaseClassifier',
        'BaseClassifierOnline',
        'BaseRegressor',
        'BaseRegressorOnline',
        'CallbackInterface',
        'CallbackHandler',
        'FitState',
        'FitControl',
        'PrintCallback',
        'ProgressBarCallback',
        'EarlyStoppingCallback',
        'LRSchedulerCallback',
        'Supervision',
        'DEFAULT_CALLBACKS',
        'StochasticWeightAveraging',
        'cut_dataset',
        'check_tensor',
        'check_tensor_dict',
        'detach',
        'RandomizedSearchOnline',
        'collate_zeros_padding',
        'make_mask'
    )

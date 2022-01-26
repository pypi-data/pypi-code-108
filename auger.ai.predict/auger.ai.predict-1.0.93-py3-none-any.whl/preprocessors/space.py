import copy

preprocessors_space_ex = {
    'nan.NanPreprocessor': {
        "thresh_col": {
            "bounds": [
                0.0,
                1.0
            ],
            "type": "float",
            "default": 0.95
        },
        "auger_enabled": True
    },
    'date_time.DateTimePreprocessor': {
        "auger_enabled": True
    },
    'categorical.CategoricalPreprocessor': {
        "max_categoricals_nunique": {
            "bounds": [
                1,
                None  # No upper bound
            ],
            "type": "int",
            "default": 50
        },
        "auger_enabled": True
    },
    'text.TextPreprocessor': {
        'vectorize': {
            "values": ['en_use_lg','hashing','en_use_md','en_use_cmlm_md','en_use_cmlm_lg'],
            "type": "categorical",
            "default": "en_use_lg"
        },
        'calc_distance': {
            "values": ['none', 'cosine', 'cityblock', 'euclidean', 'haversine', 'l1', 'l2', 'manhattan', 'nan_euclidean'],
            "type": "categorical",
            "default": "cosine"
        },

        "auger_enabled": True
    },    
    'eliminate.EliminatePreprocessor': {
        "thresh_var": {
            "bounds": [
                0.0,
                1.0
            ],
            "type": "float",
            "default": 0.05
        },
        "auger_enabled": True
    },
    'sparse.SparsePreprocessor': {
        "thresh_sparse": {
            "bounds": [
                0.1,
                1.0
            ],
            "type": "float",
            "default": 0.95
        },
        "n_comp_frac": {
            "bounds": [
                0.1,
                1.0
            ],
            "type": "float",
            "default": 0.2
        },
        "auger_enabled": True
    },
    'extra.ExtraPreprocessor': {
        "auger_enabled": True
    },
    'scale.ScalePreprocessor': {
        "auger_enabled": True
    },
    'dim_reduction.DimReductionPreprocessor': {
        'alg_name': {
            "values": [
                "PCA",
                "t-SNE"],
            "type": "categorical",
            "default": "PCA"
        },
        'n_components':
            {
                "bounds": [
                    1,
                    None
                ],
                "type": "int",
                "default": 2
            },
        "auger_enabled": False
    },

    # Time series Preprocessors
    "time_series.resample.ResamplePreprocessor": {
        "auger_enabled": True
    },
    "time_series.interpolate.InterpolatePreprocessor": {
        "method": {
            "values": ["linear", "nearest", "cubic", "spline"],
            "type": "categorical",
            "default": 'linear'
        },
        "auger_enabled": True
    },
    "time_series.embedding.EmbeddingPreprocessor": {
        "embedding_dim": {
            "bounds": [
                1,
                None  # No Upper bound
            ],
            "type": "int",
            "default": 10
        },
        "auger_enabled": True
    }
}

preprocessors_space = {
    'nan.NanPreprocessor': {
        'thresh_col': 0.95,
        'thresh_row': 0.05,
        'skip_errors': True
    },
    'date_time.DateTimePreprocessor': {
        'datetime_cols': [],
        'skip_errors': False
    },
    'categorical.CategoricalPreprocessor': {
        'cat_cols': [],
        'label_enc_cols': [],
        'max_categoricals_nunique': 50,
        'skip_errors': False,
        'run_in_process': False
    },
    'text.TextPreprocessor': {
        'text_cols': [],
        'vectorize': 'en_use_lg',
        'calc_distance': 'cosine',
        'skip_errors': False
    },        
    'eliminate.EliminatePreprocessor': {
        'thresh_var': 0.05,
        'skip_errors': True,
        'run_in_process': True        
    },
    'sparse.SparsePreprocessor': {
        'thresh_sparse': 0.95,
        'n_comp_frac': 0.2,
        'skip_errors': True,
        'run_in_process': True
    },
    'extra.ExtraPreprocessor': {
        'cyclic_cols': [],
        'interaction_cols': [],
        'skip_errors': True
    },
    'scale.ScalePreprocessor': {
        'skip_errors': False
    },
    'dim_reduction.DimReductionPreprocessor': {
        'alg_name': 'PCA',
        'n_components': 2,
        'skip_errors': False
    },

    # Time series Preprocessors
    "time_series.resample.ResamplePreprocessor": {
        'datetime_col': None,
        'sample_rate': None,
        'window_size': 1,
        'skip_errors': False
    },
    "time_series.interpolate.InterpolatePreprocessor": {
        'method': 'linear',
        'skip_errors': False
    },
    "time_series.ssa.SSAPreprocessor": {
        'lag_length': 10,
        'n_components': 5,
        'skip_errors': False
    },
    "time_series.embedding.EmbeddingPreprocessor": {
        'embedding_dim': 10,
        'skip_errors': False
    }
}

preprocessors_groups = [
    {'start': [
        'date_time.DateTimePreprocessor',
        'text.TextPreprocessor',        
        'categorical.CategoricalPreprocessor',
        'nan.NanPreprocessor'
    ]},

    {'standard': [
        'eliminate.EliminatePreprocessor',
        'sparse.SparsePreprocessor',
        'extra.ExtraPreprocessor',
        'scale.ScalePreprocessor'
    ]},
    {'standard_ex': [
        'dim_reduction.DimReductionPreprocessor'
    ]},

    {'time_series': [
        'time_series.resample.ResamplePreprocessor',
        'time_series.interpolate.InterpolatePreprocessor',
        # 'time_series.ssa.SSAPreprocessor',
        'time_series.embedding.EmbeddingPreprocessor'
    ]}
]

ts_models = ['auger_ml.algorithms.ts_lstm.TimeSeriesLSTM',
             'auger_ml.algorithms.ts_dnn.DeepTimeSeriesRegressor',
             "auger_ml.algorithms.timeseries.ARIMAXBaseRegressor",
             "auger_ml.algorithms.timeseries.VARXBaseRegressor"]

advanced_models = ['auger_ml.algorithms.cat_boost.CatBoostClassifier', 'CatBoostClassifier',
                   'auger_ml.algorithms.cat_boost.CatBoostRegressor', 'CatBoostRegressor',
                   'lightgbm.LGBMClassifier', 'LGBMClassifier',
                   'lightgbm.LGBMRegressor','LGBMRegressor']

fold_groups = [
    # if len(self.options.get('timeSeriesFeatures', [])) > 0:
    {'name': 'time_series_advanced_model',
     'groups': ['start', 'time_series'],
     'fillna': ['nan.NanPreprocessor'],
     'allow_oversampling': True},
    {'name': 'time_series_standard_model',
     'base_group': 'time_series_advanced_model',
     'groups': ['standard'],
     'fillna': ['eliminate.EliminatePreprocessor'],
     'allow_oversampling': True},

    # ds.sort(self.options['timeSeriesFeatures'])
    # ds.drop(self.options['timeSeriesFeatures'])
    {'name': 'time_series_ts_model',
     'groups': ['start', 'standard'],
     'fillna': ['nan.NanPreprocessor', 'eliminate.EliminatePreprocessor'],
     'allow_oversampling': True},

    {'name': 'advanced_model',
     'groups': ['start'],
     'fillna': ['nan.NanPreprocessor'],
     'allow_oversampling': True},
    {'name': 'standard_model',
     'base_group': 'advanced_model',
     'groups': ['standard', 'standard_ex'],
     'fillna': ['eliminate.EliminatePreprocessor'],
     'allow_oversampling': True},
]


# advanced_models = []
# fold_groups = [
#     #if len(self.options.get('timeSeriesFeatures', [])) > 0:
#     {'name':'time_series_standard_model', 'groups': ['time_series', 'start', 'standard'], 'fillna': ['eliminate.EliminatePreprocessor']},

#     #ds.sort(self.options['timeSeriesFeatures'])
#     #ds.drop(self.options['timeSeriesFeatures'])    
#     {'name':'time_series_ts_model', 'groups': ['start', 'standard'], 'fillna': ['eliminate.EliminatePreprocessor']},

#     {'name':'standard_model', 'groups': ['start', 'standard'], 'fillna': ['eliminate.EliminatePreprocessor']},
# ]

def pspace_is_advanced_model(algorithm_name):
    return algorithm_name in advanced_models


def pspace_get_fold_group(algorithm_name, time_series):
    if algorithm_name in ts_models:
        return 'time_series_ts_model'
    elif time_series:
        if algorithm_name in advanced_models:
            return 'time_series_advanced_model'
        else:
            return 'time_series_standard_model'
    else:
        if algorithm_name in advanced_models:
            return 'advanced_model'
        else:
            return 'standard_model'


def pspace_get_fold_groups(time_series):
    res = []
    for fold_group in fold_groups:
        if time_series:
            if 'time_series' in fold_group['name']:
                res.append(fold_group)
        elif not 'time_series' in fold_group['name']:
            res.append(fold_group)

    return res


# def pspace_get_preprocessors_space(time_series=False):
#     groups = ['start', 'standard', 'standard_ex']
#     if time_series:
#         groups = ['start', 'time_series', 'standard']

#     res = []
#     for group in groups:
#         for pname in ppspace_get_preprocessors_group_by_name(group)[group]:
#             params = copy.deepcopy(preprocessors_space[pname])
#             exclude_params = ['skip_errors', 'datetime_cols', 'cat_cols', 'label_enc_cols', 'run_in_process',
#                               'cyclic_cols', 'interaction_cols', 'datetime_col']
#             for name in exclude_params:
#                 if name in params:
#                     del params[name]

#             res.append({pname: params})

#     return res


def pspace_get_preprocessors_space_ex(time_series=False):
    groups = ['start', 'standard', 'standard_ex']
    if time_series:
        groups = ['start', 'time_series', 'standard']

    res = []
    for group in groups:
        for pname in ppspace_get_preprocessors_group_by_name(group)[group]:
            res.append({pname: preprocessors_space_ex[pname]})

    return res


def pspace_is_fold_group_allow_oversampling(name):
    res = True
    for fold_group in fold_groups:
        if fold_group['name'] == name:
            res = fold_group['allow_oversampling']
            break

    return res


def pspace_get_fold_group_names(time_series):
    res = pspace_get_fold_groups(time_series)

    return [fold_group['name'] for fold_group in res]


def ppspace_get_fold_group_by_name(name):
    for fold_group in fold_groups:
        if fold_group['name'] == name:
            return fold_group

    return {}


def ppspace_get_preprocessors_group_by_name(name):
    for p_group in preprocessors_groups:
        if list(p_group.keys())[0] == name:
            return p_group

    return {}


def ppspace_is_timeseries_model(algorithm_name):
    for item in ts_models:
        if algorithm_name in item:
            return True

    return False

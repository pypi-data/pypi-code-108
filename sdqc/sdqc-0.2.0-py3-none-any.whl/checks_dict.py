from . import checks as c

checks_dict = {
    # name_of_the_check: {
    #    'func': check_function,
    #    'descr': description,
    #    'flag': name_of_the_flag_in config_file_to_activate_check,
    #    'targets': [targets ('constant', 'data', 'series', 'dataseries')]
    #    'args': {
    #       name_of_the_arg_in config_file: (type, name_of_the_arg_in_function)
    #       }
    # }
    'missing_values': {
        'func': c.missing_values,
        'descr': 'Checks for missing values on the data.',
        'flag': 'missing',
        'targets': ['constant']
    },
    'missing_values_data': {
        'func': c.missing_values_data,
        'descr': 'Checks for missing values on the data giving the series.',
        'flag': 'missing',
        'targets': ['dataseries'],
        'args': {'completeness': ('str', 'completeness')}
    },
    'series_monotony': {
        'func': c.series_monotony,
        'descr': 'Checks if series is monotonically increasing.',
        'flag': 'series_monotony',
        'targets': ['series']
    },
    'series_range': {
        'func': c.series_range,
        'descr': 'Checks if series isinside a range.',
        'flag': 'series_range',
        'targets': ['series'],
        'args': {'series_range_values': ('list (float)', 'srange')}
    },
    'series_increment_type': {
        'func': c.series_increment_type,
        'descr': 'Checks if series series increment type.',
        'flag': 'series_increment',
        'targets': ['series'],
        'args': {'series_increment_type': ('str', 'type')}
    },
    'outlier_values': {
        'func': c.outlier_values,
        'descr': 'Checks for outlier values on the data.',
        'flag': 'outliers',
        'targets': ['constant', 'data'],
        'args': {'outliers_method': ('str', 'method'),
                 'outliers_nstd': ('float', 'nstd'),
                 'outliers_niqr': ('float', 'niqr')}
    }
}

import math
from typing import List

import pandas as pd

from magnumapi.optimization.design_variable.GeneticDesignVariable import GeneticDesignVariable, \
    GeneticLayerDesignVariable, GeneticBlockDesignVariable, GeneticMultiBlockDesignVariable


def init_genetic_design_variables_with_csv(csv_path: str) -> List[GeneticDesignVariable]:
    # todo: add description of columns in the dataframe
    design_variables_df = pd.read_csv(csv_path)
    genetic_design_variables = []
    for _, row in design_variables_df.iterrows():
        gen_dv = get_genetic_design_variable_class(row)
        genetic_design_variables.append(gen_dv)

    return genetic_design_variables


def get_genetic_design_variable_class(params):
    if is_param_nan(params['bcs']) and is_param_nan(params['layer']):
        kwargs = params[['xl', 'xu', 'variable_type', 'variable', 'bits']].to_dict()
        return GeneticDesignVariable(**kwargs)
    elif is_param_nan(params['bcs']) and not is_param_nan(params['layer']):
        kwargs = params[['xl', 'xu', 'variable_type', 'variable', 'layer', 'bits']].to_dict()
        return GeneticLayerDesignVariable(**kwargs)
    elif isinstance(params['bcs'], (int, float)):
        kwargs = params[['xl', 'xu', 'variable_type', 'variable', 'layer', 'bcs', 'bits']].to_dict()
        return GeneticBlockDesignVariable(**kwargs)
    elif '-' in params['bcs']:
        kwargs = params[['xl', 'xu', 'variable_type', 'variable', 'layer', 'bcs', 'bits']].to_dict()
        return GeneticMultiBlockDesignVariable(**kwargs)
    else:
        raise AttributeError('The design variable has incorrect block index value: %s.' % params['bcs'])


def is_param_nan(param):
    return param == '' or param == 'nan' or math.isnan(param)

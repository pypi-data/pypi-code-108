import os
import sys
import copy
import json
from typing import Optional, Union, Dict, List
from itertools import repeat

import pandas as pd

from quickstats.components import AsymptoticCLs, ParamParser
from quickstats.concurrent.logging import standard_log
from quickstats.utils.common_utils import execute_multi_tasks

def run_param_point(filename:str, parameters:Optional[Dict]=None,
                    outname:str="limit.json", cache:bool=True,
                    save_log:bool=True, save_summary:bool=True,
                    config:Optional[Dict]=None):

    if parameters is not None:
        param_str = "(" + ", ".join([f"{param}={round(value, 8)}" for param, value in parameters.items()]) + ")"
    else:
        param_str = ""
    sys.stdout.write(f"INFO: Evaluating limit for the workspace {filename} {param_str}\n")

    if cache and os.path.exists(outname):
        sys.stdout.write(f"INFO: Cached limit output from {outname}\n")
        with open(outname, 'r') as f:
            limits = json.load(f)
            return limits

    if save_log:
        log_path = outname.replace(".json", ".log")
    else:
        log_path = None

    config['filename'] = filename

    asymptotic_cls = None
    with standard_log(log_path) as logger:
        asymptotic_cls = AsymptoticCLs(**config)
        asymptotic_cls.evaluate_limits()
        if outname is not None:
            asymptotic_cls.save(outname, summary=save_summary)
    if asymptotic_cls is None:
        return {}
    return asymptotic_cls.limits
    
def run_param_scan(dirname:str="", file_expr:Optional[str]=None, 
                   param_expr:Optional[str]=None, outdir:str="output",
                   outname:str="limits.json", cache:bool=True,
                   save_log:bool=True, save_summary:bool=True,
                   parallel:int=-1, config:Optional[Dict]=None):
    parser = ParamParser(file_expr, param_expr)
    param_points = parser.get_param_points(dirname)
    
    if config is None:
        config = {} 
    fix_param = config.get("fix_param", "")
    
    fnames     = []
    parameters = []
    cache_outnames = []
    configs    = []
    
    for point in param_points:
        int_params = point['internal_parameters']
        ext_params = point['external_parameters']
        if set(int_params) & set(ext_params):
            raise RuntimeError("internal and external parameters are not mutually exclusive")
        if len(int_params) + len(ext_params) == 0:
            raise RuntimeError("no parameters to scan for")
        all_params = {**int_params, **ext_params}
        parameters.append(all_params)
        
        fname = point['filename']
        fnames.append(fname)
        
        point_config = copy.deepcopy(config)
        val_expr = parser.val_encode_parameters(int_params)
        fix_expr = []
        if fix_param:
            fix_expr.append(fix_param)
        if val_expr:
            fix_expr.append(val_expr)
        point_config['fix_param'] = ",".join(fix_expr)
        configs.append(point_config)

        str_encoded_name = parser.str_encode_parameters(all_params)
        cache_outname = os.path.join(outdir, f"{str_encoded_name}.json")
        cache_outnames.append(cache_outname)
        
    argument_list = (fnames, parameters, cache_outnames, repeat(cache), repeat(save_log),
                     repeat(save_summary), configs)
    
    if ((outname is not None) or cache) and not os.path.exists(outdir):
        os.makedirs(outdir, exist_ok=True)
        
    limit_result = execute_multi_tasks(run_param_point, *argument_list, parallel=parallel)
    
    final_result = []

    for fname, params, limit in zip(fnames, parameters, limit_result):
        if len(limit) == 0:
            param_str = parser.val_encode_parameters(params)
            raise RuntimeError(f'Job failed for the input "{fname}" ({param_str}). '
                               'Please check the log file for more details.')
        final_result.append({**params, **limit})
    final_result = pd.DataFrame(final_result).to_dict('list')
    
    if outname is not None:
        outpath = os.path.join(outdir, outname)
        with open(outpath, "w") as f:
            json.dump(final_result, f, indent=2)
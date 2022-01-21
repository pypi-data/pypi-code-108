from typing import Optional, Union, Dict
import os
import math
import json
from itertools import repeat

import numpy as np

import quickstats
from quickstats.components import Likelihood
from quickstats.utils.common_utils import parse_config, execute_multi_tasks, NpEncoder

import ROOT

class PValueToys():
    
    def __init__(self, filename:str, poi_name:Optional[str]=None,
                 poi_val:Optional[float]=0, binned:bool=True,
                 verbosity:Union[int, str]="ERROR",
                 fit_options:Optional[Union[Dict, str]]=None):
        self.filename = filename
        self.poi_name = poi_name
        self.poi_val = poi_val
        self.binned = binned
        self.fit_options = parse_config(fit_options)
        self.fit_options['verbosity'] = verbosity
        
    def get_properties(self, nll_mufix:float, nll_muhat:float):
        q_mu = 2*(nll_mufix - nll_muhat)
        ndof = 1
        #p_value = ROOT.Math.chisquared_cdf_c(q_mu, ndof)
        pvalue = 1 - ROOT.Math.normal_cdf(math.sqrt(q_mu), 1, 0)
        significance = ROOT.RooStats.PValueToSignificance(pvalue)
        properties = {
            'q_mu': q_mu,
            'pvalue': pvalue,
            'significance': significance
        }
        return properties
    
    def _get_toy_results(self, n_toys:int, seed:int=0, batch_index:Optional[int]=None,
                         save_as:Optional[str]=None):
        if (batch_index is not None) and (save_as is not None):
            print(f"INFO: Evaluating toys for the batch: {batch_index}")
        likelihood = Likelihood(filename=self.filename,
                                poi_name=self.poi_name,
                                data_name=None,
                                config=self.fit_options)
        
        toys = likelihood.model.generate_toys(n_toys=n_toys,
                                              seed=seed,
                                              binned=self.binned,
                                              do_import=False)
        results = []
        for i in range(n_toys):
            likelihood.minimizer.data = toys[i]
            nll_muhat = likelihood.evaluate(poi_val=self.poi_val, unconditional=True)
            muhat = likelihood.poi.getVal()
            fit_status_muhat = likelihood.minimizer.status
            nll_mufix = likelihood.evaluate(poi_val=self.poi_val, unconditional=False)
            fit_status_mufix = likelihood.minimizer.status
            properties = self.get_properties(nll_mufix, nll_muhat)
            result = {
                'toy_index': i,
                'muhat': muhat, 
                'mufix': self.poi_val,
                'nll_muhat': nll_muhat,
                'nll_mufix': nll_mufix,
                'fit_status_muhat': fit_status_muhat,
                'fit_status_mufix': fit_status_mufix}
            result.update(properties)
            results.append(result)
        if batch_index is not None:
            for result in results:
                result['batch_index'] = batch_index
        if save_as is not None:
            with open(save_as, 'w') as f:
                json.dump(results, f, indent=2, cls=NpEncoder)
        return results
        
        
    def get_toy_results(self, n_toys:int=1000, seed:int=0, batchsize:int=100,
                        save_as:Optional[str]="toy_results.json", cache:bool=True,
                        parallel:int=-1):
        n_batches = n_toys // batchsize
        remainder = n_toys % batchsize
        if remainder != 0:
            batches = np.array([batchsize] * n_batches + [remainder])
        else:
            batches = np.array([batchsize] * n_batches)
        batch_indices = np.array(range(len(batches)))
        
        results = []
        
        if save_as:
            base_dir = os.path.dirname(save_as)
            if base_dir and (not os.path.exists(base_dir)):
                os.makedirs(base_dir, exist_ok=True)
            base_savename = os.path.splitext(save_as)[0]
            extension = os.path.splitext(save_as)[1]
            batch_save_as = [f"{base_savename}_batch_{i}{extension}" for i in batch_indices]
            cached_indices = []
            if cache:
                for i, path in enumerate(batch_save_as):
                    if os.path.exists(path):
                        try:
                            result = json.load(open(path, 'r'))
                            print(f'INFO: Cached batch toy results from "{path}"')
                            results += result
                            cached_indices.append(i)
                        except:
                            pass

            batches       = np.delete(batches, cached_indices)
            batch_indices = np.delete(batch_indices, cached_indices)
        else:
            batch_save_as = [None]*len(batches)
            
        arguments = (batches, repeat(seed), batch_indices, batch_save_as)
        
        
        tmp_verbosity = quickstats._PRINT_.verbosity

        batch_results = execute_multi_tasks(self._get_toy_results, *arguments, parallel=parallel)
        
        quickstats.set_verbosity(tmp_verbosity)
        
        for batch_result in batch_results:
            results += batch_result
        
        if save_as is not None:
            with open(save_as, 'w') as f:
                json.dump(results, f, indent=2, cls=NpEncoder)
        return results
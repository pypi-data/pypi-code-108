##################################################################################################
# Based on https://gitlab.cern.ch/atlas-physics/stat/tools/StatisticsTools by Stefan Gadatsch
# Author: Alkaid Cheng
# Email: chi.lung.cheng@cern.ch
##################################################################################################
import os
import sys
import time
import json
import fnmatch
from itertools import repeat
from typing import List, Optional

import uproot
import numpy as np

from quickstats.components import ExtendedModel, ExtendedMinimizer
from quickstats.utils import root_utils, common_utils

import ROOT

class NuisanceParameterPull(object):
    @property
    def model(self):
        return self._model
    
    @property
    def workspace(self):
        return self._workspace
    @property
    def model_config(self):
        return self._model_config
    @property
    def pdf(self):
        return self._pdf
    @property
    def data(self):
        return self._data
    @property
    def nuisance_parameters(self):
        return self._nuisance_parameters
    @property
    def global_observables(self):
        return self._global_observables
    @property
    def pois(self):
        return self._pois
    @property
    def observables(self):
        return self._observables  
    
    def __init__(self):
        self._model               = None
        self._workspace           = None
        self._model_config        = None
        self._pdf                 = None
        self._data                = None
        self._nuisance_parameters = None
        self._global_observables  = None
        self._pois                = None
        self._observables         = None
    
    @staticmethod
    def evaluate_impact(model:ExtendedModel, minimizer:ExtendedMinimizer,
                        nuis, nominal_value, pois, minimizer_options, snapshot=None):
        poi_values = []
        start_time = time.time()
        if snapshot:
            model.workspace.loadSnapshot(snapshot)
        nuis.setVal(nominal_value)
        nuis.setConstant(1)   
        minimizer.minimize(**minimizer_options)
        for poi in pois:
            poi_values.append(poi.getVal())
        elapsed_time = time.time() - start_time
        return poi_values, elapsed_time

    @staticmethod
    def _run_pulls(input_file:str, data:str, snapshot:str, nuis_name:str, poi_name:str, 
                   fix_param:Optional[str]=None, profile_param:Optional[str]=None, binned:bool=True,
                   workspace:Optional[str]=None, model_config:Optional[str]=None,
                   minimizer_type:str='Minuit2', minimizer_algo:str='Migrad', 
                   precision:float=0.001, eps:float=1.0, strategy:int=0, print_level:int=1,
                   num_cpu:int=1, offset:bool=True, optimize:int=2, eigen:bool=False,
                   fix_cache:bool=True, fix_multi:bool=True, max_calls:int=-1, 
                   max_iters:int=-1, batch_mode:bool=False, int_bin_precision:float=-1.,
                   outdir:str='pulls', cache=True, logfile_path=None, **kwargs):
        # create output directory if not exists
        if not os.path.exists(outdir):
            os.makedirs(outdir, exist_ok=True)        
        outname_root = os.path.join(outdir, nuis_name + '.root')
        outname_json = os.path.join(outdir, nuis_name + '.json')
        #checkpointing:
        if (os.path.exists(outname_root) and os.path.exists(outname_json)) and cache:
            print('INFO: Jobs already finished for the NP: {}. Skipping.'.format(nuis_name))
            return None
        else:
            print('INFO: Evaluating pulls for the NP: {}'.format(nuis_name))
        if logfile_path is not None:
            common_utils.redirect_stdout(logfile_path)
        start_time = time.time()
        # load model
        model = ExtendedModel(fname=input_file, ws_name=workspace,
                              mc_name=model_config, data_name=data, 
                              snapshot_name=snapshot, binned_likelihood=binned,
                              fix_cache=fix_cache, fix_multi=fix_multi)
        if fix_param:
            model.fix_parameters(fix_param)
            
        # by default fix all POIs before floating
        model.set_parameter_defaults(model.pois, error=0.15, constant=1, remove_range=True)
        for param in model.pois:
            extra_str = 'Fixing' if param.isConstant() else 'Set'
            print('INFO: {} POI {} at value {}'.format(extra_str, param.GetName(), param.getVal()))
        
        # collect pois
        rank_pois = model.profile_parameters(poi_name)
        model.set_parameter_defaults(rank_pois, error=0.15)     
        
        # profile pois
        if profile_param:
            print('INFO: Profiling POIs')
            profile_pois = model.profile_parameters(profile_param)
        
        buffer_time = time.time()
    
        nuip = model.workspace.var(nuis_name)
        if not nuip:
            raise ValueError('Nuisance parameter "{}" does not exist'.format(parameter))
        nuip_name = nuip.GetName()
        nuip.setConstant(0)
        print('INFO: Computing error for parameter "{}" at {}'.format(nuip.GetName(), nuip.getVal()))
        
        print("INFO: Making ExtendedMinimizer for unconditional fit")
        minimizer = ExtendedMinimizer("minimizer", model.pdf, model.data)
        print("INFO: Starting minimization")
        nll_commands = [ROOT.RooFit.NumCPU(num_cpu, 3),
                        #ROOT.RooFit.Constrain(model.nuisance_parameters),
                        ROOT.RooFit.GlobalObservables(model.global_observables), 
                        ROOT.RooFit.Offset(offset)]
        if hasattr(ROOT.RooFit, "BatchMode"):
            nll_commands.append(ROOT.RooFit.BatchMode(batch_mode))
        if hasattr(ROOT.RooFit, "IntegrateBins"):
            nll_commands.append(ROOT.RooFit.IntegrateBins(int_bin_precision))            

        minimize_options = {
            'minimizer_type'   : minimizer_type,
            'minimizer_algo'   : minimizer_algo,
            'default_strategy' : strategy,
            'opt_const'        : optimize,
            'precision'        : precision,
            'eps'              : eps,
            'max_calls'        : max_calls,
            'max_iters'        : max_iters,
        }

        minimizer.minimize(nll_commands=nll_commands,
                           scan=1, scan_set=ROOT.RooArgSet(nuip),
                           **minimize_options)
        unconditional_time = time.time() - buffer_time
        print("INFO: Fitting time: {:.3f} s".format(unconditional_time))
        pois_hat = []
        for rank_poi in rank_pois:
            name = rank_poi.GetName()
            value = rank_poi.getVal()
            pois_hat.append(value)
            print('{} {}'.format(name, value))
        
        model.workspace.saveSnapshot('tmp_snapshot', model.pdf.getParameters(model.data))
        print('INFO: Made unconditional snapshot with name tmp_snapshot')
        
        # find prefit variation
        buffer_time = time.time()
        
        nuip_hat = nuip.getVal()
        nuip_errup = nuip.getErrorHi()
        nuip_errdown = nuip.getErrorLo()

        all_constraints = model.get_all_constraints()
        prefit_variation, constraint_type, nuip_nom = model.inspect_constrained_nuisance_parameter(nuip, all_constraints)
        if not constraint_type:
            print('INFO: Not a constrained parameter. No prefit impact can be determined. Use postfit impact instead.')
        prefit_uncertainty_time = time.time() - buffer_time
        print('INFO: Time to find prefit variation: {:.3f} s'.format(prefit_uncertainty_time))
        
        if rank_pois:
            new_minimizer_options = {
                'nll_commands': nll_commands,
                'reuse_nll'   : 1,
                **minimize_options
            }
            # fix theta at the MLE value +/- postfit uncertainty and minimize again to estimate the change in the POI
            print('INFO: Evaluating effect of moving {} up by {} + {}'.format(nuip_name, nuip_hat, nuip_errup))
            pois_up, postfit_up_impact_time = NuisanceParameterPull.evaluate_impact(model, minimizer,
                                                nuip, nuip_hat + abs(nuip_errup), rank_pois,
                                                new_minimizer_options,  'tmp_snapshot')
            print('INFO: Time to find postfit up impact: {:.3f} s'.format(postfit_up_impact_time))
            
            print('INFO: Evaluating effect of moving {} down by {} - {}'.format(nuip_name, nuip_hat, nuip_errup))
            pois_down, postfit_down_impact_time = NuisanceParameterPull.evaluate_impact(model, minimizer,
                                                    nuip, nuip_hat - abs(nuip_errdown), rank_pois,
                                                    new_minimizer_options,  'tmp_snapshot')
            print('INFO: Time to find postfit down impact: {:.3f} s'.format(postfit_down_impact_time))
            
            # fix theta at the MLE value +/- prefit uncertainty and minimize again to estimate the change in the POI
            
            if constraint_type:
                print('Evaluating effect of moving {} up by {} + {}'.format(nuip_name, nuip_hat, prefit_variation))
                pois_nom_up, prefit_up_impact_time = NuisanceParameterPull.evaluate_impact(model, minimizer,
                                                        nuip, nuip_hat + prefit_variation, rank_pois,
                                                        new_minimizer_options,  'tmp_snapshot')
                print('INFO: Time to find prefit up impact: {:.3f} s'.format(prefit_up_impact_time))      
                
                print('Evaluating effect of moving {} down by {} - {}'.format(nuip_name, nuip_hat, prefit_variation))
                pois_nom_down, prefit_down_impact_time = NuisanceParameterPull.evaluate_impact(model, minimizer,
                                                            nuip, nuip_hat - prefit_variation, rank_pois,
                                                            new_minimizer_options,  'tmp_snapshot')
                print('INFO: Time to find prefit down impact: {:.3f} s'.format(prefit_up_impact_time))
            else:
                print('WARNING: Prefit impact not estimated, instead postfit impact is cloned')
                pois_nom_up = [i for i in pois_up]
                pois_nom_down = [i for i in pois_down]
        else:
            pois_up, pois_down, pois_nom_up, pois_nom_down = [], [], [], []
        
        end_time = time.time()
        print('\nINFO: Time to perform all fits: {:.3f} s'.format(end_time-start_time))
        print('INFO: Unconditional minimum of NP {}: {} + {} - {}'.format(nuis_name, nuip_hat, 
              abs(nuip_errup), abs(nuip_errdown)))
        print('INFO: Prefit uncertainy of NP {}: {} +/- {}'.format(nuis_name, nuip_hat, prefit_variation))
        for i, rank_poi in enumerate(rank_pois):
            print('INFO: Unconditional minimum of POI {}: {}'.format(rank_poi.GetName(), pois_hat[i]))
            print('INFO: POI when varying NP up by 1 sigma postfit (prefit): {} ({})'.format(pois_up[i], pois_nom_up[i]))
            print('INFO: POI when varying NP down by 1 sigma postfit (prefit): {} ({})'.format(pois_down[i], pois_nom_down[i]))
            
        # store result in root file
        outname_root = os.path.join(outdir, nuis_name + '.root')
        
        result = {}
        result['nuis'] = {  'nuisance'   : nuis_name,
                            'nuis_nom'   : nuip_nom,
                            'nuis_hat'   : nuip_hat,
                            'nuis_hi'    : nuip_errup,
                            'nuis_lo'    : nuip_errdown,
                            'nuis_prefit': prefit_variation}
        result['pois'] = {}
        for i, rank_poi in enumerate(rank_pois):
            name = rank_poi.GetName()
            result['pois'][name] = { 'hat'     : pois_hat[i],
                                     'up'      : pois_up[i],
                                     'down'    : pois_down[i],
                                     'up_nom'  : pois_nom_up[i],
                                     'down_nom': pois_nom_down[i]}
            
        result_for_root = {}
        result_for_root.update(result['nuis'])
        for k,v in result['pois'].items():
            buffer = {'{}_{}'.format(k, kk): vv for kk,vv in v.items()}
            result_for_root.update(buffer)
        r_file = ROOT.TFile(outname_root, "RECREATE")
        r_tree = ROOT.TTree("result", "result")
        root_utils.fill_branch(r_tree, result_for_root)
        r_file.Write()
        r_file.Close()
        print('INFO: Saved output to {}'.format(outname_root))
        outname_json = os.path.join(outdir, nuis_name + '.json')
        json.dump(result, open(outname_json, 'w'), indent=2)
        
        if logfile_path is not None:
            common_utils.restore_stdout()

    @common_utils.timer
    def run_pulls(self, input_file:str='workspace.root', data:str='combData', poi:str='', 
                  snapshot:str='nominalNuis', outdir:str='output', profile:Optional[str]=None,
                  fix:Optional[str]=None, workspace:Optional[str]=None, model_config:Optional[str]=None,
                  minimizer_type:str='Minuit2', minimizer_algo:str='Migrad', num_cpu:int=1, 
                  binned:bool=1, precision:float=0.001, eps:float=1.0, log_level:str='INFO', eigen:bool=False, 
                  strategy:int=0, print_level:int=1, fix_cache:bool=True, fix_multi:bool=True, offset:bool=True, 
                  optimize:int=2, parameter:str="", max_calls:int=-1, max_iters:int=-1, batch_mode:bool=False, 
                  int_bin_precision:float=-1.,parallel:int=0, cache:bool=True, exclude:str='', **kwargs):
        
        # configure default minimizer options
        ExtendedMinimizer._configure_default_minimizer_options(minimizer_type, minimizer_algo,
            strategy, debug_mode=(log_level=="DEBUG"))
        
        nuis_list = ExtendedModel.get_nuisance_parameter_names(input_file, workspace, model_config)
        include_patterns = parameter.split(',')
        if parameter:
            nuis_to_include = []
            for nuis_name in nuis_list:
                # filter out nuisance parameters
                if any(fnmatch.fnmatch(nuis_name, include_pattern) for include_pattern in include_patterns):
                    nuis_to_include.append(nuis_name)
        else:
            nuis_to_include = nuis_list
        exclude_patterns = exclude.split(',')
        nuis_to_exclude = []
        if exclude_patterns:
            for nuis_name in nuis_list:
                if any(fnmatch.fnmatch(nuis_name, exclude_pattern) for exclude_pattern in exclude_patterns):
                    nuis_to_exclude.append(nuis_name)
        nuis_names = list(set(nuis_to_include) - set(nuis_to_exclude))
        
        if log_level == 'INFO':
            logfile_paths = [os.path.join(outdir, '{}.log'.format(nuis_name)) for nuis_name in nuis_names]
        else:
            logfile_paths = [None]*len(nuis_names)
            

        arguments = (repeat(input_file), repeat(data), repeat(snapshot), nuis_names, 
                     repeat(poi), repeat(fix), repeat(profile), repeat(binned),
                     repeat(workspace), repeat(model_config), repeat(minimizer_type), 
                     repeat(minimizer_algo), repeat(precision), repeat(eps), repeat(strategy),
                     repeat(print_level), repeat(num_cpu), repeat(offset), repeat(optimize), 
                     repeat(eigen), repeat(fix_cache), repeat(fix_multi), repeat(max_calls), 
                     repeat(max_iters), repeat(batch_mode), repeat(int_bin_precision),
                     repeat(outdir), repeat(cache), logfile_paths)
        common_utils.execute_multi_tasks(self._run_pulls, *arguments, parallel=parallel)

        
    @staticmethod
    def parse_root_result(fname):
        with uproot.open(fname) as file:
            result = root_utils.uproot_to_dict(file)
        return result
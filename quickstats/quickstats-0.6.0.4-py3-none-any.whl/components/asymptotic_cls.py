from typing import Optional, Union, Dict
import os
import math
import json

import numpy as np

from quickstats import semistaticmethod
from quickstats.components import AnalysisObject
from quickstats.utils.root_utils import load_macro
from quickstats.utils import common_utils
from quickstats.utils.io import Verbosity

import ROOT

class AsymptoticCLs(AnalysisObject):
    
    _SIGMA_LABEL_ = {
            2: '+2sigma',
            1: '+1sigma',
            0: 'Median',
           -1: '-1sigma',
           -2: '-2sigma',
        'obs': 'Observed',
        'inj': 'Injected'
    }
    
    def __init__(self, filename:str, poi_name:str=None, data_name:str='combData', 
                 CL:float=0.95, precision:float=0.005, do_tilde:bool=True,
                 do_better_bands:bool=True, predictive_fit:bool=False,
                 better_negative_bands:bool=False, do_blind:bool=True,
                 binned_likelihood:bool=True, fix_param:str='', profile_param:str='',
                 ws_name:Optional[str]=None, mc_name:Optional[str]=None,
                 snapshot_name:Optional[str]=None, timer:bool=False,
                 minimizer_type:str='Minuit2', minimizer_algo:str='Migrad', 
                 eps:float=1.0, strategy:int=1, print_level:int=-1, 
                 num_cpu:int=1, offset:bool=True, optimize:int=2,
                 fix_cache:bool=True, fix_multi:bool=True, max_calls:int=-1,
                 max_iters:int=-1, constrain_nuis:bool=True, batch_mode:bool=False,
                 int_bin_precision:float=-1., verbosity:Optional[Union[int, str]]="INFO", **kwargs):
        """
        args:
            precision: precision in mu that defines iterative cutoff
            do_tilde: bound mu at zero if true and do the \tilde{q}_{mu} asymptotics
            use_predictive_fit: experimental, extrapolate best fit nuisance parameters based on previous fit results
        """

        config = {
            'filename': filename,
            'data_name': data_name,
            'poi_name': poi_name,
            'binned_likelihood' : binned_likelihood,
            'fix_param': fix_param,
            'profile_param': profile_param,
            'ws_name': ws_name,
            'mc_name': mc_name,
            'snapshot_name': snapshot_name,
            'minimizer_type': minimizer_type,
            'minimizer_algo': minimizer_algo,
            'eps': eps,
            'strategy': strategy,
            'num_cpu': num_cpu,
            'offset': offset,
            'optimize': optimize,
            'eigen': False,
            'print_level': print_level,
            'timer': timer,
            'fix_cache': fix_cache,
            'fix_multi': fix_multi,
            'max_calls': max_calls,
            'max_iters': max_iters,
            'constrain_nuis': constrain_nuis,
            'batch_mode': batch_mode,
            'int_bin_precision': int_bin_precision,
            'verbosity': verbosity
        }

        super().__init__(**config)

        self.do_blind = do_blind
        self.CL = CL
        self.precision = precision
        self.do_tilde = do_tilde
        self.use_predictive_fit = predictive_fit
        self.do_better_bands = do_better_bands
        self.better_negative_bands = better_negative_bands
        self.direction = 1
        self.global_status = 0
        
        # define simplified names
        self.ws = self.model.workspace
        self.globs = self.model.global_observables
        self.pdf = self.model.pdf
        self.data = self.model.data
        self.nuis = self.model.nuisance_parameters
        if not self.nuis:
            self.nuis = ROOT.RooArgSet()
        # define names used for various objects
        names = self.model._DEFAULT_NAMES_
        self.nom_glob_name = names['nominal_globs']
        self.nom_nuis_name = names['nominal_nuis']
        self.nll_snapshot_name = names['nll_snapshot']
        self.load_extension()
        self.LimitTool = ROOT.AsymptoticCLsTool(1 - self.CL, precision, do_tilde)

    @semistaticmethod
    def load_extension(self):
        try:
            if not hasattr(ROOT, 'AsymptoticCLsTool'):
                result = load_macro('AsymptoticCLsTool')
                if hasattr(ROOT, 'AsymptoticCLsTool'):
                    self.stdout.info('INFO: Loaded extension module "AsymptoticCLsTool"')
        except Exception as e:
            print(e)
            
    def set_poi(self, poi_name:Optional[str]=None):
        if poi_name is None:
            self.poi = self.model.pois.first()
            self.stdout.info('INFO: POI name not given. Set to first poi "{}" by default.'.format(self.poi.GetName()))
        else:
            self.poi = self.model.get_poi(poi_name)
            self.stdout.info('INFO: POI set to "{}"'.format(poi_name))
        
    def set_poi_value(self, val:float):
        if math.isnan(val):
            raise ValueError("cannot set poi to nan")
        if ( val > 0 ) and (self.poi.getMax() < val):
            self.poi.setMax(2*val)
        if ( val < 0 ) and (self.poi.getMin() > val):
            self.poi.setMin(2*val)
        self.poi.setVal(val)
        
    def save_snapshot(self, name:str, target:str="nuis"):
        if target == "nuis":
            self.ws.saveSnapshot(name, self.nuis)
        elif target == "globs":
            self.ws.saveSnapshot(name, self.globs)
            
    def load_snapshot(self, name:str):
        snapshot = self.ws.getSnapshot(name)
        if snapshot == None:
            raise RuntimeError('snapshot "{}" does not exist'.format(name))
        self.stdout.debug('INFO: Loaded snapshot "{}"'.format(name))
        self.ws.loadSnapshot(name)
            
    def save_nll_snapshot(self, nll, mu):
        name = self.nll_snapshot_name.format(nll_name=nll.GetName(), mu=mu)
        self.ws.saveSnapshot(name, self.nuis)
        
    def load_nll_snapshot(self, nll, mu):
        name = self.nll_snapshot_name.format(nll_name=nll.GetName(), mu=mu)
        self.load_snapshot(name) 
    
    def load_conditional_snapshot(self, mu:float, target:str="nuis"):
        name = self.get_conditional_snapsot_name(mu, target)
        self.load_snapshot(name)
    
    def get_conditional_snapsot_name(self, mu:float, target:str="nuis"):
        if target == "nuis":
            name = self.model._DEFAULT_NAMES_['conditional_nuis'].format(mu=mu)
        elif target == "globs":
            name = self.model._DEFAULT_NAMES_['conditional_globs'].format(mu=mu)
        else:
            raise ValueError('unknown conditional snapshot target "{}"'.format(target))
        return name

    def get_nll_val(self, nll:"ROOT.RooNLLVar"):
        snapshot_name = self.nll_maps[nll].get('snapshot', None)
        if snapshot_name:
            self.load_snapshot(snapshot_name)
        else:
            raise RuntimeError('Failed to load snapshot for nll "{}"'.format(nll.GetName()))
        if Verbosity.DEBUG >= self.stdout.verbosity:
            self.stdout.debug("DEBUG: Before Fit ----------------------------------------------")
            self.model.print_summary(items=['poi', 'nuisance_parameter', 'global_observable'])             
        self.global_status += self.minimizer.minimize(nll)
        self.minimizer_calls += 1
        nll_val = nll.getVal()
        if Verbosity.DEBUG >= self.stdout.verbosity:
            self.stdout.debug("DEBUG: After Fit ----------------------------------------------")
            self.model.print_summary(items=['poi', 'nuisance_parameter', 'global_observable'])          
        self.load_snapshot(self.nom_glob_name)
        return nll_val
    
    def create_nll(self, dataset:"ROOT.RooDataSet"):
        return self.pdf.createNLL(dataset, *self.minimizer.nll_command_list)
        
    def get_qmu(self, nll:"ROOT.RooNLLVar", mu:float):
        nll_muhat = self.nll_maps[nll].get('nll_mu_hat', None)
        if nll_muhat is None:
            raise RuntimeError('Failed to get nominal nll for "{}"'.format(nll.GetName()))
        is_const = self.poi.isConstant()
        self.poi.setConstant(1)
        self.set_poi_value(mu)
        nll_value = self.get_nll_val(nll)
        self.poi.setConstant(is_const)
        qmu = 2*(nll_value - nll_muhat)
        if qmu < 0 :
            raise RuntimeError("qmu is negative which means the globally minimized "
                               "NLL is larger then the NLL of interest")
        return qmu

    def do_predictive_fit(self, nll:"ROOT.RooNLLVar", mu1:float, mu2:float, mu:float):
        if (abs(mu2-mu) < self.direction*mu*self.precision*4):
            self.load_nll_snapshot(nll, mu2)
            return None
        if not self.nuis:
            return None
        # extrapolate to mu using mu1 and mu2 assuming nuis scale linear in mu
        n_nuis = self.nuis.getSize()
        self.load_nll_snapshot(nll, mu1)
        theta_mu1 = np.array([v.getVal() for v in self.nuis])
        self.load_nll_snapshot(nll, mu2)
        theta_mu2 = np.array([v.getVal() for v in self.nuis])
        m = (theta_mu2 - theta_mu1)/(mu2-mu1)
        theta_extrap = m*mu + theta_mu2 - m*mu2
        for i, param in enumerate(self.nuis):
            param.setVal(theta_extrap[i])
            
    def get_limit(self, nll:"ROOT.RooNLLVar", initial_guess:float, summary_label:Optional[int]=None):
        self.global_status = 0
        nll_name = nll.GetName()
        self.stdout.info("----------------------------------")
        self.stdout.info(f"Getting limit for nll: {nll_name}")
        self.poi.setConstant(0)
        asimov_0_nll = self.summary[0]['nll']
        if nll == asimov_0_nll:
            self.set_poi_value(0)
            self.poi.setConstant(1)
        # case for observed limit
        if (nll not in self.nll_maps) or ('nll_mu_hat' not in self.nll_maps[nll]):
            nll_val = self.get_nll_val(nll)
            mu_hat = self.poi.getVal()           
            self.save_nll_snapshot(nll, mu_hat)
            if (mu_hat < 0) and (self.do_tilde):
                self.set_poi_value(0)
                self.poi.setConstant(1)
                nll_val = self.get_nll_val(nll)
            self.nll_maps[nll]['mu_hat'] = mu_hat
            self.nll_maps[nll]['nll_mu_hat'] = nll_val
        else:
            mu_hat = self.nll_maps[nll]['mu_hat']
        
        if (mu_hat < 0.1) or (initial_guess != 0):
            self.set_poi_value(initial_guess)
        
        mu = self.poi.getVal()
        qmu = self.get_qmu(asimov_0_nll, mu)
        sigma_guess = self.LimitTool.getSigma(mu, 0, qmu)
        sigma_b = sigma_guess
        mu_guess = self.LimitTool.findCrossing(sigma_guess, sigma_b, mu_hat)
        pmu = self.LimitTool.calcPmu(qmu, sigma_b, mu_guess)
        pb = self.LimitTool.calcPb(qmu, sigma_b, mu_guess)
        CLs = self.LimitTool.calcCLs(qmu, sigma_b, mu_guess)
        qmu95 = self.LimitTool.getQmu95(sigma_b, mu_guess)
        self.set_poi_value(mu_guess)
        self.stdout.info(f"Initial guess:  {mu_guess}")
        self.stdout.info(f"Sigma(obs):     {sigma_guess}")
        self.stdout.info(f"Sigma(mu,0):    {sigma_b}")
        self.stdout.info(f"muhat:          {mu_hat}")
        self.stdout.info(f"qmu95:          {qmu95}")
        self.stdout.info(f"qmu:            {qmu}")
        self.stdout.info(f"pmu:            {pmu}")
        self.stdout.info(f"1-pb:           {pb}")
        self.stdout.info(f"CLs:            {CLs}")

        n_damping = 1
        guess_to_corr = {}
        damping_factor = 1.0
        n_iter = 0
        mu_pre = mu_hat
        mu_pre2 = mu_hat
        
        while (abs(mu_pre-mu_guess) > self.precision*mu_guess):
            self.stdout.info('----------------------------------')
            self.stdout.info('Starting iteration {} of {}'.format(n_iter, nll_name))
            # do this to avoid comparing multiple minima in the conditional and unconditional fits           
            if (n_iter == 0):
                self.load_nll_snapshot(nll, mu_hat)
            elif self.use_predictive_fit:
                self.do_predictive_fit(nll, mu_pre2, mu_pre, mu_guess)
            else:
                self.load_nll_snapshot(asimov_0_nll, mu_pre)
            qmu = self.get_qmu(nll, mu_guess)
            sigma_guess = self.LimitTool.getSigma(mu_guess, mu_hat, qmu)
            self.save_nll_snapshot(nll, mu_guess)
            
            if (nll != asimov_0_nll):
                if (n_iter == 0):
                    self.load_nll_snapshot(asimov_0_nll, self.nll_maps[asimov_0_nll]['mu_hat'])
                elif self.use_predictive_fit:
                    if (n_iter == 1):
                        self.do_predictive_fit(nll, self.nll_maps[nll]['mu_hat'], mu_pre, mu_guess)
                    else:
                        self.do_predictive_fit(nll, mu_pre2, mu_pre, mu_guess)
                else:
                    self.load_nll_snapshot(asimov_0_nll, mu_pre)
                qmuA = self.get_qmu(asimov_0_nll, mu_guess)
                sigma_b = self.LimitTool.getSigma(mu_guess, 0, qmuA)
                self.save_nll_snapshot(asimov_0_nll, mu_guess)
            else:
                sigma_b = sigma_guess
                qmuA = qmu
            corr = damping_factor*(mu_guess - self.LimitTool.findCrossing(sigma_guess, sigma_b, mu_hat))
            for first, second in guess_to_corr.items():
                if (abs(first - (mu_guess - corr)) < self.direction*mu_guess*0.02) and \
                (abs(corr) > self.direction*mu_guess*self.precision):
                    damping_factor *= 0.8
                    self.stdout.info('Changing damping factor to {}, n_damping = {}'.format(damping_factor, n_damping))
                    n_damping += 1
                    if n_damping > 10:
                        n_damping = 1
                        damping_factor = 1.0
                    corr *= damping_factor
                    break
            # subtract off the difference in the new and damped correction
            guess_to_corr[mu_guess] = corr
            mu_pre2 = mu_pre
            mu_pre = mu_guess
            mu_guess -= corr

            pmu = self.LimitTool.calcPmu(qmu, sigma_b, mu_pre)
            pb = self.LimitTool.calcPb(qmu, sigma_b, mu_pre)
            CLs = self.LimitTool.calcCLs(qmu, sigma_b, mu_pre)
            qmu95 = self.LimitTool.getQmu95(sigma_b, mu_pre)
            
            self.stdout.info(f"NLL:            {nll_name}")
            self.stdout.info(f"Previous guess: {mu_pre}")
            self.stdout.info(f"Sigma(obs):     {sigma_guess}")
            self.stdout.info(f"Sigma(mu,0):    {sigma_b}")
            self.stdout.info(f"muhat:          {mu_hat}")
            self.stdout.info(f"pmu:            {pmu}")
            self.stdout.info(f"1-pb:           {pb}")
            self.stdout.info(f"CLs:            {CLs}")
            self.stdout.info(f"qmu95:          {qmu95}")
            self.stdout.info(f"qmu:            {qmu}")
            self.stdout.info(f"qmuA0:          {qmuA}")
            self.stdout.info(f"Precision:      {self.direction*mu_guess*self.precision}")
            self.stdout.info(f"Correction:     {-corr}")
            self.stdout.info(f"New guess:      {mu_guess}")
            
            n_iter += 1
            if (n_iter > 25):
                raise RuntimeError('infinite loop detected in get_limit()')
        
        if summary_label is not None:
            summary = {
                'NLL_name': nll_name,
                'limit': mu_guess,
                'sigma_obs': sigma_guess,
                'sigma_b': sigma_b,
                'muhat': mu_hat,
                'pmu': pmu,
                '1-pb': pb,
                'CLs': CLs,
                'qmu95': qmu95,
                'qmu': qmu,
                'qmuA0': qmuA,
                'precision': self.direction*mu_guess*self.precision,
                'correction': -corr,
                'status': self.global_status
            }
            if summary_label not in self.summary:
                self.summary[summary_label] = summary
            else:
                self.summary[summary_label].update(summary)
        self.stdout.info('Found limit for nll {}: {}'.format(nll_name, mu_guess))
        self.stdout.info('Finished in {} itreations'.format(n_iter))
        return mu_guess
    
    @staticmethod
    def get_approx_limits(median_limit:float, target_cls:float=0.05):
        limits = {}
        sigma = median_limit/math.sqrt(3.84)
        limits[0]  = median_limit
        limits[2]  = sigma*(ROOT.Math.gaussian_quantile(1 - target_cls*ROOT.Math.gaussian_cdf( 2), 1) + 2)
        limits[1]  = sigma*(ROOT.Math.gaussian_quantile(1 - target_cls*ROOT.Math.gaussian_cdf( 1), 1) + 1)
        limits[-1] = sigma*(ROOT.Math.gaussian_quantile(1 - target_cls*ROOT.Math.gaussian_cdf(-1), 1) - 1)
        limits[-2] = sigma*(ROOT.Math.gaussian_quantile(1 - target_cls*ROOT.Math.gaussian_cdf(-2), 1) - 2)
        return limits
    
    def reset(self):
        self.global_status = 0
        self.minimizer_calls = 0
        self.approx_limits = {}
        self.limits = {}
        # mapping from RooNLLVar to other objects
        self.nll_maps = {} 
        # mapping from RooDataSet to RooNLLVar (and other objects)
        self.dataset_maps = {}
        # summary for various sigma values
        self.summary = {}
        
    def fill_mappings(self, nll:"ROOT.RooNLLVar", dataset:"ROOT.RooDataSet",
                      mu_hat:float, nll_mu_hat:float):
        snapshot_name = self.get_conditional_snapsot_name(mu_hat, target="globs")
        self.nll_maps[nll] = {}
        self.nll_maps[nll]['dataset'] = dataset
        self.nll_maps[nll]['snapshot'] = snapshot_name
        self.nll_maps[nll]['mu_hat'] = mu_hat
        self.nll_maps[nll]['nll_mu_hat'] = nll_mu_hat
        self.dataset_maps[dataset] = nll
        
    def print_failures(self):
        has_failtures = any(self.summary[sigma].get('status', 0) > 0 for sigma in self.summary)
        if has_failtures:
            self.stdout.info('-----------------------------------------------')
            self.stdout.info('Unresolved fit failures detected')
            for sigma in self.summary:
                label = self._SIGMA_LABEL_.get(sigma, sigma)
                self.stdout.info("{}:".format(label).ljust(10) + str(self.summary[sigma].get('status', None)))
            self.stdout.info('-----------------------------------------------')

    def print_summary(self):
        if (not self.limits) or (not self.approx_limits):
            print("No limits evaluated")
            return None
        print('')
        self.print_failures()
        if self.do_better_bands:
            self.stdout.info('Guess for bands')
        self.stdout.info(f'+2sigma:  {self.approx_limits[2]}')
        self.stdout.info(f'+1sigma:  {self.approx_limits[1]}')
        self.stdout.info(f'-1sigma:  {self.approx_limits[-1]}')
        self.stdout.info(f'-2sigma:  {self.approx_limits[-2]}')
        if self.do_better_bands:
            self.stdout.info('\nCorrect bands')
            self.stdout.info(f'+2sigma:  {self.limits[2]}')
            self.stdout.info(f'+1sigma:  {self.limits[1]}')
            self.stdout.info(f'-1sigma:  {self.limits[-1]}')
            self.stdout.info(f'-2sigma:  {self.limits[-2]}')
        self.stdout.info('Injected: {}'.format(self.limits['inj']))
        self.stdout.info(f'Median:   {self.limits[0]}')
        self.stdout.info('Observed: {}'.format(self.limits['obs']))
        self.stdout.info('')
        
    def save(self, filename:str='limits.json', summary=True):
        json.dump(self.limits, open(filename, 'w'), indent=2)
        if summary:
            data = {k:{kk:vv for kk,vv in self.summary[k].items() if kk not in ['nll', 'dataset']} \
                    for k,v in self.summary.items()}
            summary_filename = os.path.splitext(filename)[0]+'_summary'+os.path.splitext(filename)[1]
            json.dump(data, open(summary_filename, 'w'), indent=2)
        
    def evaluate_limit_band(self, n:int, med_limit:float):
        init_target_cls = self.LimitTool.getTargetCLs()
        self.LimitTool.setTargetCLs(2*(1 - ROOT.Math.gaussian_cdf(abs(n))))
        if n < 0:
            self.direction = -1
            self.LimitTool.setDirection(-1)
        asimov_0_nll = self.summary[0]['nll']
        mu_guess = n*med_limit/math.sqrt(3.84)
        n_times_sigma = self.get_limit(asimov_0_nll, mu_guess)
        status = self.global_status
        sigma = n_times_sigma/n
        self.stdout.info('Found N * sigma = {} * {}'.format(n, sigma))
        snapshot_0_name = self.nll_maps[asimov_0_nll]['snapshot']
        self.load_snapshot(snapshot_0_name)
        asimov_data_n = self.model.generate_asimov(self.poi.GetName(), poi_val=n_times_sigma,
                                                   do_fit=False, modify_globs=True,
                                                   restore_states=1)
        asimov_n_nll = self.create_nll(asimov_data_n)
        self.load_conditional_snapshot(n_times_sigma, target="globs")
        self.load_conditional_snapshot(n_times_sigma, target="nuis")
        self.set_poi_value(n_times_sigma)
        nll_value = asimov_n_nll.getVal()
        self.save_nll_snapshot(asimov_n_nll, n_times_sigma)
        if (n < 0) and (self.do_tilde):
            self.set_poi_value(0)
            self.poi.setConstant(1)
            nll_value = self.get_nll_val(asimov_n_nll)
        self.fill_mappings(asimov_n_nll, asimov_data_n, n_times_sigma, nll_value)
        self.LimitTool.setTargetCLs(init_target_cls)
        self.direction = 1
        self.LimitTool.setDirection(1)
        mu_guess = self.LimitTool.findCrossing(sigma, sigma, n_times_sigma)
        limit = self.get_limit(asimov_n_nll, mu_guess, n)
        return limit    
    
    @common_utils.timer
    def evaluate_limits(self):
        # TODO: maybe load nominal snapshot first
        self.reset()
        obs_nll = self.create_nll(self.data)
        self.nll_maps[obs_nll] = {"dataset": self.data, "snapshot": self.nom_glob_name}
        self.dataset_maps[self.data] = obs_nll
        
        self.save_snapshot(self.nom_glob_name, target="globs")
        self.save_snapshot(self.nom_nuis_name, target="nuis")
        
        asimov_data_0 = self.model.generate_asimov(self.poi.GetName(), poi_val=0,
                                                   poi_profile=0, 
                                                   do_fit=not self.do_blind,
                                                   modify_globs=not self.do_blind,
                                                   dataset=self.data,
                                                   restore_states=1)
        asimov_0_nll = self.create_nll(asimov_data_0)
        self.summary[0] = {'dataset': asimov_data_0, 'nll': asimov_0_nll}
        self.set_poi_value(0)
        self.save_nll_snapshot(asimov_0_nll, 0)
        self.load_conditional_snapshot(0, target="globs")
        self.load_conditional_snapshot(0, target="nuis")
        nll_value = asimov_0_nll.getVal()
        self.fill_mappings(asimov_0_nll, asimov_data_0, 0, nll_value)
        
        self.LimitTool.setTargetCLs(1 - self.CL)
        
        med_limit = self.get_limit(asimov_0_nll, 1.0, 0)
        approx_limits = self.get_approx_limits(med_limit, self.LimitTool.getTargetCLs())
        limits = approx_limits.copy()
        
        sigma = med_limit/math.sqrt(3.84)
        self.poi.setRange(-5*sigma, 5*sigma)
        
        # compute better sigma bands
        bands_to_improve = []
        if self.do_better_bands:
            if self.better_negative_bands:
                bands_to_improve = [2, 1, -1, -2]
            else:
                bands_to_improve = [2, 1]
        
        for n in bands_to_improve:
            limits[n] = self.evaluate_limit_band(n, med_limit)
        
        # compute observed limit
        self.load_conditional_snapshot(0, target="nuis")
        obs_limit = 0 if self.do_blind else self.get_limit(obs_nll, med_limit, 'obs')
        limits['obs'] = obs_limit
        
        # injection test not supported yet
        limits['inj'] = 0
        
        self.limits = limits
        self.approx_limits = approx_limits
        
        self.print_summary()
        
        self.stdout.info('INFO: Finished with {} calls to minimize(nll)'.format(self.minimizer_calls))
        return limits
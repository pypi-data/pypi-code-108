from typing import Optional, Union, List, Dict
import os
import time
import math
import json
from itertools import repeat

from quickstats import semistaticmethod
from quickstats.components import AbstractObject, ExtendedModel
from quickstats.components.numerics import str_encode_value
from quickstats.utils.common_utils import execute_multi_tasks
from quickstats.utils.root_utils import load_macro
from quickstats.utils.roostats_utils import process_hypotest_results, merge_toy_results

import ROOT

class ToyLimitCalculator(AbstractObject):
    
    HYPOTEST_OPTIONS = {
        'remove_mu_with_failed_teststat': True,
        'remove_unconverged_toys': True,
        'use_qmu': False,
        'do_invert': True
    }
    
    def __init__(self, filename:str, data_name:str,
                 n_toys:int, seed:int=1234,
                 poi_name:Optional[str]=None,
                 poi_min:Optional[float]=None,
                 poi_max:Optional[float]=None,
                 minimizer_type:str="Minuit2", strategy:int=1,
                 eps:float=0.05, tolerance:float=1., print_level:int=-1,
                 offset:bool=False, do_coarse_scan:bool=False,
                 fix_param:str='', profile_param:str='',
                 snapshot_name:Optional[Union[List[str], str]]=None,                 
                 verbosity:Optional[Union[int, str]]=None,
                 hypotest_options:Optional[Dict]=None,
                 mode:str='toy',
                 use_custom_teststat_cls:bool=True):
        super().__init__(verbosity=verbosity)
        self.model_base = ExtendedModel(filename,
                                        data_name=data_name,
                                        snapshot_name=snapshot_name,
                                        verbosity="WARNING")
        
        self.inverter_verbose = print_level >= 0
        
        self.hypotest_options = self.HYPOTEST_OPTIONS
        if hypotest_options is not None:
            self.hypotest_options.update(hypotest_options)
        
        if fix_param:
            self.model_base.fix_parameters(fix_param)
        if profile_param:
            self.model_base.profile_parameters(profile_param)
        
        self.poi = self.model_base.get_poi(poi_name)
        self.poi.setConstant(False)
        poi_range = [self.poi.getRange()[0], self.poi.getRange()[1]]
        if poi_min is not None:
            poi_range[0] = poi_min
        if poi_max is not None:
            poi_range[1] = poi_max
        self.poi.setRange(poi_range[0], poi_range[1])
        self.stdout.info("INFO: Using POI \"{}\" with range [{}, {}]".format(self.poi.GetName(),
                                                                       poi_range[0],
                                                                       poi_range[1]))
        
        self.model_SB = self.model_base.model_config
        self.poi.setVal(1)
        self.model_SB.SetSnapshot(self.poi)
        
        self.model_B = self.model_base.model_config.Clone("B_only")
        self.poi.setVal(0)
        self.model_B.SetSnapshot(self.poi)
        
        self.seed = seed
        self.random_generator = ROOT.RooRandom.randomGenerator()
        self.random_generator.SetSeed(seed)
        
        pdf_SB = self.model_SB.GetPdf()
        globs_SB = self.model_SB.GetGlobalObservables()
        
        if use_custom_teststat_cls:
            self.load_extension()
            teststat_cls = ROOT.RooStats.ProfileLikelihoodTestStatEx
        else:
            teststat_cls = ROOT.RooStats.ProfileLikelihoodTestStat
        self.plr = teststat_cls(pdf_SB)
        self.plr.SetGlobalObservables(globs_SB)
        self.plr.SetOneSided(True)
        self.plr.SetPrintLevel(print_level)
        self.plr.SetMinimizer(minimizer_type)
        self.plr.SetStrategy(strategy)
        self.plr.SetLOffset(offset)
        self.plr.SetTolerance(tolerance)
        
        self.toy_mc = ROOT.RooStats.ToyMCSampler(self.plr, n_toys)
        
        # If we use the frequentist calculator for counting experiments 
        # (instead of models of distributions) we should instruct the sampler 
        # to generate one event for each toy. ( This is the case because we model 
        # counting experiments in RooFit as a single observation in distribution of event counts. )
        if (not self.model_SB.GetPdf().canBeExtended()):
            self.toy_mc.SetNEventsPerToy(1)        

        if mode == 'toy':
            self.calculator = ROOT.RooStats.FrequentistCalculator(self.model_base.data, 
                                                                  self.model_B, 
                                                                  self.model_SB,
                                                                  self.toy_mc)
        elif mode == 'asymptotic':
            self.calculator = ROOT.RooStats.AsymptoticCalculator(self.model_base.data, 
                                                                 self.model_B, 
                                                                 self.model_SB)
            self.calculator.SetOneSided(True)
            self.calculator.SetQTilde(True)
            self.calculator.SetPrintLevel(print_level)
            self.calculator.Initialize()
        else:
            raise ValueError("mode must be either `toy` or `asymptotic`")

        self.do_coarse_scan = do_coarse_scan
        self.eps            = eps
        self.mode           = mode
        
        self.reset_results()
        

    @semistaticmethod
    def load_extension(self):
        try:
            if not hasattr(ROOT, 'ProfileLikelihoodTestStatEx'):
                result = load_macro('ProfileLikelihoodTestStatEx')
                if hasattr(ROOT, 'ProfileLikelihoodTestStatEx'):
                    self.stdout.info('INFO: Loaded extension module "ProfileLikelihoodTestStatEx"')
        except Exception as e:
            print(e)        
        
    def reset_results(self):
        result = ROOT.RooStats.HypoTestInverterResult("result", self.poi, 0.95)
        result.SetConfidenceLevel(0.95)
        result.UseCLs()
        result.SetInterpolationOption(ROOT.RooStats.HypoTestInverterResult.kLinear)
        self.result = result
        
    @staticmethod
    def scan_result_to_dict(scan_result):
        result = {}
        result["limits"] = {
            "obs": scan_result.UpperLimit(),
            0: scan_result.GetExpectedUpperLimit(0),
            1: scan_result.GetExpectedUpperLimit(1),
            2: scan_result.GetExpectedUpperLimit(2),
            -1: scan_result.GetExpectedUpperLimit(-1),
            -2: scan_result.GetExpectedUpperLimit(-1),
        }
        result["data"] = {
            "mu": [],
            "CLb": [],
            "CLs": [],
            "CLsplusb": [],
            "CLsplusbError": []
        }
        
        for i in range(scan_result.ArraySize()):
            result["data"]["mu"].append(scan_result.GetXValue(i))
            result["data"]["CLb"].append(scan_result.CLb(i))
            result["data"]["CLs"].append(scan_result.CLs(i))
            result["data"]["CLsplusb"].append(scan_result.CLsplusb(i))
            result["data"]["CLsplusbError"].append(scan_result.CLsplusbError(i))
        return result

    def display_limits(self, scan_result):
        limits = ToyLimitCalculator.scan_result_to_dict(scan_result)['limits']
        self.stdout.info("Limit Bands")
        self.stdout.info(f"+2 sigma : {limits[2]}")
        self.stdout.info(f"+1 sigma : {limits[1]}")
        self.stdout.info(f"-1 sigma : {limits[-1]}")
        self.stdout.info(f"-2 sigma : {limits[-2]}")
        self.stdout.info(f"  Median : {limits[0]}")
        self.stdout.info("Observed : {}".format(limits["obs"]))
        
    def check_test_statistics(self, scan_min:float, scan_max:float, steps:int):
        poi_val_0 = self.poi.getVal()
        self.stdout.info("INFO: Checking convergence of test statistics...")
        interval = (scan_max - scan_min) / (steps - 1)
        for i in range(steps):
            mu = scan_min + i * interval
            self.poi.setVal(mu)
            test_statistic = self.plr.EvaluateProfileLikelihood(0, 
                                                                self.model_base.data,
                                                                ROOT.RooArgSet(self.poi))
            self.stdout.info("INFO: mu = {}, test statistic = {}".format(mu, test_statistic))
            if test_statistic < 0:
                raise RuntimeError("test statistic failed to converge")
                
    def append(self, result: Union[ROOT.RooStats.HypoTestInverterResult,
                                   ROOT.RooStats.HypoTestResult]):
        processed_result = merge_toy_results([result], self.poi,
                                             **self.hypotest_options,
                                             silent=True)
        self.result.Add(processed_result)
        
    def run_coarse_scan(self, scan_min:float, scan_max:float):
        
        scale      = 10**(1/3)
        steps      = (math.log(scan_max / scan_min) / math.log(scale)) + 1
        steps_ceil = math.ceil(steps)
        start, end = scan_min, scan_max
        
        self.stdout.info("INFO: Starting coarse search")
        self.stdout.info(f"INFO: Evaluating {steps_ceil} logarithmic points from {start} to {end}")
        
        inverter = ROOT.RooStats.HypoTestInverter(self.calculator)
        inverter.SetVerbose(self.inverter_verbose)
        # 95% CLs limits
        inverter.SetConfidenceLevel(0.95) 
        inverter.UseCLs(True)
        
        self.stdout.info("INFO: Checking for problematic CLs values...")
        
        snapshot_0 = self.freq_calculator.GetNullModel().GetSnapshot()

        for i in range(steps_ceil):
            start = math.exp(math.log(scan_min) + i * math.log(scan_max / scan_min) / (steps - 1))
            self.poi.setVal(start)
            self.freq_calculator.GetNullModel().SetSnapshot(self.poi)
            result = self.freq_calculator.GetHypoTest()
            cls = result.CLs()
            if (math.isfinite(cls) and cls >= 0.):
                break
        if start >= end :
            raise RuntimeError("No acceptable points found in coarse scan")
        for i in range(steps_ceil):
            end = math.exp(math.log(scan_min) + (steps - 1 - i) * math.log(scan_max / scan_min) / (steps - 1))
            self.poi.setVal(end)
            self.freq_calculator.GetNullModel().SetSnapshot(self.poi)
            result = self.freq_calculator.GetHypoTest()
            cls = result.CLs()
            if (math.isfinite(cls) and cls >= 0.):
                break
        if start >= end :
            raise RuntimeError("No acceptable points found in coarse scan")
        steps      = math.log(end / start) / math.log(scale) + 1
        steps_ceil = math.ceil(steps)
        self.freq_calculator.GetNullModel().SetSnapshot(snapshot_0)
        self.stdout.info(f"INFO: Recalculated scan running {steps_ceil} logarithmic points from {start} to {end}")
        
        self.stdout.info("INFO: Running fixed scan")
        inverter.SetFixedScan(steps, start, end, True)
        result = inverter.GetInterval()
        result.SetInterpolationOption(ROOT.RooStats.HypoTestInverterResult.kLinear)
        
        return result        

    def run_scans(self, scan_min:float, scan_max:float, steps:Optional[int]=None, 
                  use_log:bool=False, append:bool=True):
            
        time_start = time.time()
        start, end = scan_min, scan_max
        
        if self.do_coarse_scan:
            coarse_result = self.run_coarse_scan(scan_min, scan_max, mode=mode)
            start = coarse_result.minus_2 / 10**(1/3)
            end   = coarse_result.plus_2 / 10**(1/3)
            if (not math.isfinite(start)) or (not math.isfinite(end)):
                raise RuntimeError("Got non-finite bound from coarse limits")
            if (start < self.poi.getRange()[0]):
                raise RuntimeError("Got lower bound beyond POI minimum range")
            self.stdout.info(f"INFO: Bounds for fine search: [{start}, {end}]")
            self.display_limits(coarse_result)
        
        self.stdout.info("INFO: Starting fine search")
        
        if steps is None:
            scale      = 1. + self.eps
            steps      = (math.log(end / start) / math.log(scale)) + 1
            steps_ceil = math.ceil(steps)
            use_log   = True
            self.stdout.info(f"INFO: Evaluating {steps_ceil} logarithmic points from {start} to {end}")
        else:
            self.stdout.info(f"INFO: Evaluating {steps} points from {start} to {end}")
        inverter = ROOT.RooStats.HypoTestInverter(self.calculator)
        inverter.SetVerbose(self.inverter_verbose)
        # 95% CLs limits
        inverter.SetConfidenceLevel(0.95) 
        inverter.UseCLs(True)
        
        if self.mode == 'toy':
            self.check_test_statistics(start, end, steps)
        
        self.stdout.info("INFO: Running fixed scan")
        inverter.RunFixedScan(steps, start, end, use_log)
        result = inverter.GetInterval()
        result.SetInterpolationOption(ROOT.RooStats.HypoTestInverterResult.kLinear)
        result.SetName("scan_{}_{}_{}".format(str_encode_value(scan_min, 10),
                                              str_encode_value(scan_max, 10),
                                              steps))
        time_end = time.time()
        
        self.stdout.info("INFO: Scan finished. Total time taken: {}s".format(time_end-time_start))
        
        self.display_limits(result)
        
        if append:
            self.append(result)
        
        return result
    
    def run_one_point(self, poi_val:float, append=True):      
        
        poi_val_0 = self.poi.getVal()
        
        self.stdout.info(f"INFO: Running HypoTest on mu value {poi_val}.")
    
        self.poi.setVal(poi_val)
        self.calculator.GetNullModel().SetSnapshot(self.poi)
        result = self.calculator.GetHypoTest()
        result.SetBackgroundAsAlt(True)
        result.SetName(f"{self.poi.GetName()}_{poi_val}")
        
        self.poi.setVal(poi_val_0)
        
        if append and self.mode == 'toy':
            self.append(result)
        
        return result
    
    def get_teststat(self, poi_val:float):
        poi_val_0 = self.poi.getVal()
        self.poi.setVal(poi_val)
        teststat = self.toy_mc.EvaluateTestStatistic(self.model_base.data, 
                                                     ROOT.RooArgSet(self.poi))
        #self.EvaluateProfileLikelihood(0, data, ROOT.RooArgSet(poi)
        self.poi.setVal(poi_val_0)
        return teststat
    

    
    def save_as_root(self, basename:str="toy_result_seed_{seed}.root"):
        if not self.result:
            self.stdout.warning("WARNING: No result to save.")
            return None
        filename = basename.format(seed=self.seed)
        self.write_to_root(self.result, filename)
            
    def write_to_root(self, result, filename):
        f = ROOT.TFile(filename, "RECREATE")
        f.cd()
        result.Write()
        f.Write()
        f.Close()
        self.stdout.info(f"INFO: Saved toy limit result as `{filename}`.")
    
    def save(self, filename:str="toy_limit_result.json"):
        
        if (self.result is None) and (self.coarse_result is None) and (self.one_point_result is None):
            self.stdout.warning("WARNING: No result to save")

        base_dir = os.path.dirname(filename)
        base_name = os.path.basename(filename)
        extension = os.path.splitext(filename)[1]
            
        if self.coarse_result is not None:
            result = self.scan_result_to_dict(self.coarse_result)
            filename_coarse = os.path.join(base_dir, f"{base_name}_coarse{extension}")
            with open(filename_coarse) as f:
                json.dump(result, f, indent=2)
            self.stdout.info(f"INFO: Saved coarse toy limit result as `{filename}`.")
            
        if self.result is not None:
            result = self.scan_result_to_dict(self.result)
            with open(filename) as f:
                json.dump(result, f, indent=2)
            self.stdout.info(f"INFO: Saved toy limit result as `{filename}`.")

        if self.one_point_result is not None:
            for mu_val in self.one_point_result:
                mu_str = str_encode_value(mu_val)
                result = self.scan_result_to_dict(self.one_point_result[mu_val])
                filename_one_point = os.path.join(base_dir, f"{base_name}_{mu_str}{extension}")
                with open(filename_one_point) as f:
                    json.dump(result, f, indent=2)
                self.stdout.info(f"INFO: Saved toy limit result for mu = {mu_val} as `{filename}`.")
                
def evaluate_toy_limits(filename:str, data_name:str, 
                        scan_min:Optional[float]=None, 
                        scan_max:Optional[float]=None, 
                        steps:int=10,
                        mu_val:Optional[float]=None,
                        poi_min:Optional[float]=None, poi_max:Optional[float]=None,
                        n_toys:int=1000, seed:int=1234, 
                        outname:str="toy_result_seed_{seed}.root",
                        poi_name:Optional[str]=None,
                        minimizer_type:str="Minuit2", strategy:int=1,
                        eps:float=0.05, tolerance:float=1., offset:bool=True,
                        print_level:int=-1, do_coarse_scan:bool=False, 
                        fix_param:str='', profile_param:str='',
                        snapshot_name:Optional[Union[List[str], str]]=None,                 
                        verbosity:Optional[Union[int, str]]=None):
    toy_limit_calculator = ToyLimitCalculator(filename=filename,
                                              data_name=data_name,
                                              n_toys=n_toys, seed=seed,
                                              poi_name=poi_name,
                                              poi_min=poi_min,
                                              poi_max=poi_max,
                                              minimizer_type=minimizer_type,
                                              strategy=strategy,
                                              eps=eps, tolerance=tolerance,
                                              offset=offset,
                                              print_level=print_level,
                                              do_coarse_scan=do_coarse_scan,
                                              fix_param=fix_param,
                                              profile_param=profile_param,
                                              snapshot_name=snapshot_name,
                                              verbosity=verbosity)
    if all([p is not None for p in [scan_min, scan_max]]) and (mu_val is None):
        toy_limit_calculator.run_scans(scan_min=scan_min, scan_max=scan_max, steps=steps)
    elif (mu_val is not None) and all([p is None for p in [scan_min, scan_max]]):
        toy_limit_calculator.run_one_point(mu_val)
    else:
        raise ValueError("please provide either (scan_min, scan_max, steps) for running a scan or (mu_val)"
                         " for running a single point")
    toy_limit_calculator.save_as_root(basename=outname)
                
def evaluate_batched_toy_limits(filename:str, data_name:str, 
                                scan_min:Optional[float]=None,
                                scan_max:Optional[float]=None,
                                steps:int=10, 
                                mu_val:Optional[float]=None,
                                poi_min:Optional[float]=None, poi_max:Optional[float]=None,
                                n_toys:int=1000, batchsize:int=100, seed:int=1234, 
                                outname:str="toy_result_seed_{seed}_batch_{batch}.root",
                                poi_name:Optional[str]=None, minimizer_type:str="Minuit2", 
                                strategy:int=1, eps:float=0.05, tolerance:float=1., 
                                offset:bool=True, print_level:int=-1,
                                do_coarse_scan:bool=False, parallel:int=-1,
                                fix_param:str='', profile_param:str='',
                                snapshot_name:Optional[Union[List[str], str]]=None,                 
                                verbosity:Optional[Union[int, str]]=None):
    if n_toys % batchsize == 0:
        toy_batches = [batchsize] * (n_toys // batchsize)
    else:
        toy_batches = [batchsize] * (n_toys // batchsize) + [n_toys % batchsize]
    seeds = [seed + 10000*i for i in range(len(toy_batches))]
    
    dirname = os.path.dirname(outname)
    if dirname and (not os.path.exists(dirname)):
        os.makedirs(dirname, exist_ok=True)
    
    outnames = [outname.format(seed=seed, batch=i) for i in range(len(toy_batches))]
    
    args = (repeat(filename), repeat(data_name), repeat(scan_min), repeat(scan_max),
            repeat(steps), repeat(mu_val), repeat(poi_min), repeat(poi_max),
            toy_batches, seeds, outnames, repeat(poi_name), repeat(minimizer_type), 
            repeat(strategy), repeat(eps), repeat(tolerance), repeat(offset),
            repeat(print_level), repeat(do_coarse_scan), repeat(fix_param), 
            repeat(profile_param), repeat(snapshot_name), repeat(verbosity))
    execute_multi_tasks(evaluate_toy_limits, *args, parallel=parallel)
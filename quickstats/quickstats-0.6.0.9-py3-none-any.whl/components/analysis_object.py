from typing import Optional, Union, List

from quickstats.components import AbstractObject, ExtendedModel, ExtendedMinimizer
from quickstats.utils.common_utils import get_class_that_defined_method
import ROOT

class AnalysisObject(AbstractObject):
    def __init__(self, filename:Optional[str]=None, poi_name:Optional[str]=None, 
                 data_name:str='combData', binned_likelihood:bool=True, 
                 fix_param:str='', profile_param:str='', ws_name:Optional[str]=None, 
                 mc_name:Optional[str]=None, snapshot_name:Optional[Union[List[str], str]]=None,
                 minimizer_type:str='Minuit2', minimizer_algo:str='Migrad', precision:float=0.001, 
                 eps:float=1.0, strategy:int=1, print_level:int=-1, timer:bool=False,
                 num_cpu:int=1, offset:bool=True, optimize:int=2, eigen:bool=False,
                 fix_cache:bool=True, fix_multi:bool=True, max_calls:int=-1, 
                 max_iters:int=-1, constrain_nuis:bool=True, batch_mode:bool=False,
                 int_bin_precision:float=-1., verbosity:Optional[Union[int, str]]="INFO"):
        super().__init__(verbosity=verbosity)    
        self.model = None
        self.minimizer = None
        
        if filename is not None:
            self.setup_model(filename, data_name, binned_likelihood, ws_name, mc_name, 
                             snapshot_name, fix_cache, fix_multi, verbosity=verbosity)
            self.set_poi(poi_name)
            self.setup_parameters(fix_param, profile_param)
            self.setup_minimizer(minimizer_type, minimizer_algo, precision, eps, strategy, num_cpu,
                                 offset, optimize, eigen, max_calls, max_iters, print_level,
                                 timer, constrain_nuis, batch_mode, int_bin_precision,
                                 verbosity=verbosity)
    # black magic
    def _inherit_init(self, init_func, **kwargs):
        import inspect
        this_parameters = list(inspect.signature(AnalysisObject.__init__).parameters)
        if "self" in this_parameters:
            this_parameters.remove("self")
        that_parameters = list(inspect.signature(init_func).parameters)
        is_calling_this = set(this_parameters) == set(that_parameters)
        if is_calling_this:
            init_func(**kwargs)
        else:
            that_kwargs = {k:v for k,v in kwargs.items() if k in that_parameters}
            this_kwargs = {k:v for k,v in kwargs.items() if k not in that_parameters}
            init_func(config=this_kwargs, **that_kwargs)

    def set_poi(self, poi_name:Optional[str]=None):
        self.poi = self.model.get_poi(poi_name)
        if poi_name is not None:
            self.stdout.info('INFO: POI set to "{}"'.format(poi_name))            
        
    def setup_model(self, filename, data_name='combData', binned_likelihood:bool=True, 
                    ws_name:Optional[str]=None, mc_name:Optional[str]=None, 
                    snapshot_name:Optional[str]=None, fix_cache:bool=True, 
                    fix_multi:bool=True, verbosity:Optional[Union[int, str]]="INFO"):
        model = ExtendedModel(fname=filename, ws_name=ws_name, mc_name=mc_name, data_name=data_name, 
                              snapshot_name=snapshot_name, binned_likelihood=binned_likelihood,
                              fix_cache=fix_cache, fix_multi=fix_multi, verbosity=verbosity)
        self.model = model
    
    def setup_parameters(self, fix_param:str='', profile_param:str=''):
        if not self.model:
            raise RuntimeError('uninitialized analysis object')
        if fix_param:
            self.model.fix_parameters(fix_param)
        if profile_param:
            self.model.profile_parameters(profile_param)
            
    def setup_minimizer(self, minimizer_type:str='Minuit2', minimizer_algo:str='Migrad', 
                        precision:float=0.001, eps:float=1.0, strategy:int=0, 
                        num_cpu:int=1, offset:bool=True, optimize:bool=True, eigen:bool=False,
                        max_calls:int=-1, max_iters:int=-1, print_level:int=-1, timer:bool=False,
                        constrain_nuis:bool=True, batch_mode:bool=False, int_bin_precision:float=-1.,
                        verbosity:Optional[Union[int, str]]="INFO"):
        
        minimizer = ExtendedMinimizer("Minimizer", self.model.pdf, self.model.data, verbosity=verbosity)
        
        nll_commands = [ROOT.RooFit.NumCPU(num_cpu, 3), 
                        ROOT.RooFit.Offset(offset)]
        if (constrain_nuis and self.model.nuisance_parameters):
            #nll_commands.append(ROOT.RooFit.Constrain(self.model.nuisance_parameters))
            nll_commands.append(ROOT.RooFit.GlobalObservables(self.model.global_observables))
            nll_commands.append(ROOT.RooFit.ConditionalObservables(self.model.model_config.GetConditionalObservables()))
            #nll_commands.append(ROOT.RooFit.ExternalConstraints(ROOT.RooArgSet()))
        if hasattr(ROOT.RooFit, "BatchMode"):
            nll_commands.append(ROOT.RooFit.BatchMode(batch_mode))
        if hasattr(ROOT.RooFit, "IntegrateBins"):
            nll_commands.append(ROOT.RooFit.IntegrateBins(int_bin_precision))
        minimizer_options = {
            'minimizer_type'   : minimizer_type,
            'minimizer_algo'   : minimizer_algo,
            'default_strategy' : strategy,
            'opt_const'        : optimize,
            'precision'        : precision,
            'eps'              : eps,
            'eigen'            : eigen,
            'max_calls'        : max_calls,
            'max_iters'        : max_iters,
            'print_level'      : print_level,
            'timer'            : timer
        }

        minimizer.configure(nll_commands=nll_commands, **minimizer_options)
        
        self.minimizer = minimizer
        self.minimizer_options = minimizer_options
        self.nll_commands      = nll_commands
    
    def set_data(self, data_name:str='combData'):
        data = self.model.workspace.data(data_name)
        if not data:
            raise RuntimeError(f"workspace does not contain the dataset \"{data_name}\"")
        self.minimizer.set_data(data)
        self.model._data = data
        
    def load_snapshot(self, snapshot_name:Optional[str]=None):
        if snapshot_name is not None:
            self.model.workspace.loadSnapshot(snapshot_name)
        
    def save(self, fname:str, recreate:bool=True):
        self.model.save(fname, recreate=recreate)
        self.stdout.info(f"INFO: Saved workspace file as `{fname}`")
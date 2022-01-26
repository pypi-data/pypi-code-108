from typing import Optional, Dict, List, Union
import enum

from quickstats.components import AnalysisObject
from quickstats.utils.common_utils import parse_config

class AsimovType(enum.Enum):
    Temp                   = -999
    S_NP_Nom               = -2
    B_NP_Nom               = -1
    B_NP_Fit               = 0
    S_NP_Fit               = 1
    S_NP_Fit_muhat         = 2
    B_unconstrained_NP_Fit = 3
    S_unconstrained_NP_Fit = 4
    S_unconstrained_NP_Fit_muhat = 5
    
class AsimovGenerator(AnalysisObject):

    ASIMOV_SETTINGS = {
        AsimovType.Temp: None,
        AsimovType.S_NP_Nom: {
            "asimov_name": "asimovData_1_NP_Nominal",
            "asimov_snapshot": "asimovData_1_NP_Nominal",
            "poi_val": 1,
            "poi_profile": 1,
            "do_fit": False,
            "modify_globs": False
        },
        AsimovType.B_NP_Nom: {
            "asimov_name": "asimovData_0_NP_Nominal",
            "asimov_snapshot": "asimovData_0_NP_Nominal",
            "poi_val": 0,
            "poi_profile": 0,
            "do_fit": False,
            "modify_globs": False
        },
        AsimovType.B_NP_Fit: {
            "asimov_name": "asimovData_0_NP_Profile",
            "asimov_snapshot": "asimovData_0_NP_Profile",
            "poi_val": 0,
            "poi_profile": 0,
            "do_fit": True,
            "modify_globs": True
        },
        AsimovType.S_NP_Fit: {
            "asimov_name": "asimovData_1_NP_Profile",
            "asimov_snapshot": "asimovData_1_NP_Profile",
            "poi_val": 1,
            "poi_profile": 1,
            "do_fit": True,
            "modify_globs": True
        },
        AsimovType.S_NP_Fit_muhat: {
            "asimov_name": "asimovData_muhat_NP_Profile",
            "asimov_snapshot": "asimovData_muhat_NP_Profile",
            "poi_val": 1,
            "poi_profile": None,
            "do_fit": True,
            "modify_globs": True
        },
        AsimovType.B_unconstrained_NP_Fit: {
            "asimov_name": "asimovData_0_unconstrained_NP_Profile",
            "asimov_snapshot": "asimovData_0_unconstrained_NP_Profile",
            "poi_val": 0,
            "poi_profile": 0,
            "do_fit": True,
            "modify_globs": True,
            "constraint_option": 1
        },
        AsimovType.S_unconstrained_NP_Fit: {
            "asimov_name": "asimovData_1_unconstrained_NP_Profile",
            "asimov_snapshot": "asimovData_1_unconstrained_NP_Profile",
            "poi_val": 1,
            "poi_profile": 1,
            "do_fit": True,
            "modify_globs": True,
            "constraint_option": 1
        },
        AsimovType.S_unconstrained_NP_Fit_muhat: {
            "asimov_name": "asimovData_muhat_unconstrained_NP_Profile",
            "asimov_snapshot": "asimovData_muhat_unconstrained_NP_Profile",
            "poi_val": 1,
            "poi_profile": None,
            "do_fit": True,
            "modify_globs": True,
            "constraint_option": 1
        }
    }    
    
    DEFAULT_ASIMOV_TYPES = [AsimovType.B_NP_Fit, AsimovType.S_NP_Fit, AsimovType.S_NP_Fit_muhat]
    
    def __init__(self, filename:str, poi_name:str=None,
                 data_name:str='combData', 
                 config:Optional[Union[Dict, str]]=None,
                 verbosity:Optional[Union[int, str]]="INFO"):
        config = parse_config(config)
        config['filename']  = filename
        config['poi_name']  = poi_name
        config['data_name'] = data_name
        config['verbosity'] = verbosity
        self._inherit_init(super(AsimovGenerator, self).__init__, **config)
        
    
    def generate_standard_asimov(self, asimov_types:Optional[Union[List[AsimovType], List[int]]]=None,
                                 asimov_names:Optional[Union[List[str], str]]=None,
                                 asimov_snapshots:Optional[Union[List[str], str]]=None,
                                 poi_scale:Optional[float]=None):
        if asimov_types is None:
            asimov_types = self.DEFAULT_ASIMOV_TYPES
        if isinstance(asimov_types, (int, AsimovType)):
            asimov_types = [asimov_types]
        if asimov_names is not None:
            if isinstance(asimov_names, str):
                asimov_names = [asimov_names]
            assert len(asimov_names) == len(asimov_types)
        if asimov_snapshots is not None:
            if isinstance(asimov_snapshots, str):
                asimov_snapshots = [asimov_snapshots]
            assert len(asimov_snapshots) == len(asimov_types)            
        if poi_scale is None:
            poi_scale = 1.0
        poi_name = self.poi.GetName()
        self.model.workspace.saveSnapshot("temp", self.model.workspace.allVars())
        for i, asimov_type in enumerate(asimov_types):
            self.load_snapshot("temp")
            if isinstance(asimov_type, int):
                asimov_type = AsimovType(asimov_type)
            kwargs = self.ASIMOV_SETTINGS[asimov_type]
            if kwargs is None:
                continue
            kwargs['poi_name'] = poi_name
            for key in ['poi_val', 'poi_profile']:
                if kwargs[key] is not None:
                    kwargs[key] *= poi_scale
            if asimov_names is not None:
                kwargs['asimov_name'] = asimov_names[i]
            if asimov_snapshots is not None:
                kwargs['asimov_snapshot'] = asimov_snapshots[i]
            kwargs['minimizer_options'] = self.minimizer_options
            kwargs['nll_options'] = self.nll_commands
            self.model.generate_asimov(**kwargs)
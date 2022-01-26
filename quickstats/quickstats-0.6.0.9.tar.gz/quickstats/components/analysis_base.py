from typing import Optional, Union, List, Dict

from quickstats.components import AnalysisObject, Likelihood, AsimovGenerator

class AnalysisBase(Likelihood, AsimovGenerator):
    def __init__(self, filename:str, poi_name:str=None, 
                 data_name:str='combData', 
                 config:Optional[Union[Dict, str]]=None,
                 verbosity:Optional[Union[int, str]]="INFO", **kwargs):
        super().__init__(filename=filename,
                         poi_name=poi_name,
                         data_name=data_name,
                         config=config,
                         verbosity=verbosity)
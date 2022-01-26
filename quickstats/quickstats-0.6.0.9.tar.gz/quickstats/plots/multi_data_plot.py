from typing import Dict, Optional, Union, List

import pandas as pd
from cycler import cycler

from quickstats.plots import AbstractPlot, QUICKSTATS_PALETTES
from quickstats.utils.common_utils import combine_dict

class MultiDataPlot(AbstractPlot):
    
    COLOR_CYCLER = cycler(color=QUICKSTATS_PALETTES['darklines'])
    
    def __init__(self, data_map:Union[pd.DataFrame, Dict[str, pd.DataFrame]],
                 label_map:Optional[Dict]=None,
                 styles_map:Optional[Dict]=None,
                 color_cycler=None,
                 styles:Optional[Union[Dict, str]]=None,
                 analysis_label_options:Optional[Dict]=None):
        
        self.data_map = data_map
        self.label_map = label_map
        self.styles_map = styles_map
        
        if color_cycler is not None:
            self.color_cycler = color_cycler
        else:
            self.color_cycler = self.COLOR_CYCLER
            
        super().__init__(styles=styles, 
                         analysis_label_options=analysis_label_options)            
            
    def get_default_legend_order(self):
        if not isinstance(self.data_map, dict):
            return []
        else:
            return list(self.data_map)
    
    def draw_frame(self, **kwargs):
        ax = super().draw_frame(**kwargs)
        ax.set_prop_cycle(self.color_cycler)
        return ax
    
from typing import Optional, Union, Dict, List

from quickstats.plots.template import single_frame, parse_styles, parse_analysis_label_options
from quickstats.utils.common_utils import combine_dict

class AbstractPlot:
    
    COLOR_PALLETE = {}
    COLOR_PALLETE_SEC = {}
    
    def __init__(self,
                 color_pallete:Optional[Dict]=None,
                 color_pallete_sec:Optional[Dict]=None,
                 styles:Optional[Union[Dict, str]]=None,
                 analysis_label_options:Optional[Dict]=None):
        
        self.color_pallete = combine_dict(self.COLOR_PALLETE, color_pallete)
        self.color_pallete_sec = combine_dict(self.COLOR_PALLETE_SEC, color_pallete_sec)
            
        self.styles = parse_styles(styles)
        
        if analysis_label_options is None:
            self.analysis_label_options = None
        else:
            self.analysis_label_options = parse_analysis_label_options(analysis_label_options)
            
        self.legend_order = self.get_default_legend_order()
        
        self.legend_data = {}
        self.legend_data_sec = {}
    
    def get_default_legend_order(self):
        return []
    
    def update_legend_handles(self, handles:Dict, sec:bool=False):
        if not sec:
            legend_data = self.legend_data
        else:
            legend_data = self.legend_data_sec
            
        for key in handles:
            handle = handles[key]
            if isinstance(handle, (tuple, list)):
                label = handle[0].get_label()
            else:
                label = handle.get_label()
            if label and not label.startswith('_'):
                legend_data[key] = {
                    'handle': handle,
                    'label': label
                }
            else:
                raise RuntimeError(f"the handle {handle} does not have an associated label")

    def get_legend_handles_labels(self, sec:bool=False):
        handles = []
        labels = []
        if not sec:
            legend_data = self.legend_data
        else:
            legend_data = self.legend_data_sec        
        for key in self.legend_order:
            if key in legend_data:
                handle = legend_data[key]['handle']
                label = legend_data[key]['label']
                handles.append(handle)
                labels.append(label)
        return handles, labels
    
    def draw_frame(self, **kwargs):
        ax = single_frame(styles=self.styles,
                          analysis_label_options=self.analysis_label_options,
                          **kwargs)
        return ax
    
    def draw_axis_labels(self, ax, xlabel:Optional[str]=None, ylabel:Optional[str]=None):
        if xlabel is not None:
            ax.set_xlabel(xlabel, **self.styles['xlabel'])
        if ylabel is not None:
            ax.set_ylabel(ylabel, **self.styles['ylabel'])
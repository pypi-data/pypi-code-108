from typing import Dict, Optional, Union, List
import pandas as pd

from quickstats.plots import MultiDataPlot
from quickstats.plots.template import create_transform
from quickstats.utils.common_utils import combine_dict

class Likelihood1DPlot(MultiDataPlot):
    
    CONFIG = {
        'sigma_values': (1, 4),
        'sigma_names': ('1 $\sigma$', '2 $\sigma$'),
        'sigma_line_styles':{
            'color': 'gray',
            'linestyle': '--'
        }
    }
    def __init__(self, data_map:Union[pd.DataFrame, Dict[str, pd.DataFrame]],
                 label_map:Optional[Dict]=None,
                 styles_map:Optional[Dict]=None,
                 color_cycler=None,
                 styles:Optional[Union[Dict, str]]=None,
                 analysis_label_options:Optional[Dict]=None):
        super().__init__(data_map=data_map,
                         label_map=label_map,
                         styles_map=styles_map,
                         color_cycler=color_cycler,
                         styles=styles,
                         analysis_label_options=analysis_label_options)
        self.config = combine_dict(self.CONFIG)
        
    def draw_single_data(self, ax, data:pd.DataFrame, 
                         styles:Optional[Dict]=None,
                         label:Optional[str]=None,
                         xattrib:str='mu', yattrib:str='qmu'):
        x = data[xattrib]
        y = data[yattrib]
        draw_styles = combine_dict(self.styles['plot'], styles)
        handle = ax.plot(x, y, **draw_styles, label=label)
        return handle[0]
    
    def draw(self, xattrib:str='mu', yattrib:str='qmu', xlabel:Optional[str]=None, 
             ylabel:Optional[str]="$-2\Delta ln(L)$",
             ymax:float=7, xmin:Optional[float]=None, xmax:Optional[float]=None,
             draw_sigma_line:bool=True):
        ax = self.draw_frame()
        if isinstance(self.data_map, pd.DataFrame):
            self.draw_single_data(ax, self.data_map, self.styles_map,
                                  xattrib=xattrib, yattrib=yattrib)
        elif isinstance(self.data_map, dict):
            if self.styles_map is None:
                styles_map = {k:None for k in self.data_map}
            else:
                styles_map = self.styles_map
            if self.label_map is None:
                label_map = {k:k for k in data_map}
            else:
                label_map = self.label_map
            handles = {}
            for key in self.data_map:
                data = self.data_map[key]
                styles = styles_map.get(key, None)
                label = label_map.get(key, "")
                handle = self.draw_single_data(ax, data, styles, 
                                               label=label,
                                               xattrib=xattrib,
                                               yattrib=yattrib)
                handles[key] = handle
            self.update_legend_handles(handles)
        else:
            raise ValueError("invalid data format")
            
        if draw_sigma_line:
            transform = create_transform(transform_x="axis", transform_y="data")
            sigma_line_styles = self.config['sigma_line_styles']
            sigma_values = self.config['sigma_values']
            sigma_names = self.config['sigma_names']
            ax.hlines(sigma_values, xmin=0, xmax=1, transform=transform,
                      **sigma_line_styles)
            if sigma_names:
                for sigma_value, sigma_name in zip(sigma_values, sigma_names):
                    ax.text(0.93, sigma_value, sigma_name, color='gray', ha='left', va='bottom', fontsize=20, transform=transform)
            
        handles, labels = self.get_legend_handles_labels()
        ax.legend(handles, labels, **self.styles['legend'])
        ax.set_ylim([0, ymax])
        ax.set_xlim([xmin, xmax])
        
        self.draw_axis_labels(ax, xlabel=xlabel, ylabel=ylabel)
        
        return ax

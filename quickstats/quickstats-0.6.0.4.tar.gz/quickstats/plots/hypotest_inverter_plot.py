from typing import Optional, Union, Dict, List

import matplotlib.patches as patches
import matplotlib.lines as lines
import pandas as pd
import ROOT

from quickstats.plots import AbstractPlot
from quickstats.plots.template import single_frame, parse_styles
from quickstats.utils.roostats_utils import get_array_quantiles

class HypoTestInverterPlot(AbstractPlot):
    
    COLOR_PALLETE = {
        '2sigma': '#FDC536',
        '1sigma': '#4AD9D9',
        'CLs': 'r',
        'CLb': 'k',
        'CLsplusb': 'b'
    }
    
    def __init__(self, result, nsig:int=2, 
                 color_pallete:Optional[Dict]=None,
                 styles:Optional[Union[Dict, str]]='limit',
                 analysis_label_options:Optional[Dict]=None):
        self.result = result
        
        super().__init__(color_pallete=color_pallete,
                         styles=styles,
                         analysis_label_options=analysis_label_options)
        
    def get_expected_CLs_data(self):
        n_entries = self.result.ArraySize()
        data = {}
        for i in range(n_entries):
            s = self.result.GetExpectedPValueDist(i)
            if not s:
                continue
            values = s.GetSamplingDistribution().data()
            mu = self.result.GetXValue(i)
            data[mu] = get_array_quantiles(values)
        return data
        
    def draw_expected(self, ax, nsig:int=2):
        data = self.get_expected_CLs_data()
        df = pd.DataFrame(data).transpose().sort_index()
        mu_values = df.index.values
        n2sigma = df[-2].values
        n1sigma = df[-1].values
        median  = df[0].values
        p1sigma = df[1].values
        p2sigma = df[2].values

        if nsig >= 2:
            ax.fill_between(mu_values, n2sigma, p2sigma, facecolor=self.color_pallete['2sigma'], 
                            label='Expected CLs $\pm 2\sigma$')
        if nsig >= 1:
            ax.fill_between(mu_values, n1sigma, p1sigma, facecolor=self.color_pallete['1sigma'], 
                            label='Expected CLs $\pm 1\sigma$')
        ax.plot(mu_values, median, 'k--', label='Expected CLs Median')            
    
    def get_observed_CL_data(self):
        n_entries = self.result.ArraySize()
        data = {}
        for i in range(n_entries):
            mu = self.result.GetXValue(i)
            data[mu] = {
                'CLs'          : self.result.CLs(i),
                'CLb'          : self.result.CLb(i),
                'CLsplusb'     : self.result.CLsplusb(i),
                'CLsError'     : self.result.CLsError(i),
                'CLbError'     : self.result.CLbError(i),
                'CLsplusbError': self.result.CLsplusbError(i),
            }
        return data
    
    def draw_observed(self, ax, draw_CLs:bool=True, draw_CLb:bool=True, 
                      draw_CLsplusb:bool=True):
        data = self.get_observed_CL_data()
        df = pd.DataFrame(data).transpose().sort_index()
        mu_values = df.index.values
        CLs = df['CLs'].values
        CLb = df['CLb'].values
        CLsplusb = df['CLsplusb'].values
        CLsError = df['CLsError'].values
        CLbError = df['CLbError'].values
        CLsplusbError = df['CLsplusbError'].values
        if draw_CLs:
            ax.errorbar(mu_values, CLs, yerr=CLsError, **self.styles['errorbar'], 
                        color=self.color_pallete['CLs'], linestyle='-', 
                        label='Observed CLs')
        if draw_CLb:
            ax.errorbar(mu_values, CLb, yerr=CLbError, **self.styles['errorbar'], 
                        color=self.color_pallete['CLb'], linestyle='-',
                        label='Observed CLb')
        if draw_CLsplusb:
            ax.errorbar(mu_values, CLsplusb, yerr=CLsplusbError, **self.styles['errorbar'], 
                        color=self.color_pallete['CLsplusb'], linestyle='dotted', 
                        label='Observed CLs+b')

    def draw(self, nsig:int=2, draw_CLs:bool=True, 
             draw_CLb:bool=True, draw_CLsplusb:bool=True,
             ymax:float=0.55, draw_CL:bool=True):
        if nsig < 0 or nsig > 2:
            raise ValueError("nsig must be between 0 and 2")
            
        ax = self.draw_frame()
        
        self.draw_expected(ax, nsig=nsig)
        self.draw_observed(ax, draw_CLs=draw_CLs,
                           draw_CLb=draw_CLb,
                           draw_CLsplusb=draw_CLsplusb)
        ax.set_xlabel("$\mu$", **self.styles['xlabel'])
        ax.set_ylabel("p value", **self.styles['ylabel'])
        
        ax.set_ylim(-0.01, ymax)
        n_entries = self.result.ArraySize()
        mu_list = []
        for i in range(n_entries):
            mu_list.append(self.result.GetXValue(i))
        ax.set_xlim(min(mu_list), max(mu_list))
        
        if draw_CL:
            ax.axhline(y=0.05, color='r', linestyle='-', linewidth=1)
        # border for the legend
        border_leg = patches.Rectangle((0, 0), 1, 1, facecolor = 'none', edgecolor = 'black', linewidth = 1)        
        # reorder legends
        handles, labels = ax.get_legend_handles_labels()
        if nsig == 0:
            handles = handles[1:] + [handles[0]]
            labels = labels[1:] + [labels[0]]
        elif nsig == 1:
            handles[1].set_linewidth(1.0)
            handles = handles[2:] + [handles[0], (handles[1], border_leg)]
            labels = labels[2:] + [labels[0], labels[1]]
        elif nsig == 2:
            handles[1].set_linewidth(1.0)
            handles[2].set_linewidth(1.0)
            handles = handles[3:] + [handles[0], (handles[1], border_leg), (handles[2], border_leg)]
            labels = labels[3:] + [labels[0], labels[1], labels[2]]
        ax.legend(handles, labels, loc='upper right', frameon=False, **self.styles['legend'])
        return ax
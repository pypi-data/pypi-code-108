from typing import Optional, Union, Dict, List

import matplotlib.patches as patches
import matplotlib.lines as lines
import numpy as np
import pandas as pd

from quickstats.plots.template import single_frame, parse_styles, format_axis_ticks, create_transform
from quickstats.plots import AbstractPlot
from quickstats.utils.common_utils import combine_dict

class UpperLimit1DPlot(AbstractPlot):
    
    COLOR_PALLETE = {
        '2sigma': 'hh:darkyellow',
        '1sigma': 'hh:lightturquoise',
        'expected': 'k',
        'observed': 'k',
    }
    
    LABELS = {
        '2sigma': r'Expected limit $\pm 2\sigma$',
        '1sigma': r'Expected limit $\pm 1\sigma$',
        'expected': r'Expected limit',
        'observed': r'Observed limit',
    }    
    
    def __init__(self, category_df, label_map, line_below=None,
                 color_pallete:Optional[Dict]=None,
                 labels:Optional[Dict]=None,
                 styles:Optional[Union[Dict, str]]='limit_point',
                 analysis_label_options:Optional[Union[Dict, str]]=None):
        super().__init__(color_pallete=color_pallete,
                         styles=styles,
                         analysis_label_options=analysis_label_options)
        self.category_df = category_df
        self.label_map = label_map
        self.line_below = line_below
        
        self.labels = combine_dict(self.LABELS, labels)  
    
    def draw(self, logx:bool=False, xlabel:Optional[str]=None, markersize:float=50.,
             draw_observed:bool=True, draw_stat:bool=False, sig_fig:int=2):
        if (draw_observed + draw_stat) > 1:
            raise RuntimeError("draw_observed and draw_stat can not be both True")
        n_category = len(self.category_df.columns)
        ax = self.draw_frame(logx=logx)
        transform = create_transform(transform_x='axis', transform_y='data')
        
        if draw_observed:
            text_pos = {'observed': 0.775, 'expected': 0.925}
        if draw_stat:
            text_pos = {'expected': 0.775, 'stat': 0.925}
        if (not draw_observed) and (not draw_stat):
            text_pos = {'expected': 0.925}
        
        for i, category in enumerate(self.category_df):
            df = self.category_df[category]
            # draw observed
            if draw_observed:
                observed_limit = df['obs']
                ax.vlines(observed_limit, i, i+1, colors=self.color_pallete['observed'], linestyles='solid', 
                          zorder=1.1, label=self.labels['observed'] if i == 0 else '')
                ax.scatter(observed_limit, i + 0.5, s=markersize, marker='o', 
                           color=self.color_pallete['observed'], zorder=1.1)
                ax.text(text_pos['observed'], i + 0.5, f"{{:.{sig_fig}f}}".format(observed_limit), 
                        horizontalalignment='center', 
                        verticalalignment='center',
                        transform=transform,
                        **self.styles['text'])
            # draw stat
            if draw_stat:
                stat_limit = df['stat']
                ax.text(text_pos['stat'], i + 0.5, f"({{:.{sig_fig}f}})".format(stat_limit), 
                        horizontalalignment='center', 
                        verticalalignment='center',
                        transform=transform,
                        **self.styles['text'])
            # draw expected
            expected_limit = df['0']
            ax.vlines(expected_limit, i, i + 1, colors=self.color_pallete['expected'], linestyles = 'dotted',
                      zorder = 1.1, label=self.labels['expected'] if i==0 else '')
            ax.text(text_pos['expected'], i + 0.5, f"{{:.{sig_fig}f}}".format(expected_limit), 
                    horizontalalignment='center', 
                    verticalalignment='center',
                    transform=transform,
                    **self.styles['text'])
            # draw +1
            ax.fill_betweenx([i, i + 1], df['-2'], df['2'], facecolor=self.color_pallete['2sigma'], 
                             label=self.labels['2sigma'] if i==0 else '')
            ax.fill_betweenx([i, i + 1], df['-1'], df['1'], facecolor=self.color_pallete['1sigma'], 
                             label=self.labels['1sigma'] if i==0 else '')
        xlim = ax.get_xlim()
        ax.set_xlim(xlim[0] - (xlim[1]/0.7 - xlim[1])*0.5, xlim[1]/0.7)
        ax.set_ylim(0, len(self.category_df.columns) + 2.2)
        ax.set_yticks(np.arange(n_category) + 0.5, minor=False)
        ax.tick_params(axis="y", which="minor", length=0)
        for axis in ['top', 'bottom', 'left', 'right']:
            ax.spines[axis].set_linewidth(2)
        ax.set_yticklabels([self.label_map[i] for i in self.category_df.columns.to_list()], 
                           horizontalalignment='right')
        # draw horizonal dashed lines
        ax.axhline(n_category, color = 'k', ls = '--', lw=1)
        if self.line_below is not None:
            for category in self.line_below:
                position = np.where(np.array(self.category_df.columns, dtype='str') == category)[0]
                if position.shape[0] != 1:
                    raise ValueError("category `{}` not found in dataframe".format(category))
                ax.axhline(position[0], color = 'k', ls = '--', lw=1)
        if draw_observed:
            ax.text(text_pos['observed'], n_category + 0.3, 'Obs.', 
                    horizontalalignment='center', 
                    verticalalignment='center',
                    transform=transform,
                    **self.styles['text'])
        if draw_stat:
            ax.text(text_pos['stat'], n_category + 0.3, '(Stat.)', 
                    horizontalalignment='center', 
                    verticalalignment='center',
                    transform=transform,
                    **self.styles['text'])
        ax.text(text_pos['expected'], n_category + 0.3, 'Exp.', 
                horizontalalignment='center', 
                verticalalignment='center',
                transform=transform,
                **self.styles['text'])
        if xlabel is not None:
            ax.set_xlabel(xlabel, **self.styles['xlabel'])
        # border for the legend
        border_leg = patches.Rectangle((0, 0), 1, 1, facecolor = 'none', edgecolor = 'black', linewidth = 1)

        handles, labels = ax.get_legend_handles_labels()
        if draw_observed:
            handles = [handles[0], handles[1], (handles[3], border_leg), (handles[2], border_leg)]
            labels  = [labels[0], labels[1], labels[3], labels[2]]
        if draw_stat:
            handles = [handles[0], (handles[2], border_leg), (handles[1], border_leg)]
            labels  = [labels[0], labels[2], labels[1]]
        ax.legend(handles, labels, **self.styles['legend'])
        return ax
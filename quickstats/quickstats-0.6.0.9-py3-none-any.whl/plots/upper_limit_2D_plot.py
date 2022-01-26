from typing import Optional, Union, Dict, List

import matplotlib.patches as patches
import matplotlib.lines as lines
import pandas as pd
import ROOT

from quickstats.plots.template import single_frame, parse_styles, format_axis_ticks, draw_atlas_label
from quickstats.plots import AbstractPlot
from quickstats.utils.common_utils import combine_dict

class UpperLimit2DPlot(AbstractPlot):
    
    COLOR_PALLETE = {
        '2sigma': '#FDC536',
        '1sigma': '#4AD9D9',
        'expected': 'k',
        'observed': 'k'
    }
    
    COLOR_PALLETE_SEC = {
        '2sigma': '#FDC536',
        '1sigma': '#4AD9D9',
        'expected': 'r',
        'observed': 'r'
    }
    
    LABELS = {
        '2sigma': 'Expected limit $\pm 2\sigma$',
        '1sigma': 'Expected limit $\pm 1\sigma$',
        'expected': 'Expected limit (95% CL)',
        'observed': 'Observed limit (95% CL)'
    }
    
    LABELS_SEC = {
        '2sigma': 'Expected limit $\pm 2\sigma$',
        '1sigma': 'Expected limit $\pm 1\sigma$',
        'expected': 'Expected limit (95% CL)',
        'observed': 'Observed limit (95% CL)'
    }

    CONFIG = {
        'primary_hatch'  : '\\\\\\',
        'secondary_hatch': '///',
        'primary_alpha'  : 0.9,
        'secondary_alpha': 0.8,
        'curve_line_styles': {
            'color': 'darkred' 
        },
        'curve_fill_styles':{
            'color': '#F2385A'
        },
        'highlight_styles': {
            'linewidth' : 0,
            'marker' : '*',
            'markersize' : 20,
            'color' : '#E9F1DF',
            'markeredgecolor' : 'black'
        }
    }
    
    def __init__(self, data, data_sec=None,
                 scale_factor=None,
                 color_pallete:Optional[Dict]=None,
                 color_pallete_sec:Optional[Dict]=None,
                 labels:Optional[Dict]=None,
                 labels_sec:Optional[Dict]=None,
                 styles:Optional[Union[Dict, str]]='limit',
                 analysis_label_options:Optional[Union[Dict, str]]='default'):
        super().__init__(color_pallete=color_pallete,
                         color_pallete_sec=color_pallete_sec,
                         styles=styles,
                         analysis_label_options=analysis_label_options)
        self.data     = data
        # secondary data
        self.data_sec = data_sec
        
        self.labels = combine_dict(self.LABELS, labels)
        self.labels_sec = combine_dict(self.LABELS_SEC, labels_sec)
            
        self.scale_factor = scale_factor
        
        self.curve_data     = None
        self.highlight_data = None
    
        self.config = combine_dict(self.CONFIG)
        
    def get_default_legend_order(self):
        return ['observed', 'expected', '1sigma', '2sigma', 'curve', 'highlight']
    
    def add_curve(self, x, y, yerrlo=None, yerrhi=None,
                  label:str="Theory prediction",
                  line_styles:Optional[Dict]=None,
                  fill_styles:Optional[Dict]=None):
        curve_data = {
            'x'     : x,
            'y'     : y,
            'yerrlo'  : yerrlo,
            'yerrhi'  : yerrhi,
            'label' : label,
            'line_styles': line_styles,
            'fill_styles': fill_styles,
        }
        self.curve_data = curve_data
                        
    def add_highlight(self, x:float, y:float, label:str="SM prediction",
                      styles:Optional[Dict]=None):
        highlight_data = {
            'x'     : x,
            'y'     : y,
            'label' : label,
            'styles': styles
        }
        self.highlight_data = highlight_data        
    
    def draw_curve(self, ax, data):
        line_styles = data['line_styles']
        fill_styles = data['fill_styles']
        if line_styles is None:
            line_styles = self.config['curve_line_styles']
        if fill_styles is None:
            fill_styles = self.config['curve_fill_styles']
        handle_line = ax.plot(data['x'], data['y'], label=data['label'], **line_styles)
        handle_fill = ax.fill_between(data['x'], data['yerrlo'], data['yerrhi'],
                                      label=data['label'], **fill_styles)
        self.update_legend_handles({'curve': (handle_fill, handle_line[0])})
        
    def draw_highlight(self, ax, data):
        styles = data['styles']
        if styles is None:
            styles = self.config['highlight_styles']
        handle = ax.plot(data['x'], data['y'], label=data['label'], **styles)
        self.update_legend_handles({'highlight': handle[0]})
        
    def draw_single_data(self, ax, data, scale_factor=None,
                         log:bool=False, 
                         draw_observed:bool=True,
                         color_pallete:Optional[Dict]=None,
                         labels:Optional[Dict]=None,
                         observed_marker:Optional[str]='o', 
                         sigma_band_hatch:Optional[str]=None,
                         alpha:float=1.,
                         sec:bool=False):
        
        if color_pallete is None:
            color_pallete = self.color_pallete
        if labels is None:
            labels = self.labels
        if scale_factor is None:
            scale_factor = 1.0
            
        indices = data.index.astype(float).values
        exp_limits = data['0'].values * scale_factor
        n1sigma_limits = data['-1'].values * scale_factor
        n2sigma_limits = data['-2'].values * scale_factor
        p1sigma_limits = data['1'].values * scale_factor
        p2sigma_limits = data['2'].values * scale_factor
        
        handles_map = {}
        
        # draw +- 1, 2 sigma bands 
        handle_2sigma = ax.fill_between(indices, n2sigma_limits, p2sigma_limits, 
                                        facecolor=color_pallete['2sigma'],
                                        label=labels['2sigma'],
                                        hatch=sigma_band_hatch,
                                        alpha=alpha)
        handle_1sigma = ax.fill_between(indices, n1sigma_limits, p1sigma_limits, 
                                        facecolor=color_pallete['1sigma'],
                                        label=labels['1sigma'],
                                        hatch=sigma_band_hatch,
                                        alpha=alpha)
        handles_map['1sigma'] = handle_1sigma
        handles_map['2sigma'] = handle_2sigma
        
        if log:
            draw_fn = ax.semilogy
        else:
            draw_fn = ax.plot
 
        if draw_observed:
            obs_limits = data['obs'].values * scale_factor
            handle_observed = draw_fn(indices, obs_limits, color=color_pallete['observed'], 
                                      label=labels['observed'], 
                                      marker=observed_marker,
                                      alpha=alpha)
            handles_map['observed'] = handle_observed[0]
            
        handle_expected = draw_fn(indices, exp_limits, color=color_pallete['expected'],
                                  linestyle='--',
                                  label=labels['expected'],
                                  alpha=alpha)
        handles_map['expected'] = handle_expected[0]

        self.update_legend_handles(handles_map, sec=sec)
            
    def draw(self, xlabel:str="", ylabel:str="", ylim=None, xlim=None,
             log:bool=False, draw_observed:bool=True, observed_marker:Optional[str]='o'):
        ax = single_frame(styles=self.styles)

        if self.data_sec is not None:
            self.draw_single_data(ax, self.data_sec,
                                  scale_factor=self.scale_factor,
                                  log=log, 
                                  draw_observed=draw_observed,
                                  color_pallete=self.color_pallete_sec,
                                  labels=self.labels_sec,
                                  observed_marker=observed_marker, 
                                  sigma_band_hatch=self.config['secondary_hatch'],
                                  alpha=self.config['secondary_alpha'],
                                  sec=True)
            sigma_band_hatch = self.config['primary_hatch']
            alpha = self.config['primary_alpha']
        else:
            sigma_band_hatch = None
            alpha = 1.
        self.draw_single_data(ax, self.data,
                              scale_factor=self.scale_factor,
                              log=log, 
                              draw_observed=draw_observed,
                              color_pallete=self.color_pallete,
                              labels=self.labels,
                              observed_marker=observed_marker, 
                              sigma_band_hatch=sigma_band_hatch,
                              alpha=alpha)
        if self.curve_data is not None:
            self.draw_curve(ax, self.curve_data)   
        if self.highlight_data is not None:
            self.draw_highlight(ax, self.highlight_data)            
        ax.set_xlabel(xlabel, **self.styles['xlabel'])
        ax.set_ylabel(ylabel, **self.styles['ylabel'])
        format_axis_ticks(ax, **self.styles['axis'])
        
        if ylim is not None:
            ax.set_ylim(*ylim)
        if xlim is not None:
            ax.set_xlim(*xlim)
        
        if self.analysis_label_options is not None:
            draw_atlas_label(ax, dy=0.05, text_options=self.styles['text'], **self.analysis_label_options)
        # border for the legend
        border_leg = patches.Rectangle((0, 0), 1, 1, facecolor = 'none', edgecolor = 'black', linewidth = 1)
        self.legend_data['1sigma']['handle'] = (self.legend_data['1sigma']['handle'], border_leg)
        self.legend_data['2sigma']['handle'] = (self.legend_data['2sigma']['handle'], border_leg)
        if self.curve_data is not None:
            self.legend_data['curve']['handle'] = (*self.legend_data['curve']['handle'], border_leg)
        
        if self.data_sec is not None:
            self.legend_data_sec['1sigma']['handle'] = (self.legend_data_sec['1sigma']['handle'], border_leg)
            self.legend_data_sec['2sigma']['handle'] = (self.legend_data_sec['2sigma']['handle'], border_leg)
            
        handles, labels = self.get_legend_handles_labels()
        if self.data_sec is not None:
            handles_sec, labels_sec = self.get_legend_handles_labels(sec=True)
            handles = handles + handles_sec
            labels  = labels + labels_sec
        ax.legend(handles, labels, **self.styles['legend'])
        return ax
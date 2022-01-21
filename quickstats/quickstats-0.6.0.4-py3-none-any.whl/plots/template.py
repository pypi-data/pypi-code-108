from typing import Optional, Union, Dict, List, Tuple
from copy import deepcopy
import re
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.transforms as transforms
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,
                               AutoMinorLocator, ScalarFormatter,
                               Locator, Formatter, AutoLocator)

from quickstats.utils.common_utils import update_nested_dict

class NumericFormatter(ScalarFormatter):
    def __call__(self, x, pos=None):
        tmp_format = self.format
        if x.is_integer():
            self.format = re.sub(r"1\.\d+f", r"1.0f", self.format)
        result = super().__call__(x, pos)
        self.format = tmp_format
        return result

COLOR_PALLETE = ['#000000', '#F2385A', '#4AD9D9', '#FDC536', '#125125', '#E88EED', '#B68D40']


PLOT_STYLES = {
    'distributions': {
        'marker': 'o',
        'markersize': 1,
        'linewidth': 1
    }
}

TEMPLATE_STYLES = {
    'default': {
        'figure':{
            'figsize': (11.111, 8.333),
            'dpi': 72,
            'facecolor': "#FFFFFF"
        },
        'legend_Line2D': {
            'linewidth': 3
        },
        'annotation':{
            'fontsize': 12
        },
        'axis': {
            'major_length': 16,
            'minor_length': 8,
            'major_width': 2,
            'minor_width': 1,
            'spine_width': 2,
            'labelsize': 20,
            'tick_bothsides': True
        },
        'xtick':{
            'format': 'numeric',
            'steps': None,
            'prune': None
        },
        'ytick':{
            'format': 'numeric', 
            'steps': None,
            'prune': None
        },        
        'xlabel': {
            'fontsize': 22,
            'loc' : 'right',
            'labelpad': 10
        },
        'ylabel': {
            'fontsize': 22,
            'loc' : 'top',
            'labelpad': 15
        },
        'text':{
            'fontsize': 20,
        },
        'plot':{
            'linewidth': 2
        },
        'errorbar': {
            "marker": 'x',
            "linewidth": 0,
            "markersize": 0,
            "elinewidth": 1,
            "capsize": 2,
            "capthick": 1
        },
        'legend':{
            "fontsize": 20
        }
    },
    'limit': {
        'axis':{
            'tick_bothsides': False
        },
        'errorbar': {
            "linewidth": 1,
            "markersize": 5,
            "marker": 'o',
        }
    },
    'limit_point':{
        'figure':{
            'figsize': (11.111, 10.333),
            'dpi': 72,
            'facecolor': "#FFFFFF"
        },        
        'axis':{
            'tick_bothsides': False
        },
        'legend':{
            'fontsize': 22
        },
        'text':{
            'fontsize': 22
        }
    },
    'teststat_dist': {
        'legend': {
            'fontsize': 12
        },
        'annotation':{
            'fontsize': 12
        }
    }
}

ANALYSIS_OPTIONS = {
    'default': {
        'loc': (0.05, 0.95),
        'fontsize': 20
    },
    'Run2': {
        'status': 'int', 
        'energy' : '13 TeV', 
        'lumi' : 139,
    }
}

def parse_styles(styles:Optional[Union[Dict, str]]=None):
    default_styles = deepcopy(TEMPLATE_STYLES['default'])
    if styles is None:
        styles = default_styles
    elif isinstance(styles, str):
        template_styles = TEMPLATE_STYLES.get(styles, None)
        if template_styles is None:
            raise ValueError(f"template styles `{styles}` not found")
        styles = update_nested_dict(default_styles, deepcopy(template_styles))
    else:
        styles = update_nested_dict(default_styles, deepcopy(styles))
    return styles

def parse_analysis_label_options(options:Optional[Dict]=None):
    default_options = deepcopy(ANALYSIS_OPTIONS['default'])
    if options is None:
        options = default_styles
    elif isinstance(options, str):
        template_options = ANALYSIS_OPTIONS.get(options, None)
        if template_options is None:
            raise ValueError(f"template analysis label options `{styles}` not found")
        options = update_nested_dict(default_options, deepcopy(template_options))
    else:
        options = update_nested_dict(default_options, deepcopy(options))
    return options

def single_frame(logx:bool=False, logy:bool=False, 
                 styles:Optional[Union[Dict, str]]=None,
                 analysis_label_options:Optional[Union[Dict, str]]=None):
    plt.clf()
    styles = parse_styles(styles)
    fig, ax = plt.subplots(nrows=1, ncols=1, **styles['figure'])
    if logx:
        ax.set_xscale('log')
    if logy:
        ax.set_yscale('log')
    format_axis_ticks(ax, x_axis=True, y_axis=True, xtick_styles=styles['xtick'],
                      ytick_styles=styles['ytick'], **styles['axis'])
        
    if analysis_label_options is not None:
        draw_atlas_label(ax, dy=0.05, text_options=styles['text'], **analysis_label_options)
        
    return ax


def suggest_markersize(nbins:int):
    if nbins <= 20:
        return 10
    elif (nbins > 20) and (nbins <= 200):
        return nbins/20
    return 1

def format_axis_ticks(ax, x_axis=True, y_axis=True, major_length:int=16, minor_length:int=8,
                      spine_width:int=2, major_width:int=2, minor_width:int=1, 
                      label_bothsides:bool=False, tick_bothsides:bool=False,
                      labelsize:Optional[int]=None,
                      x_axis_styles:Optional[Dict]=None, 
                      y_axis_styles:Optional[Dict]=None,
                      xtick_styles:Optional[Dict]=None,
                      ytick_styles:Optional[Dict]=None):
    if x_axis:
        if (ax.get_xaxis().get_scale() != 'log'):
            ax.xaxis.set_minor_locator(AutoMinorLocator())
        styles = {"labelsize":labelsize}
        styles['labeltop'] = label_bothsides
        styles['labelbottom'] = True
        styles['top'] = tick_bothsides
        styles['bottom'] = True
        if x_axis_styles is not None:
            styles.update(x_axis_styles)
        ax.tick_params(axis="x", which="major", direction='in', length=major_length,
                       width=major_width, **styles)
        ax.tick_params(axis="x", which="minor", direction='in', length=minor_length,
                       width=minor_width, **styles)
    if y_axis:
        if (ax.get_yaxis().get_scale() != 'log'):
            ax.yaxis.set_minor_locator(AutoMinorLocator())    
        styles = {"labelsize":labelsize}
        styles['labelleft'] = True
        styles['labelright'] = label_bothsides
        styles['left'] = True
        styles['right'] = tick_bothsides
        if y_axis_styles is not None:
            styles.update(y_axis_styles)
        ax.tick_params(axis="y", which="major", direction='in', length=major_length,
                       width=major_width, **styles)
        ax.tick_params(axis="y", which="minor", direction='in', length=minor_length,
                       width=minor_width, **styles)
    for axis in ['top','bottom','left','right']:
        ax.spines[axis].set_linewidth(spine_width)
        
    set_axis_tick_styles(ax.xaxis, xtick_styles)
    set_axis_tick_styles(ax.yaxis, ytick_styles)

def set_axis_tick_styles(ax, styles=None):
    if styles is None:
        return None
    fmt = styles['format']
    if fmt is not None:
        formatter = None
        if isinstance(fmt, str):
            if fmt == 'numeric':
                formatter = NumericFormatter()
        if isinstance(fmt, Formatter):
            formatter = fmt
        if formatter is None:
            raise ValueError(f"unsupported axis tick format {fmt}")
        ax.set_major_formatter(formatter)
    locator = AutoLocator()
    locator_params = {}
    for param in ['steps', 'prune']:
        value = styles[param]
        if value is not None:
            locator_params[param] = value
    locator.set_params(**locator_params)
    ax.set_major_locator(locator)
                

def centralize_axis(ax, which='x'):
    if which == 'x':
        limits = ax.get_xlim()
        xmax = np.max(np.abs(limits))
        ax.set_xlim(-xmax, xmax)
    elif which == 'y':
        limits = ax.get_ylim()
        ymax = np.max(np.abs(limits))
        ax.set_ylim(-ymax, ymax)
        
def parse_transform(obj:str):
    if not obj:
        transform = None
    elif obj == 'figure':
        transform = plt.gcf().transFigure
    elif obj == 'axis':
        transform = plt.gca().transAxes
    elif obj == 'data':
        transform = plt.gca().transData
    return transform

def create_transform(transform_x:str='axis', transform_y:str='axis'):
    transform = transforms.blended_transform_factory(parse_transform(transform_x), 
                                                     parse_transform(transform_y))
    return transform

def get_box_dimension(box):
    axis = plt.gca()
    plt.gcf().canvas.draw()
    bb = box.get_window_extent()
    points  = bb.transformed(axis.transAxes.inverted()).get_points().transpose()
    xmin = np.min(points[0])
    xmax = np.max(points[0])
    ymin = np.min(points[1])
    ymax = np.max(points[1])
    return xmin, xmax, ymin, ymax

def draw_sigma_bands(axis, ymax, height=1.0):
    # +- 2 sigma band
    axis.add_patch(Rectangle((-2, -height/2), 2*2, ymax + height/2, fill=True, color='yellow'))
    # +- 1 sigma band
    axis.add_patch(Rectangle((-1, -height/2), 1*2, ymax + height/2, fill=True, color='lime'))
    
def draw_sigma_lines(axis, ymax, height=1.0, **styles):
    y = [-height/2, ymax*height - height/2]
    axis.add_line(Line2D([-1, -1], y, **styles))
    axis.add_line(Line2D([+1, +1], y, **styles))
    axis.add_line(Line2D([0, 0], y, **styles)) 
    
def draw_hatches(axis, ymax, height=1.0, **styles):
    x_min    = axis.get_xlim()[0]
    x_max    = axis.get_xlim()[1]
    x_range  = x_max - x_min
    y_values = np.arange(0, height*ymax, 2*height) - height/2
    transform = create_transform(transform_x='axis', transform_y='data')
    for y in y_values:
        axis.add_patch(Rectangle((0, y), 1, 1, **styles, zorder=-1, transform=transform))

def draw_text(axis, x, y, s, transform_x:str='axis', 
              transform_y:str='axis', **styles):
    transform = transforms.blended_transform_factory(parse_transform(transform_x), 
                                                     parse_transform(transform_y))
    text = axis.text(x, y, s, transform=transform, **styles)
    xmin, xmax, ymin, ymax = get_box_dimension(text)
    return xmin, xmax, ymin, ymax


def draw_ATLAS_label(axis, loc=(0.05, 0.95), fontsize=25, extra='Internal', 
                     transform_x='axis', transform_y='axis', 
                     vertical_align='top', horizontal_align='left'):
    current_axis = plt.gca()
    plt.sca(axis)
    if vertical_align not in ['top', 'bottom']:
        raise ValueError('only "top" or "bottom" vertical alignment is allowed')
    if horizontal_align not in ['left', 'right']:
        raise ValueError('only "left" or "right" horizontal alignment is allowed') 
    transform = transforms.blended_transform_factory(parse_transform(transform_x), 
                                                     parse_transform(transform_y))
    x, y = loc
    text_atlas = axis.text(x, y, 'ATLAS', fontsize=fontsize, transform=transform,
                           horizontalalignment=horizontal_align,
                           verticalalignment=vertical_align,
                           fontproperties={"weight":"bold", "style":"italic"})
    xmin, xmax, ymin, ymax = get_box_dimension(text_atlas)
    text_width = xmax - xmin
    dx = text_width/15
    text_extra = axis.text(xmax + dx, ymin, extra, fontsize=fontsize, transform=axis.transAxes,
                           horizontalalignment='left', verticalalignment='bottom')
    plt.sca(current_axis)
    _, xmax, _, ymax = get_box_dimension(text_atlas)
    return xmin, xmax, ymin, ymax

def draw_atlas_label(axis, loc=(0.05, 0.95), fontsize=25, status:str='int',
                     energy:Optional[str]=None, lumi:Optional[str]=None,
                     extra_text:Optional[str]=None, dy:float=0.05,
                     transform_x:str='axis', transform_y:str='axis',
                     text_options:Optional[Dict]=None):
    if status == "final":
        status_str = ""
    elif status == "int":
        status_str = "Internal"
    elif status == "wip":
        status_str = "Work in Progress"
    elif status == "prelim":
        status_str = "Preliminary"
    elif status == "opendata":
        status_str = "Open Data"
    else:
        status_str = status
        
    xmin, xmax, ymin, ymax = draw_ATLAS_label(axis, loc, fontsize, extra=" "+status_str,
                                              transform_x=transform_x,
                                              transform_y=transform_y)

    elumi_text = []
    if energy is not None:
        elumi_text.append(r"$\sqrt{s} = $" + energy )
    if lumi is not None:
        elumi_text.append(lumi)

    elumi_text = ", ".join(elumi_text)
    
    texts = []
    if elumi_text:
        texts.append(elumi_text)
        
    if extra_text is not None:
        texts += extra_text.split("//")
    
    if text_options is None:
        text_options = {}
    
    for text in texts:
        _, _, ymin, _ = draw_text(axis, xmin, ymin - dy, text, **text_options)
        
    return

def add_collective_data(ax, data, plot_styles=None):
    if plot_styles is None:
        plot_styles = None
    color_iter = iter(COLOR_PALLETE)
    for label in data:
        styles = plot_styles.copy()
        x = data[label]['x']
        y = data[label]['y']
        nbins = len(x)
        if 'markersize' not in styles:
            styles['markersize'] = suggest_markersize(nbins)        
        if 'color' not in styles:
            styles['color'] = next(color_iter)
        styles['label'] = label
        ax.plot(x, y, **styles)

def plot_distributions(data, xlabel='', ylabel='', 
                       figsize=(14, 8), plot_styles=None, atlas_label=False):
    plt.clf()
    base_size = figsize[0]
    fig = plt.figure(figsize=figsize)
    ax = plt.gca()
    styles = PLOT_STYLES['distributions'].copy()
    if plot_styles is not None:
        styles.update(plot_styles)
    add_collective_data(ax, data, styles)
    limits = ax.get_ylim()
    ax.set_ylim(limits[0], limits[1]*1.2)
    ax.set_xlabel(xlabel, fontsize=base_size*1.6,  labelpad=base_size*0.7)
    ax.set_ylabel(ylabel, fontsize=base_size*1.6,  labelpad=base_size*0.7)
    format_axis_ticks(ax, major_length=14, minor_length=7, major_width=1.3, 
                      minor_width=1.3, labelsize=base_size*1.4)
    if atlas_label:
        draw_ATLAS_label(ax, fontsize=base_size*1.8)
    ax.legend(fontsize=base_size*1.2)
    return plt
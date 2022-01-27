import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pydantic import validate_arguments
from typing import List, Tuple, Dict, Any, Union, Optional
import matplotlib.pyplot as plt
import matplotlib as mpl

@validate_arguments(config=dict(arbitrary_types_allowed=True))
def formations_plot(
    formations: pd.DataFrame,
    depth_ref:str,
    ylims : Tuple[float, float],
    xlims : Tuple[float, float],
    ax: plt.Axes,
    config: Dict[str, Any] = {},
):
    def_formation_kw = {
    'color': 'black',
    'linestyle':'-',
    'linewidth': 2,
    'fill':False,
    'cmap':'jet',
    'alpha':0.15
    }    
    for (k,v) in def_formation_kw.items():
        if k not in config:
            config[k]=v


    formation_ann = config.pop('ann',False)
    formation_ann_fontsize = config.pop('fontsize',8)
    formation_fill = config.pop('fill',False)
    formation_cmap = config.pop('cmap','jet')
    formation_alpha = config.pop('alpha',0.2)
    formation_ann_xytext = config.pop('xytext',(0,-2))

    if depth_ref == 'tvdss':
        formations = formations.loc[(formations[f'{depth_ref}_top']<= ylims[0])&(formations[f'{depth_ref}_top']>= ylims[1]),:]
    else:
        formations = formations.loc[(formations[f'{depth_ref}_top']>= ylims[0])&(formations[f'{depth_ref}_top']<= ylims[1]),:]
    formation_cmap_shape = config.pop('cmap_shape',formations.shape[0])
    
    if 'color_id' not in formations.columns:
        formations['color_id'] = np.arange(formations.shape[0])
    for i,r in formations.iterrows():
        # Fill with color between the top and bottom of each formation
        if formation_fill:
            if depth_ref == 'tvdss':
                fill_top = ylims[0] if r[f'{depth_ref}_top'] >= ylims[0] else r[f'{depth_ref}_top']
                fill_bottom = ylims[1] if r[f'{depth_ref}_bottom'] <= ylims[1] else r[f'{depth_ref}_bottom']
            else:
                fill_top = ylims[0] if r[f'{depth_ref}_top'] <= ylims[0] else r[f'{depth_ref}_top']
                fill_bottom = ylims[1] if r[f'{depth_ref}_bottom'] >= ylims[1] else r[f'{depth_ref}_bottom']
            
            ax.fill_between(list(xlims),fill_top,fill_bottom,color=mpl.cm.get_cmap(formation_cmap,formation_cmap_shape)(r['color_id'])[:3]+(formation_alpha,))

        ax.hlines([r[f'{depth_ref}_top']],xlims[0],xlims[1], **config)
        if formation_ann:
            ax.annotate(
                f"Top of {i}",
                xy=(xlims[0]+formation_ann_xytext[0],r[f'{depth_ref}_top']+formation_ann_xytext[1]),
                xycoords='data',
                horizontalalignment='right', 
                fontsize=formation_ann_fontsize,
                bbox={'boxstyle':'round', 'fc':'0.8'})
        
    return ax


@validate_arguments(config=dict(arbitrary_types_allowed=True))
def correlations_plot(
    correlations: pd.DataFrame,
    depth_ref:str,
    ylims : Tuple[float, float],
    xlims : Tuple[float, float],
    ax: plt.Axes,
    config: Dict[str, Any] = {},
):
    
    def_corr_kw = {
    'color': 'red',
    'linestyle':'--',
    'linewidth': 2
    }    
    for (k,v) in def_corr_kw.items():
        if k not in config:
            config[k]=v
    
    cor_ann = config.pop('ann',False)
    cor_ann_fontsize = config.pop('fontsize',8)
    for i in correlations.iterrows():
        if depth_ref == 'tvdss':
            if i[1]['depth'] >= ylims[0] or i[1]['depth'] <= ylims[1]:
                continue
        else:
            if i[1]['depth'] < ylims[0] or i[1]['depth'] > ylims[1]:
                continue
        ax.hlines(i[1]['depth'],xlims[0],xlims[1], **config)
        if cor_ann:
            try:
                ax.annotate(f"{i[1]['depth']} - {i[1]['comment']} ",xy=(xlims[0],i[1]['depth']-1),
                                xycoords='data',horizontalalignment='right',bbox={'boxstyle':'roundtooth', 'fc':'0.8'},
                                fontsize = cor_ann_fontsize)
            except:
                ax.annotate(f"{i[1]['depth']}",xy=(xlims[0],i[1]['depth']-1),
                                xycoords='data',horizontalalignment='right',
                                bbox={'boxstyle':'roundtooth', 'fc':'0.8'},
                                fontsize = cor_ann_fontsize)
            
    return ax

@validate_arguments(config=dict(arbitrary_types_allowed=True))
def perforations_plot(
    perforations: pd.DataFrame,
    depth_ref:str,
    ylims : Tuple[float, float],
    xlims : Tuple[float, float],
    ax: plt.Axes,
    config: Dict[str, Any] = {},
):

    def_perf_kw = {
    'color': 'black',
    'linestyle':'-',
    'linewidth': 1
    }    
    for (k,v) in def_perf_kw.items():
        if k not in config:
            config[k]=v

    perf_ann = config.pop('ann',False)
    perf_ann_fontsize = config.pop('fontsize',8)
    perf_ann_xytext = config.pop('xytext',(-180,0))
    for i in perforations.iterrows():
        if depth_ref == 'tvdss':
            if i[1][f'{depth_ref}_top'] >= ylims[0] or i[1][f'{depth_ref}_top'] <= ylims[1]:
                continue
        else:
            if i[1][f'{depth_ref}_top'] <= ylims[0] or i[1][f'{depth_ref}_top'] >= ylims[1]:
                continue
        if perf_ann:
            try:
                ax.annotate(f"Top:{i[1][f'{depth_ref}_top']} \nBottom:{i[1][f'{depth_ref}_bottom']} \nNote:{i[1]['comment']}",
                            xy=(0,(i[1][f'{depth_ref}_top']+i[1][f'{depth_ref}_bottom'])/2),xycoords='data',
                            xytext=(-180, 0), textcoords='offset points',
                            arrowprops=dict(arrowstyle="->"))
            except:
                ax.annotate(f"Top:{i[1][f'{depth_ref}_top']} \nBottom:{i[1][f'{depth_ref}_bottom']}",
                xy=(0,(i[1][f'{depth_ref}_top']+i[1][f'{depth_ref}_bottom'])/2),xycoords='data',
                xytext=perf_ann_xytext, textcoords='offset points', fontsize = perf_ann_fontsize,
                arrowprops=dict(arrowstyle="->"))
            else: 
                pass
        if depth_ref == 'tvdss':
            for j in np.arange(i[1][f'{depth_ref}_bottom'],i[1][f'{depth_ref}_top'],0.5):
                ax.hlines(j,0,15,**config)
        else:
            for j in np.arange(i[1][f'{depth_ref}_top'],i[1][f'{depth_ref}_bottom'],0.5):
                ax.hlines(j,0,15,**config)
                
    return ax
            

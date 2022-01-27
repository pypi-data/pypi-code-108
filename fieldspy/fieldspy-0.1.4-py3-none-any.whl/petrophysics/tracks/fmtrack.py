import matplotlib.pyplot as plt 
import pandas as pd
import numpy as np
from typing import Union, Tuple, Dict
from pydantic import validate_arguments
from .utils import formations_plot, perforations_plot, correlations_plot
import matplotlib as mpl

@validate_arguments(config=dict(arbitrary_types_allowed=True))
def fmtrack(
    df: pd.DataFrame,
    ylims:Tuple[float,float] = None,
    xlims:Tuple[float,float] = (0,1),
    depth_ref:str = 'md',
    area_kw:dict = {},
    line_kw:dict = {},
    fm_colormap: str='winter',
    fontsize:int = 8 , 
    ax=None,
    formations: pd.DataFrame = None,
    units: pd.DataFrame = None,
    perforations: pd.DataFrame = None,
    correlations: pd.DataFrame = None,
    formations_kw:Dict={},
    units_kw:Dict={},
    perforations_kw:Dict={},
    correlations_kw:Dict={},
    ann:bool=True,
    rotation:Union[str,float] = 'vertical',
    ticks_formation:bool=True
):

    list_axes = []
    #fm=None,lims=None, top='top',bottom='bottom',name='name',ax=None):

    # Default kwargs for area
    def_area_kw = {
    'xmin': 0,
    'xmax': 1,
    'alpha': 0.2
    }
    for (k,v) in def_area_kw.items():
        if k not in area_kw:
            area_kw[k]=v

    # Default kwargs for lines
    def_line_kw = {
        'linewidth': 1
    }
    for (k,v) in def_line_kw.items():
        if k not in line_kw:
            line_kw[k]=v

    fax=ax or plt.gca()
        
    if ylims==None: #Depth Limits
        ylims=[df.loc[:,f'{depth_ref}_top'].min(),df.loc[:,f'{depth_ref}_bottom'].max()]
    fax.set_ylim([ylims[1],ylims[0]])
    fax.set_xlim(list(xlims))
    dff = df[(df[f'{depth_ref}_top']>=ylims[0]) & (df[f'{depth_ref}_bottom']<=ylims[1])]
    cmap = mpl.cm.get_cmap(fm_colormap,dff.shape[0])
    c = 0
    for i,r in dff.iterrows():
        fax.axhspan(r[f'{depth_ref}_top'],r[f'{depth_ref}_bottom'],color=cmap(c),**area_kw)
        fax.hlines([r[f'{depth_ref}_top'],r[f'{depth_ref}_bottom']],xlims[0],xlims[1], **line_kw)
        if ann:
            y_coord = (r[f'{depth_ref}_top']+r[f'{depth_ref}_bottom'])/2
            x_coord = (xlims[0] + xlims[1])/2
            fax.annotate(
                f"{i}",
                xy=(x_coord, y_coord),
                xycoords='data',
                fontsize = fontsize,
                rotation = rotation,
            )
        c += 1
    
    if ticks_formation:
        fax.set_yticks(dff[f'{depth_ref}_top'])
        fax.set_yticklabels(dff.index)
    
    
   #Add formations tops
    if formations is not None:
        fax = formations_plot(
            formations,
            depth_ref,
            ylims,
            xlims,
            fax,
            config=formations_kw
        )

    # #Add units tops
    if units is not None:
        fax = formations_plot(
            units,
            depth_ref,
            ylims,
            xlims,
            fax,
            config=units_kw
        )

    #  #Add Interval Perforated
    if perforations is not None:
        fax = perforations_plot(
            perforations,
            depth_ref,
            ylims,
            xlims,
            fax,
            config=perforations_kw
        )
        
    if correlations is not None:
        fax = correlations_plot(
            correlations,
            depth_ref,
            ylims,
            xlims,
            fax,
            config=correlations_kw
        )
    
    
    list_axes.append(fax)
    return fax
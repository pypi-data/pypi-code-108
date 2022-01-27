import matplotlib.pyplot as plt 
import pandas as pd
import numpy as np
from typing import Union, Tuple, Dict
from pydantic import validate_arguments
from .utils import formations_plot, perforations_plot, correlations_plot

@validate_arguments(config=dict(arbitrary_types_allowed=True))
def flagtrack(
    df: pd.DataFrame,
    sand: Union[str,list] = None,
    res: Union[str,list] = None,
    pay: Union[str,list] = None,
    ax=None,
    ylims: Tuple[float,float] = None,
    xlims: Tuple[float,float] = (0,1),
    fontsize:int = 8,
    legend:bool = True,
    formations: pd.DataFrame = None,
    units: pd.DataFrame = None,
    perforations: pd.DataFrame = None,
    correlations: pd.DataFrame = None,
    formations_kw:Dict={},
    units_kw:Dict={},
    perforations_kw:Dict={},
    correlations_kw:Dict={},
    corr_kw={},
    sand_kw={},
    res_kw={},
    pay_kw={},
    depth_ref:str='md'
):
    list_axes = []
    #Create the axes
    fax=ax or plt.gca()
    
    #Default kwargs for lines
    def_sand_kw = {
    'linestyle':'-',
    'linewidth': 0.1
    }
    
    for (k,v) in def_sand_kw.items():
        if k not in sand_kw:
            sand_kw[k]=v
            
    def_res_kw = {
    'linestyle':'-',
    'linewidth': 0.1
    }
    
    for (k,v) in def_res_kw.items():
        if k not in res_kw:
            res_kw[k]=v
            
    def_pay_kw = {
    'linestyle':'-',
    'linewidth': 0.1
    }
    
    for (k,v) in def_pay_kw.items():
        if k not in pay_kw:
            pay_kw[k]=v
    
    def_corr_kw = {
    'color': 'red',
    'linestyle':'--',
    'linewidth': 2
    }    
    for (k,v) in def_corr_kw.items():
        if k not in corr_kw:
            corr_kw[k]=v
            

    depth = df.index if depth_ref=='md' else df[depth_ref]
    # Plot main Lines
    if sand is not None:
        fax.plot(df[sand]*0.33, depth,**sand_kw)
        fax.fill_betweenx(depth,0,df[sand]*0.33, color='yellow',label='Sand')
        
    if res is not None:
        fax.plot(df[res]*0.66, depth,**res_kw)
        fax.fill_betweenx(depth,0.33,df[res]*0.66, where=(df[res]*0.66>0.33), color='orange',label='Res')
        
    if pay is not None:
        fax.plot(df[pay], depth,**pay_kw)
        fax.fill_betweenx(depth,0.66,df[pay], where=(df[pay]>0.66), color='green',label='pay')

    # Set The ylims of depth    
    fax.set_xlim(list(xlims))          
    if ylims==None: #Depth Limits
        ylims=[depth.min(),depth.max()]

    fax.set_ylim([ylims[1],ylims[0]])
        
    #Set the vertical grid spacing
        
    #Set Gridding and ticks
    fax.set_xlabel('Flags')
    fax.tick_params("both",labelsize=fontsize)
    fax.xaxis.set_label_position("top")
    fax.set_yticklabels([])
    fax.set_xticklabels([])    
    fax.set_yticks([],minor=True)
    fax.set_yticks([])
    fax.set_xticks([],minor=True)
    fax.set_xticks([])
    #fax.axis('off')
    fax.spines["top"].set_visible(False)
    fax.spines["right"].set_visible(False)
    fax.spines["bottom"].set_visible(False)
    fax.spines["left"].set_visible(False)
    
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
    

    if legend:
        fax.legend()
        
    list_axes.append(fax)
    return list_axes
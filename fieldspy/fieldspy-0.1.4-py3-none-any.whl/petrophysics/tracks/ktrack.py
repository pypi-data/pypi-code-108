import matplotlib.pyplot as plt 
import matplotlib as mpl
import pandas as pd
import numpy as np
from typing import Union, Tuple, Dict
from pydantic import validate_arguments
from .utils import formations_plot, perforations_plot, correlations_plot

@validate_arguments(config=dict(arbitrary_types_allowed=True))
def ktrack(
    df: pd.DataFrame, 
    perm: Union[str,list] = None, 
    ylims: Tuple[float,float] = None,
    k_lims:Tuple[float,float] =(0.2,20000),
    dtick: bool =False, 
    ax=None,
    formations: pd.DataFrame = None,
    units: pd.DataFrame = None,
    perforations: pd.DataFrame = None,
    correlations: pd.DataFrame = None,
    formations_kw:Dict={},
    units_kw:Dict={},
    perforations_kw:Dict={},
    correlations_kw:Dict={},
    fontsize:int =8,
    grid_numbers : list = [11,51],
    steps: list  = None,
    legend:bool = True,
    perm_colormap: str='Reds',
    corr_kw:Dict={},
    perm_kw:Dict={},
    depth_ref:str='md'
):
    list_axes = []
    #get number of curves to build the colormap
    
    kax=ax or plt.gca()
    defkwa = {
    "linestyle":'-',
    "linewidth": 1
    }
    for (k,v) in defkwa.items():
        if k not in perm_kw:
            perm_kw[k]=v
    
    def_corr_kw = {
    'color': 'red',
    'linestyle':'--',
    'linewidth': 2
    }    
    for (k,v) in def_corr_kw.items():
        if k not in corr_kw:
            corr_kw[k]=v
    
    depth = df.index if depth_ref=='md' else df[depth_ref]
    #Plot main Lines
    if perm is not None:
        if isinstance(perm,str):
            kax.plot(df[perm],depth,**perm_kw)   #Plotting
        elif isinstance(perm,list):
            cmap = mpl.cm.get_cmap(perm_colormap,len(perm))
            for i,g in enumerate(perm):
                perm_kw['color']=cmap(i)
                kax.plot(df[g],depth,**perm_kw)
    
    if ylims==None: #Depth Limits
        ylims=[depth.min(),depth.max()]

    kax.set_ylim([ylims[1],ylims[0]])
        
    #Set the vertical grid spacing
    if steps is None:
        mayor_grid = np.linspace(ylims[0],ylims[1],grid_numbers[0])
        minor_grid = np.linspace(ylims[0],ylims[1],grid_numbers[1])
    else:
        mayor_grid = np.arange(ylims[0],ylims[1],steps[0])
        minor_grid = np.arange(ylims[0],ylims[1],steps[1])
     
    #Set the gridding and ticks
    kax.set_xscale("log")
    kax.set_xlim(list(k_lims))
    ticks=np.round(np.power(10,np.linspace(np.log10(k_lims[0]),np.log10(k_lims[1]),int(np.log10(k_lims[1]/k_lims[0])+1))),decimals=1)
    kax.set_xticks(ticks)
    kax.set_xticklabels(ticks)
    kax.set_xlabel("K Perm")
    kax.xaxis.tick_top()
    kax.xaxis.set_label_position("top")
    kax.tick_params("both",labelsize=fontsize)
    kax.xformatter = 'auto'
    kax.set_yticks(minor_grid,minor=True)
    kax.set_yticks(mayor_grid)
    if dtick==True:
        kax.set_yticklabels(mayor_grid)
    else:
        kax.set_yticklabels([])
    kax.grid(True,linewidth=1.0)
    kax.grid(True,which='minor', linewidth=0.5)
    
    #Add formations tops
    if formations is not None:
        kax = formations_plot(
            formations,
            depth_ref,
            ylims,
            k_lims,
            kax,
            config=formations_kw
        )

    # #Add units tops
    if units is not None:
        kax = formations_plot(
            units,
            depth_ref,
            ylims,
            k_lims,
            kax,
            config=units_kw
        )

    #  #Add Interval Perforated
    if perforations is not None:
        kax = perforations_plot(
            perforations,
            depth_ref,
            ylims,
            k_lims,
            kax,
            config=perforations_kw
        )
        
    if correlations is not None:
        kax = correlations_plot(
            correlations,
            depth_ref,
            ylims,
            k_lims,
            kax,
            config=correlations_kw
        )
    if legend:
        kax.legend()
    
    list_axes.append(kax)
    return list_axes
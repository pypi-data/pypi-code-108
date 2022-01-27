import matplotlib.pyplot as plt 
import matplotlib as mpl
import pandas as pd
import numpy as np
from typing import Union, Tuple, Dict
from pydantic import validate_arguments
from .utils import formations_plot, perforations_plot, correlations_plot

@validate_arguments(config=dict(arbitrary_types_allowed=True))
def gastrack(
    df: pd.DataFrame, 
    gas: Union[str,list] = None, 
    ylims: Tuple[float,float] = None,
    gas_lims: Tuple[float,float] = (0.2,20000),
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
    fontsize:int = 8,
    grid_numbers : Tuple[float,float] = (11,51),
    steps: list  = None,
    legend:bool = True,
    gas_colormap: str='gist_rainbow',
    corr_kw:dict={},
    gas_kw:Dict={},
    depth_ref:str='md'
):
    list_axes = []
    #get number of curves to build the colormap
    
    gax=ax or plt.gca()
    defkwa = {
    'linestyle':'-',
    'linewidth': 1
    }
    for (k,v) in defkwa.items():
        if k not in gas_kw:
            gas_kw[k]=v
    
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
    if gas is not None:
        if isinstance(gas,str):
            gas.plot(df[gas],depth,**gas_kw)   #Plotting
        elif isinstance(gas,list):
            cmap = mpl.cm.get_cmap(gas_colormap,len(gas))
            for i,g in enumerate(gas):
                gas_kw['color']=cmap(i)
                gas.plot(df[g],depth,**gas_kw)
    
    if ylims==None: #Depth Limits
        ylims=[depth.min(),depth.max()]

    gax.set_ylim(list(ylims))   
        
    #Set the vertical grid spacing
    if steps is None:
        mayor_grid = np.linspace(ylims[0],ylims[1],grid_numbers[0])
        minor_grid = np.linspace(ylims[0],ylims[1],grid_numbers[1])
    else:
        mayor_grid = np.arange(ylims[0],ylims[1],steps[0])
        minor_grid = np.arange(ylims[0],ylims[1],steps[1])
     
    #Set the gridding and ticks
    gax.set_xscale("log")
    gax.set_xlim(list(gas_lims))
    ticks=np.round(np.power(10,np.linspace(np.log10(gas_lims[0]),np.log10(gas_lims[1]),int(np.log10(gas_lims[1]/gas_lims[0])+1))),decimals=1)
    gax.set_xticks(ticks)
    gax.set_xticklabels(ticks)
    gax.set_xlabel("Gas Chromatografy")
    gax.xaxis.tick_top()
    gax.xaxis.set_label_position("top")
    gax.tick_params("both",labelsize=fontsize)
    gax.xformatter = 'auto'
    gax.set_yticks(minor_grid,minor=True)
    gax.set_yticks(mayor_grid)
    if dtick==True:
        gax.set_yticklabels(mayor_grid)
    else:
        gax.set_yticklabels([])
    gax.grid(True,linewidth=1.0)
    gax.grid(True,which='minor', linewidth=0.5)
    
    #Add formations tops
    if formations is not None:
        gax = formations_plot(
            formations,
            depth_ref,
            ylims,
            gas_lims,
            gax,
            config=formations_kw
        )

    # #Add units tops
    if units is not None:
        gax = formations_plot(
            units,
            depth_ref,
            ylims,
            gas_lims,
            gax,
            config=units_kw
        )

    #  #Add Interval Perforated
    if perforations is not None:
        gax = perforations_plot(
            perforations,
            depth_ref,
            ylims,
            gas_lims,
            gax,
            config=perforations_kw
        )
        
    if correlations is not None:
        gax = correlations_plot(
            correlations,
            depth_ref,
            ylims,
            gas_lims,
            gax,
            config=correlations_kw
        )
        
    if legend:
        gax.legend()
    
    list_axes.append(gax)
    return list_axes
import matplotlib.pyplot as plt 
import matplotlib as mpl
import pandas as pd
import numpy as np
from typing import Union, Tuple, Dict
from pydantic import validate_arguments
from .utils import formations_plot, perforations_plot, correlations_plot

@validate_arguments(config=dict(arbitrary_types_allowed=True))
def khtrack(
    df:pd.DataFrame, 
    kh:Union[str,list]=None, 
    ylims:Tuple[float,float]=None,
    kh_lims:Tuple[float,float]=(0,1),
    dtick:bool=False,
    fill:bool=True, 
    ax=None,
    formations: pd.DataFrame = None,
    units: pd.DataFrame = None,
    perforations: pd.DataFrame = None,
    correlations: pd.DataFrame = None,
    formations_kw:Dict={},
    units_kw:Dict={},
    perforations_kw:Dict={},
    correlations_kw:Dict={},
    fontsize: int=8,
    grid_numbers : list = [11,51],
    steps: list  = None,
    kh_kw={},
    corr_kw={},
    fill_kh_kw={},
    kh_colormap:str='gray',
    depth_ref:str='md'
):
    list_axes = []
    hax=ax or plt.gca()
    
    def_kh_kw = {
    'color': 'black',
    'linestyle':'-',
    'linewidth': 1
    }
    
    for (k,v) in def_kh_kw.items():
        if k not in kh_kw:
            kh_kw[k]=v
            
    def_corr_kw = {
    'color': 'red',
    'linestyle':'--',
    'linewidth': 2
    }    
    for (k,v) in def_corr_kw.items():
        if k not in corr_kw:
            corr_kw[k]=v

    def_fill_kh_kw = {
    'color': (0.5,0.5,0.5),
    }    
    for (k,v) in def_fill_kh_kw.items():
        if k not in fill_kh_kw:
            fill_kh_kw[k]=v

    depth = df.index if depth_ref=='md' else df[depth_ref]
    if kh is not None:
        if isinstance(kh,str):
            hax.plot(df[kh],depth,**kh_kw)   #Plotting
        elif isinstance(kh,list):
            cmap = mpl.cm.get_cmap(kh_colormap,len(kh))
            for i,g in enumerate(kh):
                kh_kw['color']=cmap(i)
                hax.plot(df[g],depth,**kh_kw)
    
    if ylims==None: #Depth Limits
        ylims=[depth.min(),depth.max()]

    hax.set_ylim(list(ylims))
    hax.set_xlim(list(kh_lims))

    if steps is None:
        mayor_grid = np.linspace(ylims[0],ylims[1],grid_numbers[0])
        minor_grid = np.linspace(ylims[0],ylims[1],grid_numbers[1])
    else:
        mayor_grid = np.arange(ylims[0],ylims[1],steps[0])
        minor_grid = np.arange(ylims[0],ylims[1],steps[1])
    
    hax.set_xlim(list(kh_lims))
    hax.set_xlabel("Kh Norm")
    hax.set_xticks(np.linspace(0,1,4))
    hax.set_xticklabels(np.round(np.linspace(0,1,4),decimals=2))
    hax.xaxis.tick_top()
    hax.xaxis.set_label_position("top")
    hax.tick_params("both",labelsize=fontsize)
    hax.set_yticks(mayor_grid)
    hax.set_yticks(minor_grid,minor=True)        
    if dtick==True:
        hax.set_yticklabels(mayor_grid)
    else:
        hax.set_yticklabels([])

    if fill==True:
        hax.fill_betweenx(depth,kh_lims[0],df[kh],**fill_kh_kw)
        
    #Add formations tops
    if formations is not None:
        hax = formations_plot(
            formations,
            depth_ref,
            ylims,
            kh_lims,
            hax,
            config=formations_kw
        )

    # #Add units tops
    if units is not None:
        hax = formations_plot(
            units,
            depth_ref,
            ylims,
            kh_lims,
            hax,
            config=units_kw
        )

    #  #Add Interval Perforated
    if perforations is not None:
        hax = perforations_plot(
            perforations,
            depth_ref,
            ylims,
            kh_lims,
            hax,
            config=perforations_kw
        )
        
    if correlations is not None:
        hax = correlations_plot(
            correlations,
            depth_ref,
            ylims,
            kh_lims,
            hax,
            config=correlations_kw
        )
        
    list_axes.append(hax)
    return hax
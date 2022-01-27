import matplotlib.pyplot as plt 
import matplotlib as mpl
import pandas as pd
import numpy as np
from pydantic import validate_arguments
from typing import Union, Tuple, Dict
from .utils import formations_plot, perforations_plot, correlations_plot


@validate_arguments(config=dict(arbitrary_types_allowed=True))
def cbltrack(
    df:pd.DataFrame,
    cbl:Union[str,list]=None, 
    ylims: Tuple[float,float] = None,
    cbl_lims : Tuple[float,float] = (0,100),
    cbl2_lims : Tuple[float,float] = (0,20),
    dtick: bool=False, 
    ax=None,
    fontsize=8,
    grid_numbers : Tuple[float,float] = (11,51),
    steps: Tuple[float,float] = None,
    legend:bool = True,
    cbl_colormap:str='cool',
    formations: pd.DataFrame = None,
    units: pd.DataFrame = None,
    perforations: pd.DataFrame = None,
    correlations: pd.DataFrame = None,
    formations_kw:Dict={},
    units_kw:Dict={},
    perforations_kw:Dict={},
    correlations_kw:Dict={},
    cbl_kw:dict={},
    cblx5_kw:dict={},
    depth_ref:str='md'
):
    list_axes = []
    cblax=ax or plt.gca()
    cbl2ax=cblax.twiny()
    
    def_cbl_kw = {
    'color': 'black',
    'linestyle':'-',
    'linewidth': 1
    }
    
    for (k,v) in def_cbl_kw.items():
        if k not in cbl_kw:
            cbl_kw[k]=v

    def_cblx5_kw = {
    'color': 'blue',
    'linestyle':'-',
    'linewidth': 2
    }
    
    for (k,v) in def_cblx5_kw.items():
        if k not in cblx5_kw:
            cblx5_kw[k]=v


    depth = df.index if depth_ref=='md' else df[depth_ref]
    if cbl is not None:
        cblax.plot(df[cbl],df.index,**cbl_kw)
        cbl2ax.plot(df[cbl],df.index,**cblx5_kw)
        if isinstance(cbl,str):
            cblax.plot(df[cbl],depth,**cbl_kw)   #Plotting
            cbl2ax.plot(df[cbl],depth,**cblx5_kw)
        elif isinstance(cbl,list):
            cmap = mpl.cm.get_cmap(cbl_colormap,len(cbl))
            for i,g in enumerate(cbl):
                cbl_kw['color']=cmap(i)
                cblax.plot(df[g],depth,**cbl_kw)
                cbl2ax.plot(df[g],depth,**cblx5_kw)
    
    # Set The lims of depth               
    if ylims==None: #Depth Limits
        lims=[depth.min(),depth.max()]

    cblax.set_ylim([lims[1],lims[0]])
        
    #Set the vertical grid spacing
    if steps is None:
        mayor_grid = np.linspace(lims[0],lims[1],grid_numbers[0])
        minor_grid = np.linspace(lims[0],lims[1],grid_numbers[1])
    else:
        mayor_grid = np.arange(lims[0],lims[1],steps[0])
        minor_grid = np.arange(lims[0],lims[1],steps[1])
    
    cblax.set_xlim(list(cbl_lims))
    cbl2ax.set_xlim(list(cbl2_lims))
    cblax.set_xlabel("CBL")
    cbl2ax.set_xlabel("CBLx5")
    cblax.set_xticks(np.linspace(0,100,4))
    cbl2ax.set_xticks(np.linspace(0,20,4))
    cblax.set_xticklabels(np.round(np.linspace(0,100,4),decimals=2))
    cbl2ax.set_xticklabels(np.round(np.linspace(0,20,4),decimals=2))
    cblax.xaxis.tick_top()
    cblax.xaxis.set_label_position("top")
    cblax.tick_params("both",labelsize=fontsize)
    cbl2ax.tick_params("both",labelsize=fontsize)
    cblax.set_yticks(mayor_grid)
    cblax.set_yticks(minor_grid,minor=True)        
    cblax.grid(True,linewidth=1.0)
    cblax.grid(True,which='minor', linewidth=0.5)
    if dtick==True:
        cblax.set_yticklabels(mayor_grid)
    else:
        cblax.set_yticklabels([])
        
    #Add formations tops
    if formations is not None:
        cblax = formations_plot(
            formations,
            depth_ref,
            ylims,
            cbl_lims,
            cblax,
            config=formations_kw
        )

    # #Add units tops
    if units is not None:
        cblax = formations_plot(
            units,
            depth_ref,
            ylims,
            cbl_lims,
            cblax,
            config=units_kw
        )

    #  #Add Interval Perforated
    if perforations is not None:
        cblax = perforations_plot(
            perforations,
            depth_ref,
            ylims,
            cbl_lims,
            cblax,
            config=perforations_kw
        )
        
    if correlations is not None:
        cblax = correlations_plot(
            correlations,
            depth_ref,
            ylims,
            cbl_lims,
            cblax,
            config=correlations_kw
        )
        
    if legend:
        cblax.legend(loc='upper left',fontsize=fontsize)
    list_axes.append(cblax)
    list_axes.append(cbl2ax)
    return list_axes
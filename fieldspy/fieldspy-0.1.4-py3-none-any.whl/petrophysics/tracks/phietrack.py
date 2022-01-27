import matplotlib.pyplot as plt 
import matplotlib as mpl
import pandas as pd
import numpy as np
from typing import Union, Tuple, Dict
from pydantic import validate_arguments
from .utils import formations_plot, perforations_plot, correlations_plot

@validate_arguments(config=dict(arbitrary_types_allowed=True))
def phietrack(
    df: pd.DataFrame,
    phi: Union[str,list] =None, 
    ylims: Tuple[float,float] = None,
    phi_lims: Tuple[float,float] = (0,0.4),
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
    fontsize=8,
    grid_numbers : Tuple[float,float] = (11,51),
    steps: list  = None,
    legend:bool = True,
    phi_colormap: str='Dark2',
    corr_kw={},
    phi_kw:Dict = {},
    depth_ref:str='md'
 ):
    
    list_axes = []
    #get number of curves to build the colormap
    
    pax=ax or plt.gca()
    
    defkwa = {
        'linestyle':'-',
        'linewidth': 1
    }
    for (k,v) in defkwa.items():
        if k not in phi_kw:
            phi_kw[k]=v
    
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
    if phi is not None:
        if isinstance(phi,str):
            pax.plot(df[phi],depth,**phi_kw)   #Plotting
        elif isinstance(phi,list):
            cmap = mpl.cm.get_cmap(phi_colormap,len(phi))
            for i,g in enumerate(phi):
                phi_kw['color']=cmap(i)
                pax.plot(df[g],depth,**phi_kw)
    
    if ylims==None: #Depth Limits
        ylims=[depth.min(),depth.max()]

    pax.set_ylim([ylims[1],ylims[0]])

    #Set the vertical grid spacing
    if steps is None:
        mayor_grid = np.linspace(ylims[0],ylims[1],grid_numbers[0])
        minor_grid = np.linspace(ylims[0],ylims[1],grid_numbers[1])
    else:
        mayor_grid = np.arange(ylims[0],ylims[1],steps[0])
        minor_grid = np.arange(ylims[0],ylims[1],steps[1])
    
    pax.set_xlim(list(phi_lims))
    pax.set_xlabel("phie")
    pax.set_xticks(np.linspace(phi_lims[0],phi_lims[1],4))
    pax.set_xticklabels(np.round(np.linspace(phi_lims[0],phi_lims[1],4),decimals=2))
    pax.xaxis.tick_top()
    pax.xaxis.set_label_position("top")
    pax.tick_params("both",labelsize=fontsize)
    pax.set_yticks(minor_grid,minor=True)
    pax.set_yticks(mayor_grid)       
    pax.grid(True,linewidth=1.0)
    pax.grid(True,which='minor', linewidth=0.5)
    if dtick==True:
        pax.set_yticklabels(mayor_grid)
    else:
        pax.set_yticklabels([])

    #Add formations tops
    if formations is not None:
        pax = formations_plot(
            formations,
            depth_ref,
            ylims,
            phi_lims,
            pax,
            config=formations_kw
        )

    # #Add units tops
    if units is not None:
        pax = formations_plot(
            units,
            depth_ref,
            ylims,
            phi_lims,
            pax,
            config=units_kw
        )

    #  #Add Interval Perforated
    if perforations is not None:
        pax = perforations_plot(
            perforations,
            depth_ref,
            ylims,
            phi_lims,
            pax,
            config=perforations_kw
        )
        
    if correlations is not None:
        pax = correlations_plot(
            correlations,
            depth_ref,
            ylims,
            phi_lims,
            pax,
            config=correlations_kw
        )
        
    if legend:
        pax.legend()
    
    list_axes.append(pax)
    return list_axes
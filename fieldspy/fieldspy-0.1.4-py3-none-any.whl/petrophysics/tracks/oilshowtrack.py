import matplotlib.pyplot as plt
import matplotlib as mpl 
import pandas as pd
import numpy as np
from typing import Union, Tuple, Dict
from pydantic import validate_arguments
from .utils import formations_plot, perforations_plot, correlations_plot

@validate_arguments(config=dict(arbitrary_types_allowed=True))
def oilshowtrack(
    df: pd.DataFrame,
    oilshow: Union[str,list] = None, 
    ylims: Tuple[float,float] = None,
    xlims: Tuple[float,float] = (0,1),
    dtick: bool = False,
    fill: bool = True, 
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
    grid_numbers : list = [11,51],
    steps: list  = None,
    oilshow_colormap: str='summer',
    show_kw={},
    fill_kw={},
    depth_ref:str='md'
):
    list_axes = []
    oax=ax or plt.gca()
    
    defkwa = {
    'color': 'black',
    'linestyle':'-',
    'linewidth': 1
    }
    
    for (k,v) in defkwa.items():
        if k not in show_kw:
            show_kw[k]=v
    

    def_fill_kw = {
    'color': 'darkgreen',
    }    
    for (k,v) in def_fill_kw.items():
        if k not in fill_kw:
            fill_kw[k]=v

    depth = df.index if depth_ref=='md' else df[depth_ref]
    if oilshow is not None:
        if isinstance(oilshow,str):
            oax.plot(df[oilshow],depth,**show_kw)   #Plotting
        elif isinstance(oilshow,list):
            cmap = mpl.cm.get_cmap(oilshow_colormap,len(oilshow))
            for i,g in enumerate(oilshow):
                show_kw['color']=cmap(i)
                oax.plot(df[g],depth,**show_kw)
    
    if ylims==None: #Depth Limits
        ylims=[depth.min(),depth.max()]

    oax.set_ylim([ylims[1],ylims[0]])

    #Set the vertical grid spacing
    if steps is None:
        mayor_grid = np.linspace(ylims[0],ylims[1],grid_numbers[0])
        minor_grid = np.linspace(ylims[0],ylims[1],grid_numbers[1])
    else:
        mayor_grid = np.arange(ylims[0],ylims[1],steps[0])
        minor_grid = np.arange(ylims[0],ylims[1],steps[1])
    
    oax.set_xlim(list(xlims))
    oax.set_xlabel("OilShow")
    oax.set_xticks(np.linspace(0,1,4))
    oax.set_xticklabels(np.round(np.linspace(0,1,4),decimals=2))
    oax.xaxis.tick_top()
    oax.xaxis.set_label_position("top")
    oax.tick_params("both",labelsize=fontsize)
    oax.set_yticks(mayor_grid)
    oax.set_yticks(minor_grid,minor=True)        
    if dtick==True:
        oax.set_yticklabels(mayor_grid,11)
    else:
        oax.set_yticklabels([])

    if fill==True and isinstance(oilshow,str):
        oax.fill_betweenx(depth,0,df[oilshow],**fill_kw)
        
        
    #Add formations tops
    if formations is not None:
        oax = formations_plot(
            formations,
            depth_ref,
            ylims,
            xlims,
            oax,
            config=formations_kw
        )

    # #Add units tops
    if units is not None:
        oax = formations_plot(
            units,
            depth_ref,
            ylims,
            xlims,
            oax,
            config=units_kw
        )

    #  #Add Interval Perforated
    if perforations is not None:
        oax = perforations_plot(
            perforations,
            depth_ref,
            ylims,
            xlims,
            oax,
            config=perforations_kw
        )
        
    if correlations is not None:
        oax = correlations_plot(
            correlations,
            depth_ref,
            ylims,
            xlims,
            oax,
            config=correlations_kw
        )
        
    
    list_axes.append(oax)
    
    return list_axes
    
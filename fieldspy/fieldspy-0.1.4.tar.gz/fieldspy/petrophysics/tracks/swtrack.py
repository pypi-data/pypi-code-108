import matplotlib.pyplot as plt 
import matplotlib as mpl
import pandas as pd
import numpy as np
from typing import Union, Tuple, Dict
from pydantic import validate_arguments
from .utils import formations_plot, perforations_plot, correlations_plot

@validate_arguments(config=dict(arbitrary_types_allowed=True))
def swtrack(
    df: pd.DataFrame,
    sw: Union[str,list] =None, 
    ylims: Tuple[float,float] = None,
    sw_lims: Tuple[float,float] = (0,1),
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
    sw_colormap: str='winter',
    corr_kw={},
    sw_kw:Dict = {},
    depth_ref:str='md',
    fill:bool = False
 ):
    
    list_axes = []
    #get number of curves to build the colormap
    
    pax=ax or plt.gca()
    
    defkwa = {
    'linestyle':'-',
    'linewidth': 1
    }
    
    for (k,v) in defkwa.items():
        if k not in sw_kw:
            sw_kw[k]=v
            
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
           
    if sw is not None:
        if isinstance(sw,str):
            pax.plot(df[sw],depth,**sw_kw)   #Plotting
        elif isinstance(sw,list):
            cmap = mpl.cm.get_cmap(sw_colormap,len(sw))
            for i,g in enumerate(sw):
                sw_kw['color']=cmap(i)
                pax.plot(df[g],depth,**sw_kw)
    
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
    
    pax.set_xlim(list(sw_lims))
    pax.set_xlabel("sw")
    pax.set_xticks(np.linspace(sw_lims[0],sw_lims[1],4))
    pax.set_xticklabels(np.round(np.linspace(sw_lims[0],sw_lims[1],4),decimals=2))
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
        
    if fill==True and isinstance(sw,str):
       # cmap=mpl.cm.get_cmap('YlOrBr',128)
        cmap=mpl.colors.LinearSegmentedColormap.from_list('sw',
          [(52/256,194/256,90/256),(52/256,187/256,194/256),(52/256,99/256,194/256)],N=256)
        df_filtered = df.loc[(depth>=ylims[0])&(depth<=ylims[1]),sw]
        depth_f = df_filtered.index if depth_ref=='md' else df_filtered[depth_ref]
        for i in range(0,df_filtered.shape[0]-1):
            pax.fill_betweenx([depth_f[i],depth_f[i+1]],
                              [df_filtered.iloc[i],df_filtered.iloc[i+1]],
                              1,color=cmap(df_filtered.iloc[i+1]))

    #Add formations tops
    if formations is not None:
        pax = formations_plot(
            formations,
            depth_ref,
            ylims,
            sw_lims,
            pax,
            config=formations_kw
        )

    # #Add units tops
    if units is not None:
        pax = formations_plot(
            units,
            depth_ref,
            ylims,
            sw_lims,
            pax,
            config=units_kw
        )

    #  #Add Interval Perforated
    if perforations is not None:
        pax = perforations_plot(
            perforations,
            depth_ref,
            ylims,
            sw_lims,
            pax,
            config=perforations_kw
        )
        
    if correlations is not None:
        pax = correlations_plot(
            correlations,
            depth_ref,
            ylims,
            sw_lims,
            pax,
            config=correlations_kw
        )
        
    if legend:
        pax.legend()
    
    list_axes.append(pax)
    return list_axes
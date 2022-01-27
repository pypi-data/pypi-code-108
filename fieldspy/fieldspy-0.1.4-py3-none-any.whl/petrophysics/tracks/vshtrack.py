import matplotlib.pyplot as plt 
import matplotlib as mpl
import pandas as pd
import numpy as np
from typing import Union, Tuple, Dict
from pydantic import validate_arguments
from .utils import formations_plot, perforations_plot, correlations_plot

@validate_arguments(config=dict(arbitrary_types_allowed=True))
def vshtrack(
    df: pd.DataFrame,
    vsh: Union[str,list] =None, 
    ylims: Tuple[float,float] = None,
    vsh_lims: Tuple[float,float] = (0,1),
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
    fill:bool = True,
    fontsize=8,
    grid_numbers : Tuple[float,float] = (11,51),
    steps: list  = None,
    legend:bool = True,
    vsh_colormap: str='Dark2',
    corr_kw={},
    vsh_kw:Dict = {},
    depth_ref:str='md'
 ):
    
    list_axes = []
    #get number of curves to build the colormap
    
    pax=ax or plt.gca()
    
    defkwa = {
        'linestyle':'-',
        'linewidth': 1,
        'color': 'k'
    }
    for (k,v) in defkwa.items():
        if k not in vsh_kw:
            vsh_kw[k]=v

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
           
    if vsh is not None:
        if isinstance(vsh,str):
            pax.plot(df[vsh],depth,**vsh_kw)   #Plotting
        elif isinstance(vsh,list):
            cmap = mpl.cm.get_cmap(vsh_colormap,len(vsh))
            for i,g in enumerate(vsh):
                vsh_kw['color']=cmap(i)
                pax.plot(df[g],depth,**vsh_kw)
    
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
    
    pax.set_xlim(list(vsh_lims))
    pax.set_xlabel("vsh")
    pax.set_xticks(np.linspace(vsh_lims[0],vsh_lims[1],4))
    pax.set_xticklabels(np.round(np.linspace(vsh_lims[0],vsh_lims[1],4),decimals=2))
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

    if fill==True and isinstance(vsh,str):
       # cmap=mpl.cm.get_cmap('YlOrBr',128)
        cmap=mpl.colors.LinearSegmentedColormap.from_list('vsh',
          [(252/256,210/256,23/256),(66/256,59/256,20/256),(41/256,29/256,13/256)],N=256)
        df_filtered = df.loc[(depth>=ylims[0])&(depth<=ylims[1]),vsh]
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
            vsh_lims,
            pax,
            config=formations_kw
        )

    # #Add units tops
    if units is not None:
        pax = formations_plot(
            units,
            depth_ref,
            ylims,
            vsh_lims,
            pax,
            config=units_kw
        )

    #  #Add Interval Perforated
    if perforations is not None:
        pax = perforations_plot(
            perforations,
            depth_ref,
            ylims,
            vsh_lims,
            pax,
            config=perforations_kw
        )
        
    if correlations is not None:
        pax = correlations_plot(
            correlations,
            depth_ref,
            ylims,
            vsh_lims,
            pax,
            config=correlations_kw
        )
        
    if legend:
        pax.legend()
    
    list_axes.append(pax)
    return list_axes
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
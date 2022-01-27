import matplotlib.pyplot as plt 
import matplotlib as mpl
import pandas as pd
import numpy as np
from typing import Union, Tuple, Dict
from pydantic import validate_arguments
from .utils import formations_plot, perforations_plot, correlations_plot

@validate_arguments(config=dict(arbitrary_types_allowed=True))
def dntrack(
    df: pd.DataFrame,
    rho: Union[str,list] = None,
    ntr: Union[str,list] = None,
    ylims: Tuple[float,float] = None,
    rho_lims: Tuple[float,float] = (1.9,2.9),
    ntr_lims:Tuple[float,float] = (0.45,-0.15),
    lime: bool = False,
    dtick: bool =False,
    fill: bool =True,
    fontsize: int=8,
    grid_numbers : list = [11,51],
    steps: list  = None,
    formations: pd.DataFrame = None,
    units: pd.DataFrame = None,
    perforations: pd.DataFrame = None,
    correlations: pd.DataFrame = None,
    formations_kw:Dict={},
    units_kw:Dict={},
    perforations_kw:Dict={},
    correlations_kw:Dict={},
    rho_kw:Dict={},
    ntr_kw:Dict={},
    ax=None,
    rho_colormap:str='hot',
    ntr_colormap:str='winter',
    depth_ref:str='md',
    legend:bool=False,
):
    list_axes = []
    #Set Axes
    dax=ax or plt.gca()
    nax=dax.twiny()

    # Default kwargs for rho and ntr lines
    def_rho_kw = {
    'color': 'darkred',
    'linestyle':'-',
    'linewidth': 2
    }
    for (k,v) in def_rho_kw.items():
        if k not in rho_kw:
            rho_kw[k]=v

    def_ntr_kw = {
    'color': 'darkblue',
    'linestyle':'-',
    'linewidth': 1
    }    
    for (k,v) in def_ntr_kw.items():
        if k not in ntr_kw:
            ntr_kw[k]=v

  
    #Set type of sync between Neutron GammaRay
    if lime==True:
        d=2.71
    else:
        d=2.65

    m=(d-1.9)/(0-0.45)
    b=-m*0.45+1.9
    rholim=-0.15*m+b

    #Set the vertical grid spacing
    if steps is None:
        mayor_grid = np.linspace(ylims[0],ylims[1],grid_numbers[0])
        minor_grid = np.linspace(ylims[0],ylims[1],grid_numbers[1])
    else:
        mayor_grid = np.arange(ylims[0],ylims[1],steps[0])
        minor_grid = np.arange(ylims[0],ylims[1],steps[1])
    
    depth = df.index if depth_ref=='md' else df[depth_ref]
    #Set Density Axes
    if rho is not None:
        if isinstance(rho,str):
            dax.plot(df[rho],depth,**rho_kw)   #Plotting
        elif isinstance(rho,list):
            cmap = mpl.cm.get_cmap(rho_colormap,len(rho))
            for i,r in enumerate(rho):
                rho_kw['color']=cmap(i)
                dax.plot(df[r],depth,**rho_kw)

        #Set the gridding and ticks
        dax.set_xlabel("Density [g/cc]")
        dax.set_xticks(np.linspace(1.9,rholim,4))
        dax.set_xlim([rho_lims[0],rholim])
        dax.tick_params("both",labelsize=fontsize)
        dax.grid(True,linewidth=1.0)
        dax.grid(True,which='minor', linewidth=0.5)
        dax.set_yticks(minor_grid,minor=True)
        dax.set_yticks(mayor_grid)
        if dtick==True:
            dax.set_yticklabels(mayor_grid)
        else:
            dax.set_yticklabels([])

    
    #Set neutron axes
    if ntr is not None:
        if isinstance(ntr,str):
            nax.plot(df[ntr],depth,**ntr_kw)   #Plotting
        elif isinstance(ntr,list):
            cmap = mpl.cm.get_cmap(ntr_colormap,len(ntr))
            for i,r in enumerate(ntr):
                ntr_kw['color']=cmap(i)
                nax.plot(df[r],depth,**ntr_kw)
    
        nax.set_xlabel("Neutron [v/v]")
        nax.set_xticks(np.linspace(0.45,-0.15,4))
        nax.set_xlim(ntr_lims)
        nax.tick_params("both",labelsize=fontsize)
        nax.set_yticks(minor_grid,minor=True)
        nax.set_yticks(mayor_grid)
        if dtick==True:
            nax.set_yticklabels(mayor_grid)
        else:
            nax.set_yticklabels([])


    if ylims==None: #Depth Limits
        ylims=[depth.min(),depth.max()]
        
    dax.set_ylim([ylims[1],ylims[0]])
    #Convert the Neutron values to Density Values in order to fill the cross Density-Neutron
    #When the track is callibrated for sandstone use m=-1.666667 and b=2.65
    #When the track is callibrated for limestone use m=-1.8 and b=2.71
    if (ntr is not None) & (rho is not None):
        NtrTorho=df[ntr]*m+b
        ntrrho=NtrTorho.values.ravel()

        if fill==True:
            dax.fill_betweenx(depth,df[rho],ntrrho,where=(df[rho] < ntrrho),color="red")   
            
    #Add formations tops
    if formations is not None:
        dax = formations_plot(
            formations,
            depth_ref,
            ylims,
            rho_lims,
            dax,
            config=formations_kw
        )

    # #Add units tops
    if units is not None:
        dax = formations_plot(
            units,
            depth_ref,
            ylims,
            rho_lims,
            dax,
            config=units_kw
        )

    #  #Add Interval Perforated
    if perforations is not None:
        dax = perforations_plot(
            perforations,
            depth_ref,
            ylims,
            rho_lims,
            dax,
            config=perforations_kw
        )
        
    if correlations is not None:
        dax = correlations_plot(
            correlations,
            depth_ref,
            ylims,
            rho_lims,
            dax,
            config=correlations_kw
        )
        
    if legend:
        dax.legend(loc='upper left',fontsize=fontsize)
    
    list_axes.append(dax)
    list_axes.append(nax)
    return list_axes
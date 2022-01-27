import matplotlib.pyplot as plt 
import matplotlib as mpl
import pandas as pd
import numpy as np
from typing import List,Union, Tuple, Dict
from pydantic import validate_arguments
from .utils import formations_plot, perforations_plot, correlations_plot


@validate_arguments(config=dict(arbitrary_types_allowed=True))
def caltrack(
    df: pd.DataFrame,
    cali: Union[str,list] = None, 
    bit: Union[str,list] = None, 
    ylims: Tuple[float,float] =None,
    cal_lims:Tuple[float,float]=(5,20),
    dtick:bool=False,
    fill:bool=False,
    fontsize: int=8,
    grid_numbers : Tuple[float,float] = (11,51),
    steps: Tuple[float,float]  = None,
    ax=None,
    formations: pd.DataFrame = None,
    units: pd.DataFrame = None,
    perforations: pd.DataFrame = None,
    correlations: pd.DataFrame = None,
    formations_kw:Dict={},
    units_kw:Dict={},
    perforations_kw:Dict={},
    correlations_kw:Dict={},
    cal_kw:Dict={},
    bit_kw:Dict={},
    depth_ref:str='md',
    cal_colormap: str='winter',
    bit_colormap: str='bone'
):
    list_axes = []
    cal=ax or plt.gca()
    
    def_cal_kw = {
    'color': 'black',
    'linestyle':'-',
    'linewidth': 1
    }
    
    for (k,v) in def_cal_kw.items():
        if k not in cal_kw:
            cal_kw[k]=v

    def_bit_kw = {
    'color': 'darkred',
    'linestyle':'--',
    'linewidth': 2
    }    
    for (k,v) in def_bit_kw.items():
        if k not in bit_kw:
            bit_kw[k]=v
            
    #Set ylims
    if ylims==None: #Depth Limits
        ylims=[df.index.min(),df.index.max()]

    cal.set_ylim([ylims[1],ylims[0]])
        
    #Set the vertical grid spacing
    if steps is None:
        mayor_grid = np.linspace(ylims[0],ylims[1],grid_numbers[0])
        minor_grid = np.linspace(ylims[0],ylims[1],grid_numbers[1])
    else:
        mayor_grid = np.arange(ylims[0],ylims[1],steps[0])
        minor_grid = np.arange(ylims[0],ylims[1],steps[1])
    
    depth = df.index if depth_ref=='md' else df[depth_ref] 

    if cali is not None:
        if isinstance(cali,str):
            cal.plot(df[cali],depth,**cal_kw)   #Plotting
        elif isinstance(cali,list):
            cmap = mpl.cm.get_cmap(cal_colormap,len(cal))
            for i,c in enumerate(cali):
                cal_kw['color']=cmap(i)
                cal.plot(df[c],depth,**cal_kw)
        
    if bit is not None:
        if isinstance(bit,str):
            cal.plot(df[bit],depth,**cal_kw)   #Plotting
        elif isinstance(cali,list):
            cmap = mpl.cm.get_cmap(bit_colormap,len(cal))
            for i,c in enumerate(bit):
                cal_kw['color']=cmap(i)
                cal.plot(df[c],depth,**cal_kw)
    

    cal.set_xlim(cal_lims)
    cal.set_xlabel("Caliper [in]")
    cal.set_xticks(np.linspace(cal_lims[0],cal_lims[1],4))
    cal.set_xticklabels(np.round(np.linspace(cal_lims[0],cal_lims[1],4),decimals=1))
    cal.xaxis.tick_top()
    cal.xaxis.set_label_position("top")
    cal.tick_params("both",labelsize=fontsize)
    cal.set_yticks(mayor_grid)
    cal.set_yticks(minor_grid,minor=True)       
    if dtick==True:
        cal.set_yticklabels(mayor_grid)
    else:
        cal.set_yticklabels([])
        
    if fill==True:
        cal.fill_betweenx(depth,df[cali],df[bit],where=(df[cali] > df[bit]),color="orange")
        cal.fill_betweenx(depth,df[cali],df[bit],where=(df[cali]< df[bit]),color="gray")
        
    #Add formations tops
    if formations is not None:
        cal = formations_plot(
            formations,
            depth_ref,
            ylims,
            cal_lims,
            cal,
            config=formations_kw
        )

    # #Add units tops
    if units is not None:
        cal = formations_plot(
            units,
            depth_ref,
            ylims,
            cal_lims,
            cal,
            config=units_kw
        )

    #  #Add Interval Perforated
    if perforations is not None:
        cal = perforations_plot(
            perforations,
            depth_ref,
            ylims,
            cal_lims,
            cal,
            config=perforations_kw
        )
        
    if correlations is not None:
        cal = correlations_plot(
            correlations,
            depth_ref,
            ylims,
            cal_lims,
            cal,
            config=correlations_kw
        )
        
    list_axes.append(cal)
    return list_axes
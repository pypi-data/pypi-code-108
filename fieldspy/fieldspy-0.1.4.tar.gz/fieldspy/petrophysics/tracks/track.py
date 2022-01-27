import matplotlib.pyplot as plt 
import matplotlib as mpl
import pandas as pd
import numpy as np
from typing import Union, Tuple, Dict
from pydantic import validate_arguments
from .utils import formations_plot, perforations_plot, correlations_plot

@validate_arguments(config=dict(arbitrary_types_allowed=True))
def track(
    df: pd.DataFrame,
    curves: Union[str,list] = None,
    ylims: Tuple[float,float] = None, 
    xlims: Tuple[float,float] = None,
    dtick: bool = False,
    scale: str ='linear',
    curvetitle: str ='Track', 
    colormap: str='plasma',
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
    grid:bool = True,
    track_kw=[],
    depth_ref:str='md',
):
    list_axes = []
    #get number of curves to build the colormap
    n_curves = len(curves)
    cmap = mpl.cm.get_cmap(colormap,n_curves)

    tax=ax or plt.gca()
    
    defkwa = {
    'color': 'black',
    'linestyle':'-',
    'linewidth': 1
    }
    
    depth = df.index if depth_ref=='md' else df[depth_ref]
    #Plot main Lines
    if curves is not None:
        for i,g in enumerate(curves):
            if len(track_kw)<i+1:
                track_kw.append(defkwa)
                track_kw[i]['color']=cmap(i)
            for (k,v) in defkwa.items():
                if k not in track_kw[i]:
                    track_kw[i][k]=v

            scatter = track_kw[i].pop('scatter',False)
            if scatter:
                tax.scatter(df[g],depth,label=g,**track_kw[i])
            else:
                tax.plot(df[g],depth,label=g,**track_kw[i])
    
    if ylims==None: #Depth Limits
        ylims=[depth.min(),depth.max()]

    tax.set_ylim([ylims[1],ylims[0]])

    #Set the vertical grid spacing
    if steps is None:
        mayor_grid = np.linspace(ylims[0],ylims[1],grid_numbers[0])
        minor_grid = np.linspace(ylims[0],ylims[1],grid_numbers[1])
    else:
        mayor_grid = np.arange(ylims[0],ylims[1],steps[0])
        minor_grid = np.arange(ylims[0],ylims[1],steps[1])


    tax.set_xlabel(curvetitle)
    tax.set_xscale(scale)
    if xlims==None: 
        xlims=(0,1)

    tax.set_xlim(list(xlims))

    if scale=='log':
        ticks=np.round(np.power(10,np.linspace(np.log10(xlims[0]),np.log10(xlims[1]),int(np.log10(xlims[1]/xlims[0])+1))),decimals=1)
    else:
        ticks = np.round(np.linspace(xlims[0],xlims[1],4),decimals=1)

    tax.set_xticks(ticks)
    tax.set_xticklabels(ticks)
    tax.xaxis.tick_top()
    tax.xaxis.set_label_position("top")
    tax.tick_params("both",labelsize=fontsize)
    tax.set_yticks(mayor_grid)
    tax.set_yticks(minor_grid,minor=True)    

    if grid == True:
        tax.grid(True,linewidth=1.0)
        tax.grid(True,which='minor', linewidth=0.5)
        
    if dtick==True:
        tax.set_yticklabels(np.linspace(ylims[0],ylims[1],11))
    else:
        tax.set_yticklabels([])
    if legend:
        tax.legend() 
        
    if formations is not None:
        tax = formations_plot(
            formations,
            depth_ref,
            ylims,
            xlims,
            tax,
            config=formations_kw
        )

    # #Add units tops
    if units is not None:
        tax = formations_plot(
            units,
            depth_ref,
            ylims,
            xlims,
            tax,
            config=units_kw
        )

    #  #Add Interval Perforated
    if perforations is not None:
        tax = perforations_plot(
            perforations,
            depth_ref,
            ylims,
            xlims,
            tax,
            config=perforations_kw
        )
        
    if correlations is not None:
        tax = correlations_plot(
            correlations,
            depth_ref,
            ylims,
            xlims,
            tax,
            config=correlations_kw
        )
 
    list_axes.append(tax)
    
    return list_axes
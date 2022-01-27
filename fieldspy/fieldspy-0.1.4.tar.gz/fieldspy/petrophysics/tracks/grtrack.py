import numpy as np
import pandas as pd
import matplotlib.pyplot as plt 
import matplotlib as mpl
from typing import Union, Tuple, Dict
from pydantic import validate_arguments
from .utils import formations_plot, perforations_plot, correlations_plot

@validate_arguments(config=dict(arbitrary_types_allowed=True))
def grtrack(
    df: pd.DataFrame,
    gr: Union[str,list] = None,
    sp: Union[str,list] = None,
    ylims: Tuple[float,float] = None,
    gr_lims: Tuple[float,float] = (0,200),
    sp_lims:list = None,
    gr_sand_shale: pd.DataFrame = None,
    fontsize: int = 8,
    dtick: bool = True,
    grid_numbers : Tuple[float,float] = (11,51),
    steps: Tuple[float,float]  = None,
    gr_steps:int=4,
    legend:bool = False,
    gr_kw:Dict={},
    sp_kw:Dict={},
    formations: pd.DataFrame = None,
    units: pd.DataFrame = None,
    perforations: pd.DataFrame = None,
    correlations: pd.DataFrame = None,
    formations_kw:Dict={},
    units_kw:Dict={},
    perforations_kw:Dict={},
    correlations_kw:Dict={},
    gr_sand_kw:Dict={},
    gr_shale_kw:Dict={}, 
    ax=None,
    depth_ref:str='md',
    gr_colormap: str='autumn',
    sp_colormap: str='gray',
    sp_norm:bool = False,
    sp_baseline:float = 0,
    sp_fill:bool = False
):

    list_axes = []
    #Create the Axex
    grax= ax or plt.gca()
    
    
    # Default kwargs for all Lines
    def_gr_kw = {
    'color': 'darkred',
    'linestyle':'-',
    'linewidth': 2
    }
    for (k,v) in def_gr_kw.items():
        if k not in gr_kw:
            gr_kw[k]=v

    def_sp_kw = {
    'color': 'darkblue',
    'linestyle':'-',
    'linewidth': 1,
    'sp_left_color':(0.9,0.57,0.2,0.2),
    'sp_right_color':(0.28,0.9,0.79,0.2)
    }    
    for (k,v) in def_sp_kw.items():
        if k not in sp_kw:
            sp_kw[k]=v
    
    
    def_gr_sand_kw = {
    'color': 'gold',
    'linestyle':'--',
    'linewidth': 2
    }    
    for (k,v) in def_gr_sand_kw.items():
        if k not in gr_sand_kw:
            gr_sand_kw[k]=v

    def_gr_shale_kw = {
    'color': 'gray',
    'linestyle':'--',
    'linewidth': 2
    }    
    for (k,v) in def_gr_shale_kw.items():
        if k not in gr_shale_kw:
            gr_shale_kw[k]=v

 ## Plot the Main Curves      
    #If GammaRay Provided
    depth = df.index if depth_ref=='md' else df[depth_ref]   
    if gr is not None:
        if isinstance(gr,str):
            grax.plot(df[gr],depth,**gr_kw)   #Plotting
        elif isinstance(gr,list):
            cmap = mpl.cm.get_cmap(gr_colormap,len(gr))
            for i,g in enumerate(gr):
                gr_kw['color']=cmap(i)
                grax.plot(df[g],depth,**gr_kw)
        
     #If sp provided   
    if sp is not None:
        spax=grax.twiny()
        if isinstance(sp,str):
            sp_left_color = sp_kw.pop('sp_left_color',(0.9,0.57,0.2,0.2))
            sp_right_color = sp_kw.pop('sp_right_color',(0.28,0.9,0.79,0.2))
            sp_filter = df.loc[df[sp]>-999,sp]
            sp_mean = sp_filter.mean() if sp_norm else sp_baseline
            sp_norm = sp_filter - sp_mean
            sp_min = sp_norm.min()
            sp_max = sp_norm.max()
            spax.plot(df[sp]-sp_mean,depth,**sp_kw)   #Plotting
            if sp_fill==True:
                spax.fill_betweenx(depth,df[sp]-sp_mean,0,where=(df[sp]-sp_mean < 0),color=sp_left_color)
                spax.fill_betweenx(depth,df[sp]-sp_mean,0,where=(df[sp]-sp_mean > 0),color=sp_right_color)

        elif isinstance(sp,list):
            cmap = mpl.cm.get_cmap(sp_colormap,len(sp))
            for i,s in enumerate(sp):
                sp_kw['color']=cmap(i)
                sp_filter = df.loc[df[s]>-999,s]
                sp_mean = sp_filter.mean() if sp_norm else 0
                sp_norm = sp_filter - sp_mean
                sp_min = sp_norm.min()
                sp_max = sp_norm.max()
                spax.plot(df[s]-sp_mean,depth,**sp_kw)

        spax.xaxis.set_label_position("bottom")
        spax.xaxis.tick_bottom()
        spax.set_xlabel('Sp')
       
        if sp_lims is None:
            spax.set_xlim([sp_min,sp_max])
            spax.set_xticks(np.linspace(sp_min,sp_max,4))
 
        else:
            spax.set_xlim(sp_lims)
            spax.set_xticks(np.linspace(sp_lims[0],sp_lims[1],5))

        list_axes.append(spax)
         
    # Set The ylims of depth    
    grax.set_xlim(list(gr_lims))           
    if ylims==None: #Depth Limits
        ylims=(depth.min(),depth.max())

    grax.set_ylim([ylims[1],ylims[0]])

    #Set the vertical grid spacing
    if steps is None:
        mayor_grid = np.linspace(ylims[0],ylims[1],grid_numbers[0])
        minor_grid = np.linspace(ylims[0],ylims[1],grid_numbers[1])
    else:
        if depth_ref=='tvdss':
            mayor_grid = np.arange(ylims[1],ylims[0],steps[0])
            minor_grid = np.arange(ylims[1],ylims[0],steps[1])
        else:
            mayor_grid = np.arange(ylims[0],ylims[1],steps[0])
            minor_grid = np.arange(ylims[0],ylims[1],steps[1])

    #Set Gridding and ticks
    grax.set_xlabel('GammaRay')
    grax.tick_params("both",labelsize=fontsize)
    grax.grid(True,linewidth=1.0)
    grax.grid(True,which='minor', linewidth=0.5)
    plt.setp(grax.get_yticklabels(),visible=True)
    grax.set_yticks(minor_grid,minor=True)
    grax.set_yticks(mayor_grid)
    if dtick==True:
        grax.set_yticklabels(mayor_grid)
    else:
        grax.set_yticklabels([])
    grax.set_xticks(np.linspace(gr_lims[0],gr_lims[1],gr_steps))
    grax.xaxis.set_label_position("top")
    grax.xaxis.tick_top()
    
    #Add formations tops
    if formations is not None:
        grax = formations_plot(
            formations,
            depth_ref,
            ylims,
            gr_lims,
            grax,
            config=formations_kw
        )

    # #Add units tops
    if units is not None:
        grax = formations_plot(
            units,
            depth_ref,
            ylims,
            gr_lims,
            grax,
            config=units_kw
        )

    #  #Add Interval Perforated
    if perforations is not None:
        grax = perforations_plot(
            perforations,
            depth_ref,
            ylims,
            gr_lims,
            grax,
            config=perforations_kw
        )
        
    if correlations is not None:
        grax = correlations_plot(
            correlations,
            depth_ref,
            ylims,
            gr_lims,
            grax,
            config=correlations_kw
        )

    #Add Sand Gamma Ray line      
    if gr_sand_shale is not None:
        for i in gr_sand_shale.iterrows():
            try:
                grax.vlines(i[1]['gr_sand'],i[1][f'{depth_ref}_top'],i[1][f'{depth_ref}_bottom'],**gr_sand_kw)
            except:
                pass
            
            try:
                grax.vlines(i[1]['gr_shale'],i[1][f'{depth_ref}_top'],i[1][f'{depth_ref}_bottom'],**gr_shale_kw)
            except:
                pass
             
    if legend:
        grax.legend() 
    
    list_axes.append(grax)
    
    return list_axes
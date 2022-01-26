# -*- coding: utf-8 -*-
"""
Created on Wed Jun  9 17:39:13 2021

@author: Zineb Bouaoudate
"""
import numpy as np
import matplotlib.pyplot as plt
import h5py as hp
import os, sys, glob

#=============================================================================
from pythermica import Thermica
from pathlib import Path


plot_style = {
    "axes.grid": True,
    "axes.grid.axis": 'y',
    "axes.labelsize": 12,
    "axes.titlesize": 16,
    "figure.autolayout": True,
    "figure.dpi": 300,
    "figure.figsize": [6.4, 4.8],
    "font.family": "STIXGeneral",
    "grid.alpha": 0.5,
    "grid.color": "grey",
    "grid.linestyle": "dotted",
    "grid.linewidth": 0.8,
    "image.aspect": "auto",
    "image.cmap": "plasma",
    "image.interpolation": "nearest",
    "image.origin": "lower",
    "lines.linewidth": 1,
    "lines.markersize": 5,
    "mathtext.fontset": "stix",
    "savefig.format": "eps",
    "xtick.labelsize": 10,
    "xtick.minor.visible": True,
    "xtick.top": True,
    "ytick.labelsize": 10,
    "ytick.minor.visible": True,
    "ytick.right": True
}

plt.rcParams.update(plot_style)

def figure_over_nodes(therm_results,
                      temperatures,
                      times,
                      n_orbits,
                      path_list, case_names,
                      nodes_to_process = ["/Powercard P60", "/Printed Circuits",
                     "/Transponders (1)", "/Batteries"] ,
                      path_root = "./",
                      name_yaxis="Temperature",
                      filename_prefix=""):
    
    """
    generate a bunch of figures to compare simulations
    """
    
    n_path = len(path_list)
    period = times[0][-1] / n_orbits
    
    nodes_processed = []

    for idx_node, node_label in enumerate(therm_results[0].names_unique):
        """looping over all the object names, hopping they are the same between the different cases"""
        
        if node_label in nodes_to_process:
            
            nodes_processed.append(nodes_to_process)
            
            temperatures_node_average = []  # n_path lists of node-averaged temperature corresponding to n_path cases
            temperature_max = []  # maximum temperatures corresponding to n_path cases
            temperature_min = []  # minimum temperatures corresponding to n_path cases
            temperature_time_average = []  # time-averaged temperatures corresponding to n_path cases
            
            plt.figure(figsize=(10,4))
            
            for idx_path in range(n_path):
                
                index_nodes = []
                
                for i, node in enumerate(therm_results[idx_path].nodes_value):
                    if node in  therm_results[idx_path].nodes_per_names[idx_node]:
                        index_nodes.append(i)
                        
                index_nodes = np.array(index_nodes)  # index of nodes corresponding to label
                # print("the nodes for "+node_label+" are :", nodes_list_for_label)
                # print("the index nodes are :", index_nodes)
                    
                _max_temp = []
                _min_temp = []
                _average_temp = []
                for _temp in temperatures[idx_path].T[:, index_nodes]:
                    _max_temp.append(max(_temp))
                    _min_temp.append(min(_temp))
                    _average_temp.append(np.mean(_temp))
                temperatures_node_average.append(_average_temp)
                temperature_max.append(max(_max_temp))
                temperature_min.append(min(_min_temp))
                temperature_time_average.append(np.mean(_average_temp))
                
            
            
                line, = plt.plot(times[idx_path], temperatures_node_average[idx_path],
                         label=case_names[idx_path] + f" (max= {temperature_max[idx_path]:2.2f}, min=" +
                               f"{temperature_min[idx_path]:2.2f}, average=" +
                               f"{temperature_time_average[idx_path]:2.2f} over {len(index_nodes)} nodes)")
                
                for _temp in temperatures[idx_path].T[:, index_nodes].T:
                    plt.plot(times[idx_path], _temp, color=line.get_color(), alpha=0.3)
                    
                plt.hlines(temperature_time_average[idx_path],
                           times[idx_path][0],
                           times[idx_path][-1],
                           colors=line.get_color())
                
            thermobject = therm_results[0]
            
            solarFlux, time_sf = thermobject.read_solarflux("Results", "Direct Solar", "Flux")
            solarFlux = solarFlux.mean(axis=0)
            solarFlux[solarFlux>0] =  max(temperature_max)
            solarFlux[solarFlux<=0] = min(temperature_min)
            
            plt.fill_between(time_sf,
                             solarFlux,
                             min(temperature_min),
                             color="y", alpha=0.5, zorder=-999,
                             linewidth=0)
            
            plt.vlines([period*k for k in range(1, n_orbits+1)], max(temperature_max), min(temperature_min), linestyles="--")
            plt.title(node_label[1:])
            plt.xlabel('Time (hr)')
            plt.ylabel(name_yaxis)
            plt.legend(loc="upper center", bbox_to_anchor=(0.5, -0.15))
            
            plt.tight_layout()
            
            figure_name = filename_prefix + node_label[1:] + '.png'  # droping the first char which is "/"
            
            p_root = Path(path_root)
            p_img_root = p_root / "images"
            if not p_img_root.exists():
                p_img_root.mkdir()
                
            plt.savefig(p_img_root / figure_name)
            plt.close()

        
        for node in nodes_to_process:
            if node not in nodes_processed:
                print(f"WARNING ! the node {node} has not been processed")


def totalInternalDissipation(therm_results,
                      internal_dissipations,
                      time,
                      n_orbits,
                      path_list, case_names,
                      nodes_to_process = None ,
                      path_root = "./",
                      filename_prefix="Total_IQ"):
    
    """
    generate a bunch of figures to compare simulations
    """
    
    n_path = len(path_list)
    period = time[0][-1] / n_orbits
    
    
    plt.figure(figsize=(10,4))
    
    
    for idx_path in range(n_path):
        
        total_IQ = np.zeros_like(time[idx_path])
        
        if nodes_to_process is None :
            list_to_process = therm_results[idx_path].names_unique
        else :
            list_to_process = nodes_to_process
        

        for idx_node, node_label in enumerate(therm_results[idx_path].names_unique):
            """looping over all the object names, hopping they are the same between the different cases"""
            
            if node_label in list_to_process:

                index_nodes = []
                
                for i, node in enumerate(therm_results[idx_path].nodes_value):
                    if node in  therm_results[idx_path].nodes_per_names[idx_node]:
                        index_nodes.append(i)
                        
                index_nodes = np.array(index_nodes)  # index of nodes corresponding to label
                # print("the nodes for "+node_label+" are :", nodes_list_for_label)
                # print("the index nodes are :", index_nodes)
                    

                for _IQ in internal_dissipations[idx_path][index_nodes, :]:
                    
                    total_IQ += _IQ
                    

           
            
        line, = plt.plot(time[idx_path], total_IQ,
                 label=case_names[idx_path],
                 )
        
        
    ax = plt.gca()
    
    for k in range(1, n_orbits+1):
        ax.axvline(period*k, ls="--")
    
    titletext = "Total internal dissipation power"
    
    if nodes_to_process is not None:
        titletext += "\n"
        for nodename in nodes_to_process:
            titletext += nodename + ", "
                
    plt.title(titletext)    
    plt.xlabel('Time (hr)')
    plt.ylabel("internal dissipations [W]")
    plt.legend(loc="upper center", bbox_to_anchor=(0.5, -0.15))
    
    p_root = Path(path_root)
    p_img_root = p_root / "images"
    if not p_img_root.exists():
        p_img_root.mkdir()

    figure_name = filename_prefix + '.png'

    plt.savefig(p_img_root / figure_name)
    plt.close()
    

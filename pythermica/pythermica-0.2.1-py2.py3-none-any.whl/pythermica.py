# -*- coding: utf-8 -*-
# @Author: Antoine Tavant
# @Date:   2021-12-09 19:11:50
# @Last Modified by:   Antoine Tavant
# @Last Modified time: 2022-01-24 16:02:11
# the main script, mainly to test and develop the package

from fileinput import filename
import numpy as np
import matplotlib.pyplot as plt
import h5py as hp
import os, sys, glob
from pathlib import Path

#=============================================================================

class Thermica():
    """Main class to analyse the simulation results"""

    def __init__(self, path, verbose=True):
        """Init the class"""
        
        if type(path) is Path:
            self.path = path  #: path were the simulation results are stored
        elif type(path) is str:
            self.path = Path(path)  #: path were the simulation results are stored
        else:
            raise RuntimeError("path Not with rigth Type")
        self.names_unique = []  #: list of the names used to label the nodes
        self.nodes_per_names = [[]]  #: list of the lists of the nodes for each unique names
        self.nodes_value = np.array([])  #: list of the node value, order in the same way as the temperatures
        self.verbose = verbose
        
        if self.verbose:
            print("Initializing Thermica at path :")
            print(path)
            print("Files present in the path :")
            [ print(n) for n in self.path.glob("*.h5" )]

        try:
            self.process_model_nodes()
        except:
            raise RuntimeWarning("Cannot process the nodes. Maybe the temperature file is not present.")


    def get_filenames(self, type="none", sort_by="name"):
        """general fonction to get the filenames depending of the type of results wanted"""
        
        if type == "solarflux":
            extention = "*.sf.h5"
        elif type == "earthflux":
            extention = "*.pf.h5"
        elif type == "temperature":
            extention = "*.temp.h5"

        files =  list(self.path.glob(extention))
        if sort_by == "date":
            files.sort(key=os.path.getmtime)
        else:
            files.sort()

        return files
 
 
    def get_solarflux_file(self):
        """return the h5 file name with the solar flux"""
 
        filenames = self.get_filenames("solarflux")
        
        if self.verbose:
            print(filenames)
            
        if len(filenames) == 0:
            raise RuntimeError("Error, missing Solaf Flux file")
        elif len(filenames) > 1:
            print("WARNING : Multiple files match the Solar Flux extention")

 
        filename = filenames[0]
 
        return filename
 
 
    def get_temperature_file(self):
        """return the h5 file name with the temperature data"""
 
        filenames = self.get_filenames("temperature")
        
        if len(filenames) == 0:
            raise RuntimeError("No temperature file found")
        elif len(filenames) > 1:
            print("WARNING : Multiple files match the temperature extention")
        
        if self.verbose:
            print("\n the temperature files are :")
            print(filenames)
            
        filename = filenames[0]
        return filename
    
    
    def read_solarflux(self, groupname ="Results",
                       subgroupname = "Direct Solar",
                       datasetname  = "Flux"):
        
        solarfluxname = self.get_solarflux_file()
 
        with hp.File(solarfluxname, "r") as h5file:
            value = h5file[groupname][subgroupname][datasetname][()]
            time = h5file["Time"]["Computed times"][()]
 
        time -= time[0]
        time *= 24
        return value, time
 
 
    def read_temperature_results(self, groupname="Results", subgroup="Thermal", datasetname="Temperatures"):
        """Read the *.temp.h5 data file according to the group, subgroup and dataset name

        Args:
            groupname (str): name of the groupe, from
                            ["Model", "Posther"n "Results", "Run Info", "Time"].
                            Defautl is "Results"
            subgroup (str): name of the subgroup. If Group is "Results", options are
                            ["Couplings", "Electric", "Outgassing", "Properties", "Thermal", "Variables"].
                            Default is Thermal
            datasetname (str): name of the DataSet. If Subgroup is "Thermal", options are
                            ["Albedo fluxes", "Internal dissipations", "Planet IR fluxes", "Residual fluxes", "Solar fluxes", "Temperatures"].
                            Default is "Temperatures"

        Returns:
            [type]: [description]
        """
        filename = self.get_temperature_file()
 
        with hp.File(filename, "r") as h5file:
            value = h5file[groupname][subgroup][datasetname][()]
 
        return value


    def get_temperature(self):

        return self.read_temperature_results(
                                          groupname="Results",
                                          subgroup="Thermal",
                                          datasetname="Temperatures" )


    def get_internal_dissipation(self) :
        """return the value in W of the internal dissiabation for each node (each mesh cell)"""


        return self.read_temperature_results(groupname="Results", subgroup="Thermal",
                                         datasetname="Internal dissipations")

 
    def read_temperature_results2(self, groupname, datasetname):
        """Open the temperature h5 file, but access the dataset with only one groupe of hyerachi"""
        filename = self.get_temperature_file()
 
        with hp.File(filename, "r") as h5file:
            
            value = h5file[groupname][datasetname][()]
 
        return value
    
    
    def return_time_temperature(self):
        """the time vector is stor in all of the h5 files"""
 
        filename = self.get_temperature_file()
 
        with hp.File(filename, "r") as h5file:
            value = h5file["Time"]["Frequency 1"][()]
 
        value -= value[0]
        value *= 24
        return value


    def process_model_nodes(self):
        """The nodes are accessible, but this model is meat to understand better their information
        """
        
        try :
            node_liste = self.read_temperature_results2("Model", "Nodes")
        except OSError :
            raise RuntimeError("Cannot open the file. You should close any application using the file")

        self.node_liste = np.array([n[1] for n in node_liste])

        names = [d[2] for d in node_liste]
        self.nodes_value = np.array([d[1] for d in node_liste])
 
        names_unique = []
        for n in names:
            name_in_str = n.decode("utf-8")
            if not name_in_str in names_unique:
                if len(name_in_str) > 0:
                    names_unique.append(n.decode("utf-8"))
        self.names_unique = names_unique
 
        nodes_per_names = [[] for n in self.names_unique]
 
        for i, n in enumerate(self.names_unique):
            for b in node_liste:
                if b[2].decode("utf-8") == n:
                    nodes_per_names[i].append(b[1])
        self.nodes_per_names = nodes_per_names
 
        if self.verbose :
            print("We have some names :")
            print(self.names_unique)
            print()
            for i, n in enumerate(self.names_unique):
                print("nodes in ", n)
                print(self.nodes_per_names[i])
 
    
    def dump_result_file_structure(self):
        """Print the structure of the file
        """
        from pythermica.hdf5_process import h5dump
        
        filename = self.get_temperature_file()
        h5dump(filename)
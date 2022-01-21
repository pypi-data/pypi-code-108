from typing import Optional, List, Dict, Union
import os
import glob
import json
import time
import ROOT

from .builtin_methods import BUILTIN_METHODS
from .actions import *
from .parsers import RooProcConfigParser

from quickstats.components import AbstractObject

class RooProcessor(AbstractObject):
    def __init__(self, config_path:Optional[str]=None,
                 multithread:bool=True,
                 verbosity:Optional[Union[int, str]]="INFO"):
        super().__init__(verbosity=verbosity)
        self.action_list = []
        self.rdf_frames = {}
        self.rdf = None
        self.global_variables = {}
        self.external_variables = {}
        self.treename = None
        
        self.load_buildin_functions()
        
        if multithread:
            ROOT.EnableImplicitMT()
        
        if config_path is not None:
            self.load_config(config_path)
            
    def load_buildin_functions(self):
        for name, definition in BUILTIN_METHODS.items():
            RooProcDeclare.declare_expression(definition, name)
    
    def load_config(self, config_path:Optional[str]=None):
        action_list = RooProcConfigParser.parse_file(config_path)
        if len(action_list) == 0:
            raise RuntimeError("no actions found in the process card")
        first_action = action_list[0]
        if not isinstance(first_action, RooProcTreeName):
            raise RuntimeError("tree name must be specified at the beginning of the process card")
        self.treename = first_action._params['treename']
        self.action_list = action_list
    
    def run(self, filename:str):
        all_files = []
        if isinstance(filename, str):
            filename = [filename]
        if not isinstance(filename, list):
            raise ValueError("filename must be either string or list of strings")
        for fname in filename:
            if os.path.isdir(fname):
                all_files += glob.glob(os.path.join(fname, "*.root"))
            else:
                all_files = glob.glob(fname)
        if not all_files:
            raise FileNotFoundError(f"file `{filename}` does not exist")
        if len(all_files) == 1:
            self.stdout.info(f"INFO: Processing file `{all_files[0]}`.")
        else:
            self.stdout.info(f"INFO: Professing files")
            for f in all_files:
                self.stdout.info(f"\t`{f}`")
        if len(self.action_list) == 0:
            self.stdout.warning("WARNING: No actions to be performed.")
            return None
        if self.treename is None:
            raise RuntimeError("tree name is undefined")
        start = time.time()
        self.rdf = ROOT.RDataFrame(self.treename, all_files)
        for i, action in enumerate(self.action_list):
            if isinstance(action, RooProcRDFAction):
                self.rdf = action.execute(self.rdf, self.global_variables)
            elif isinstance(action, RooProcHelperAction):
                action.execute(self, self.global_variables)
            elif isinstance(action, RooProcHybridAction):
                self.rdf, _ = action.execute(self.rdf, self, self.global_variables)
            else:
                raise RuntimeError("unknown action type")
        end = time.time()
        time_taken = end - start
        self.stdout.info(f"INFO: Task finished. Total time taken: {time_taken:.3f} s.")
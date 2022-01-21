from typing import Optional, List, Dict, Union
import os
import glob
import json
import fnmatch

import ROOT

from quickstats.components import AbstractObject
from quickstats.utils.common_utils import str_list_filter

class RooInspector(AbstractObject):
    def __init__(self, tree_name:str, file_expr:Union[str, List[str]], 
                 filter_expr:Optional[str]=None,
                 verbosity:Optional[Union[int, str]]="INFO"):
        super().__init__(verbosity=verbosity)
        self.tree_name = tree_name
        self.fnames = self._parse_file_expr(file_expr)
        self.initialise(filter_expr=filter_expr)
        
    def _parse_file_expr(self, file_expr:Union[str, List[str]])->List[str]:
        fnames = []
        if isinstance(file_expr, str):
            return self._parse_file_expr([file_expr])
        else:
            for expr in file_expr:
                if os.path.isdir(expr):
                    file_expr = os.path.join(expr, "*.root")
                fnames_i = glob.glob(expr)
                if not fnames_i:
                    self.stdout.warning(f"WARNING: No root files found matching the expression {expr}")
                fnames += fnames_i
        if not fnames:
            raise RuntimeError("no root files found from the given file expression")
        return fnames
    
    def initialise(self, filter_expr:Optional[str]=None):
        self.rdf = ROOT.RDataFrame(self.tree_name, self.fnames)
        if filter_expr is not None:
            self.rdf = self.rdf.Filter(filter_expr)
        
    def get_column_names(self)->List[str]:
        column_names = sorted([str(i) for i in self.rdf.GetColumnNames()])
        return column_names
    
    def get_column_types(self, column_names:List[str])->Dict[str,str]:
        all_column_names = self.get_column_names()
        invalid_column_names = set(column_names) - set(all_column_names)
        if len(invalid_column_names) > 0:
            raise RuntimeError("unknown column names: {}".format(",".join(invalid_column_names)))
        column_types = {}
        for column_name in column_names:
            try:
                column_types[column_name] = str(self.rdf.GetColumnType(column_name))
            except:
                column_types[column_name] = "undefined"
        return column_types
    
    def get_entries(self):
        return self.rdf.Count().GetValue()
    
    def print_summary(self, suppress_print:bool=False,
                      include_patterns:Optional[List]=None, exclude_patterns:Optional[List]=None,
                      save_as:Optional[str]=None):
        summary_str = ""
        nentries = self.get_entries()
        summary_str += f"Number of Events: {nentries}\n"
        column_names = self.get_column_names()
        if include_patterns is not None:
            column_names = str_list_filter(column_names, include_patterns, inclusive=True)
        if exclude_patterns is not None:
            column_names = str_list_filter(column_names, exclude_patterns, inclusive=False)
        column_types = self.get_column_types(column_names)
        n_columns = len(column_types)
        summary_str += f"Columns of Interest ({n_columns}):\n"
        for cname, ctype in column_types.items():
            ctype_str = "(" + ctype + ")"
            summary_str += f"{ctype_str:<30}{cname}\n"
        if not suppress_print:
            self.stdout.info(summary_str)
        if save_as is not None:
            with open(save_as, "w") as f:
                f.write(summary_str)
        
        

    
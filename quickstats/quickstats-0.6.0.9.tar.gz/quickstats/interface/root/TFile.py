import numpy as np

import ROOT

class TFile:
    def __init__(self, f:ROOT.TFile):
        self.init(f)
        
    def init(self, f):
        self.obj = f
    """
    def make_branches(self, branch_data):
        branches = {}
        return branches
    
    def fill_branches(self, treename:str, branch_data):
        if self.obj is None:
            raise RuntimeError("no active ROOT file instance defined")
        tree = self.obj.Get(treename)
        if not tree:
            raise RuntimeError(f"the ROOT file does not contain the tree named \"{treename}\"")
        n_entries = tree.GetEntriesFast()
        
        for i in range(n_entries):
            for branch in branches:
                
        tree.SetDirectory(self.obj)
        # save only the new version of the tree
        tree.GetCurrentFile().Write("", ROOT.TObject.kOverwrite)
    """
    
    def close(self):
        self.obj.Close()
        self.obj = None
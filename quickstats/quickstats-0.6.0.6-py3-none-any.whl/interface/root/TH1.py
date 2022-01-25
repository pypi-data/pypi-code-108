import numpy as np

import ROOT

from quickstats.interface.root import TArrayData
from quickstats.interface.root import load_macro

class TH1(TArrayData):
    def __init__(self, h, dtype:str='double'):
        self.dtype = dtype
        self.init(h)
        
    def init(self, h):
        self.bin_content  = self.GetBinContentArray(h, self.dtype)
        self.bin_error    = self.GetBinErrorArray(h, self.dtype)
        self.bin_center   = self.GetBinCenterArray(h, self.dtype)
        self.bin_width    = self.GetBinWidthArray(h, self.dtype)
        self.bin_low_edge = self.GetBinLowEdgeArray(h, self.dtype)
        
    @staticmethod
    def GetBinContentArray(h, dtype:str='double'):
        c_vector = ROOT.TH1Utils.GetBinContentArray[dtype](h)
        return TArrayData.vec_to_array(c_vector)        
        
    @staticmethod
    def GetBinErrorArray(h, dtype:str='double'):
        c_vector = ROOT.TH1Utils.GetBinErrorArray[dtype](h)
        return TArrayData.vec_to_array(c_vector)

    @staticmethod
    def GetBinCenterArray(h, dtype:str='double'):
        c_vector = ROOT.TH1Utils.GetBinCenterArray[dtype](h)
        return TArrayData.vec_to_array(c_vector)
    
    @staticmethod
    def GetBinWidthArray(h, dtype:str='double'):
        c_vector = ROOT.TH1Utils.GetBinWidthArray[dtype](h)
        return TArrayData.vec_to_array(c_vector)

    @staticmethod
    def GetBinLowEdgeArray(h, dtype:str='double'):
        c_vector = ROOT.TH1Utils.GetBinLowEdgeArray[dtype](h)
        return TArrayData.vec_to_array(c_vector)    
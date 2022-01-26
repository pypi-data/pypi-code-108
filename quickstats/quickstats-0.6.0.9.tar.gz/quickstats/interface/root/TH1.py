import numpy as np

import ROOT

from quickstats.interface.root import TObject, TArrayData
from quickstats.interface.root import load_macro

class TH1(TObject):
    
    FUNDAMENTAL_TYPE = ROOT.TH1
    
    def __init__(self, h:ROOT.TH1, dtype:str='double', 
                 underflow_bin:int=0,
                 overflow_bin:int=0):
        self.dtype = dtype
        self.underflow_bin = underflow_bin
        self.overflow_bin  = overflow_bin
        self.init(h)
        
    def init(self, h):
        self.bin_content  = self.GetBinContentArray(h, self.dtype, self.underflow_bin, self.overflow_bin)
        self.bin_error    = self.GetBinErrorArray(h, self.dtype, self.underflow_bin, self.overflow_bin)
        self.bin_center   = self.GetBinCenterArray(h, self.dtype, self.underflow_bin, self.overflow_bin)
        self.bin_width    = self.GetBinWidthArray(h, self.dtype, self.underflow_bin, self.overflow_bin)
        self.bin_low_edge = self.GetBinLowEdgeArray(h, self.dtype, self.underflow_bin, self.overflow_bin)
        
    @staticmethod
    def GetBinContentArray(h, dtype:str='double', underflow_bin:int=0, overflow_bin:int=0):
        c_vector = ROOT.TH1Utils.GetBinContentArray[dtype](h, underflow_bin, overflow_bin)
        return TArrayData.vec_to_array(c_vector)        
        
    @staticmethod
    def GetBinErrorArray(h, dtype:str='double', underflow_bin:int=0, overflow_bin:int=0):
        c_vector = ROOT.TH1Utils.GetBinErrorArray[dtype](h, underflow_bin, overflow_bin)
        return TArrayData.vec_to_array(c_vector)

    @staticmethod
    def GetBinCenterArray(h, dtype:str='double', underflow_bin:int=0, overflow_bin:int=0):
        c_vector = ROOT.TH1Utils.GetBinCenterArray[dtype](h, underflow_bin, overflow_bin)
        return TArrayData.vec_to_array(c_vector)
    
    @staticmethod
    def GetBinWidthArray(h, dtype:str='double', underflow_bin:int=0, overflow_bin:int=0):
        c_vector = ROOT.TH1Utils.GetBinWidthArray[dtype](h, underflow_bin, overflow_bin)
        return TArrayData.vec_to_array(c_vector)

    @staticmethod
    def GetBinLowEdgeArray(h, dtype:str='double', underflow_bin:int=0, overflow_bin:int=0):
        c_vector = ROOT.TH1Utils.GetBinLowEdgeArray[dtype](h, underflow_bin, overflow_bin)
        return TArrayData.vec_to_array(c_vector)    
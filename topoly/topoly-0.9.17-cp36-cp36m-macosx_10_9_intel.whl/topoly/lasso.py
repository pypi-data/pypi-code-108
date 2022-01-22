from .invariants import Invariant
from .topoly_surfaces import c_lasso_type, c_make_surface
from .params import *

class Lasso(Invariant):
    name = 'Lasso'

    def __init__(self, coordinates, loop_indices, chain=None, model=None, bridges_type=Bridges.SSBOND, bridges=[],
                 breaks=[]):
        super().__init__(coordinates, chain=chain, model=model, bridges_type=bridges_type, bridges=bridges,
                         breaks=breaks)
        if loop_indices:
            self.loop_indices = loop_indices
        else:
            self.loop_indices = self.bridges

    def make_surface(self, precision=PrecisionSurface.HIGH, density=DensitySurface.MEDIUM, precision_output = 3):   
        coordinates = self.get_coords()
        loop_beg, loop_end = self.loop_indices
        surf = c_make_surface(coordinates, loop_beg, loop_end, precision, density)
        for T in surf:
	#T = {'A': {'x': 1.0, 'y': 2.0, 'z': 3.0}, 'B': {'x': 1.9123684942681682, 'y': 2.067676947660268, 'z': 3.735203234274578}, 'C': {'x': 2.0, 'y': 2.0, 'z': 5.0}}
        	for P,coord in T.items(): 
        		for ax in coord: coord[ax] = round(coord[ax],precision_output)        
        return surf

    def lasso_type(self, smoothing=0, precision=0, dens=1,
                   min_dist=[10, 3, 10], pic_files=SurfacePlotFormat.DONTPLOT,
                   output_prefix='', more_info=0, control_dist=0):

        def translate_string_result_to_dictionary(res):
            resD= {"class": None, "beforeN": None, "beforeC": None, "crossingsN": None, "crossingsC": None,
                   "Area": None, "loop_length": None, "Rg": None, "smoothing_iterations": 0}
    
            # res = (1) "<[SMOOTH_10]>  L0"  OR
            # res = (2) "<[SMOOTH_10]> 0 1 1 X X +36 XX 0 0 1 X X XX  L0 XX 9.59 34.90 2.23"  OR
            # res = (3) "[SMOOTH 0] Smoothed files were not produced since just first iteration of smoothing changes the lasso type."

            if len(res.split()) < 5: #(1)
                resD = res.split()[-1]
            elif "XX" in res: # (2)
                lbefore, lafter, lcl, larea = [l.split("X") for l in res.split("XX")]
                if (lbefore[0][:3]=="[SM"):
                    resD["smoothing_iterations"] = int(lbefore[0].split()[0].split("_")[1][:-1])
                resD["beforeN"], resD["beforeC"] = lbefore[-2].split(), lbefore[-1].split()
                resD["crossingsN"], resD["crossingsC"] = lafter[-2].split(), lafter[-1].split()
                resD["class"] = lcl[0].strip()
                resD["Area"] = float(larea[0].split()[0])
                resD["loop_length"] = float(larea[0].split()[1])
                resD["Rg"] = float(larea[0].split()[2])
            else: # (3)
                resD = "Smoothing not possible since first iteration of smoothing procedure changes the lasso type"
    
            return resD

        coordinates = self.get_coords()
        if pic_files == None:
            pic_files = 0                                                            
        elif type(pic_files) == int:                                                 
            pass                                                                     
        elif type(pic_files) == list:                                                
            summ = 0                                                                 
            for ext in pic_files:                                                    
                summ += ext                                                          
            pic_files = summ                                                         
        pic_files = int(bin(pic_files)[2:])
        output_type_to_cpp = -1 if not more_info else 1
        resD = {}
        if len(self.loop_indices) == 0:
            return resD
        if type(self.loop_indices[0]) is int:
            index = self.loop_indices
            res = c_lasso_type(coordinates, self.loop_indices[0],
                        self.loop_indices[1], smoothing, precision, dens,
                        min_dist[0], min_dist[1], min_dist[2], pic_files,
                        output_prefix.encode('utf-8'), output_type_to_cpp, control_dist).decode('UTF-8')
            resD[(index[0], index[1])] = translate_string_result_to_dictionary(res)
            return resD
        if type(self.loop_indices[0]) is list or type(self.loop_indices[0]) is tuple:
            for index in self.loop_indices:
                res = c_lasso_type(coordinates, index[0], index[1], smoothing, 
                          precision, dens, min_dist[0], min_dist[1],
                          min_dist[2], pic_files, output_prefix.encode('utf-8'),
                          output_type_to_cpp, control_dist).decode('UTF-8')
                resD[(index[0], index[1])] = translate_string_result_to_dictionary(res)
            return resD


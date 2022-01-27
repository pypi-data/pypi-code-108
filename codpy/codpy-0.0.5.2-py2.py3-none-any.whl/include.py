import os,sys
#######global variables#######
parent_path = os.path.dirname(__file__)
if parent_path not in sys.path: sys.path.append(parent_path)
common_path = os.path.join(parent_path,"com")
if common_path not in sys.path: sys.path.append(common_path)
data_path = os.path.join(parent_path,"data")
if data_path not in sys.path: sys.path.append(data_path)
predictors_path = os.path.join(parent_path,"pred")
if predictors_path not in sys.path: sys.path.append(predictors_path)
proj_path = os.path.join(parent_path,"proj")
if proj_path not in sys.path: sys.path.append(proj_path)
from codpy_tools import *
#######################################

from utils import *
import numpy as np
import robot
from box import *
from  cylinder import *

def _sDOF(htm, name):

  if not Utils.isaMatrix(htm,4,4):
    raise Exception("The optional parameter 'htm' should be a 4x4 homogeneous transformation matrix")
  
  if not (str(type(name)) == "<class 'str'>"):
    raise Exception("The optional parameter 'name' should be a string")    

  linkInfo = [[ 1.570, -1.570,  0.000,  0.000,  0.000,  0.000], # "theta" rotation in z
                  [ 0.335,  0.000,  0.000, -0.405,  0.000, -0.080], # "d" translation in z
                  [-1.570,  0.000,  1.570, -1.570,  1.570,  3.141], # "alfa" rotation in x
                  [ 0.075,  0.365,  0.090,  0.000,  0.000,  0], # "a" translation in x
                  [ 0.000,  0.000,  0.000,  0.000,  0.000,  0.000],
                  [ 1.570, -2.355,  1.570,  0.000,  0.000,  0.000]];# zero-configuration

  #Collision model
  colModel = [[],[],[],[],[],[]]

  #00 = Utils.trn([0,0,0.33/2])
  #01 = Utils.trn([-0.03,0.075,0.34]) @ Utils.roty(1.5707)
  #10 = Utils.trn([-0.12,0.095,0.5])
  #11 = Utils.trn([-0.04,0.075,0.71]) @ Utils.roty(1.5707)
  #12 = Utils.trn([0,0.3,0.79])

  htm_0_0=np.array([[ 7.963e-04,  1.000e+00,  1.067e-22, -7.500e-02],
       [-7.963e-04,  6.341e-07, -1.000e+00,  1.700e-01],
       [-1.000e+00,  7.963e-04,  7.963e-04, -1.354e-04],
       [ 0.000e+00,  0.000e+00,  0.000e+00,  1.000e+00]])
  
  htm_0_1=np.array([[ 7.671e-08,  1.000e+00,  7.963e-04, -2.391e-05],
       [ 1.000e+00,  6.341e-07, -8.927e-04, -4.976e-03],
       [-8.927e-04,  7.963e-04, -1.000e+00,  3.006e-02],
       [ 0.000e+00,  0.000e+00,  0.000e+00,  1.000e+00]])
  
  htm_1_0=np.array([[ 7.970e-04,  7.957e-04,  1.000e+00, -2.001e-01],
       [ 7.957e-04,  1.000e+00, -7.963e-04,  1.977e-02],
       [-1.000e+00,  7.963e-04,  7.963e-04,  1.202e-01],
       [ 0.000e+00,  0.000e+00,  0.000e+00,  1.000e+00]])
  
  htm_1_1=np.array([[-1.000e+00,  7.957e-04,  8.933e-04,  9.968e-03],
       [ 7.964e-04,  1.000e+00,  7.956e-04, -3.305e-04],
       [-8.927e-04,  7.963e-04, -1.000e+00,  4.036e-02],
       [ 0.000e+00,  0.000e+00,  0.000e+00,  1.000e+00]])
  
  htm_2_0=np.array([[ 7.970e-04,  7.957e-04,  1.000e+00,  1.787e-04],
       [-1.000e+00,  1.593e-03,  7.957e-04,  7.801e-04],
       [-1.592e-03, -1.000e+00,  7.970e-04, -2.246e-01],
       [ 0.000e+00,  0.000e+00,  0.000e+00,  1.000e+00]])


  colModel[0].append(Cylinder(htm = htm_0_0, name=name+"_C0_0",radius=0.12,height=0.33,color="red"))
  colModel[0].append(Cylinder(htm = htm_0_1, name=name+"_C0_1",radius=0.095,height=0.30,color="red"))

  colModel[1].append(Box(htm = htm_1_0, name=name+"_C1_0", width=0.1, height = 0.5, depth = 0.16, color="green" ))
  colModel[1].append(Cylinder(htm = htm_1_1, name=name+"_C1_1",radius=0.095,height=0.28,color="green"))

  colModel[2].append(Box(htm = htm_2_0, name=name+"_C2_0", width=0.143, height = 0.12, depth = 0.45, color="blue" ))

  return linkInfo, colModel
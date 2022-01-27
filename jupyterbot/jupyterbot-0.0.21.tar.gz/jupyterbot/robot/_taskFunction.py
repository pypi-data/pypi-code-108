from utils import *
import numpy as np

#Function used for task function/task Jacobian
def _taskFunction(self, htmd, q = None, htm = None):

  if q is None:
    q = self.q

  if htm is None:
    htm = self.htm

  #Error handling
  if not Utils.isaMatrix(htmd,4,4):
    raise Exception("The parameter 'htmd' should be a 4x4 homogeneous transformation matrix")
  #end error handling  

  pdes = htmd[0:3,3]
  xdes = htmd[0:3,0]
  ydes = htmd[0:3,1]
  zdes = htmd[0:3,2]

  J, FK = self.jacGeo(q, MTH0 = htm)
  p = FK[0:3,3]
  x = FK[0:3,0]
  y = FK[0:3,1]
  z = FK[0:3,2]

  r = np.zeros((6,))
  r[0:3] = p-pdes
  r[3] = sqrt(max(1 - np.transpose(xdes) @ x,0))
  r[4] = sqrt(max(1 - np.transpose(ydes) @ y,0))
  r[5] = sqrt(max(1 - np.transpose(zdes) @ z,0))

  n = len(self.links)
  Jr = np.zeros((6,n))
  Jr[0:3,:] = J[0:3,:]
  Jr[3,:] = np.transpose(xdes) @ Utils.S(x) @ J[3:6,:]
  Jr[4,:] = np.transpose(ydes) @ Utils.S(y) @ J[3:6,:]
  Jr[5,:] = np.transpose(zdes) @ Utils.S(z) @ J[3:6,:]

  return r, Jr

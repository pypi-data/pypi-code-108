from utils import *
import numpy as np

#Geometric Jacobian
def _jacGeo(self, q = None, axis = 'eef', htm0 = None):

  if q is None:
    q = self.q
  if htm0 is None:
    htm0 = self.htm

  n = len(self._linkInfo[0])

  #Error handling
  if not Utils.isaVector(q,n):
    raise Exception("The optional parameter 'q' should be a "+str(n)+" dimensional vector")

  if not (axis=="eef" or axis=="dh" or axis=="com"):
    raise Exception("The optional parameter 'axis' should be one of the following strings:\n"\
    "'eef': End-effector \n"\
    "'dh': All "+str(n)+" axis of Denavit-Hartenberg\n"\
    "'com': All "+str(n)+" axis centered at the center of mass of the objects")

  if not Utils.isaMatrix(htm0,4,4):
    raise Exception("The optional parameter 'htm' should be a 4x4 homogeneous transformation matrix")
  #end error handling

  if axis=='dh' or axis=='eef':
    T = self.FK(q,'dh',htm0)
  if axis=='com':
    T = self.FK(q,'com',htm0)

  J = np.zeros((n,6,n))
  

  for i in range(n):
    pi = T[i,0:3,3]
    for j in range(i+1):
    
      if j == 0:
        pjant = htm0[0:3,3]
        zjant = htm0[0:3,2]
      else:
        pjant = T[j-1,0:3,3]
        zjant = T[j-1,0:3,2]

      if self._links[i].jointType==0:
        J[i,0:3,j] = Utils.S(zjant) @ (pi - pjant)
        J[i,3:6,j] = zjant 
    
      if self._links[i].jointType==1:
        J[i,0:3,j] = zjant 
        J[i,3:6,j] = [[0],[0],[0]]

  #GAMBIARRA
  for i in range(n):
    J[i,3:6,5]=-J[i,3:6,5]

  if axis=='dh' or axis=='com':
    return J,T
  
  if axis=='eef':
    return J[-1,:,:], T[-1,:,:]

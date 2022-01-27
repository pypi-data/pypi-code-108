from utils import *
import numpy as np

def _FK(self, q = None, axis = 'eef', htm0 = None):

  if q is None:
    q = self.q
  if htm0 is None:
    htm0 = self.htm


  #GAMBIARRA
  q[5]=-q[5]


  n = len(self._links)

  #Error handling
  if not Utils.isaVector(q,n):
    raise Exception("The optional parameter 'q' should be a "+str(n)+" dimensional vector")

  if not (axis=="eef" or axis=="dh" or axis=="com"):
    raise Exception("The optional parameter 'axis' should be one of the following strings:\n"\
    "'eef': End-effector \n"\
    "'dh': All "+str(n)+" axis of Denavit-Hartenberg\n"\
    "'com': All "+str(n)+" axis centered at the center of mass of the objects")

  if not Utils.isaMatrix(htm0,4,4):
    raise Exception("The optional parameter 'htm0' should be a 4x4 homogeneous transformation matrix")
  #end error handling

  q = q + self._dq0

  T = np.zeros((n,4,4))

  for i in range(n):
    if i == 0:
      T[i,:,:] = htm0
    else:
      T[i,:,:] = T[i-1,:,:]

    if self._links[i].jointType==0:
        T[i,:,:] = T[i,:,:] @ Utils.rotz(q[i])
    else:
        T[i,:,:] = T[i,:,:] @ Utils.rotz(self._links[i].theta)

    if self._links[i].jointType==1:
        T[i,:,:] = T[i,:,:] @ Utils.trn([0,0,q[i]])
    else:
        T[i,:,:] = T[i,:,:] @ Utils.trn([0,0,self._links[i].d])        

    T[i,:,:] = T[i,:,:] @ Utils.rotx(self._links[i].alpha)
    T[i,:,:] = T[i,:,:] @ Utils.trn([self._links[i].a,0,0])

  if axis=='com':
    for i in range(n):
      T[i,3,0:3] = T[i,3,0:3] + T[i,0:3,0:3] @ self._links[i].centerShift      

  if axis=='eef':
    T = T[-1,:,:]

  return T 
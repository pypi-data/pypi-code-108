from utils import *
import numpy as np

#(Private function) Used in IK
def _evolveConfig(self, q, ptol, atol, FK, iterRemain):

  n = len(self.links)
  found = False
  zerou = False
  iterEnd = False

  dt=min(ptol,0.005*atol,0.01)
  K=2
  eps=0.001
  tolu=0.0001/dt
  i=0

  while (not found) and (not zerou) and (not iterEnd):

    r, Jr = self.taskFunction(FK, np.array(q))

    #pD = FK[0:3,3]
    #xD = FK[0:3,0]
    #yD = FK[0:3,1]
    #zD = FK[0:3,2]

    #J,FKC = self.jacGeo(np.array(q))
    #p = FKC[0:3,3]
    #x = FKC[0:3,0]
    #y = FKC[0:3,1]
    #z = FKC[0:3,2]  

    #r = np.zeros((n,))
    #r[0:3] = p-pD
    #r[3] = sqrt(max(1 - np.transpose(xD) @ x,0))
    #r[4] = sqrt(max(1 - np.transpose(yD) @ y,0))
    #r[5] = sqrt(max(1 - np.transpose(zD) @ z,0))

    #Jr = np.zeros((6,n))
    #Jr[0:3,:] = J[0:3,:]
    #Jr[3,:] = np.transpose(xD) @ Utils.S(x) @ J[3:6,:]
    #Jr[4,:] = np.transpose(yD) @ Utils.S(y) @ J[3:6,:]
    #Jr[5,:] = np.transpose(zD) @ Utils.S(z) @ J[3:6,:]

    u = Utils.dpinv(Jr,eps) @ (-K*r)
    q = q + u*dt

    epos = max(abs(r[0:3]))
    eori = max([57.29577*acos(min(max(1-num*num,-1),1)) for num in r[3:6]])
    i+=1

    found = (epos < ptol) and (eori < atol)
    zerou = max(abs(u))<tolu
    iterEnd = i > iterRemain


  return found, i, q

#Inverse kinematics for the end-effector
def _IK(self, htm, q0 = None, ptol=0.005, atol=5, noIterMax=2000):

  n = len(self._links)
  if q0 is None:
    q0 = 6.2831*np.random.rand(n)-3.1416  

  #Error handling
  if not Utils.isaMatrix(htm,4,4):
    raise Exception("The parameter 'htm' should be a 4x4 homogeneous transformation matrix")

  if not Utils.isaNaturalNumber(noIterMax):
    raise Exception("The optional parameter 'noIterMax' should be a nonnegative integer number")  

  if not Utils.isaVector(q0,n):
    raise Exception("The optional parameter 'q0' should be a "+str(n)+" dimensional vector")

  if (not Utils.isaNumber(ptol)) or ptol<=0:
    raise Exception("The optional parameter 'pol' should be a nonnegative number")

  if (not Utils.isaNumber(atol)) or atol<=0:
    raise Exception("The optional parameter 'atol' should be a nonnegative number")

  
  #end error handling   

  j=0
  found = False
  q=q0
  noIterRemain = noIterMax

  while not found and noIterRemain>=0:
    found, i, q = _evolveConfig(self,q,ptol,atol,htm,noIterRemain)
    noIterRemain -= i
    if not found:
      q = 6.2831*np.random.rand(n)  

  if not found:     
    raise Exception("Solution for IK not found. You can try the following: \n"\
    " Increasing the maximum number of iterations, 'noIterMax' (currently "+str(noIterMax)+")\n"\
    " Increasing the tolerance for the position, 'ptol' (currently "+str(ptol)+" meters)\n"\
    " Increasing the tolerance for the orientation, 'atol' (currently "+str(atol)+" degrees)")
  else:
    return q

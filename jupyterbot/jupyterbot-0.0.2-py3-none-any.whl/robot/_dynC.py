from utils import *
import numpy as np

#Dynamic parameter Coriolis-Centrifugal
def _dynC(self, qdot, q = None):

  if q is None:
    q = self.q

  #Error handling
  if not Utils.isaVector(qdot,n):
    raise Exception("The parameter 'qdot' should be a "+str(n)+" dimensional vector")

  if not Utils.isaVector(q,n):
    raise Exception("The optional parameter 'q' should be a "+str(n)+" dimensional vector")
  #end error handling  

  Jc, FKc = self.jacGeo(q,'com') 
  return self._dynCaux(qdot, q, Jc, FKc)

#Dynamic parameter Coriolis-Centrifugal
def _dynCaux(self, qdot, q, Jc, FKc):


  if (Jc is None) or (FKc is None):
    Jc, FKc = self.jacGeo(q,'com')

  #Error handling
  if not Utils.isaVector(qdot,n):
    raise Exception("The parameter 'qdot' should be a "+str(n)+" dimensional vector")

  if not Utils.isaVector(q,n):
    raise Exception("The optional parameter 'q' should be a "+str(n)+" dimensional vector")
  #end error handling


  M = self.dynM(q,Jc,FKc)
  n = len(self._links)

  dq=0.001
  dMdq = []
  for i in range(n):
    dqi = np.zeros((n,))
    dqi[i] = dq
    Mpi = self.dynM(q+dq)
    dMdq.append((Mpi-M)/dq)

  C1 = np.zeros((n,))
  C2 = np.zeros((n,))

  for j in range(n):
    C1 = C1 + (qdot[j]*dMdq[j]) @ qdot
    
  for i in range(n):
    C2[i] = 0.5 * np.transpose(qdot) @ dMdq[i] @ qdot

  return np.reshape(C1-C2,(n,))

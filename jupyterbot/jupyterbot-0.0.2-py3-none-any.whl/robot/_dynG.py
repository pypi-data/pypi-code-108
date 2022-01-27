from utils import *
import numpy as np

#Dynamic parameter Gravity
def _dynG(self, q = None):

  if q is None:
    q = self.q

  #Error handling
  if not Utils.isaVector(qdot,n):
    raise Exception("The parameter 'qdot' should be a "+str(n)+" dimensional vector")
  #end error handling  

  Jc, FKc = self.jacGeo(q,'com') 
  return self._dynGaux(qdot, q, Jc, FKc)    

def _dynGaux(self, q, Jc, FKc):

  n = len(self._links)
  G = np.zeros((n,))
  g = 9.8;
  for i in range(n):
    G = G + g * self._links[i].mass * np.transpose(Jc[i,3,:]),
  
  return np.reshape(G,(n,))
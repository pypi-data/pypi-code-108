from utils import *
import numpy as np

#Dynamic parameter Inertia Matrix
def _dynM(self, q = None):

  if q is None:
    q = self.q
  
  n = len(self._links)

  #Error handling
  if not Utils.isaVector(q,n):
    raise Exception("The optional parameter, 'q', should be a "+str(n)+" dimensional vector")
  #end error handling

  Jc, FKc = self.jacGeo(q,'com')

  return self._dynMaux(q,Jc,FKc)

def _dynMaux(self, q, Jc, FKc):

  n = len(self._links)
  M = np.zeros((n,n))

  for i in range(n):
    M = M + self._links[i].mass * np.transpose(Jc[i,0:3,:]) @ Jc[i,0:3,:]
    M = M + np.transpose(Jc[i,3:6,:]) @ FKc[i,0:3,0:3] @ \
            self._links[i].inertiaMatrix @ \
            np.transpose(FKc[i,0:3,0:3]) @ Jc[i,3:6,:]

  return M

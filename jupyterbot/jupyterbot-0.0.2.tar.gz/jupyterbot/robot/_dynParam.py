from utils import *
import numpy as np
from ._dynM import _dynM
from ._dynC import _dynC
from ._dynG import _dynG

#Dynamic parameter All
def _dynParam(self, qdot, q = None):

  if q is None:
    q = self.q

  #Error handling
  if not Utils.isaVector(qdot,n):
    raise Exception("The parameter 'qdot' should be a "+str(n)+" dimensional vector")

  if not Utils.isaVector(q,n):
    raise Exception("The optional parameter 'q' should be a "+str(n)+" dimensional vector")
  #end error handling  

  Jc, FKc = self.jacGeo(q,'com')

  M = self._dynM(q, Jc, FKc)
  C = self._dynC(qdot, q, Jc, FK)
  G = self._dynG(q, Jc, FK)

  return M, C, G 
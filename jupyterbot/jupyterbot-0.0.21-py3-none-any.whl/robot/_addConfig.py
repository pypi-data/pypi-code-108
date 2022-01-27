from utils import *
import numpy as np

#Add config to animation queue
def _addConfig(self, q, htm = None):


  if htm is None:
    htm = self.htm

  n = len(self._linkInfo[0])

  #Error handling
  if not Utils.isaVector(q,n):
    raise Exception("The parameter 'q' should be a "+str(n)+" dimensional vector")

  if not Utils.isaMatrix(htm,4,4):
    raise Exception("The parameter 'htm' should be a 4x4 homogeneous transformation matrix")
  #end error handling

  self._q = np.array(q)

  f = [htm[0][0], htm[0][1], htm[0][2], htm[0][3],
        htm[1][0], htm[1][1], htm[1][2], htm[1][3],
        htm[2][0], htm[2][1], htm[2][2], htm[2][3],
        0        ,         0,         0,         1, np.ndarray.tolist(q) ]


  self._htm = htm
  self._frames.append(f)
  

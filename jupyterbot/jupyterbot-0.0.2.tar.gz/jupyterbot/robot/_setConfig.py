from utils import *
import numpy as np

#Set config. Restart animation queue
def _setConfig(self, q = None, htm = None):

  if q is None:
    q= self.q0

  if htm is None:
    htm = self.htm

  n = len(self._linkInfo[0])
 
  self._frames = []
  self.code = ''
  self.addConfig(q,htm)

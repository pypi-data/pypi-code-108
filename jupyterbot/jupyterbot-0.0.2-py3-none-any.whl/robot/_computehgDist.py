from utils import *
import numpy as np
from ._distStruct import _DistStruct


#Compute the distance from each link to an object, for the current configuration
#of the robot
def _computehgDist(self, obj, h, g, q = None, htm = None, oldDistStruct=None, tol = 0.0005, noIterMax = 20):

  n = len(self.links)

  if q is None:
    q = self.q

  if htm is None:
    htm = self.MTH

  #Error handling
  if not Utils.isaVector(q,n):
    raise Exception("The optional parameter 'q' should be a "+str(n)+" dimensional vector")

  if not Utils.isaMatrix(htm,4,4):
    raise Exception("The optional parameter 'htm' should be a 4x4 homogeneous transformation matrix")
  
  if not(oldDistStruct is None):
    try:
      idRobot = oldDistStruct.idRobot
      idObj = oldDistStruct.idObj
      if not ( idObj == id(obj) and idRobot == id(self)):
        Exception("The optional parameter 'oldDistStruct' is a 'DistStruct' object, but it "\
        "must have to be relative to the SAME robot object and SAME external object, and "\
        "this is not the case")
    except:
      raise Exception("The optional parameter 'oldDistStruct' must be a 'DistStruct' object")
  
  #end error handling



  distStruct = _DistStruct(obj,self)

  J, FK = self.jacGeo(q, "dh", htm)

  colObjectCopy=[]

  #Update all collision objects of all links
  for i in range(n):
    colObjectCopy.append([])
    for j in range(len(self.links[i].colObject)):
      tempCopy = self.links[i].colObject[j][0].copy()
      htmd = self.links[i].colObject[j][1]
      tempCopy.setConfig(FK[i,:,:] @ htmd)
      colObjectCopy[i].append(tempCopy)
      #self.links[i].colObject[j][0].addConfig(FK[i,:,:] @ htmd)

  #Compute the distance structure
  for i in range(n):
    for j in range(len(self.links[i].colObject)):

      if oldDistStruct is None:
        pObj0 = np.random.uniform(-100,100, size=(3,))  
      else:
        pObj0 = oldDistStruct.getItem(i,j)["pObj"]


      pObj, pObjCol, d = Utils.computehgDist(obj, colObjectCopy[i][j], h, g, pObj0, tol, noIterMax)      
      
      JobjCol = J[i,0:3,:]-Utils.S(pObjCol-FK[i,0:3,3]) @ J[i,3:6,:]
      Jd = (np.transpose(pObjCol-pObj) @ JobjCol)/d

      distStruct._append(i, j, d, pObj, pObjCol, Jd)
      #st = {
      #  "linkNumber": i,
      #  "linkColObjNumber": j,
      #  "hgDistance": d,
      #  "pObj": pObj,
      #  "pObjCol": pObjCol,
      #  "jacDist": Jd
      #}

      #listStruct.append(st)
  
  return distStruct
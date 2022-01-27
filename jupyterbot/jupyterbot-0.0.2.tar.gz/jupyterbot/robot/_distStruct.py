import numpy as np



class _DistStruct:

  #######################################
  # Attributes
  #######################################
  
	@property
	def idObj(self):
		"""Return the memory address for the associated object."""
		return self._idObj

	@property
	def idRobot(self):
		"""Return the memory address for the associated robot."""
		return self._idRobot

	@property
	def jacDistMat(self):
		"""
		Return the matrix in which each row we have the distance Jacobian (gradient) for each robot link.
		"""    
		return self._jacDistMat

	@property
	def distVect(self):
		"""
		Return the vector in which each row we have the distance for each robot link.
		"""       
		return np.array(self._distVect).reshape((self.noItems,))

	@property
	def noItems(self):
		"""Return the number of items."""
		return self._noItems


	def __getitem__(self, key):
		return self._listDict[key]

  #######################################
  # Constructor
  #######################################
      
	def __init__(self, obj, robot):

		self._idObj = id(obj)
		self._idRobot = id(robot)
		self._objName = obj.name
		self._robotName = robot.name
		self._noItems = 0

		n = len(robot.links)  		
		self._listDict = [];
		self._jacDistMat = np.zeros((0,n))
		self._distVect = []


  #######################################
  # Std. Print
  #######################################

	def __repr__(self):
    
		return "Distance struct between robot '"+self._robotName+"' and object '"\
    +self._objName+"', with "+str(self.noItems)+" items"



  #######################################
  # Methods
  #######################################
  
	def _append(self, i, j, d, pObj, pObjCol, Jd):
		self._listDict.append({
        "linkNumber": i,
        "linkColObjNumber": j,
        "hgDistance": d,
        "pObj": pObj,
        "pObjCol": pObjCol,
        "jacDist": Jd
    })

		self._jacDistMat = np.vstack((self._jacDistMat, Jd))
		self._distVect.append(d)
		self._noItems+=1

	def getItem(self, i, j):
		for d in self._listDict:
			if i==d["linkNumber"] and j==d["linkColObjNumber"]:		
				return d

		raise Exception("Item not found!")  

	def getClosestItem(self):
		dmin=float('inf')
		imin=-1
		for i in range(self._noItems):
			if self[i]["hgDistance"]<dmin:
				dmin=self[i]["hgDistance"]
				imin=i
    
		return self[imin]

import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

import numpy as np
from utils import *
from links import *
from ._FK import _FK
from ._IK import _IK
from ._setConfig import _setConfig
from ._addConfig import _addConfig
from ._jacGeo import _jacGeo
from ._dynM import _dynM
from ._dynC import _dynC
from ._dynG import _dynG
from ._dynParam import _dynParam
from ._sDOF import _sDOF
from ._computehgDist import _computehgDist
from ._genCode import _genCode
from ._taskFunction import _taskFunction


class Robot:
	"""
  A class that contains a robot object in jupyterbot.

  Parameters
  ----------
  linkInfo : list of lists
      Contains the link info in a 6 x n list of lists, in which n is the
      number of joints.

      The first line is the "theta" parameter of Denavit-Hartenberg;

      The second line is the "d" parameter of Denavit-Hartenberg;

      The third line is the "alpha" parameter of Denavit-Hartenberg;

      The fourth line is the "a" parameter of Denavit-Hartenberg; 

      The fifth line is the joint type (0=revolute, 1 = prismatic);

      The sixth line is the configuration shift (sets the "zero" configuration
      of the robot).      

  htm : 4x4 numpy array or 4x4 nested list
      The robot base's configuration
      (default: 4x4 identity matrix).
  name : string
      The robot name 
      (default: 'genRobot').
  rtype : string
      The robot type
      (default: 'generic').
  colModel : list of list
      A list that contains at most n lists (n is the number of joints). Each
      list contains objects as balls, cylinders and boxs that compose the 
      collision model of the robot.
      (default: empty list).      
  """

  #######################################
  # Attributes
  #######################################


	@property
	def q(self):
		"""The current joint configuration."""
		return np.array(self._q)

	@property
	def htm(self):
		"""
		The current base configuration. 
		A 4x4 homogeneous matrix written is scenario coordinates.
		"""
		return np.array(self._htm)

	@property
	def links(self):
		"""Data structures containing the links of the robot."""
		return self._links

	@property
	def name(self):
		"""Name of the object."""
		return self._strName
  
  #######################################
  # Constructor
  #######################################

	_ROBOTTYPE = ["generic","sDOF"]
  
	def __init__(self, linkInfo, htm = np.identity(4), name = "genRobot", rtype = "generic", colModel = None ):
    #Error handling

		if not (str(type(linkInfo)) == "<class 'list'>"):
			raise Exception("The parameter 'linkInfo' should be a list with 6 with sublists, each with n float parameters")
		else:
			if not (len(linkInfo) == 6):
				raise Exception("The parameter 'linkInfo' should be a list 6 with sublists, , each with n float parameters")
			else:
				try:
					np.array(linkInfo, dtype=object)
				except:
					raise Exception("The parameter 'linkInfo' should be a list 6 with sublists, , each with n float parameters")


		if colModel is None:
			colModel = [[]]

		n = len(linkInfo[0])

		for i in range(n):
			if not(linkInfo[4][i]==0 or linkInfo[4][i]==1):
				raise Exception("The fifth list in 'linkInfo' should have either 0 (revolute) or 1 (prismatic)")


		if not (str(type(colModel)) == "<class 'list'>"):
			raise Exception("The optional parameter 'colModel' should be a list with at most "+str(n)+" sublist, each with ball, boxes or cylinders")
		else:
			if not (len(colModel) <= n):
				raise Exception("The optional parameter 'colModel' should be a list with at most "+str(n)+" sublist, each with ball, boxes or cylinders")
			else:
				for i in range(len(colModel)):
					try:
						for j in range(len(colModel[i])):
							if not Utils.isaSimpleObject(colModel[i][j]):
								raise Exception("The optional parameter 'colModel' should be a list with at most "+str(n)+" sublist, each with ball, boxes or cylinders")
					except:
						raise Exception("The optional parameter 'colModel' should be a list with at most "+str(n)+" sublist, each with ball, boxes or cylinders")            

		if not Utils.isaMatrix(htm,4,4):
			raise Exception("The optional parameter 'htm' should be a 4x4 homogeneous transformation matrix")

		if not (str(type(name)) == "<class 'str'>"):
			raise Exception("The optional parameter 'name' should be a string")

		if not (rtype in Robot._ROBOTTYPE):
			raise Exception("The optional parameter 'rtype' type can only be one of the following" \
      "strings: "+str(Robot._ROBOTTYPE))  

    #end error handling

		self._frames = []
		self._linkInfo = linkInfo
		self._strlinkInfo = str(self._linkInfo)    
		self._htm = np.array(htm)
		self._strName = name
		self._rtype = rtype


		self._links = []
		for i in range(n):
			self._links.append(
        Link(self,i,
             self._linkInfo[0][i],
             self._linkInfo[1][i],
             self._linkInfo[2][i],
             self._linkInfo[3][i],
             self._linkInfo[4][i],
             self._linkInfo[5][i]))
			for j in range(len(colModel[i])):
				self._links[i].attachColObject(colModel[i][j],colModel[i][j].htm)	

    #Recover initial configuration and shift configuration from DH table    

		self._q0 = np.zeros((n,))
		self._dq0 = np.reshape(self._linkInfo[5],(n,))

		for i in range(n):
			if  self._links[i].jointType==0:
				self._q0[i] = self._links[i].theta-self._dq0[i]

			if self._links[i].jointType==1:
				self._q0[i] = self._links[i].d-self._dq0[i]


    #Set initial total configuration
		self.setConfig(self._q0,self._htm)

  #######################################
  # Std. Print
  #######################################

	def __repr__(self):
		n = len(self._linkInfo[0])

		string = "Robot with name '"+self._strName+"': \n\n"
		string += " Number of joints: "+str(n)+"\n"
		string += " Joint types: "

		for i in range(n):
			string += "R" if self._links[i].jointType==0 else "P"
    
		string+="\n"
		string+=" Current configuration: "+str( [round(num, 3) for num in np.ndarray.tolist(self._q)] )+"\n"
		string+=" Current base HTM: \n"+str(self._htm)+"\n"
		string+=" Current end-effector HTM: \n"+str(self.FK())
		return string

  #######################################
  # Methods for configuration changing
  #######################################


	def addConfig(self, q, htm = None):
		"""
    Add a single configuration to the object's animation queue.

    Parameters
    ----------
    q : nd numpy vector or array
        The manipulator's joint configuration.
    htm : 4x4 numpy array or 4x4 nested list
        The robot base's configuration
        (default: the same as the current HTM).

    Returns
    -------
    None
    """
		return _addConfig(self, q, htm)

	def setConfig(self, q = None, htm = None):
		"""
    Reset object's animation queue and add a single configuration to the 
    object's animation queue.

    Parameters
    ----------
    q : nd numpy vector or array
        The manipulator's joint configuration 
        (default: the default joint configuration for the manipulator).
    htm : 4x4 numpy array or 4x4 nested list
        The robot base's configuration
        (default: the same as the current HTM).

    Returns
    -------
    None
    """    
		return _setConfig(self, q, htm)

  #######################################
  # Methods for kinematics model
  #######################################

	def FK(self, q = None, axis = 'eef', htm = None):
		"""
    Compute the forward kinematics for an axis at a given joint and base
    configuration. Everything is written in the scenario coordinates.

    Parameters
    ----------
    q : nd numpy vector or array
        The manipulator's joint configuration 
        (default: the default joint configuration for the manipulator).
    axis : string
        For which axis you want to compute the FK:
        'eef': for the end-effector
        'dh': for all Denavit-Hartenberg axis
        'com': for all center-of-mass axis
        (default: 'eef').    
    htm0 : 4x4 numpy array or 4x4 nested list
        The robot base's configuration
        (default: the same as the current HTM).

    Returns
    -------
    FK : 4x4 or nx4x4 numpy matrix
        For axis='eef', returns a single htm. For the other cases, return
        n htms as a nx4x4 numpy matrix.
    """    
		return _FK(self, q, axis, htm0)

	def IK(self, htm, q0 = None, ptol=0.005, atol=5, noIterMax=2000):
		"""
    Try to solve the inverse kinematic problem for the end-effector, given a
    desired homogeneous transformation matrix. It returns the manipulator
    configuration. 

    Uses an iterative algorithm.

    The algorithm can fail, throwing an Exception when it happens.

    Parameters
    ----------
    htm0 : 4x4 numpy array or 4x4 nested list
        The desired end-effector HTM, written in scenario coordinates    
    q0 : nd numpy vector or array
        Initial guess for the algorithm for the joint configuration
        (default: a random joint configuration).
    ptol : positive float
        The accepted error for the end-effector position, in meters
        (default: 0.005 m).    
    atol : positive float
        The accepted error for the end-effector orientation, in degrees
        (default: 5 degrees). 
    noIterMax : positive int
        The maximum number of iterations for the algoritm
        (default: 2000 iterations). 

    Returns
    -------
    q : nd numpy vector or array
        The configuration that solves the IK problem
    """    
		return _IK(self, htm, q0, ptol, atol, noIterMax)

	def jacGeo(self, q = None, axis = 'eef', htm0 = None):
		"""
    Compute the geometric Jacobian for an axis at a given joint and base
    configuration. Also returns the forward kinematics as a by-product.
    Everything is written in the scenario coordinates.

    Parameters
    ----------
    q : nd numpy vector or array
        The manipulator's joint configuration 
        (default: the default joint configuration for the manipulator).
    axis : string
        For which axis you want to compute the FK:
        'eef': for the end-effector
        'dh': for all Denavit-Hartenberg axis
        'com': for all center-of-mass axis
        (default: 'eef').    
    htm0 : 4x4 numpy array or 4x4 nested list
        The robot base's configuration 
        (default: the same as the current htm).

    Returns
    -------
    J : 6xn or nx6xn numpy matrix
        For axis='eef', returns a single 6xn Jacobian. For the other cases, 
        return n Jacobians as a nx6xn numpy matrix.

    FK : 4x4 or nx4x4 numpy matrix
        For axis='eef', returns a single htm. For the other cases, return
        n htms as a nx4x4 numpy matrix.
    """ 
		return _jacGeo(self, q, axis, htm0)


  #######################################
  # Methods for dynamics model
  #######################################

	def dynM(self, q = None):
		"""
    Compute the generalized inertia matrix at a given joint configuration.

    Parameters
    ----------
    q : nd numpy vector or array
        The manipulator's joint configuration, a nD numpy vector or nD array 
        (default: the default joint configuration for the manipulator).
    Returns
    -------
    M : nxn numpy array
        The generalized inertia matrix at the joint configuration q.
    """    
		return _dynM(self, q)

	def dynC(self, qdot, q = None):
		"""
    Compute the generalized Coriolis-Centrifugal torques at a given joint 
    configuration speed and joint configuration.

    Parameters
    ----------
    qdot : nd numpy vector or array
        The manipulator's joint configuration speed. 

    q : nd numpy vector or array
        The manipulator's joint configuration 
        (default: the default joint configuration for the manipulator).

    Returns
    -------
    C : nD numpy vector
        The generalized Coriolis-Centrifugal torques at the joint 
        configuration q and joint configuration speed qdot.
    """     
		return _dynC(self, qdot, q)

	def dynG(self, q = None):
		"""
    Compute the generalized gravity torques at a given joint configuration.

    Parameters
    ----------
    q : nd numpy vector or array
        The manipulator's joint configuration, a nD numpy vector or nD array 
        (default: the default joint configuration for the manipulator).
    Returns
    -------
    G : nD numpy vector
        The generalized gravity torques at the joint configuration q.
    """        
		return _dynG(self, q)

	def dynParam(self, qdot, q = None):
		"""
    Compute all the three dynamic parameters at a given joint configuration
    and joint configuration speed. It is more efficient than calling them
    separatedly.

    Parameters
    ----------
    qdot : nd numpy vector or array
        The manipulator's joint configuration speed .

    q : nd numpy vector or array
        The manipulator's joint configuration 
        (default: the default joint configuration for the manipulator).

    Returns
    -------
    M : nxn numpy array
        The generalized inertia matrix at the joint configuration q.

    G : nD numpy vector
        The generalized gravity torques at the joint configuration q.

    C : nD numpy vector
        The generalized Coriolis-Centrifugal torques at the joint 
        configuration q and joint configuration speed qdot.
    """    
		return _dynParam(self, qdot, q)


  #######################################
  # Methods for control
  #######################################

	def taskFunction(self, FKd, q = None, htm = None):
		"""
    6-dimensional task function for end-effector pose control, given a joint 
    configuration, a base configuration and the desired pose FKd. Everything 
    is written in scenario coordinates.
    Also returns the Jacobian of this function.

    Parameters
    ----------
    Fkd : 4x4 numpy array or 4x4 nested list
        The desired end-effector pose. 
 
    q : nd numpy vector or array
        The manipulator's joint configuration 
        (default: the default joint configuration for the manipulator).

    htm : 4x4 numpy array or 4x4 nested list
        The robot base's configuration 
        (default: the same as the current htm).

    Returns
    -------
    r : 6-dimensional numpy vector
        The task function.

    Jr : 6xn numpy matrix
        The respective task Jacobian.
    """    
		return _taskFunction(self, FKd, q, htm)

  #######################################
  # Methods for simulation
  #######################################

	def genCode(self):
		"""Generate code for injection."""   
		_genCode(self)

  #######################################
  # Robot constructors
  #######################################

	def sDOF(htm = np.identity(4), name = 'sdofRobot'):
		"""
    Create a six-degree of freedom manipulator.

    Parameters
    ----------
    htm : 4x4 numpy array or 4x4 nested list
        The initial base configuration for the robot. 
 
    name : string
        The robot name
        (default: 'sdofRobot').

    htm : 4x4 numpy array or 4x4 nested list
        The robot base's configuration 
        (default: the same as the current htm).

    Returns
    -------
    R : Robot object
        The robot.

    """    
		linkInfo, colModel = _sDOF(htm, name)
		return Robot(linkInfo, htm, name, 'sDOF',colModel)

  #######################################
  # Advanced methods
  #######################################

	def computehgDist(self, obj, h=0.1, g=0.1, q = None, htm = None, oldDistStruct=None, tol = 0.0005, noIterMax = 20):
		"""
    Compute (h,g) distance structure from each one of the robot's link to a 
    'simple' external object (ball, box or cylinder), given a joint and base 
    configuration.

    Use an iterative algorithm, based no h-projections and a modification of 
    Von Neumann's cyclic projection algorithm.

    Parameters
    ----------
    obj : a simple object (ball, box or cylinder)
        The external object for which the distance structure is going to be 
        computed, for each robot link.
    h : positive float
        Smoothing parameter for the robot's links, in meters
        (default: 0.1 m).    
    g : positive float
        Smoothing parameter for the external object
        (default: 0.1 m).
    q : nd numpy vector or array
        The manipulator's joint configuration 
        (default: the default joint configuration for the manipulator).
    htm : 4x4 numpy array or 4x4 nested list
        The robot base's configuration 
        (default: the same as the current htm).
    oldDistStruct : 'DistStruct' object
        'DistStruct' obtained previously for the same robot and external object.
        Can be used to enhance the algorith speed using the previous closest 
        point as an initial guess
        (default: None).
    tol : positive float
        Tolerace for convergence in the iterative algorithm, in meters.
        (default: 0.0005 m).        
    noIterMax : positive int
        The maximum number of iterations for the algoritm
        (default: 20 iterations). 

    Returns
    -------
    distStruct : 'DistStruct' object
        Distance struct for each one of the m objects that compose the robot's
        collision model. Contais m dictionaries. Each one of these dictionaries 
        contains the following entries:
        
        'linkNumber', containing the robot link index for this entries

        'linkColObjNumber', containing the link index for the covering object 
          at that link

        'hgDistance', containing the smoothed hg distance

        'pObj', containing the closest point at the external object

        'pObjCol', containing the closest point at the covering object in the 
          link
        
        'jacDist', containing the Jacobian (gradient) of this distance function       
    """

		return _computehgDist(self, obj, h, g, q, htm, oldDistStruct, tol, noIterMax)

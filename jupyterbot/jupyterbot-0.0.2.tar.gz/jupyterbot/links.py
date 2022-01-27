import numpy as np
from utils import *


class Link:

  #######################################
  # Attributes
  #######################################
  
	@property
	def theta(self):
    """The 'theta' parameter of the Denavit-Hartenberg convention (in rad)"""
		return self._theta

	@property
	def d(self):
    """The 'd' parameter of the Denavit-Hartenberg convention (in meters)"""    
		return self._d

	@property
	def a(self):
    """The 'a' parameter of the Denavit-Hartenberg convention (in meters)"""        
		return self._a

	@property
	def alpha(self):
    """The 'alpha' parameter of the Denavit-Hartenberg convention (in rad)"""     
		return self._alpha

	@property
	def jointNumber(self):
    """The joint number in the kinematic chain."""      
		return self._jointNumber

	@property
	def jointType(self):
    """The joint type (0=revolute, 1=prismatic)."""        
		return self._jointType

	@property
	def centerShift(self):
    """???"""     
		return self._centerShift

	@property
	def mass(self):
    """The link's mass, in kg."""        
		return self._mass

	@property
	def inertiaMatrix(self):
    """The link's inertia matrix, in kg m²."""           
		return self._inertiaMatrix

	@property
	def modelPath(self):
    """Path to the geometric model."""       
		return self._modelPath

	@property
	def colObject(self):
    """Collection of objects that compose the collision model of this link.""" 
		return self._colObject

  #######################################
  # Constructor
  #######################################
      
	def __init__(self, robot, jointNumber, theta, d, alpha, a, jointType,
  jointShift=0, centerShift = np.zeros((3,)), mass=1, inertiaMatrix = np.identity(3), modelPath=""  ):

    #Error handling
		if str(type(robot)) != "<class 'jupyterbot.robot.robot.Robot'>":
			raise Exception("The 'robot' parameter should be a robot handle")

		if str(type(jointNumber)) != "<class 'int'>" or jointNumber<0:
			raise Exception("The 'jointNumber' parameter should be a nonnegative integer")

		if not Utils.isaNumber(theta):
			raise Exception("The 'theta' parameter should be a float")

		if not Utils.isaNumber(d):
			raise Exception("The 'd' parameter should be a float")

		if not Utils.isaNumber(alpha):
			raise Exception("The 'alpha' parameter should be a float")

		if not Utils.isaNumber(a):
			raise Exception("The 'a' parameter should be a float")

		if jointType != 0 and jointType != 1:
			raise Exception("The 'jointType' parameter should be either '0' (rotative) or '1' (prismatic)")

    #Code

		self._robot = robot
		self._jointNumber = jointNumber
		self._theta = theta
		self._d = d
		self._alpha = alpha
		self._a = a
		self._jointType = jointType
		self._colObject = []

		self._jointShift = jointShift
		self._centerShift = np.array(centerShift)
		self._mass = mass 
		self._inertiaMatrix = np.array(inertiaMatrix)
		self._modelPath = modelPath


    #Error handling
		if not Utils.isaNumber(self._jointShift):
			raise Exception("The parameter 'jointShift' should be a float")

		if not Utils.isaVector(self._centerShift,3):
			raise Exception("The parameter 'centerShift' should be a 3D array") 

		if not Utils.isaNumber(self._mass) or self._mass<0 :
			raise Exception("The parameter 'mass' should be a positive float")
          
		if not Utils.isaPDMatrix(self._inertiaMatrix,3):
			raise Exception("The parameter 'inertiaMatrix' should be a symmetric positive definite 3x3 matrix")

		if not (str(type(self._modelPath)) == "<class 'str'>"):
			raise Exception("The parameter 'modelPath' should be a string")

  #######################################
  # Std. Print
  #######################################

	def __repr__(self):
    
		string = "Link "+str(self._jointNumber)+" of robot '"+str(self._robot.name)+"' "

		if self._jointType == 0:
			string += "with rotative joint:\n\n"
			string += " θ (rad): "+str(round(self._robot.q[self._jointNumber],3))+" [variable] \n"
			string += " d (m)  : "+str(self._d)+" \n"
		if self._jointType == 1:
			string += "with prismatric joint:\n\n" 
			string += " θ (rad): "+str(self._theta)+" \n"
			string += " d (m)  : "+str(round(self._robot.q[self._jointNumber],3))+" [variable] \n"
    
		string += " α (rad): "+str(self._alpha)+" \n"
		string += " a (m)  : "+str(self._a)+" \n"
		string += " Link mass (kg): "+str(self._mass)+"\n"  
		string += " Link inertia matrix (kg*m²): \n "+str(self._inertiaMatrix)+"\n" 
		string += " Link model path: "+str(self._modelPath)+"\n"

		return string

  #######################################
  # Methods
  #######################################
  
	def attachColObject(self, obj, htm):

    #Error handling
		if not Utils.isaMatrix(htm,4,4):
			raise Exception("The parameter 'htm' should be a 4x4 homogeneous transformation matrix")


		if not( Utils.isaSimpleObject(obj) ):
			raise Exception("The parameter 'obj' must be either a box, a ball or a cylinder")

		self._colObject.append([obj,htm])
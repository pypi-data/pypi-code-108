from utils import *
import numpy as np

class Cylinder:
  """
  A cylinder object.

  Parameters
  ----------
  htm : 4x4 numpy array or 4x4 nested list
      The object's configuration
      (default: the same as the current HTM).

  name : string
      The object's name
      (default: 'genBall').

  radius : positive float
      The cylinder base radius, in meters.
      (default: 1).    

  height : positive float
      The cylinder's height, in meters
      (default: 1).  

  mass : positive float
      The object's mass, in kg
      (default: 1).  

  color : string
      The object's color, in HTML compatible string
      (default: "red").              
  """

  #######################################
  # Attributes
  #######################################

  @property
  def radius(self):
    """The cylinder base radius, in meters."""
    return self._radius

  @property
  def height(self):
    """The cylinder height, in meters."""
    return self._height

  @property
  def name(self):
    """The object name."""     
    return self._name

  @property
  def htm(self):
    """
    Object pose. 
    A 4x4 homogeneous transformation matrix written is scenario coordinates.
    """     
    return np.array(self._htm)  

  @property
  def mass(self):
    """Mass of the object, in kg.""" 
    return self._mass 

  @property
  def color(self):
    """Color of the object, HTML compatible""" 
    return self._color
  #######################################
  # Constructor
  #######################################
  
  def __init__(self, htm = np.identity(4), name="genCyl", radius=1, height=1, mass=1, color="red"):

    #Error handling
    if not Utils.isaMatrix(htm,4,4):
      raise Exception("The parameter 'htm' should be a 4x4 homogeneous transformation matrix")

    if not Utils.isaNumber(mass) or mass<0 :
      raise Exception("The parameter 'mass' should be a positive float")

    if not Utils.isaNumber(radius) or radius<0 :
      raise Exception("The parameter 'radius' should be a positive float")

    if not Utils.isaNumber(height) or height<0 :
      raise Exception("The parameter 'height' should be a positive float")

    if not (str(type(name)) == "<class 'str'>"):
      raise Exception("The parameter 'name' should be a string")     

    if not Utils.isaColor(color):
      raise Exception("The parameter 'color' should be a color") 
    #end error handling
    
    self._radius = radius
    self._height = height
    self._color = color
    self._htm = np.array(htm)
    self._strColor = "'" + str(self._color) + "'"
    self._name = name
    self._strName = "'" + name + "'"
    self._mass = 1
    self._isaSimpleObject = True
    
    #Set initial total configuration
    self.setConfig(self._htm)

  #######################################
  # Std. Print
  #######################################

  def __repr__(self):

    string = "Cylinder with name '"+self._name+"': \n\n"
    string += " Radius (m): "+str(self._radius)+"\n"
    string += " Height (m): "+str(self._height)+"\n"
    string += " Color: "+str(self._color)+"\n"    
    string += " Mass (kg): "+str(self._mass)+"\n"
    string += " HTM: \n"+str(self._htm)+"\n"
    
    return string


  #######################################
  # Methods
  #######################################


  def addConfig(self, htm = None):
    """
    Add a single configuration to the object's animation queue.

    Parameters
    ----------
    htm : 4x4 numpy array or 4x4 nested list
        The object's configuration
        (default: the same as the current HTM).

    Returns
    -------
    None
    """       
    if htm is None:
      htm = self._htm

    #Error handling
    if not Utils.isaMatrix(htm,4,4):
      raise Exception("The parameter 'htm' should be a 4x4 homogeneous transformation matrix")
    #end error handling

    f = [ htm[0][0], htm[0][2], -htm[0][1], htm[0][3],
          htm[1][0], htm[1][2], -htm[1][1], htm[1][3],
          htm[2][0], htm[2][2], -htm[2][1], htm[2][3],
          0        ,         0,         0,         1]

    self._htm = htm
    self._frames.append(f)

  def setConfig(self, htm = None):
    """
    Reset object's animation queue and add a single configuration to the 
    object's animation queue.

    Parameters
    ----------
    htm : 4x4 numpy array or 4x4 nested list
        The object's configuration
        (default: the same as the current HTM).

    Returns
    -------
    None
    """
    if htm is None:
      htm = self._htm

    #Error handling
    if not Utils.isaMatrix(htm,4,4):
      raise Exception("The optional parameter 'htm' should be a 4x4 homogeneous transformation matrix")
    #end error handling      

    self._frames = []
    self.code = ''
    self.addConfig(htm)

  def genCode(self):
    """Generate code for injection.""" 
    self._strFrames = str(self._frames)
    self.code ='''
		const ''' + self._name + ''' = new Cylinder(''' + self._strName + ''',''' + str(self._radius) + ''',''' + str(self._height) + ''',''' + self._strColor + ''',''' + self._strFrames + ''');
		sceneElements.push(''' + self._name + ''');
		//USER INPUT GOES HERE
		'''

  #Compute inertia matrix with respect to the inertia frame
  def inertiaMatrix(self, htm = None):
    """
    The 3D inertia matrix of the object, written in the 'inertia frame', that is, a frame attached to the center of mass of the object which has the same orientation as the scenario frame.

    Parameters
    ----------
    htm : 4x4 numpy array or 4x4 nested list
        The object's configuration for which the inertia matrix will be computed
        (default: the same as the current HTM).

    Returns
    -------
     inertiaMatrix : 3x2 numpy array
        The 3D inertia matrix.
    """  

    if htm is None:
      htm = self._htm

    #Error handling
    if not Utils.isaMatrix(htm,4,4):
      raise Exception("The optional parameter 'htm' should be a 4x4 homogeneous transformation matrix")
    #end error handling      

    Ixx = (1/12)*self._mass*(3*self._radius*self._radius + self._height*self._height)
    Iyy = (1/12)*self._mass*(3*self._radius*self._radius + self._height*self._height)   
    Izz = (1/2)*self._mass*(self._radius*self._radius)
    Q = htm[0:3,0:3]

    return np.transpose(Q) @ np.diag([Ixx, Iyy, Izz]) @ Q 

  def copy(self):
    """Return a deep copy of the object, without copying the animation frames."""    
    return Cylinder(self.htm, self.name+"_copy", self.radius, self.height, self.mass, self.color)
    
  #Compute the h projection of a point into an object
  def hProjection(self, point, h = 0.001, htm = None):
    """
    The h projection of a point in the object, that is, the 
    h-closest point in the object to a point 'point'.

    Parameters
    ----------
    point : 3D vector
        The point for which the projection will be computed.

    h : positive float
        Smoothing parameter, in meters
        (defalt: 0.001 m)

    htm : 4x4 numpy array or 4x4 nested list
        The object's configuration
        (default: the same as the current HTM).            

    Returns
    -------
     projPoint : 3D vector
        The h-projection of the point 'point' in the object.

     d : positive float
        The h-distance between the object and 'point'.     
    """  

    if htm is None:
      htm = self._htm

     #Error handling
    if not Utils.isaMatrix(htm,4,4):
      raise Exception("The optional parameter 'htm' should be a 4x4 homogeneous transformation matrix")

    if not Utils.isaVector(point,3):
      raise Exception("The parameter 'point' should be a 3D vector")

    if not Utils.isaNumber(h) or h<=0:
      raise Exception("The optional parameter 'h' should be a positive number")
    #end error handling        
    tpoint = np.transpose(htm[0:3,0:3]) @ (point - htm[0:3,3])

    delta = 0.001

    r = sqrt( tpoint[0]*tpoint[0] + tpoint[1]*tpoint[1])

    drf = Utils.funCir(r+delta,h, self.radius)
    drb = Utils.funCir(r-delta,h, self.radius)

    dzf = Utils.funInt(tpoint[2]+delta,h, 0.5*self.height)
    dzb = Utils.funInt(tpoint[2]-delta,h, 0.5*self.height)

    dr = (drf - drb)/(2*delta)

    x = tpoint[0] - dr*tpoint[0]/(r+0.00001)
    y = tpoint[1] - dr*tpoint[1]/(r+0.00001)    
    z = tpoint[2] - (dzf-dzb)/(2*delta)

    d = 0.5*(drf+drb+dzf+dzb) 

    return htm[0:3,0:3] @ np.array([x,y,z]) + htm[0:3,3], d      
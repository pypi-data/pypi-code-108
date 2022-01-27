from utils import *
import numpy as np

class Box:
  """
  A box object.

  Parameters
  ----------
  htm : 4x4 numpy array or 4x4 nested list
      The object's configuration
      (default: the same as the current HTM).

  name : string
      The object's name
      (default: 'genBall').

  width : positive float
      The object's width, in meters
      (default: 1).    

  depth : positive float
      The object's depth, in meters
      (default: 1).  

  height : positive float
      The object's height, in meters
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
  def width(self):
    """The box width, in meters."""  
    return self._width

  @property
  def height(self):
    """The box height, in meters."""      
    return self._height

  @property
  def depth(self):
    """The box depth, in meters."""     
    return self._depth

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
  
  def __init__(self, htm = np.identity(4), name="genBox", width=1, height=1, depth=1, mass=1, color="red"):

    #Error handling
    if not Utils.isaMatrix(htm,4,4):
      raise Exception("The parameter 'htm' should be a 4x4 homogeneous transformation matrix")

    if not Utils.isaNumber(mass) or mass<0 :
      raise Exception("The parameter 'mass' should be a positive float")

    if not Utils.isaNumber(width) or width<0 :
      raise Exception("The parameter 'width' should be a positive float")

    if not Utils.isaNumber(height) or height<0 :
      raise Exception("The parameter 'height' should be a positive float")

    if not Utils.isaNumber(depth) or depth<0 :
      raise Exception("The parameter 'depth' should be a positive float")

    if not (str(type(name)) == "<class 'str'>"):
      raise Exception("The parameter 'name' should be a string")     

    if not Utils.isaColor(color):
      raise Exception("The parameter 'color' should be a color") 
    #end error handling
    
    self._width = width
    self._height = height
    self._depth = depth
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

    string = "Box with name '"+self._name+"': \n\n"
    string += " Width (m): "+str(self._width)+"\n"
    string += " Depth (m): "+str(self._depth)+"\n"
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
		const ''' + self._name + ''' = new Box(''' + self._strName + ''',''' + str(self.width) + ''',''' + str(self.height) + ''',''' + str(self.depth) + ''',''' + self._strColor + ''',''' + self._strFrames + ''');
		sceneElements.push(''' +  self._name + ''');
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
    
    Ixx = (1/12)*self._mass*(self._height*self._height + self._depth*self._depth)
    Iyy = (1/12)*self._mass*(self._width*self._width + self._depth*self._depth)    
    Izz = (1/12)*self._mass*(self._height*self._height + self._width*self._width)
    Q = htm[0:3,0:3]

    return np.transpose(Q) @ np.diag([Ixx, Iyy, Izz]) @ Q

  def copy(self):
    """Return a deep copy of the object, without copying the animation frames."""
    return Box(self.MTH, self.name+"_copy", self.width, self.height, self.depth, self.mass, self.color)
    
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

    dxf = Utils.funInt(tpoint[0]+delta,h, 0.5*self.width )
    dxb = Utils.funInt(tpoint[0]-delta,h, 0.5*self.width )

    dyf = Utils.funInt(tpoint[1]+delta,h, 0.5*self.depth )
    dyb = Utils.funInt(tpoint[1]-delta,h, 0.5*self.depth ) 

    dzf = Utils.funInt(tpoint[2]+delta,h, 0.5*self.height)
    dzb = Utils.funInt(tpoint[2]-delta,h, 0.5*self.height)

    d = 0.5*(dxf+dxb+dyf+dyb+dzf+dzb)
    x = tpoint[0] - (dxf-dxb)/(2*delta)
    y = tpoint[1] - (dyf-dyb)/(2*delta)
    z = tpoint[2] - (dzf-dzb)/(2*delta)

    return htm[0:3,0:3] @ np.array([x,y,z]) + htm[0:3,3], d
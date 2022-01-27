from math import *
import numpy as np
from colour import Color
import plotly.express as px

class Utils:
    """A library that contains some utilities for jupyterbox"""

  #######################################
  # Constants
  #######################################

    _PI  = 3.1415926
    _SQRTHALFPI = 1.2533141
    _SQRT2 = 1.4142135
    _CONSTJA = 2.7889
    _CONSTI0HAT1 = 0.24273
    _CONSTI0HAT2 = 0.43023

  #######################################
  # Basic functions
  #######################################

    def S(v):
      """
      Returns a 3x3 matrix that implements the cross product for a 3D vector  
      as a matricial product, that is, a matrix S(v) such that for any other 
      3D column  vector w, S(v)w = cross(v,w).
      
      Parameters
      ----------
      v : a 3D vector
          The vector for which the S matrix will be created.

      Returns
      -------
      S : 3x3 numpy matrix
          A matrix that implements the cross product with v.
      """       
      vv = np.reshape(v,(3,))
      return np.array([[ 0   , -vv[2] ,  vv[1]],
                       [ vv[2],  0    , -vv[0]],  
                       [-vv[1],  vv[0] ,  0   ]])


    def rot(axis, angle):
      """
      Homogeneous transformation matrix that represents the rotation of an
      angle in an axis.
      
      Parameters
      ----------
      axis : a 3D vector
          The axis of rotation.
      
      angle: float
          The angle of rotation, in radians.

      Returns
      -------
      T : 4x4 numpy matrix
          The homogeneous transformation matrix.
      """          
      a = np.reshape( axis,(3,))
      a = a/np.linalg.norm(a)
      K = Utils.S(a)
      Q = np.identity(3)+sin(angle)*K + (1-cos(angle))*(K @ K)
      return np.hstack([np.vstack([Q, np.array([0,0,0])]),np.array([[0],[0],[0],[1]])])

    def trn(vector):
      """
      Homogeneous transformation matrix that represents the displacement
      of a vector
      
      Parameters
      ----------
      vector : a 3D vector
          The displacement vector.
      
      Returns
      -------
      T : 4x4 numpy matrix
          The homogeneous transformation matrix.
      """      
      v = np.reshape(vector,(3,))
      return np.hstack([np.vstack([np.identity(3), 
            np.array([0,0,0])]),np.array([[v[0]],[v[1]],[v[2]],[1]])])

    def rotx(angle):
      """
      Homogeneous transformation matrix that represents the rotation of an
      angle in the 'x' axis.
      
      Parameters
      ----------
      angle: float
          The angle of rotation, in radians.

      Returns
      -------
      T : 4x4 numpy matrix
          The homogeneous transformation matrix.
      """      
      return Utils.rot([ 1,0,0] , angle )
    
    def roty(angle):
      """
      Homogeneous transformation matrix that represents the rotation of an
      angle in the 'y' axis.
      
      Parameters
      ----------
      angle: float
          The angle of rotation, in radians.

      Returns
      -------
      T : 4x4 numpy matrix
          The homogeneous transformation matrix.
      """        
      return Utils.rot( [0,1,0] , angle )   
  
    def rotz(angle):
      """
      Homogeneous transformation matrix that represents the rotation of an
      angle in the 'z' axis.
      
      Parameters
      ----------
      angle: float
          The angle of rotation, in radians.

      Returns
      -------
      T : 4x4 numpy matrix
          The homogeneous transformation matrix.
      """        
      return Utils.rot( [0,0,1] , angle)


    def axisAngle(T):
      """
      Given an homogeneous transformation matrix representing a rotation, 
      return the rotation axis angle.
      
      Parameters
      ----------
      T: 4X4 numpy array or nested list 
          Homogeneous transformation matrix of the rotation.

      Returns
      -------
      axis : 3D numpy vector
          The rotation axis.

      angle : float
          The rotation angle, in radians.        
      """        
      Q = T[0:3,0:3]
      trace = Q[0,0]+Q[1,1]+Q[2,2]
      angle = acos((trace-1)/2)
      G = Q @ Q -2*cos(angle)*Q + np.identity(3)
      ok = False
      while not ok:
          v = np.random.uniform(-100,100, size=(3,))
          w = np.random.uniform(-100,100, size=(3,))
          r = G @ v
          nr = np.linalg.norm(r)
          prod = np.transpose(w) @ r
          if nr>0.01:
            ortr = w - prod * r/(nr*nr)
            axis = Utils.S(ortr) @ ( Q @ ortr)
            naxis = np.linalg.norm(axis)
            ok = naxis > 0.01

      axis = axis/naxis
      return axis, angle

    def dpinv(A,eps):
      """
      Compute the damped pseudoinverse of the matrix A.
      
      Parameters
      ----------
      A: nxm numpy array
          The matrix to compute the damped pseudoinverse.
      
      eps: positive float
          The damping factor.
      Returns
      -------
      pinvA: mxn numpy array
          The damped pseudoinverse of A.    
      """     
      n = len(A[0,:])
      return np.linalg.inv( np.transpose(A) @ A + eps*np.identity(n)) @ np.transpose(A)

  #######################################
  # Type check functions
  #######################################

    def isaNumber(x):
      """
      Check if the argument is a float or int number
      
      Parameters
      ----------
      x: object
          Object to be verified.
      
      Returns
      -------
      isType: boolean
          If the object is of the type.   
      """   

      return str(type(x)) == "<class 'int'>" or str(type(x)) == "<class 'float'>"

    def isaNaturalNumber(x):
      """
      Check if the argument is a natural number (integer and >=0)
      
      Parameters
      ----------
      x: object
          Object to be verified.
      
      Returns
      -------
      isType: boolean
          If the object is of the type.   
      """   

      return str(type(x)) == "<class 'int'>" and x >= 0

    def isaMatrix(x , n = None, m = None):
      """
      Check if the argument is a nxm matrix of floats.
      
      Parameters
      ----------
      x: object
          Object to be verified.

      n: positive int
          Number of rows
          (default: it does not matter).

      m: positive int
          Number of columns
          (default: it does not matter).

      Returns
      -------
      isType: boolean
          If the object is of the type.   
      """  

      value = str(type(x)) == "<class 'numpy.ndarray'>" or str(type(x)) == "<class 'list'>"

      if str(type(x)) == "<class 'numpy.ndarray'>":
        shp = np.shape(x)
        if len(shp)==1:
          if (not n is None) and (not m is None): 
            value = (shp[0]==n and m==1) or (shp[0]==m and n==1)

          if (not n is None) and (m is None): 
            value = (shp[0]==n) or (n==1)

          if (n is None) and (not m is None): 
            value = (m==1) or (shp[0]==m)

          if (n is None) and (m is None): 
            value = True

        if len(shp)==2:
          if (not n is None) and (not m is None): 
            value = shp[0]==n and shp[1]==m

          if (not n is None) and (m is None): 
            value = shp[0]==n 

          if (n is None) and (not m is None): 
            value = shp[1]==m

          if (n is None) and (m is None): 
            value = True

        if len(shp)>2:
          value = False

      if str(type(x)) == "<class 'list'>":
        return Utils.isaMatrix(np.array(x),n,m)
      else:
        return value

    def isaVector(x , n= None):
      """
      Check if the argument is a n vector of floats.
      
      Parameters
      ----------
      x: object
          Object to be verified.

      n: positive int
          Number of elements
          (default: it does not matter).

      Returns
      -------
      isType: boolean
          If the object is of the type.   
      """
      return Utils.isaMatrix(x,n,1) or Utils.isaMatrix(x,1,n)

    def isaPDMatrix(x , n = None):
      """
      Check if the argument is a symmetric nxn positive (semi)-definite matrix.
      
      Parameters
      ----------
      x: object
          Object to be verified.

      n: positive int
          Dimension of the square matrix
          (default: it does not matter).
    
      Returns
      -------
      isType: boolean
          If the object is of the type.   
      """
      value = Utils.isaMatrix(x,n,n)

      if value:
        value = np.allclose(x, np.transpose(x), rtol=1e-05, atol=1e-08)

      if value:
        try:
          np.linalg.cholesky(x)
        except:
          value=False
      
      return value

    def isaColor(color):
      """
      Check if the argument is a HTML-compatible string that represents a color.
      
      Parameters
      ----------
      x: object
          Object to be verified.
      
      Returns
      -------
      isType: boolean
          If the object is of the type.   
      """

      try:
        color = color.replace(" ", "")
        Color(color)
        return True
      except ValueError: 
        return False

    def isaSimpleObject(obj):
      """
      Check if the argument is a ball, box or cylinder.
      
      Parameters
      ----------
      x: object
          Object to be verified.
      
      Returns
      -------
      isType: boolean
          If the object is of the type.   
      """      
      try:
        return obj._isaSimpleObject
      except:
        return False

  #######################################
  # Plotting functions
  #######################################

    def plot(xv , yv, title="", xname="x", yname="y", labels="" ):

      fig = px.line(width=800, height=400)

      #Error handling


      if not Utils.isaVector(xv):
        raise Exception("The parameter 'xv' should be a vector")

      m = max(np.shape(xv))

      if not Utils.isaMatrix(yv,None,m):
        raise Exception("The parameter 'yv' should be a matrix with "+str(m)+" columns.")

      n = 1 if len(np.shape(yv))==1 else np.shape(yv)[0]

      listNames=[]

      if str(type(labels)) == "<class 'str'>":
        for i in range(n):
          listNames.append(labels+"_"+str(i+1))

      else:
        if str(type(labels)) == "<class 'list'>" and len(labels)==n:
          for i in range(n):
            if str(type(labels[i])) == "<class 'str'>":
              listNames.append(labels[i])
            else:
              raise Exception("Optional parameter 'labels' must be either a string or a list of "+str(n)+" strings")
        else:
          raise Exception("Optional parameter 'labels' must be either a string or a list of "+str(n)+" strings")


      #end error handling
      if n>1:
        for i in range(n):
          fig.add_scatter(x=xv, y=yv[i], mode="lines", name=listNames[i])
      else:
          fig.add_scatter(x=xv, y=yv, mode="lines", name=listNames[0])

      fig.update_xaxes(title_text=xname)
      fig.update_yaxes(title_text=yname)
      fig.show()

      return fig

  #######################################
  # Distance computation functions
  #######################################

    def _funJ(u):
      return Utils._CONSTJA/((Utils._CONSTJA-1)*sqrt(Utils._PI*u*u) + sqrt(Utils._PI*u*u+Utils._CONSTJA*Utils._CONSTJA))

    def funInt( v, h, L):
      v = abs(v)
      if v<=L:
        A1 = exp(-(L-v)*(L-v)/(2*h*h))*Utils._funJ((v-L)/(Utils._SQRT2*h))
        A2 = exp(-(L+v)*(L+v)/(2*h*h))*Utils._funJ((v+L)/(Utils._SQRT2*h))
        return -h*h*log(Utils._SQRTHALFPI*(h/(2*L))*(2-A1-A2))
      else:
        A1 = Utils._funJ((v-L)/(Utils._SQRT2*h))
        A2 = exp(-2*L*v/(h*h))*Utils._funJ((v+L)/(Utils._SQRT2*h))
        return 0.5*(v-L)*(v-L) -h*h*log(Utils._SQRTHALFPI*(h/(2*L))*(A1-A2))

    def _funI0hat(u):
      return pow(1+0.25*u*u,-0.25)*(1 + Utils._CONSTI0HAT1*u*u)/(1 + Utils._CONSTI0HAT2*u*u)

    def _funf(nu, rho):
      A1 = exp(-0.5*(rho-nu)*(rho-nu))
      A2 = exp(-0.5*(rho+nu)*(rho+nu))
      return rho*(A1+A2)*Utils._funI0hat(rho*nu)

    def _funfhat(nu, rho, rhobar):
      A1 = exp(-0.5*(rho-nu)*(rho-nu) + 0.5*(rhobar-nu)*(rhobar-nu))
      A2 = exp(-0.5*(rho+nu)*(rho+nu) + 0.5*(rhobar-nu)*(rhobar-nu))
      return rho*(A1+A2)*Utils._funI0hat(rho*nu)

    def funCir(v, h, R):

      v = abs(v) 
      N=7
      node= [0.94910, -0.74153, -0.40584, 0, 0.40584, 0.74153, 0.94910]
      weight= [0.12948, 0.27970, 0.38183, 0.4179, 0.38183, 0.27970, 0.12948]

      if v <= R:
        F_low = max(0,sqrt((v/h)*(v/h)+1)-3)
        F_up = min(R/h, sqrt((v/h)*(v/h)+1)+3)
        delta = 0.5*(F_up-F_low)
        y=0
        for i in range(N):
          y = y + weight[i]*Utils._funf(v/h,F_low + delta*(node[i]+1))

        y = delta * y
        return -h*h*log(y*(h/R)*(h/R))
      else:
        F_low = 0
        F_up = R/h
        delta = 0.5*(F_up-F_low)
        rhobar = F_low + delta *(node[N-1]+1)
        y=0;
        for i in range(N):
          y = y + weight[i]*Utils._funfhat(v/h,F_low + delta *(node[i]+1) , rhobar)

        y = delta * y
        return 0.5*(v-h*rhobar)*(v-h*rhobar)-h*h*log(y*(h/R)*(h/R))
      
    def funSph( v, h, R):  

      v = abs(v);
      C = 3*(h*h)/(2*R*R*R)

      if v <= R :
        if v==0:
          return -h*h*log(C*(-2*R*exp(-(R*R)/(2*h*h)) + 2*R*exp(-Utils.funInt(0,h,R)/(h*h))))
        else:
          A1 = exp(-((R+v)*(R+v)/(2*h*h)))
          A2 = exp(-((R-v)*(R-v)/(2*h*h)))
          return -h*h*log(C*(h*h*(A1-A2)/v + 2*R*exp(-Utils.funInt(v,h,R)/(h*h))))
   
      else:
        A1 = exp(-(2*R*v/(h*h)))
        A2 = 1
        return 0.5*(v-R)*(v-R)-h*h*log(C*(h*h*(A1-A2)/v + 2*R*exp((0.5*(v-R)*(v-R)-Utils.funInt(v,h,R))/(h*h))))  

    def computehgDist(objA, objB, h=0.001, g = 0.001, pA = None, tol = 0.001, maxIter=20):
    
      if pA is None:
        pA = np.random.uniform(-3,3, size=(3,))

      #Error handling

      if not Utils.isaSimpleObject(objA):
        raise Exception("The parameter 'objA' must be either a box, a ball or a cylinder")

      if not Utils.isaSimpleObject(objB):
        raise Exception("The parameter 'objB' must be either a box, a ball or a cylinder")

      if not Utils.isaNumber(h) or h<=0:
        raise Exception("The optional parameter 'h' must be nonnegative number")

      if not Utils.isaNumber(g) or g<=0:
        raise Exception("The optional parameter 'g' must be nonnegative number")

      if not Utils.isaVector(pA,3):
        raise Exception("The optional parameter 'pA' must be a 3D vector")

      if not Utils.isaNumber(tol) or tol<=0:
        raise Exception("The optional parameter 'tol' must be a nonnegative number")

      if not Utils.isaNaturalNumber(maxIter):
        raise Exception("The optional parameter 'maxIter' must be a nonnegative integer")

      #end error handling

      algEnd=False
      i=0

      while (not algEnd) and i < maxIter:
        pAant = pA
        pB, dpA = objB.hProjection(pA,g)
        pA, dpB = objA.hProjection(pB,h)
        algEnd = np.linalg.norm(pA-pAant) <tol
        i+=1

      dist = np.linalg.norm(pA-pB)
      d = sqrt(2*(dpA+dpB - 0.5*dist*dist))

      return pA, pB, d
      
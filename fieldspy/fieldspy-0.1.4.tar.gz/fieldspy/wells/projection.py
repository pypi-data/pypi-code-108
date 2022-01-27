import numpy as np 
import pandas as pd  
from typing import Union
from pydantic import validate_arguments
from typing import Tuple

@validate_arguments
def unit_vector(azi:float):
    """
    Get the unit vector2D of a given azimuth
    Input:
        azi -> (int,float) Azimuth in Degrees
    Return:
        u -> (np.ndarray) numpy array with a shape of (2,1) with the x and y components of unit vector
    """
    if azi >270:
        alpha = 450 - azi
    else:
        alpha = 90 - azi
    alpha_rad = np.deg2rad(alpha)
    x = np.cos(alpha_rad)
    y = np.sin(alpha_rad)
    p = np.array([[x,y]])
    return p

@validate_arguments(config=dict(arbitrary_types_allowed=True))
def projection_1d(x:np.ndarray, azi:float, center:Tuple[float,float]=None):
    """
    Get the 1D projection of a series of 2D Coordinates within a given azimuth direction

    Input:
        x -> (np.ndarray) Numpy array of shape (m,2) being m the number of coordinates
        azi -> (int,float) Azimuth in Degrees
        center -(list,np.ndarray)  list or numpy array with the center 
    Return:
        u -> (np.ndarray) numpy array with a shape of (m,1)
    """
    
    if center:
        center = np.atleast_1d(center)
    else:
        center = x.mean(axis=0)
    #Normalize the coordinates by substracting the average coordinates

    x = x - center

    # Get the unit vector
    u = unit_vector(azi)

    # Projection over the azimuth direction
    cv = np.squeeze(np.dot(x,u.T))

    return cv, (center[0], center[1])

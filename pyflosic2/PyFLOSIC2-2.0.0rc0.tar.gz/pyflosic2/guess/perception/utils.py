import numpy

""" Utility functions """

def check_spin(symbols,elec_symbols=['X','He']):
    """
        Check spin
        ----------
        Get Na and Nb from current symbols.
    """
    sym_fod1, sym_fod2 = elec_symbols
    values, counts = numpy.unique(numpy.array(symbols),return_counts=True)
    Na = counts[values==sym_fod1]
    Nb = counts[values==sym_fod2]
    spin = abs(Na - Nb)
    M = spin + 1
    return Na, Nb, M

def perpendicular_vector(v):
    """
        perpendicular vector
        --------------------
        
        Output 
        ------
        app : numpy.array(), arbitary perpendicular point (app) 
    """
    if v[1] == 0 and v[2] == 0:
        if v[0] == 0:
            raise ValueError('zero vector')
        else:
            return numpy.cross(v, [0, 1, 0])
    return numpy.cross(v, [1, 0, 0])

def rotation_matrix(axis, theta):
    """
        Rotation matrix 
        ---------------
        Return the rotation matrix associated with counterclockwise rotation about
        the given axis by theta radians.

        Input 
        -----
        axis:   numpy.array(), rotation axis 
        theta:  float(), rotation angles [radians] 

    """
    axis = numpy.asarray(axis)
    axis = axis / numpy.sqrt(numpy.dot(axis, axis))
    a = numpy.cos(theta / 2.0)
    b, c, d = -axis * numpy.sin(theta / 2.0)
    aa, bb, cc, dd = a * a, b * b, c * c, d * d
    bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
    return numpy.array([[aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)],
                     [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)],
                     [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc]])



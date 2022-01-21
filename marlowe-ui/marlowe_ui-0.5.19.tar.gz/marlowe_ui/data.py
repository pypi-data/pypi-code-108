class Error(Exception):
    pass

class _Elem(object):
    """Atomic element data used in &Atom record"""
    def __init__(self):
        self.type_ = "''" # symoble name, 2-chars.
        self.z = 1.0 # atomic number
        self.w = 1.0 # atomic mass
        self.inel = 4 # inelastic energy loss model
        self.equit = 0 # minum kinetic energy for an atom to continue in motion

class _Atom(object):
    """&ATOM record"""
    def __init__(self):
        """initialize and set default value"""
        self.ntype = 0  # number of atoms up to 5
        # properties for each atom
        self.elems = []
        # record common parameters
        self.lox = 0 # binding energy model
        self.ebnd = [0.0, 0.0, 0.0] # energy parameters for binding model
        self.dist = 1.0 # The distance in units of BASE defining the size of the neighborhood for the damage-dependent binding model 
        # lattice assignment
        self.locks = [] # number of 
        self.orders = [] # [list of (I, J, Weight)]
        

    
class Data(object):
    """marlowe input data"""
    def __init__(self):
        self.comment1 = '' # comment for 1st line
        self.comment2 = '' # comment for 2nd line

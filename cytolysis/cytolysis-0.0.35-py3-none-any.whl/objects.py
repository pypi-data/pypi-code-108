# /usr/bin/python3
####### PACKAGES
from . import anutils as an
import numpy as np



# Check if we can plot stuff
__IPV__ = False
try:
    import ipyvolume as ipv
    __IPV__ = True
except:
    print("Unable to import Ipyvolume")


### This should definitely be in a yaml file
# No really, how stupid is that !!!!
__N_DIM__= 3
# This is just convenient
__NARR__= np.array([None])


# a generic class for an object set
class Object_set(list):
    """ Object_set
        A class that contains a list of objects plus extra methods and properties
        
    """
    def __init__(self, *args, id=1,
                 config=None, name=None,  read=None, type=None, dim=__N_DIM__, **kwargs):
        list.__init__(self)

        # Filling info
        self.name = name
        self.id = id
        self.type = type
        self.plots = []
        self.dim = dim
        # Reading properties
        self.properties = an.get_prop_dicts(config, type=type, name=name)

        # We allow a custom constructor
        if read is not None:
            read(self, *args, **kwargs)
        else:
            self.read_objects(*args, **kwargs)

    def read_objects(self, *args, reports=None, build=None, **kwargs):
        """
            Reads from config file into a dictionary repoints of numpy arrays
            We expect somthing like :
            repoints["position"] = [[...]]
            repoints["force"] = [[...]]
        """
        if reports is None:
            reports = {}

        repoints = {}

        for kind, lines in reports.items():
            repoints[kind] = np.loadtxt(lines, comments="%")

        if build is not None:
            build(self, *args, repoints=repoints, name=self.name, **kwargs)
        else:
            self.build_objects(*args, repoints=repoints, name=self.name, **kwargs)

    def build_objects(self,*args, repoints=None, name=None, **kwargs ):
        """
            Build from the numpy arrays
            Specific to an object type
        """
        if repoints is None:
            repoints = {}
        if name is None:
            name = self.name
        if "position" in repoints.keys():
            points = repoints["position"]
            if len(points.shape)>1:
                for i, pts in enumerate(points):
                    id = pts[1]
                    position = pts[2:2+__N_DIM__]
                    self.append(Object(*args, position=position, id=id, name=name, **kwargs))
            else:
                id = points[1]
                position = points[2:2 + __N_DIM__]
                self.append(Object(*args, position=position, id=id, name=name, **kwargs))


    def analyze(self, obj, analyzer=None, *args, **kwargs):
        """
            Generic analyzer
                wraps user specified analysis
        """
        #analysis = {'id' : obj.id}
        analysis = {}
        if analyzer is not None:
            for name, func in analyzer.items():
                analysis[name] = func(obj)

        return analysis

    def plot(self,*args, sorter=None, plotter=None, **kwargs):
        """
            Plots from Object set, with a possibilty to sort which object to sort
            Saved ploted items to Object_set.plots
        """
        if __IPV__:
            # Do we need to sort which objects to plot ?
            if sorter is not None:
                objs = filter(sorter, self)
            else:
                objs = self

            # Is there a custom plotter ?
            if plotter is not None:
                self.plots.extend( plotter(objs, *args, **kwargs))
                return True
            else:
                self.plots.extend( self.plot_objs(objs, *args, **kwargs) )
                return True
        else:
            return False

    def plot_objs(self, objs, *args, **kwargs):
        """
            Plot objs is called by Object_set's plot.
             A method to plot a list of objects
        """
        try:
            positions=np.array([obj.position for obj in objs])
            if self.dim==3:
                s = ipv.scatter(positions[:,0], positions[:,1], positions[:,2], **kwargs)
            elif self.dim==2:
                s = ipv.scatter(positions[:, 0], positions[:, 1], 0, **kwargs)
            return [s]
        except:
            print("Did not manage to plot objects %s. Maybe object.position is not defined" %self.name)
        return []



# A class to contain a single object :
class Object():
    """ Object
        Generic object, not completely useless
        Most objects need id and position
        """

    def __init__(self, *args,  id=1, position=None, **kwargs):
        self.id = id
        self.position = position


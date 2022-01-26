# /usr/bin/python3
####### PACKAGES
import numpy as np
from .objects import Object_set

# This is just convenient
__NARR__= np.array([None])

# Check if we can plot stuff
__IPV__ = False
try:
    import ipyvolume as ipv
    __IPV__ = True
except:
    print("Unable to import Ipyvolume")

# a bit of cleanup needed for creation
class Fiber_set(Object_set):
    """ Fiber_set
        A class that contains a list of filaments plus extra methods and properties
        Built upon the Object_set class, itself a class derived from List
    """
    def __init__(self, *args, id=1, config=None, name="fiber", read=None,
                 build=None, type="fiber", **kwargs):
        # We allow a custom constructor
        if build is None:
            build = self.build_fibers

        Object_set.__init__(self, *args, name=name, id=id, type=type,
                            config=config, build=build, **kwargs)


    def build_fibers(self,*args, repoints=None , **kwargs):
        """
            A specific function to build the fibers from the reports
        """
        ids = __NARR__
        if repoints is None:
            repoints = {}
        keys = repoints.keys()

        # cheapest option first... yeah i'm such a cheapstake
        if 'fibers' in keys:
            ids = np.unique(repoints['fibers'][:, 0])
        elif 'points' in keys:
            ids = np.unique(repoints['points'][:, 0])

        for id in ids:
            pts = __NARR__
            curvs = __NARR__
            keys = repoints.keys()
            length = None
            end2end = None
            position = __NARR__
            direction = __NARR__

            # Here is the dirty job : finding out what is really in the report.
            # aieaieaie !
            if "points" in keys:
                points = repoints["points"]
                points = points[np.where(points[:, 0] == id)]
                pts = points[:,1:self.dim+1]
                curvs = points[:, self.dim+1]

            if "fibers" in keys:
                fib = repoints["fibers"]
                fib = fib[np.where(fib[:, 1] == id)][0]
                length = fib[2]
                position = fib[3:6]
                direction = fib[6:9]
                end2end = fib[9]

            # todo : read other kind of exports
            self.append(Fiber(*args, id=id, points=pts, curvatures = curvs,
                              position=position, direction=direction,
                              length=length, end2end=end2end,   **kwargs))

        # print(len(filaments))

    def analyze(self, fiber, analyzer=None, *args, **kwargs):
        # Wrapper for analysis
        analysis = {'id' : fiber.id}
        if analyzer is not None:
            for name, func in analyzer.items():
                analysis[name] = func(fiber)

        analysis['deformation_energy'] = self.compute_deformation_energy(fiber, *args,  **kwargs)

        return analysis

    def compute_deformation_energy(self, fiber, *args, **kwargs):
        try:
            rigidity=self.properties['rigidity']
        except:
            rigidity=1.0

        segments = get_segments(fiber.points)
        seg_lengths = np.sqrt(np.sum(np.square(segments), axis=1) )

        if fiber.n_points>1:
            mid_lengths = 0.5 * (seg_lengths[0:-1] + seg_lengths[1:])
        else:
            mid_lengths = []

        if fiber.n_points > 2:
            return 0.5 * rigidity * np.sum(np.square(fiber.curvatures[1:-1]) * mid_lengths)
        else:
            return 0.0

    # Plot objs is called by Object_set's plot.
    def plot_objs(self, fibers, *args, **kwargs):
        plots=[]
        for fiber in fibers:
            plots.append(self.plot_fiber(fiber, *args, **kwargs))
        return plots

    def plot_fiber(self, fiber, *args, **kwargs):
        if self.dim == 3:
            p = ipv.plot(fiber.points[:, 0], fiber.points[:, 1], fiber.points[:, 2], **kwargs)
        elif self.dim ==2:
            p = ipv.plot(fiber.points[:, 0], fiber.points[:, 1], 0, **kwargs)
        return p


###### A class to contain a single filament : trying to make it leaner !

class Fiber:
    """ Fiber
        A class that contains a filament. Yep, a whole class for that.
         initiated by providing a numpy array points :
         points is a column of row vectors.
         each row vector is of the format x y z C (3D) or x y C (2D)
         with C the curvature
        """
    #def __new__(cls, *args, points = __NARR__,  **kwargs):
    #    return np.asarray(points).view(cls)

    def __init__(self, *args, name="fiber", id=1, points = None,
                 curvatures=__NARR__, position=None, direction=None,
                 length=None, end2end=None, **kwargs):

        if points is None: points = __NARR__
        if position is None: position = __NARR__
        if direction is None: direction = __NARR__

        self.name = name
        self.points = points
        self.position = position
        self.direction = direction
        self.length = length
        self.end2end = end2end
        self.id = id
        self.n_points = self.points.shape[0]
        self.curvatures = curvatures



def get_segments(points):
    """ get_segment(points)
     computes segment vectors from a numpy array
     Assume point coordinates to be row vectors.
     points is thus a column of points
     """
    n_points = points.shape[0]
    if n_points>1:
        return points[1:, :] - points[0:-1, :]
    else:
        return []

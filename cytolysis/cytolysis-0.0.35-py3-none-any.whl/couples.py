# /usr/bin/python3
####### PACKAGES
import numpy as np
from . import anutils as an
from .objects import Object_set

# Note : having couple as a list is nice but it prevents couples from being an iterator
# that may be a cool thing to do if we want to save memory
# couple could be an iterator, with some things built lazily ?
# .... This is clearly overthinking !
class Couple_set(Object_set):
    """ Couple_set
        A class that contains a list of couples plus extra methods and properties
        
    """
    def __init__(self, *args, id=1,
                 config=None, hand1_props=None, hand2_props=None, type="couples",
                 name="couple", build=None, **kwargs):

        if build is None:
            build = self.build_couples

        if hand1_props is None:
            hand1_props = {}

        if hand2_props is None:
            hand2_props = {}

        # We create couple set from the object set method
        Object_set.__init__(self, *args, name=name, id=id, type=type,
                            config=config, build=build, **kwargs)

        # Additional properties reading
        try:
            hand1 = self.properties['hand1']
            hand2 = self.properties['hand2']
            hand1_props = an.get_prop_dicts(config, type="hand", name=hand1)
            hand2_props = an.get_prop_dicts(config, type="hand", name=hand2)
        except:
            print("Warning : could not read hand properties for complex %s" %name)

        self.hand1_props = hand1_props
        self.hand2_props = hand2_props


    def build_couples(self, *args, repoints=None, name=None , **kwargs):
        """ Building from numpy array read in report file"""
        if repoints is None:
            repoints = {}
        if name is None:
            name=self.name
        if 'state' in repoints.keys():
            self.make_couples_from_state_lines(*args, points=repoints["state"], name=name, **kwargs)


    def make_couples_from_state_lines(self,*args, points=None, **kwargs):
        """ helper function"""
        if points is None:
            points = np.array([[]])

        for line in points:
            self.append(Couple(id=line[1],fiber1=line[6],fiber2=line[8],
                               position=line[3:6]))


###### A class to contain a single couple :

class Couple():
    """ Couple
        A class that contains a couple. Yep, a whole class for that.
        """

    def __init__(self, *args,  id=1,
                 fiber1=None, fiber2=None, hand1=None, hand2=None,
                 position=None, state=None, **kwargs):

        self.id = id
        self.state = state
        self.fiber1 = fiber1
        self.fiber2 = fiber2
        self.hand1 = hand1
        self.hand2 = hand2
        self.position = position

        # State = number of hands bounds
        if fiber1 is not None and fiber2 is not None:
            self.state = 1.0*(fiber1>0)+1.0*(fiber2>0)

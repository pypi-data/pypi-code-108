# /usr/bin/python3

import pandas as pd

if not __package__:
    from cytolysis.fibers import Fiber_set
    from cytolysis.couples import Couple_set
    from cytolysis.objects import Object_set
    from cytolysis import read_config as rc
    from cytolysis import anutils as an
else:
    from .fibers  import Fiber_set
    from .couples import Couple_set
    from .objects import Object_set
    from . import read_config as rc
    from . import anutils as an

__IPV__ = False
try:
    import ipyvolume as ipv
    from ipywidgets import widgets, interact
    __IPV__ = True
except:
    print("Unable to import Ipyvolume")

__VERSION__ = "0.0.35"

"""
    A module to analyze cytosim simulations

    see README.txt for operation
"""

########## TODO :
# - have yaml config ? at least a default conf ! e.g. for dimension=2 or =3

##### General architecture :
# Objects (fibers, couples...) are stored in objects sets, one object set by frame and by name
#   Each object_set contains methods to analyze its components : object_set.analyze(object, ... )
#   Simulation is a set of frame
#   Analysis are passed through dictionaries of functions { 'object_name' : { 'property' :  function } }


### This should definitely be in a yaml file
# No really, how stupid is that !!!!
__N_DIM__= 3
__NAMED_SETS__ = {"fiber": Fiber_set, "couple": Couple_set}

export_analysis=an.export_analysis

# Each frame contains a fibers, couples, and stuff
class Frame():
    """
    A frame is a data structure containing several objects: Fibers, Couples, Space, etc.

        frame.objects is a dictionary index by types, of dictionaries indexed by names, of objecs.
        e.g. frame.objects["fiber"]["microtubule"] = list_MT
        where list_MT = [MT1, MT2, ... ], with MT1, MT2, ... being instances of class Fiber

    """
    def __init__(self, *args, number=None, blocks = None, **kwargs):
        self.objects = {}
        self.analysis = {}
        self.id = number

        if blocks is not None:
            self.initialize(*args, blocks=blocks, **kwargs)
        else:
            print("Empty frame")

    def initialize(self, *args,
                   blocks =None,
                   config=None, options=None, dim=__N_DIM__, **kwargs):
        """
        Actually create the objects inside the frame
        """
        if options is None:
            options = {}
        if blocks is None:
            blocks = {}

        for key, block in blocks.items():
            self.objects[key] = {}
            opt = {"type": key}
            for name, lines_dict in block.items():
                opt.update(an.get_options(options, name=name, type=key))
                try:
                    self.objects[key][name] = opt["set"](name=name, dim=dim,
                                                         reports=lines_dict, config=config, **opt)
                except:
                    if key in __NAMED_SETS__.keys():
                        self.objects[key][name] = __NAMED_SETS__[key](name=name, dim=dim,
                                                                      reports=lines_dict, config=config, **opt)
                    else:
                        self.objects[key][name] = Object_set(name=name, dim=dim,
                                                             reports=lines_dict, config=config, **opt)

    def make_analysis(self, *args, **kwargs):
        """
            A wrapper for object analysis
        """
        for key, object in self.objects.items():
            #analysis = an.make_analysis(object, *args, analyzer= analyzer, **kwargs)
            analysis = an.make_analysis(object, *args, **kwargs)
            for name, ana in analysis.items():
                self.analysis[name] = ana

    def plot(self, *args, options=None, **kwargs):
        """
            A wrapper for object plotting
        """
        for set in self.objects.values():
            for name, set in set.items():
                opts={}
                if options is not None:
                    try:
                        opts = options[name]
                    except:
                        opts = {}
                set.plot(*args, **opts,  **kwargs)
        return None

    def hide(self):
        """
            Hides a frame from display
        """
        for set in self.objects.values():
            for name, set in set.items():
                for plot in set.plots:
                    plot.visible=False

    def show(self):
        """
            Shows a frame in display
        """
        for set in self.objects.values():
            for name, set in set.items():
                for plot in set.plots:
                    plot.visible = True


class Simulation(list):
    """
    Simulation is the main class
        it is a list of frames  initiated with reports and config files,
        eg : config=config.cym, fibers_reports={ "microtubule" : { "points" : "fiber_points.txt" } }
        ...
    """
    def __init__(self, *args, dim = __N_DIM__, **kwargs):
        list.__init__(self)
        self.config=None
        self.analysis=None
        self.frames_analysis=None
        self.properties={}
        self.name='frame'
        self.type = None
        self.id = 0
        self.n_frames=0
        self.shown = False
        self.dim = dim
        # Actual initialization
        self.initialize(*args,**kwargs)


    # Initialization step
    def initialize(self, *args, config=None, options=None, **kwargs):
        """
            We actually build the simulation here
            We will make the frames from the report files using iterators over these files

            iters is a dictionary of dictionary of dictionaries of iterators :
            e.g.
            iters["fiber] = { "microtubule" : { "points" : iterator_to_fiber_points } }
        """
        if options is None:
            options = {}

        # A dictionary of reports
        reports = {}
        # A dictionary of iterators for reports
        iters = {}

        if config is not None:
            self.read_config(config, *args, **kwargs)

        # looking at the reports we have
        for key, item in kwargs.items():
            if key.endswith("_report"):
                name = key.split("_")[0]
                if name.endswith("s"):
                    typename = name[:-1]
                else:
                    typename = name
                # Here is a small trick to incorporate in options things of the like type_options = {...}
                tt = "%s_options"%name
                if tt in kwargs.keys():
                    try:
                        options[typename].update(kwargs[tt])
                        print(options)
                    except:
                        options[typename] = kwargs[tt]
                reports[typename] = item

        # Initializing the iters
        for key in reports.keys():
            iters[key] = an.make_iter_dict(reports[key])
            an.make_block_dict(iters[key])

        keep = True
        flags = {}
        while keep:
            blocks = {}
            for key, iter in iters.items():
                blocks[key], flags[key] = an.make_block_dict(iter)

            if not any(flags.values()):
                keep = False
            else:
                self.append(Frame(*args, number=len(self),blocks=blocks, options=options,
                                  config=self.config, dim=self.dim, **kwargs))

        self.n_frames = len(self)


    def read_config(self, config, simul_props=None, **kwargs ):
        if simul_props is None:
            simul_props = {}

        self.config = rc.parse(config)
        com = ['set', 'simul', '*']
        props = an.get_dict_from_pile(self.config, com)
        self.properties = {**self.properties, **props, **simul_props}


    def analyze(self, frame, *args, analyzer=None, **kwargs):
        """ Analysis per frame """
        analysis = {'id': frame.id}
        if analyzer is not None:
            for name,func in analyzer.items():
                analysis[name] = func(frame)

        return analysis


    def make_analysis(self,*args, analyzer=None, **kwargs):
        """Analyzes the whole simulation (simulation, frames, and objects) """
        if analyzer is None:
            analyzer = {}

        for key, lyzer in kwargs.items():
            if key.endswith("_analyzer"):
                name = key.split("_analyzer")[0]
                if name.endswith("s"):
                    name = name[:-1]

                if name in analyzer.keys():
                    analyzer[name].update(lyzer)
                else:
                    analyzer[name] = lyzer

        for frame in self:
            frame.make_analysis(*args, analyzer=analyzer, **kwargs)

        self.frames_analysis = an.objects_analysis(self, *args, analyzer=analyzer, **kwargs)

        if "simulation" in analyzer.keys():
            lyzer = analyzer['simulation']

            analysis = {}

            for name, func in lyzer.items():
                analysis[name] = func(self)

            if analysis:
                keys = analysis.keys()
                datas = pd.DataFrame(columns=keys)
                datas.loc[self.id] = [analysis[key] for key in keys]
                self.analysis = datas

    def show(self, *args, **kwargs):
        """ Show the plotted system """
        if not __IPV__:
            raise ValueError("Could not import module iPyVolume")
        else:

            if len(args) == 0:
                ipv.show()
                self.shown=True
            else:
                number=args[0]
                if len(args)>1:
                    args = args[1:]
                else:
                    args = []

                self[number].plot(*args, **kwargs)

    def plot(self, number, *args, **kwargs):
        """ Plots a frame number """
        if not __IPV__:
            raise ValueError("Could not import module iPyVolume")
        else:
            self[number].plot(*args, **kwargs)

    def plot_all(self, *args, **kwargs):
        """ Plots all frames """
        if not __IPV__:
            raise ValueError("Could not import module iPyVolume")
        else:
            for frame in self:
                frame.plot(*args, **kwargs)

    def show_frame(self, number, *args, **kwargs):
        """ shows a specific frame """
        for frame in self:
            if frame.id == number:
                frame.show()
            else:
                frame.hide()

    def frame_player(self, interval=2000, *args, **kwargs):
        """ Shows the system frame by frame """
        if not __IPV__:
            raise ValueError("Could not import module iPyVolume")
        else:
            self.plot_all(*args, **kwargs)
            self.show_frame(0)

            #play = widgets.Play( interval=interval, value=0, min=0, max=len(self)-1, step=1 )
            slider = widgets.IntSlider(value=0, min=0, max=len(self)-1,step=1)

            #widgets.jslink((play, 'value'), (slider, 'value'))
            interact(self.show_frame, number=slider)
            self.show()
            #widgets.HBox([play, slider])

    def figure(self):
        """ Whatever that does """
        if not __IPV__:
            raise ValueError("Could not import module iPyVolume")
        else:
            ipv.figure()

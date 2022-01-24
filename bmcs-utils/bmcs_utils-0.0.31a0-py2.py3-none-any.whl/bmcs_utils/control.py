
import traits.api as tr

class Control(tr.HasTraits):

    run = tr.Str
    """Name of the method running the model simulation
    """

    reset = tr.Str
    """Name of the method resetting the model simulation
    """

    time_change_notifier = tr.Str
    """Name of a trait that can be used by the ui 
    to register time update method
    """

    time_range_change_notifier = tr.Str
    """Name of a trait that can be used by the ui 
    to register time range update method
    """

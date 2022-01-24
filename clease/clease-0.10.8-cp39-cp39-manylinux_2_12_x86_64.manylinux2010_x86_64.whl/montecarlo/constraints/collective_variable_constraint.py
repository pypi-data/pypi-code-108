from .mc_constraint import MCConstraint


class CollectiveVariableConstraint(MCConstraint):
    """
    Constraint that ensures that the collective variable defined by the getter
    stays within certain bounds

    Parameters:

    xmin: float
        Minimum value for the collective variable

    xmax: float
        Maximum value for the collective variable

    getter: MCObserver
        MCObsrever that support peak keyword that returns the collective
        variable after the proposed move
    """

    def __init__(self, xmin=0.0, xmax=1.0, getter=None):
        self.xmin = xmin
        self.xmax = xmax
        self.getter = getter

    def __call__(self, system_change):
        x = self.getter(system_change, peak=True)
        return self.xmin <= x < self.xmax

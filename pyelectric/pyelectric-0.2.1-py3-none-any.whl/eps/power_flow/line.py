from .bar import Bar


class Line:
    admittance: float
    bar1: Bar
    bar2: Bar

    def __init__(self, bar1: Bar, bar2: Bar, *, admittance: complex = None, impedance: complex = None):
        assert admittance is not None or impedance is not None
        self.bar1 = bar1
        self.bar2 = bar2
        if admittance is not None:
            self.admittance = admittance
        else:
            self.admittance = 1/impedance

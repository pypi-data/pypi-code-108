from .bar import Bar


def complex_to_str(c: complex) -> str:
    return f'{c.real:.4e} + {c.imag:.4e}j'


class Line:
    admittance: float
    bar1: Bar
    bar2: Bar
    amperage: complex = 0 + 0j

    def __init__(self, bar1: Bar, bar2: Bar, *, admittance: complex = None, impedance: complex = None):
        assert admittance is not None or impedance is not None
        self.bar1 = bar1
        self.bar2 = bar2
        if admittance is not None:
            self.admittance = admittance
        else:
            self.admittance = 1/impedance

    def __str__(self) -> str:
        Y = complex_to_str(self.admittance)
        Z = complex_to_str(1/self.admittance)
        I = complex_to_str(self.amperage)
        bar1 = self.bar1.name
        bar2 = self.bar2.name
        return f'{bar1} ━━ {bar2}: Z = {Z}, Y = ({Y}), I = ({I})'

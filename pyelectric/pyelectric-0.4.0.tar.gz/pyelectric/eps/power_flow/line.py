from termcolor import colored

from .bar import Bar


def complex_to_str(c: complex) -> str:
    return f'{c.real:.4e} + {c.imag:.4e}j'


class Line:
    admittance: complex
    bar1: Bar
    bar2: Bar
    amperage: complex = 0 + 0j
    power: complex = 0 + 0j
    power_reverse: complex = 0 + 0j

    def __init__(self, bar1: Bar, bar2: Bar, *, admittance: complex = None, impedance: complex = None):
        assert admittance is not None or impedance is not None
        self.bar1 = bar1
        self.bar2 = bar2
        if admittance is not None:
            self.admittance = admittance
        elif impedance is not None:
            self.admittance = 1/impedance

    def __str__(self) -> str:
        S12 = colored(complex_to_str(self.power), 'green')
        S21 = colored(complex_to_str(self.power_reverse), 'green')
        S = colored(complex_to_str(self.power + self.power_reverse), 'green')
        bar1 = colored(self.bar1.name, 'blue')
        bar2 = colored(self.bar2.name, 'blue')
        return f'{bar1} ━━ {bar2}: S = ({S}), S{bar1}{bar2} = ({S12}), S{bar2}{bar1} = ({S21})'

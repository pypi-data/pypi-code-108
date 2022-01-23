from termcolor import colored


def complex_to_str(c: complex) -> str:
    return f'{c.real:.4e} + {c.imag:.4e}j'


class Bar:
    name: str
    voltage: complex = 0 + 0j
    power: complex = 0 + 0j

    def __init__(self, name: str):
        self.name = name

    def __str__(self) -> str:
        V = colored(complex_to_str(self.voltage), 'green')
        S = colored(complex_to_str(self.power), 'green')
        bar = colored(self.name, 'blue')
        return f'{bar}: V = ({V}), S = ({S})'

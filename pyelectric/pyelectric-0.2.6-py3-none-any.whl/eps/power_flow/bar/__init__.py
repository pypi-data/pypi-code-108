def complex_to_str(c: complex) -> str:
    return f'{c.real:.4e} + {c.imag:.4e}j'


class Bar:
    name: str
    voltage: complex = 0 + 0j
    power: complex = 0 + 0j

    def __init__(self, name: str):
        self.name = name

    def __str__(self) -> str:
        v_str = complex_to_str(self.voltage)
        s_str = complex_to_str(self.power)
        return f'{self.name}: V = ({v_str}), S = ({s_str})'

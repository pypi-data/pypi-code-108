class Result:
    V_load: complex
    I: complex

    def __init__(self, V_load: complex, I: complex):
        self.V_load = V_load
        self.I = I

    def __getitem__(self, item: int) -> complex:
        if item == 0:
            return self.V_load
        elif item == 1:
            return self.I
        else:
            raise IndexError("Index out of range")


def check_max_error(V_load: complex, V_load_old: complex, max_error: float) -> bool:
    real_error = abs(abs(V_load) - abs(V_load_old))
    imag_error = abs(V_load.imag - V_load_old.imag)
    if real_error <= max_error or imag_error <= max_error:
        return True
    return False


def constant_current(S_load: complex, Z_line: complex, V: complex) -> Result:
    V_load = V
    I = (S_load/V_load).conjugate()
    V_line = Z_line*I
    V_load = V - V_line

    return Result(V_load, I)


def constant_power(S_load: complex, Z_line: complex, V: complex, max_error: float) -> Result:
    V_load = V
    V_load_old: complex = max_error + 1

    while True:
        I = (S_load.conjugate()/V_load)
        V_line = Z_line*I
        V_load = V - V_line

        if check_max_error(V_load, V_load_old, max_error):
            break
        V_load_old = V_load

    I = S_load.conjugate()/V_load
    return Result(V_load, I)


def constant_impedance(S_load: complex, Z_line: complex, V: complex, max_error: float) -> Result:
    V_load = V
    V_load_old: complex = max_error + 1

    while True:
        Z_load = (V**2/S_load).conjugate()
        I = V_load/Z_load
        V_line = Z_line*I
        V_load = V - V_line

        if check_max_error(V_load, V_load_old, max_error):
            break
        V_load_old = V_load

    Z_load = (V**2/S_load).conjugate()
    I = V_load/Z_load
    return Result(V_load, I)

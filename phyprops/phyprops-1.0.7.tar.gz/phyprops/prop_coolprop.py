import CoolProp.CoolProp as cp


def set_reference_ASHRAE(refrigerant):
    if refrigerant != "WATER":
        cp.set_reference_state(refrigerant, 'ASHRAE')


def tc(refrigerant):
    set_reference_ASHRAE(refrigerant)
    return cp.PropsSI(refrigerant, "Tcrit")-273.15


def pc(refrigerant):
    set_reference_ASHRAE(refrigerant)
    return cp.PropsSI(refrigerant, "Pcrit")/1.0e6


def tx_p(t, x, refrigerant):
    set_reference_ASHRAE(refrigerant)
    return cp.PropsSI('P', 'T', 273.15+t,
                      'Q', x, refrigerant)/1.0e6


def tx_h(t, x, refrigerant):
    set_reference_ASHRAE(refrigerant)
    return cp.PropsSI('H', 'T', 273.15+t,
                      'Q', x, refrigerant)/1000.0


def tx_s(t, x, refrigerant):
    set_reference_ASHRAE(refrigerant)
    return cp.PropsSI('S', 'T', 273.15+t,
                      'Q', x, refrigerant)/1000.0


def px_t(p, x, refrigerant):
    set_reference_ASHRAE(refrigerant)
    return cp.PropsSI('T', 'P', p*1.0e6, 'Q', x, refrigerant)-273.15


def px_h(p, x, refrigerant):
    set_reference_ASHRAE(refrigerant)
    return cp.PropsSI('H', 'P', p*1.0e6, 'Q', x, refrigerant)/1000


def px_s(p, x, refrigerant):
    set_reference_ASHRAE(refrigerant)
    return cp.PropsSI('S', 'P', p*1.0e6, 'Q', x, refrigerant)/1000


def pt_h(p, t, refrigerant):
    set_reference_ASHRAE(refrigerant)
    return cp.PropsSI('H', 'P', p*1.0e6, 'T', t+273.15, refrigerant)/1000


def pt_s(p, t, refrigerant):
    set_reference_ASHRAE(refrigerant)
    return cp.PropsSI('S', 'P', p*1.0e6, 'T', t+273.15, refrigerant)/1000


def ps_h(p, s, refrigerant):
    set_reference_ASHRAE(refrigerant)
    return cp.PropsSI('H', 'P', p*1.0e6, 'S',
                      s*1000, refrigerant)/1000


def ps_t(p, s, refrigerant):
    set_reference_ASHRAE(refrigerant)
    return cp.PropsSI('T', 'P', p*1.0e6, 'S',
                      s*1000, refrigerant)-273.15


def ps_x(p, s, refrigerant):
    set_reference_ASHRAE(refrigerant)
    x = cp.PropsSI('Q', 'P', p*1.0e6, 'S', s*1000, refrigerant)
    if x == -1:
        x = None
    return x


def ph_s(p, h, refrigerant):
    set_reference_ASHRAE(refrigerant)
    return cp.PropsSI('S', 'P', p*1.0e6, 'H', h*1000, refrigerant)/1000


def ph_t(p, h, refrigerant):
    set_reference_ASHRAE(refrigerant)
    return cp.PropsSI('T', 'P', p*1.0e6, 'H', h*1000, refrigerant)-273.15


def ph_x(p, h, refrigerant):
    set_reference_ASHRAE(refrigerant)
    x = cp.PropsSI('Q', 'P', p*1.0e6, 'H', h*1000, refrigerant)
    if x == -1:
        x = None
    return x

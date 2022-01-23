import sys

try:
    # framework is running
    from .startup_choice import *
except ImportError as _excp:
    # class is imported by itself
    if (
        'attempted relative import with no known parent package' in str(_excp)
        or 'No module named \'omfit_classes\'' in str(_excp)
        or "No module named '__main__.startup_choice'" in str(_excp)
    ):
        from startup_choice import *
    else:
        raise

if framework:
    print('Loading fusion utility functions...')

from omfit_classes.utils_base import *
from omfit_classes.utils_math import *

# Decorator @_available_to_user_fusion is used to define which functions should appear in the OMFIT documentation
__all__ = []


def _available_to_user_fusion(f):
    OMFITaux.setdefault('OMFITfusion_functions', [])
    OMFITaux['OMFITfusion_functions'].append(f)
    __all__.append(f.__name__)
    return f


# Basic constants
from scipy import constants

pi = constants.pi
e_charge = eV2J = constants.e
epsilon_0 = constants.epsilon_0
m_e = constants.m_e
m_p = constants.m_p
mu0 = constants.mu_0


# Custom exceptions
class UtilsFusionBadInput(ValueError, doNotReportException):
    """An invalid input was given"""


#  The first section of this file contains functions which attempt to
#  implement in python form the equations presented in Jim Callen's
#  ParNeoResREF.nb Mathematica file. Later in the file are other handy
#  fusion related functions


@_available_to_user_fusion
def gyroradius(T, Bt, Z, m):
    """
    This function calculates plasma gyroradius

    :param T: Ion temperature [eV]

    :param Bt: Magnetic field [T]

    :param Z: charge

    :param m: mass [AMU]

    :return: gyroradius [m]
    """

    M = m * m_p
    vt = np.sqrt(T / M * e_charge)
    r_gyro = M * vt / abs(e_charge * Z * Bt)

    return r_gyro


@_available_to_user_fusion
def banana_width(T, Bt, Z, m, epsilon, q):
    """
    This function estimates the banana orbit width

    :param T: Temperature [eV]

    :param Bt: Magnetic field [T]

    :param Z: Charge

    :param m: Mass [AMU]

    :param epsilon: Inverse aspect ratio

    :param q: Safety factor

    :return: Estimate of banana orbit width [m]
    """
    r_gyro = gyroradius(T, Bt, Z, m)

    r_banana = 2.0 * epsilon ** (-0.5) * abs(q) * r_gyro
    return r_banana


# Define necessary parts for ln_lambda
@_available_to_user_fusion
def lambda_debye(**keyw):
    r"""
    Debye length [m]

    Needs ne [m^-3], te [eV]

    Formula: :math:`\sqrt{\frac{\varepsilon_0 T_e}{q_e n_e}}`
    """
    ne = keyw['ne']
    te = keyw['te']
    return (epsilon_0 * te / (e_charge * ne)) ** 0.5


@_available_to_user_fusion
def bmin_classical(**keyw):
    """
    Classical distance of minimum approach [m]

    Needs zeff [-], te [eV]
    """
    zeff = keyw['zeff']
    te = keyw['te']
    return 4.8e-10 * zeff / te


@_available_to_user_fusion
def bmin_qm(**keyw):
    """
    Quantum mechanical distance of minimum approach [m]

    Needs te [eV]
    """
    te = keyw['te']
    return 1.1e-10 / te ** 0.5


@_available_to_user_fusion
def ln_Lambda(**keyw):
    """
    Coulomb logarithm [-]

    Needs te [eV], zeff [-], ne [m^-3]
    """
    b_min = np.array(bmin_classical(**keyw))
    tmp2 = np.array(bmin_qm(**keyw))
    if len(b_min.shape) == 0 and len(tmp2.shape) == 0:
        if tmp2 > b_min:
            b_min = tmp2
    else:
        b_min[tmp2 > b_min] = tmp2[tmp2 > b_min]
    return ulog(lambda_debye(**keyw) / b_min)


# Define electron collisionality
@_available_to_user_fusion
def nu_e(**keyw):
    """
    Electron collision frequency [1/s]
    Eq. (A9) in UW CPTC 09-6R

    Needs te [eV], zeff [-], ne [m^-3]
    """
    ne = keyw['ne']
    te = keyw['te']
    zeff = keyw['zeff']
    fac = 4 * np.sqrt(2 * pi) * e_charge ** 4 / (4 * pi * epsilon_0) ** 2 / 3.0 / m_e ** 0.5 * eV2J ** -1.5 * 17
    return fac * ne * zeff * ln_Lambda(**keyw) / 17.0 / te ** 1.5


@_available_to_user_fusion
def vTe(**keyw):
    """
    Electron thermal velocity [m/s]

    Needs te [eV]
    """
    te = keyw['te']
    return usqrt(2 * te * eV2J / m_e)


@_available_to_user_fusion
def lambda_e(**keyw):
    """
    Electron mean free path [m]

    Needs te [eV], zeff [-], ne [m^-3]
    """
    return vTe(**keyw) / nu_e(**keyw)


@_available_to_user_fusion
def omega_transit_e(**keyw):
    """
    Electron transit frequency [1/s]

    Needs q [-], R0 [m], te [eV]
    """
    q = abs(keyw['q'])
    R0 = keyw['R0']
    return vTe(**keyw) / (R0 * q)


@_available_to_user_fusion
def epsilon(**keyw):
    """
    Inverse aspect ratio [-]

    Needs (rho [m], R0 [m]) or (r_minor, R_major)
    """
    if 'r_minor' in keyw:
        r = keyw['r_minor']
    else:
        r = keyw['rho']
    if 'R_major' in keyw:
        R = keyw['R_major']
    else:
        R = keyw['R0']
    return r / R


@_available_to_user_fusion
def f_c(**keyw):
    """
    Flow-weighted fraction of circulating particles

    Needs epsilon inputs
    """
    eps_tmp = epsilon(**keyw)
    return (1 - eps_tmp) ** 2 / (usqrt(1 - eps_tmp ** 2) * (1.0 + 1.46 * usqrt(eps_tmp) + 0.2 * eps_tmp))


@_available_to_user_fusion
def f_t(**keyw):
    """
    Flow-weighted fraction of trapped particles

    Needs epsilon inputs
    """
    return 1 - f_c(**keyw)


@_available_to_user_fusion
def fsa_B2_over_fsa_b_dot_B(**keyw):
    """
    Approximation of geometric factor <B_0^2>/<(b.grad(B_0))^2>.  [m^-2]

    Needs R0 [m], q [-], epsilon inputs
    """
    R0 = keyw['R0']
    q = keyw['q']
    return epsilon(**keyw) ** 2 / (2 * R0 ** 2 * q ** 2)


@_available_to_user_fusion
def nu_star_e(**keyw):
    """
    Electron collisionality parameter [-]

    Needs R0 [m], q [-], te [eV], zeff [-], ne [m^-3], epsilon inputs
    """
    return f_t(**keyw) / f_c(**keyw) * nu_e(**keyw) * omega_transit_e(**keyw) / (2.92 * vTe(**keyw) ** 2) / fsa_B2_over_fsa_b_dot_B(**keyw)


# Banana, Plateau, and Pfirsch-Schluter regime viscosity components:
def K00B(**keyw):
    """
    Banana viscosity component [-]

    Needs zeff [-]
    """
    zeff = keyw['zeff']
    return (zeff + 0.533) / zeff


def K01B(**keyw):
    """
    Banana viscosity component [-]

    Needs zeff [-]
    """
    zeff = keyw['zeff']
    return (zeff + 0.707) / zeff


def K11B(**keyw):
    """
    Banana viscosity component [-]

    Needs zeff [-]
    """
    zeff = keyw['zeff']
    return (2 * zeff + 1.591) / zeff


def K00P(**keyw):
    """
    Plateau viscosity component [-]

    Needs nothing
    """
    return 1.77


def K01P(**keyw):
    """
    Plateau viscosity component [-]

    Needs nothing
    """
    return 5.32


def K11P(**keyw):
    """
    Plateau viscosity component [-]

    Needs nothing
    """
    return 21.27


def Denom(**keyw):
    """
    Pfirsch-Schluter viscosity component [-]

    Needs zeff [-]
    """
    zeff = keyw['zeff']
    return 2.4 * zeff ** 2 + 5.32 * zeff + 2.225


def K00PS(**keyw):
    """
    Pfirsch-Schluter viscosity component [-]

    Needs zeff [-]
    """
    zeff = keyw['zeff']
    return (4.25 * zeff + 3.02) / Denom(**keyw)


def K01PS(**keyw):
    """
    Pfirsch-Schluter viscosity component [-]

    Needs zeff [-]
    """
    zeff = keyw['zeff']
    return (20.13 * zeff + 12.43) / Denom(**keyw)


def K11PS(**keyw):
    """
    Pfirsch-Schluter viscosity component [-]

    Needs zeff [-]
    """
    zeff = keyw['zeff']
    return (101.06 * zeff + 58.65) / Denom(**keyw)


# Combine previous coefficients
@_available_to_user_fusion
def omega_transit_e_tau(**keyw):
    """
    Dimensionless omega_transit [-]

    Needs te [eV], zeff [-], ne [m^-3], q [-], R0 [m]
    """
    zeff = keyw['zeff']
    return zeff * omega_transit_e(**keyw) / nu_e(**keyw)


def K00tot(**keyw):
    """
    Dimensionless multi-collisionality viscosity coefficient [-]

    Needs te [eV], zeff [-], ne [m^-3], q [-], R0 [m]
    """
    nustare = nu_star_e(**keyw)
    return K00B(**keyw) / (
        (1.0 + usqrt(nustare) + 2.92 * nustare * K00B(**keyw) / K00P(**keyw))
        * (1.0 + 2.0 * K00P(**keyw) / (3.0 * omega_transit_e_tau(**keyw) * K00PS(**keyw)))
    )


def K01tot(**keyw):
    """
    Dimensionless multi-collisionality viscosity coefficient [-]

    Needs te [eV], zeff [-], ne [m^-3], q [-], R0 [m]
    """
    nustare = nu_star_e(**keyw)
    return K01B(**keyw) / (
        (1.0 + usqrt(nustare) + 2.92 * nustare * K01B(**keyw) / K01P(**keyw))
        * (1.0 + 2.0 * K01P(**keyw) / (3.0 * omega_transit_e_tau(**keyw) * K01PS(**keyw)))
    )


def K11tot(**keyw):
    """
    Dimensionless multi-collisionality viscosity coefficient [-]

    Needs te [eV], zeff [-], ne [m^-3], q [-], R0 [m]
    """
    nustare = nu_star_e(**keyw)
    return K11B(**keyw) / (
        (1.0 + usqrt(nustare) + 2.92 * nustare * K11B(**keyw) / K11P(**keyw))
        * (1.0 + 2.0 * K11P(**keyw) / (3.0 * omega_transit_e_tau(**keyw) * K11PS(**keyw)))
    )


@_available_to_user_fusion
def M_visc_e(**keyw):
    """
    Dimensionless electron viscosity matrix M_e  [-]
    2 x 2 x len(ne)

    Needs te [eV], zeff [-], ne [m^-3], q [-], R0 [m]
    """
    zeff = keyw['zeff']
    k00tot = K00tot(**keyw)
    k01tot = K01tot(**keyw)
    k11tot = K11tot(**keyw)
    return (
        zeff
        * (f_t(**keyw) / f_c(**keyw))
        * np.array([[k00tot, 2.5 * k00tot - k01tot], [2.5 * k00tot - k01tot, k11tot - 5.0 * k01tot + 6.25 * k00tot]])
    )


@_available_to_user_fusion
def N_fric_e(**keyw):
    """
    Dimensionless electron friction matrix N_e [-]
    2 x 2 x len(zeff)

    Needs zeff [-]
    """
    zeff = keyw['zeff']
    return np.array([[zeff, 1.5 * zeff], [1.5 * zeff, 1.414 + 3.25 * zeff]])


@_available_to_user_fusion
def inverse_N(**keyw):
    """
    Inverse of the electron friction matrix [-]

    Needs zeff
    """
    tmp = N_fric_e(**keyw)
    A = tmp[0, 0]
    B = tmp[0, 1]
    C = tmp[1, 0]
    D = tmp[1, 1]
    return 1 / (A * D - B * C) * np.array([[D, -B], [-C, A]])


@_available_to_user_fusion
def Spitzer_factor(**keyw):
    """
    Spitzer resistivity factor [-]

    Needs zeff [-]
    """
    zeff = keyw['zeff']
    return 1.0 / (zeff * inverse_N(**keyw)[0, 0])


@_available_to_user_fusion
def inverse_NM(**keyw):
    """
    Inverse of the sum N_fric_e + M_fric_e [-]

    Needs te [eV], zeff [-], ne [m^-3], q [-], R0 [m]
    """

    tmp = N_fric_e(**keyw) + M_visc_e(**keyw)
    A = tmp[0, 0]
    B = tmp[0, 1]
    C = tmp[1, 0]
    D = tmp[1, 1]
    return 1 / (A * D - B * C) * np.array([[D, -B], [-C, A]])


@_available_to_user_fusion
def resistive_factor(**keyw):
    """
    Resistive factor [-]

    Needs te [eV], zeff [-], ne [m^-3], q [-], R0 [m]
    """
    zeff = keyw['zeff']
    return 1.0 / (zeff * inverse_NM(**keyw)[0, 0])


@_available_to_user_fusion
def eta_0(**keyw):
    """
    Reference resistivity [ohm-m]

    Needs ne [m^-3], te [eV], zeff [-]
    """
    ne = keyw['ne']
    return m_e * nu_e(**keyw) / (ne * e_charge ** 2)


@_available_to_user_fusion
def eta_par_neo(**keyw):
    """
    Parallel neoclassical resistivity [ohm-m]

    Needs te [eV], zeff [-], ne [m^-3], q [-], R0 [m]
    """
    return eta_0(**keyw) * resistive_factor(**keyw)


@_available_to_user_fusion
def q_rationals(x, q, nlist, mlist=None, doPlot=False):
    """
    Evaluate rational flux surfaces (m/n) give a q profile

    :param x: x axis over which q profile is defined

    :param q: q profile

    :param nlist: list of `n` mode number

    :param mlist: list of `m` mode number (if None returns all possible (m/n) rationals)

    :param doPlot: Plot (either True or matplotlib axes)

    :return: dictionary with (m,n) keys and `x` intersections as values
    """
    q = abs(q)
    nlist = tolist(nlist)
    mlist = tolist(mlist, [None])
    mq = min(q)
    Mq = max(q)
    vals = {}
    rationals = []
    for n in sorted(nlist)[::-1]:
        first_n = True
        final_mlist = mlist
        if not mlist:
            final_mlist = range(int(np.ceil(Mq) * n))
        for m in final_mlist:
            qq = float(m) / float(n)
            if mq < qq < Mq:
                vals.setdefault((m, n), [])
                it = line_intersect(np.array((x, q)).T, np.array(((min(x), max(x)), (qq, qq))).T)
                vals[(m, n)].extend([i[0] for i in it])
    if doPlot is True:
        doPlot = pyplot.gca()
    if doPlot:
        plotted = []
        plotted_n = []
        for m, n in sorted(vals, key=lambda x: '%06d%06d' % (x[1], x[0])):
            qq = float(m) / float(n)
            if qq not in plotted:
                for x0 in vals[(m, n)]:
                    if n in plotted_n:
                        label = ''
                    else:
                        label = str(n)
                        plotted_n.append(n)
                    doPlot.scatter(
                        [x0], [qq], color=color_cycle(max(nlist) + 1, n, cmap_name='jet'), marker='o', edgecolor='none', label=label
                    )
                    doPlot.text(x0, qq, ' $\\frac{%d}{%d}$\n' % (m, n))
                plotted.append(qq)
        doPlot.plot(x, q, color='k')
        doPlot.legend(loc=0)
    return vals


# Non-physics
def print_assertion(name, val_expect, val_calc):
    diff = (val_expect - val_calc) / val_expect * 100
    print('%s:\n\t%8g\t=\t%8g\t Difference: \t%8g %s' % (name, val_expect, val_calc, diff, '%'))


def test():
    data = dict(
        ne=np.array(1.65e19),
        te=np.array(320),
        zeff=np.array(2.83),
        R0=np.array(1.7),
        q=np.array(4.4),
        rho=np.array(0.6),
        r_minor=np.array(0.6),
        R_major=np.array(1.7),
    )
    import pylab

    print_assertion('lambda_debye', lambda_debye(**data), 0.0000327383)
    print_assertion('bmin_classical', bmin_classical(**data), 4.245e-12)
    print_assertion('bmin_qm', bmin_qm(**data), 6.14919e-12)
    print_assertion('ln_Lambda', ln_Lambda(**data), 15.4877)
    print_assertion('nu_e', nu_e(**data), 367197)
    print_assertion('vTe', vTe(**data), 1.06097e7)
    print_assertion('lambda_e', lambda_e(**data), 28.8938)
    print_assertion('omega_transit_e', omega_transit_e(**data), 1.41841e6)
    print_assertion('epsilon', epsilon(**data), 0.352941)
    print_assertion('f_c', f_c(**data), 0.230904)
    print_assertion('f_t', f_t(**data), 0.769096)
    print_assertion('nu_star_e', nu_star_e(**data), 4.7412)
    print_assertion('K00B', K00B(**data), 1.18834)
    print_assertion('K01B', K01B(**data), 1.24982)
    print_assertion('K11B', K11B(**data), 2.56219)
    print_assertion('K00P', K00P(**data), 1.77)
    print_assertion('K01P', K01P(**data), 5.32)
    print_assertion('K11P', K11P(**data), 21.27)
    print_assertion('Denom', Denom(**data), 36.502)
    print_assertion('K00PS', K00PS(**data), 0.412238)
    print_assertion('K01PS', K01PS(**data), 1.90121)
    print_assertion('K11PS', K11PS(**data), 9.44195)
    print_assertion('omega_transit_e_tau', omega_transit_e_tau(**data), 10.9317)
    print_assertion('K00tot', K00tot(**data), 0.0755077)
    print_assertion('K01tot', K01tot(**data), 0.166043)
    print_assertion('K11tot', K11tot(**data), 0.464945)
    print_assertion('M_visc_e[0,0]', M_visc_e(**data)[0, 0], 0.711748)
    print_assertion('M_visc_e[0,1]', M_visc_e(**data)[0, 1], 0.214222)
    print_assertion('M_visc_e[1,0]', M_visc_e(**data)[1, 0], 0.214222)
    print_assertion('M_visc_e[1,1]', M_visc_e(**data)[1, 1], 1.00533)
    print_assertion('N_fric_e[0,0]', N_fric_e(**data)[0, 0], 2.83)
    print_assertion('N_fric_e[0,1]', N_fric_e(**data)[0, 1], 4.245)
    print_assertion('N_fric_e[1,0]', N_fric_e(**data)[1, 0], 4.245)
    print_assertion('N_fric_e[1,1]', N_fric_e(**data)[1, 1], 10.6115)
    print_assertion('Inverse_N[0,0]', inverse_N(**data)[0, 0], 0.883517)
    print_assertion('Inverse_N[0,1]', inverse_N(**data)[0, 1], -0.35344)
    print_assertion('Inverse_N[1,0]', inverse_N(**data)[1, 0], -0.35344)
    print_assertion('Inverse_N[1,1]', inverse_N(**data)[1, 1], 0.235627)
    print_assertion('SpFactor', Spitzer_factor(**data), 0.399943)
    print_assertion('Inverse_NM[0,0]', inverse_NM(**data)[0, 0], 0.546437)
    print_assertion('Inverse_NM[0,1]', inverse_NM(**data)[0, 1], -0.209755)
    print_assertion('Inverse_NM[1,0]', inverse_NM(**data)[1, 0], -0.209755)
    print_assertion('Inverse_NM[1,1]', inverse_NM(**data)[1, 1], 0.166598)
    print_assertion('ResFactor', resistive_factor(**data), 0.646656)
    print_assertion('eta_0', eta_0(**data), 7.89717e-7)
    print_assertion('eta_par_neo', eta_par_neo(**data), 5.10675e-7)
    print(pylab.matrix(N_fric_e(**data)) * pylab.matrix(inverse_N(**data)))
    print('')


####################################################################
#        END OF THE CALLEN ParNeoResREF.nb Mathematica PORT        #
####################################################################


##################################################
# Set up the tokamak() and is_device() functions #
##################################################
_user_2_internal = {
    'ASDX': 'ASDEX',
    'AUGD': 'AUG',
    'IGTR': 'IGNITOR',
    'DIIID': 'DIII-D',
    'DIII-D': 'DIII-D',
    'DIII': 'DIII-D',
    'D3D': 'DIII-D',
    'NSTX-U': 'NSTXU',
    'NSTXU': 'NSTXU',
    'NSTU': 'NSTXU',
    'KSTR': 'KSTAR',
    'TORS': 'TS',
    'HL-2A': 'HL-2A',
    'HL2A': 'HL-2A',
    '2A': 'HL-2A',
    'HL-2M': 'HL-2M',
    'HL2M': 'HL-2M',
    '2M': 'HL-2M',
}

# This is the list of tokamaks strings recognized by TRANSP
for _k in [
    'ARC',
    'ARIS',
    'ASDX',
    'AUGD',
    'BPX',
    'CFNS',
    'CIT',
    'CMOD',
    'D3D',
    'DEMO',
    'DIII',
    'EAST',
    'FIRE',
    'FNSF',
    'HL1M',
    'HL2A',
    'IGTR',
    'ISX',
    'ITER',
    'JET',
    'JT60',
    'JULI',
    'KDMO',
    'KSTR',
    'LTX',
    'MAST',
    'MST',
    'NCSX',
    'NHTX',
    'NSST',
    'NSTX',
    'NSTU',
    'PBX',
    'PBXM',
    'PDX',
    'PLT',
    'TFTR',
    'RFXM',
    'SSSP',
    'TORS',
    'TXTR',
    'WRK',
]:
    if _k not in _user_2_internal:
        _user_2_internal[_k] = _k

_internal_2 = {
    'OMFIT': {},
    'TRANSP': {'CASE': 'upper', 'DIII-D': 'D3D', 'NSTX-U': 'NSTU', 'NSTXU': 'NSTU', 'KSTAR': 'KSTR'},
    'GPEC': {
        'CASE': 'lower',
        'ASDEX': 'aug',
        'ASDX': 'aug',
        'AUG': 'aug',
        'AUGD': 'aug',
        'COMPASS': 'compass',
        'DIII-D': 'd3d',
        'EAST': 'east',
        'ITER': 'iter',
        'JET': 'jet',
        'JTEXT': 'jtext',
        'KSTAR': 'kstar',
        'MAST': 'mast',
        'NSTX-U': 'nstx',
        'NSTXU': 'nstx',
        'NSTX': 'nstx',
        'RFXMOD': 'rfxmod',
        'RFXM': 'rfxmod',
        'SPECTOR': 'spector',
    },
    'OMAS': {'CASE': 'lower', 'DIII-D': 'd3d', 'NSTX-U': 'nstxu', 'NSTXU': 'nstxu', 'NSTX': 'nstx'},
}


@_available_to_user_fusion
def tokamak(tokamak, output_style='OMFIT', allow_not_recognized=True, translation_dict=None):
    """
    function that sanitizes user input `tokamak` in a format that is recognized by other codes

    :param tokamak: user string of the tokamak

    :param output_style: format of the tokamak used for the output one of ['OMFIT','TRANSP','GPEC']

    :param allow_not_recognized: allow a user to enter a tokamak which is not recognized

    :param translation_dict: dictionary used for further translation. This is handy for example in
                             situations where we want to get the same string back independently of
                             whether it is a older tokamak or its upgraded version. For example
                             `tokamak('NSTX-U', translation_dict={'NSTXU':'NSTX'})`

    :return: sanitized string
    """
    tokamak = evalExpr(tokamak)
    if tokamak is None:
        if allow_not_recognized:
            return None
        else:
            raise ValueError("Tokamak is set as None")

    if translation_dict is None:
        translation_dict = {}

    if tokamak not in list(_user_2_internal.values()):
        s0 = bestChoice(_user_2_internal, tokamak)
        if s0[1] > 0.8:
            tokamak = s0[0]
        elif not allow_not_recognized:
            raise ValueError("Tokamak '" + tokamak + "' was not recognized")

    if output_style.upper() in _internal_2:
        tmp = _internal_2[output_style].get(tokamak, tokamak)
        if _internal_2[output_style].get('CASE', '') == 'lower':
            tmp = tmp.lower()
        elif _internal_2[output_style].get('CASE', '') == 'upper':
            tmp = tmp.upper()
        tmp = translation_dict.get(tmp, tmp)
        return tmp
    else:
        raise ValueError(
            "Tokamak output_style representation '"
            + output_style
            + "' was not recognized. Valid options are: "
            + repr(list(_internal_2.keys()))
        )


@_available_to_user_fusion
def is_device(devA, devB):
    """
    Compare strings or lists of strings for equivalence in tokamak name

    :param devA: A string or list of strings
    :param devB: A string or list of strings

    :return: True or False

    Example: is_device('D3D',['DIII-D','MAST'])
    """
    devA = tolist(evalExpr(devA), [None])
    devB = tolist(evalExpr(devB), [None])
    for A in devA:
        for B in devB:
            if A is not None and B is not None:
                if A.upper() == B.upper():
                    return True
                elif A.upper() in list(_user_2_internal.values()) and B.upper() in list(_user_2_internal.values()):
                    pass
            if tokamak(A) == tokamak(B):
                return True
    return False


#########################
# Device specifications #
#########################
@_available_to_user_fusion
def device_specs(device='DIII-D'):
    """
    Returns a dictionary of information that is specific to a particular tokamak

    :param device: The name of a tokamak. It will be evaluated with the tokamak() function so variation in spelling and
        capitalization will be tolerated. This function has some additional translation capabilities for associating
        MDSplus servers with tokamaks; for example, "EAST_US", which is the entry used to access the eastdata.gat.com
        MDSplus mirror, will be translated to EAST.

    :return: A dictionary with as many static device measurements as are known
    """
    from collections import OrderedDict

    dev0 = device  # Copy the input so we don't bother the entry in the tree
    printd('Looking up specifications for device = {:}...'.format(dev0))

    # Additional translation table
    if dev0.upper() in ['EAST_US', 'EASTDATA']:
        dev0 = 'EAST'
    if dev0.upper() == 'VIDAR':
        print(
            'Server is vidar.gat.com, which is not specific to any tokamak! Please update your call to pass in \n'
            'the tokamak you are working with! However, the most likely possibility is DIII-D, so device will \n'
            'default to DIII-D.'
        )
        dev0 = 'DIII-D'
    # Done with additional translations

    # tokamak() call to resolve spelling and capitalization variations
    dev0 = tokamak(dev0)

    # Empty dictionary by default
    specs = OrderedDict()
    specs['tokamak'] = dev0

    # Defaults that will be overridden as appropriate (they are all here to enforce the order of the dictionary)
    specs['error'] = False  # Hopefully this one will not need to be overwritten!
    specs['R0'] = None
    specs['home'] = None
    specs['location'] = None
    specs['upgrade_of'] = None  # Some devices are built new from scratch!
    specs['long_name'] = specs['tokamak']  # Not all names are acronyms (I know this is weird but it's actually true)

    # Descriptions all start with units or pseudo-units in parentheses (or empty parentheses if there are no relevant units)
    descriptions = OrderedDict(
        [
            ('tokamak', '() The name of the tokamak'),
            ('error', '(T/F) Flag for whether or not an error occurred while building the specifications dictionary'),
            ('R0', '(m) Geometric center of the vacuum vessel. Not sensitive to plasma configuration in any way.'),
            ('home', '() Name of home institution'),
            ('location', '(Country / State or Provence / City or municipal area) Geographic location of the device.'),
            (
                'upgrade_of',
                '() Name of the previous device that shared some key hardware, or None if the device was not a modification, upgrade, or overhaul of a previous tokamak',
            ),
            ('long_name', "() The long form of the tokamak's name, such as spelling out an acronym"),
        ]
    )

    if is_device(dev0, 'DIII-D'):  # DIII-D -------------------------------------------------------------------------------------
        # Technical specifications
        specs['R0'] = 1.6955  # (m) This measurement is found consistently in several internal memos and scripts.

        # More information - put this last
        specs['home'] = 'General Atomics'
        specs['location'] = 'United States / California / San Diego'
        specs['upgrade_of'] = 'Doublet III'

    elif is_device(dev0, ['NSTX', 'NSTXU']):  # NSTX and preliminary setup for NSTX-U -------------------------------------------
        # NSTX-U is a different device than NSTX and it will get its own section later, but we can copy a lot if we
        # arrange the script this way

        # Technical specifications
        specs['R0'] = 0.85  # (m)

        # More information - put this last
        specs['home'] = 'PPPL'
        specs['location'] = 'United States / New Jersey / Princeton'
        specs['long_name'] = 'National Spherical Tokamak eXperiment'

    elif is_device(dev0, 'ITER'):  # ITER ---------------------------------------------------------------------------------------
        # Technical specifications
        specs['R0'] = 6.1828  # (m)
        print(
            'Warning: Assigned ITER vacuum vessel geometric center R0 although ITER has not been built. Actual'
            'results after construction may vary.'
        )

        # More information - put this last
        specs['home'] = 'ITER Organization'
        specs['location'] = "France / Provence-Alpes-Cote-d'Azur / Saint-Paul-les-Durance"
        specs['long_name'] = 'ITER'  #'International Thermonuclear Experimental Reactor'  # ITER used to be an acronym, but the
        # the word thermonuclear freaks people out so now the story is that ITER is latin for "the way".

    elif is_device(dev0, 'EAST'):  # EAST ---------------------------------------------------------------------------------------
        # Technical specifications

        # More information - put this last
        specs['home'] = 'ASIPP'
        specs['location'] = "China / Anhui / Hefei"
        specs['long_name'] = 'Experimental Advanced Superconducting Tokamak'

    elif is_device(dev0, 'KSTAR'):  # KSTAR -------------------------------------------------------------------------------------
        # Technical specifications
        specs['R0'] = 1.79  # (m)

        # More information - put this last
        specs['home'] = 'KFE'
        specs['location'] = "Korea /  / Daejeon"
        specs['long_name'] = 'Korea Superconducting Tokamak Advanced Reactor'

    elif is_device(dev0, 'JET'):  # JET -------------------------------------------------------------------------------------
        # Technical specifications
        specs['R0'] = 2.96  # (m)

        # More information - put this last
        specs['home'] = 'CCFE'
        specs['location'] = "Culham /  / United Kingdom"
        specs['long_name'] = 'Joint European Torus'

    elif is_device(dev0, 'MAST'):  # MAST -------------------------------------------------------------------------------------
        # Technical specifications
        specs['R0'] = 1.0  # (m)

        # More information - put this last
        specs['home'] = 'CCFE'
        specs['location'] = "Culham /  / United Kingdom"
        specs['long_name'] = 'Mega Amp Spherical Tokamak'

    elif is_device(dev0, 'SPECTOR'):  # SPECTOR ---------------------------------------------------------------------------------
        # Technical specifications

        # More information - put this last
        specs['home'] = 'General Fusion'
        specs['location'] = "Canada / BC / Burnaby"
        specs['long_name'] = 'Spherical Compact Toroid'

    else:  # FAIL ------------------------------------------------------------------------------------------------------
        # Unrecognized device
        printe('WARNING! Unrecognized or unimplemented device! Please try again')
        specs['error'] = True

    if is_device(dev0, 'NSTXU'):  # NSTX-U updates-------------------------------------------------------------------------------
        # Most NSTX-U settings should've been set in the NSTX section, so this section only has to update any changes.

        # Technical specifications
        print('Warning: R0 value for NSTX-U has been copied from NSTX. ' 'This could be right or at least close but has not been checked.')

        # More information - put this last
        specs['upgrade_of'] = 'NSTX'
        specs['long_name'] = 'National Spherical Tokamak eXperiment - Upgrade'

    specs['descriptions'] = descriptions
    if not specs['error']:
        printd(
            'Got specifications for {:}. Please note that technical specifications are fixed: we have assumed that '
            'tokamaks do not swap vacuum vessels without changing their name to note an upgrade or '
            'modification'.format(dev0)
        )
    return specs


#############################
# Neoclassical Conductivity #
#############################
# These are the available versions. You can index this list to pick one instead of remembering all of the options:
jbs_versions = ['jB_fsa', 'osborne', 'jboot1', 'jboot1BROKEN', 'neo_2021']  # jboot1 is the best for <J.B>; otherwise use osborne


@_available_to_user_fusion
def nclass_conductivity(
    psi_N=None,
    Te=None,
    ne=None,
    Ti=None,
    q=None,
    eps=None,
    R=None,
    fT=None,
    volume=None,
    Zeff=None,
    nis=None,
    Zis=None,
    Zdom=None,
    version=jbs_versions[1],
    return_info_pack=False,
    plot_slice=None,
    sigma_compare=None,
    sigma_compare_label='Input for comparison',
    spitzer_compare=None,
    spitzer_compare_label='Spitzer input for comparison',
    charge_number_to_use_in_ion_collisionality='Koh',
    charge_number_to_use_in_ion_lnLambda='Zavg',
):
    """
    Calculation of neoclassical conductivity

    See: O. Sauter, et al., Phys. Plasmas 6, 2834 (1999); doi:10.1063/1.873240
    Neoclassical conductivity appears in equations: 5, 7, 13a, and unnumbered equations in the conclusion

    Other references:

    S Koh, et al., Phys. Plasmas 19, 072505 (2012); doi: 10.1063/1.4736953
        for dealing with ion charge number when there are multiple species
    T Osborne, "efit.py Kinetic EFIT Method", private communication (2013);
        this is a word file with a description of equations used to form the current profile constraint
    O Sauter, et al., Phys. Plasmas 9, 5140 (2002); doi:10.1063/1.1517052
        this has corrections for Sauter 1999 but it also has a note on what Z to use in which equations; it argues that ion equations should use the
        charge number of the main ions for Z instead of the ion effective charge number from Koh 2012
    `Sauter website <https://crppwww.epfl.ch/~sauter/neoclassical/>`_
        Accurate neoclassical resistivity, bootstrap current and other
        transport coefficients (Fortran 90 subroutines and matlab functions): has some code that was used to check
        the calculations in this script (BScoeff.m, nustar.m, sigmaneo.m, jdotB_BS.m)
    `GACODE NEO source <https://github.com/gafusion/gacode/blob/master/neo/src/neo_theory.f90>`_
        Calculations from NEO (E. A. Belli)
     Update August 2021 : add new set of analytical formulae for the computation of the neoclassical condactivity from
        A.Redl, et al., Phys. Plasma 28, 022502 (2021) https://doi.org/10.1063/5.0012664  and all relevant variables are mentioned as neo_2021

    This function was initially written as part of the Kolemen Group Automatic Kinetic EFIT Project (auto_kEFIT).

    :param psi_N: position basis for all profiles, required only for plotting (normalized poloidal magnetic flux)

    :param Te: electron temperature in eV as a function of time and position (time should be first axis, then position)

    :param ne: electron density in m^-3 (vs. time and psi)

    :param Ti: ion temperature in eV

    :param Zeff: [optional if nis and Zis are provided] effective charge state of ions
        = sum_j(n_j (Z_j)^2)/sum_j(n_j Z_j)  where j is ion species (this is probably a sum over deuterium and carbon)

    :param nis: [optional if Zeff is provided] list of ion densities in m^-3

    :param Zis: [optional if Zeff is provided] ion charge states (list of scalars)

    :param Zdom: [might be optional] specify the charge number of the dominant ion species. Defaults to the one with the
        highest total number of particles (volume integral of ni). If using the estimation method where only Zeff is
        provided, then Zdom is assumed to be 1 if not provided.

    :param q: safety factor

    :param eps: inverse aspect ratio

    :param R: major radius of the geometric center of each flux surface

    :param fT: trapped particles fraction

    :param volume: [not needed if Zdom is provided, unlikely to cause trouble if not provided even when "needed"] volume
        enclosed by each flux surface, used to identify dominant ion species if dominant ion species is not defined
        explicitly by doing a volume integral (so we need this so we can get dV/dpsiN). If volume is needed but not
        provided, it will be crudely estimated. Errors in the volume integral are very unlikely to affect the selection
        of the dominant ion species (it would have to be a close call to begin with), so it is not critical that volume
        be provided with high quality, if at all.

    :param return_info_pack: Boolean: If true, returns a dictionary full of many intermediate variables from this
        calculation instead of just conductivity

    :param plot_slice: Set to the index of the timeslice to plot in order to plot one timeslice of the calculation,
        including input profiles and intermediate quantities. Set to None for no plot (default)

    :param sigma_compare: provide a conductivity profile for comparison in Ohm^-1 m^-1

    :param sigma_compare_label: plot label to use with sigma_compare

    :param spitzer_compare: provide another conductivity profile for comparison (so you can compare neoclassical and
        spitzer) (Ohm^1 m^1)

    :param spitzer_compare_label: plot label to use with spitzer_compare

    :param charge_number_to_use_in_ion_collisionality: instruction for replacing single ion species charge number Z in
        nuistar equation when going to multi-ion species plasma.
        Options are: ['Koh', 'Dominant', 'Zeff', 'Zavg', 'Koh_avg']

        Dominant uses charge number of ion species which contributed the most electrons (recommended by Sauter 2002)
        Koh uses expression from Koh 2012 page 072505-11 evaluated for dominant ion species (recommended by Koh 2012)
        Koh_avg evaluates Koh for all ion species and then averages over species
        Zeff uses Z_eff   (No paper recommends using this but it appears to be used by ONETWO)
        Zavg uses ne/sum(ni) (Koh 2012 recommends using this except for collision frequency)

        Use Koh for best agreement with TRANSP

    :param charge_number_to_use_in_ion_lnLambda: instruction for replacing single ion species charge number Z in
        lnLambda equation when going to multi-ion species plasma.
        Options are: ['Koh', 'Dominant', 'Zeff', 'Zavg', 'Koh_avg']

        Use Koh for best agreement with TRANSP

    :return: neoclassical conductivity in (Ohm^-1 m^-1) as a function of time and input psi_N
        (after interpolation/extrapolation).
        If output with "return_info_pack", the return is a dictionary containing several intermediate variables which
        are used in the calculation (collisionality, lnLambda, etc.)
    """

    printd('Starting nclass_conductivity()...')

    # Check inputs
    if Te is None:
        raise Exception('Please provide Te: electron temperature in eV')
    if ne is None:
        raise Exception('Please provide ne: electron density in m^-3')
    if Ti is None:
        raise Exception('Please provide Ti: ion temperature in eV')
    if q is None:
        raise Exception('Please provide q: safety factor')
    if eps is None:
        raise Exception('Please provide eps: inverse aspect ratio')
    if R is None:
        raise Exception('Please provide R: geometric major radius')
    if fT is None:
        raise Exception('Please provide fT: trapped particles fraction')
    if Zeff is None and (nis is None or Zis is None):
        raise Exception('Please provide Zeff or nis and Zis')

    def identify_dominant_ion(psi_N, nis, volume=None):
        # Pick the dominant ion species based on which one has the most particles in the plasma
        if volume is None:
            x = psi_N
            # This is made up based on looking at dVdpsi for a DIII-D shot
            a = [26, -50, 50, 20, -5, -45, 40]
            dVdpsi = a[0] + x * a[1] + x ** 2 * a[2] + x ** 3 * a[3] + x ** 4 * a[4] + x ** 5 * a[5] + x ** 6 * a[6]
        else:
            if len(volume[:, 0]) == 1:
                vol = volume[0, :]
            else:
                vol = volume.flatten()
            if len(vol) != len(psi_N):
                psivol = np.linspace(0, 1, len(vol))  # Assume volume is evenly gridded. Only has to be roughly true
                vol = interp1e(psivol, vol, bounds_error=False)(psi_N)  # interpolate to same grid
            dVdpsi = deriv(psi_N, vol)  # This is just 1D, no time variation
        printd(
            'np.shape(psi_N) = {:}, np.shape(dVdpsi) = {:}, np.shape(nis) = {:}, np.shape(nis[0]) = {:}'.format(
                np.shape(psi_N), np.shape(dVdpsi), np.shape(nis), np.shape(nis[0])
            )
        )
        Ni = [np.sum(n * dVdpsi[np.newaxis, :]) for n in nis]  # Number of ions in the whole plasma for each ion species
        printd('utils_fusion/nclass_conductivity pick dominant ion species by total number for each species = {:}'.format(Ni))
        Zdom = Zis[np.array(Ni).argmax()]  # The dominant ion species is the one that has contributed the most electrons
        printd('Zdom = {:}'.format(Zdom))
        return Zdom

    printd('nis is none = ', nis is None)
    printd('Zis is none = ', Zis is None)
    printd('Zeff is none = ', Zeff is None)

    # Estimate ni
    if nis is None or Zis is None:
        printe('Got Zeff instead of nis and Zis: density and charge state lists for ion species.')
        printe("I CAN GIVE YOU AN APPROXIMATION BUT IT'S NOT GOING TO BE AS GOOD AS IF YOU GAVE ME LISTS OF DENSITIES.")
        printe('You will get a better result if you do not pass in Zeff but use nis and Zis instead.')
        ni = ne / Zeff
        if Zdom is None:
            Zdom = 1  # This could be a bad assumption but we don't have enough information to do better
    else:
        ni = 0
        for idens in nis:
            ni += idens
        if Zdom is None:
            Zdom = identify_dominant_ion(psi_N, nis, volume=volume)

    # Calculate Zeff if needed (if ni1 and ni2 were provided instead of Zeff)
    if Zeff is None:
        printd('Zeff calculation: Zi={:}'.format(Zis))
        top = 0
        bot = 0
        for n, Z in zip(nis, Zis):
            top += n * Z ** 2
            bot += n * Z
        Zeff = top / bot

    # Figure out what Z to use
    # ----------------------
    # Electron contributions should use Zeff. Formulae that were set up
    # around a single ion species but are being applied to use multi-ion
    # species should use Zi_use as derived in Koh 2012
    Zavg = ne / ni  # With crude approx, this is the same as Zeff, but is different if you give nis and Zis
    Zion = (Zdom ** 2 * Zavg * Zeff) ** 0.25  # Thanks to memo from T. Osborne for pointing out how to do this correctly.
    # Zion is the thing defined on page 072505-11 of Koh 2012. It actually is different for each ion species & we are
    #   taking the dominant ion species only here.

    Zions = [(Zi ** 2 * Zavg * Zeff) ** 0.25 for Zi in Zis]
    Zions_avg = np.mean(Zions, axis=0)  # Average Zion over ion species

    # Zi_use = Zeff  # ##OVERRIDE! #this provides a closer match to ONETWO's collisionality (this one is pretty close!)
    # Zi_use = (1+6)/2.  # Another attempt to guess what ONETWO is using for Z in the collisionality formula. No good
    # Attempt to guess what ONETWO is using for Z in collisionality formula:
    # Zi_use = ((1**2*Zavg*Zeff)**0.25+(6**2*Zavg*Zeff)**0.25)/2.  # Maybe okay, but Zeff is simplest & is quite close
    #               this is just Zions_avg without the fast ions

    charges = {'Koh': Zion, 'Zeff': Zeff, 'Zavg': Zavg, 'Dominant': Zdom, 'Koh_avg': Zions_avg}
    Zi_use_L = charges[charge_number_to_use_in_ion_lnLambda]  # Default should be Zavg according to Koh 2012
    Zi_use_C = charges[charge_number_to_use_in_ion_collisionality]  # Default should be Koh according to Koh 2012
    # Sauter 2002 argues that both Zi_use_L and Zi_use_C should be Zdom

    # Get lnLambda
    # Te in eV, ne in m^-3
    lnLambda_e = 31.3 - ulog(usqrt(ne) / (Te))  # Coulomb logarithm for electrons, equation 18d  #checked 20161228
    #            double checked against nustar.m 20170109
    lnLambda_i = 30.0 - ulog(Zi_use_L ** 3 * usqrt(ni) / (Ti ** 1.5))  # coulomb log for ions, equation 18e # corrected 20161228
    #            Found error in 18e on 20161228: there was no exponent on Ti
    #            Double checked against nustar.m 20170109

    # This is a slightly better approximation for lnLambda_e
    lnLambda_e = (
        23.5 - ulog(usqrt(ne / 1e6) * Te ** (-5.0 / 4.0)) - (1e-5 + (ulog(Te) - 2) ** 2 / 16.0) ** 0.5
    )  # from NRL plasma formulary 2009

    # For testing: these are the values from TRANSP run 163518Z02 at 3161.8301 ms
    # lnLambda_e = np.array([16.45740492, 16.45745642, 16.45752222, 16.45762113, 16.45775022, 16.45790002, 16.45808447, 16.45835436, 16.45870941, 16.45910423, 16.45954932, 16.46018447, 16.46115912, 16.46238336, 16.46373288, 16.46507791, 16.46613178, 16.46677864, 16.46712405, 16.46718826, 16.46696071, 16.46674591, 16.46638516, 16.46495035, 16.4622057, 16.45838299, 16.45336374, 16.44712286, 16.43965871, 16.43097303,16.42172391,16.41268799,16.40372831,16.39453695,16.38529412,16.37617337,16.36720527,16.35857188,16.35072915,16.34355907,16.33629672,16.32882735,16.32139261,16.31396888,16.30636077,16.29821606,16.28908594,16.27838027,16.2658098, 16.25153383,16.23575693,16.21868639,16.20064944,16.18179137,16.16214103,16.14130336,16.11949054,16.09860627,16.07964074,16.06246154,16.04718249,16.03380838,16.02224146,16.01230328,16.00376401,15.99635613,15.98981701,15.9839138, 15.97846824,15.97339238,15.96822162,15.96245737,15.95642003,15.95041827,15.94426674,15.93778579,15.93100812,15.92396606,15.91647038,15.90830126,15.89927442,15.88925517,15.87803925,15.86512585,15.84983709,15.83096977,15.80759477,15.77921036,15.74565235,15.71095877,15.6805883, 15.65213927,15.62158566,15.58554183,15.52893339,15.43768248,15.31066696,15.15191654,14.96521764,14.74801185,14.51373066])
    # lnLambda_i = np.array([19.08457943, 19.08457045, 19.08453606, 19.08442039, 19.0841699, 19.08374097, 19.08307654, 19.08212694, 19.08086408, 19.07925627, 19.07726828, 19.07491088,19.07219271,19.06904422,19.06537592,19.06102342,19.05582741,19.04981124,19.04305752,19.03558596,19.02735736,19.01841191,19.00868028,18.99790959,18.98608369,18.97326995,18.95947305,18.94482622,18.92933777,18.91298187,18.89624088,18.87966111,18.86320301,18.84680991,18.83076295,18.81520821,18.80014086,18.78571484,18.77228396,18.7596463,18.7472592, 18.73529049,18.72391538,18.71291144,18.70192696,18.69037918,18.67769735,18.66348879,18.64766356,18.6304599,18.6122358, 18.59335548,18.57405567,18.55416246,18.53370998,18.51292077,18.49192448,18.47151272,18.45182219,18.43284742,18.41544709,18.39956384,18.3847349, 18.37090236,18.35793759,18.34563778,18.33373955,18.32182786,18.30931369,18.29472676,18.27758341,18.26008298,18.24357106,18.2279728, 18.2136288,18.20078569,18.1892778, 18.17857076,18.16795028,18.15682111,18.14480479,18.13168372,18.11737756,18.10183052,18.08481964,18.06577437,18.04447571,18.02150786,17.99782206,17.97638193,17.96077681,17.9500812, 17.94295325,17.93910024,17.93083772,17.90983098,17.87411739,17.82301861,17.75768593,17.6772152,17.58794751])

    # Sanitize lnLambda_e in case it somehow got negative.
    lle_min = lnLambda_e[lnLambda_e > 0].min()
    lnLambda_e[lnLambda_e < lle_min] = lle_min

    # Calculate collisionality
    eps_nz = copy.copy(eps)
    eps_nz[eps == 0] = min(eps[eps != 0])  # Prevent divide by zero
    # Te in eV, ne in m^-3
    nuestar = 6.921e-18 * abs(q) * R * ne * Zeff * lnLambda_e / (Te ** 2 * eps_nz ** 1.5)  # equation 18b  #checked 20161228
    #                       eqn 18b double checked against nustar.m 20170109
    nuistar = 4.90e-18 * abs(q) * R * ni * Zi_use_C ** 4 * lnLambda_i / (Ti ** 2 * eps_nz ** 1.5)  # equation 18c #checked 20161228
    #            eqn 18c checked against nustar.m 20170109, Zi_use in nustar.m is just main ion charge
    # collsionalities from TRANSP are about 0.62 as big as these. What is that about?
    # Uncomment these for testing to make collisionalities match TRANSP better:
    # nuestar *= 0.62
    # nuistar *= 0.62

    # Spitzer conductivity
    def NZ(Z):
        return 0.58 + 0.74 / (0.76 + Z)  # equation 18a line 2 #checked 20161228 # dbl check against sigmaneo.m 20170109

    # Te in eV:
    spitzer_conductivity = 1.9012e4 * Te ** 1.5 / (Zeff * NZ(Zeff) * lnLambda_e)  # equation 18a line 1 (Ohm^-1 m^-1)
    #             spitzer_conductivity checked 20161228 # result doesn't match TRANSP
    #             double checked against sigmaneo.m 20170109
    #
    #             neo_theory.f90 defines this very differently! DISCREPANCY FOUND 20170126:                            #
    #                   sigma_spitzer = dens_ele / ( mass(is_ele) * nue_S ) &
    #                        * 0.58 * 32 / (3.0*pi) / (0.58 + 0.74/(0.76+zeff))
    #                 I haven't yet intercepted the output so I don't know how different the result actually looks.

    # coefficients in neoclassical conductivity
    if version == 'neo_2021':
        f33teff = fT / (
            1 + 0.25 * (1 - 0.7 * fT) * usqrt(nuestar) * (1 + 0.45 * (Zeff - 1) ** 0.5) + 0.61 * (1 - 0.41 * fT) * nuestar / Zeff ** 0.5
        )  # eq (18) A.Redl, et al.
        F33 = 1 - (1 + 0.21 / Zeff) * f33teff + 0.54 / Zeff * f33teff ** 2 - 0.33 / Zeff * f33teff ** 3  # from eq (17) A.Redl, et al.
    else:
        f33teff = fT / (1 + (0.55 - 0.1 * fT) * usqrt(nuestar) + 0.45 * (1 - fT) * nuestar * Zeff ** (-1.5))  # eqn 13b, checked 20161228
        #                   eqn 13b double checked against neo_theory.f90 20170126
        F33 = 1 - (1 + 0.36 / Zeff) * f33teff + 0.59 / Zeff * f33teff ** 2 - 0.23 / Zeff * f33teff ** 3  # equation 13a, checked 20161228
        #                                                                    eqn 13a checked against neo_theory.f90 20170126
        # F33 doesn't match TRANSP: can be compared by ratio of sigma_neo/sigma_spitzer
    # F33 can be compared to TRANSP using OMFIT['nclass_testing']['scripts']['compare_spitzer_nclass_cond_ratio'],
    # which is one of the helper scripts generated by regression/test_nclass_conductivity.py
    #        equations 13a & 13b double checked against Sauter 1999 on 20170109 due to unresolved disagreement w/ TRANSP
    #                                       changing nuestar *= 0.62 does not remove disagreement.
    #        double checked 13a and 13b against sigmaneo.m 20170109

    neoclassical_conductivity = spitzer_conductivity * F33  # equation 13a ( 1/(Ohm m) )

    def plot_nc(display_slice):
        # Diagnostic plot for neoclassical conductivity calculation

        # Form the plot
        from matplotlib import pyplot

        f, ax = pyplot.subplots(3, 3, sharex=True)

        # Plot input profiles
        inputcol = 0  # Make it easy to reassign which column the input profiles go in
        inputcol2 = 1
        axtemp = ax[0, inputcol]  # axes to use for Te and Ti #make it easy to assign which plot goes where
        axdens = ax[1, inputcol]  # axes to use for ne and ni
        axze = ax[2, inputcol]  # axes to use for Zeff
        axq = ax[0, inputcol2]  # axes to use for safety factor q
        axgeo = ax[1, inputcol2]  # axes to use for geometry stuff like R and inverse aspect ratio
        axtrap = ax[2, inputcol2]  # axes to use for trapped particle fraction

        x = np.atleast_2d(psi_N)[display_slice, :]  # iI psi_N is 2D, extract the correct slice

        if axtemp is not None:
            axtemp.set_ylabel('(ev)')
            axtemp.set_title('Input: temperature')
            axtemp.plot(x, np.atleast_2d(Te)[display_slice, :], label='$T_e$')
            axtemp.plot(x, np.atleast_2d(Ti)[display_slice, :], label='$T_i$')

        if axdens is not None:
            axdens.set_ylabel('(m$^{-3}$)')
            axdens.set_title('Input: density')
            axdens.plot(x, np.atleast_2d(ne)[display_slice, :], label='$n_e$')
            axdens.plot(x, np.atleast_2d(ni)[display_slice, :], label=r'$\Sigma n_{i,thermal}$')

        if axze is not None:
            axze.set_title('Input: effective charge state')
            axze.plot(x, np.atleast_2d(Zeff)[display_slice, :], label='$Z_{eff}$')

        if axq is not None:
            axq.set_title('Input: safety factor')
            axq.plot(x, np.atleast_2d(q)[display_slice, :], label='$q$')

        if axgeo is not None:
            axgeo.set_title('Input: geometry')
            axgeo.plot(x, np.atleast_2d(eps)[display_slice, :], label=r'$\epsilon$')
            axgeo.plot(x, np.atleast_2d(R)[display_slice, :], label='R (m)')

        if axtrap is not None:
            axtrap.set_title('Input: trapped particle fraction')
            axtrap.plot(x, np.atleast_2d(fT)[display_slice, :], label='$f_T$')

        # Plot results
        resultscol = 2  # Define column and axes to use here to make it easy to rearrange
        axsig = ax[0, resultscol]  # axes to use for conductivity sigma
        axnu = ax[1, resultscol]  # axes for collisionality nu
        axln = ax[2, resultscol]  # axes for lnLambda

        axs = {
            'temp': axtemp,
            'dens': axdens,
            'zeff': axze,
            'q': axq,
            'geo': axgeo,
            'trap': axtrap,
            'sigma': axsig,
            'nu': axnu,
            'lnLambda': axln,
        }  # Dictionary of axes to return

        # Main result: conductivity
        if axsig is not None:
            axsig.set_ylabel(r'$\sigma$ (Ohm$^{-1}$ m$^{-1})$')
            axsig.plot(x, np.atleast_2d(neoclassical_conductivity)[display_slice, :], label='Neoclassical', lw=2, color='k')  # Key result
            axsig.plot(
                x, np.atleast_2d(spitzer_conductivity)[display_slice, :], label='Spitzer', color='r', linestyle='--'
            )  # Spitzer for reference
            axsig.set_title('Conductivity')
            if sigma_compare is not None:
                if len(np.shape(sigma_compare)) > 1:
                    sigcomp = sigma_compare[display_slice, :]  # If 2D, slice it like all the calculations
                else:
                    sigcomp = sigma_compare  # 1D is allowed
                axsig.plot(x, sigcomp, label=sigma_compare_label)  # User supplied conductivity for comparison
            if spitzer_compare is not None:
                if len(np.shape(spitzer_compare)) > 1:
                    spcomp = spitzer_compare[display_slice, :]  # If 2D, slice it like all the calculations
                else:
                    spcomp = spitzer_compare  # 1D is allowed
                axsig.plot(x, spcomp, '--', label=spitzer_compare_label)  # Compare user supplied spitzer conductivity

        # Intermediate quantity in calculation: collisionality
        if axnu is not None:
            axnu.set_ylabel(r'$\nu_*$')
            axnu.set_title('Collisionality')
            axnu.plot(x, np.atleast_2d(nuestar)[display_slice, :], label='Electrons')
            axnu.plot(x, np.atleast_2d(nuistar)[display_slice, :], label='Ions')
            # There is a big spike on-axis. This plot gets stuck on the on-axis value & goes stupid if auto-scaled
            # axnu.set_yscale('log')  # This is one option
            w = (0.1 < x) & (x < 0.9)  # Take the max value on this interval to define the y-axis limit
            axnu.set_ylim([0, max([max(nuestar[display_slice, w]), max(nuistar[display_slice, w])])])

        # Intermediate quantity: lnLambda
        if axln is not None:
            axln.set_ylabel(r'$ln\Lambda$')
            axln.set_title('Coulomb logarithm')
            axln.plot(x, np.atleast_2d(lnLambda_e)[display_slice, :], label=r'$ln\Lambda_e$')
            axln.plot(x, np.atleast_2d(lnLambda_i)[display_slice, :], label=r'$ln\Lambda_i$')

        # Clean up axes limits and put in horizontal/vertical marks at 0 and 1
        for axx in ax.flatten():
            axx.legend(loc=0).draggable()
            if axx.get_ylabel() != r'$ln\Lambda$':
                if min(axx.get_ylim()) > 0:
                    axx.set_ylim(0)
                else:
                    axx.axhline(0, linestyle='--', color='k')
            axx.axvline(1, linestyle='--', color='k')

        for i in range(len(ax[0, :])):
            ax[-1, i].set_xlabel(r'$\psi_N$')

        if os.environ.get('OMFIT_NO_GUI', '0') == '0':
            try:
                pyplot.tight_layout()
            except RuntimeError:
                pass
        return axs  # End of plot

    if plot_slice is not None:
        axs = plot_nc(plot_slice)
    else:
        axs = None

    if return_info_pack:  # This is for debugging or seeing terms that are used inside the calculation
        return {
            'neoclassical_conductivity': neoclassical_conductivity,
            'spitzer_conductivity': spitzer_conductivity,
            'electron_collisionality': nuestar,
            'ion_collisionality': nuistar,
            'lnLambda_e': lnLambda_e,
            'lnLambda_i': lnLambda_i,
            'q': q,
            'R': R,
            'eps': eps,
            'fT': fT,
            'Zeff': Zeff,  # Zeff, ni1, & ni2 can be inputs, but missing ones may be estimated from what is given
            'charge_state_details': {
                'Zions': Zions,
                'Zions_avg': Zions_avg,  # Average over ion species of Zions
                'Zion': Zion,  # This is the same as the Zions entry for main ion
                'Zdom': Zdom,
                'Zavg': Zavg,
            },
            'nis': nis,
            'ni': ni,
            'plot_axes': axs,
            'units_of_conductivity': 'Ohm^-1 m^-1',
        }

    return neoclassical_conductivity  # Units are 1/(Ohm*meter)


#########################################################
# nclass_conductivity wrapper providing g-file services #
#########################################################
@_available_to_user_fusion
def nclass_conductivity_from_gfile(
    psi_N=None,
    Te=None,
    ne=None,
    Ti=None,
    gEQDSK=None,
    Zeff=None,
    nis=None,
    Zis=None,
    Zdom=None,
    return_info_pack=False,
    plot_slice=None,  # Set to a time slice index to plot, set to None for no plot
    charge_number_to_use_in_ion_collisionality='Koh',
    charge_number_to_use_in_ion_lnLambda='Zavg',
):
    """
    WRAPPER FOR nclass_conductivity THAT EXTRACTS GFILE STUFF AND INTERPOLATES FOR YOU
    Calculation of neoclassical conductivity
    See: O. Sauter, et al., Phys. Plasmas 6, 2834 (1999); doi:10.1063/1.873240
    Neoclassical conductivity appears in equations: 5, 7, 13a, and unnumbered equations in the conclusion

    This function was initially written as part of the Kolemen Group Automatic Kinetic EFIT Project (auto_kEFIT).

    :param psi_N: position basis for all non-gfile profiles

    :param Te: electron temperature in eV as a function of time and position (time should be first axis, then position)

    :param ne: electron density in m^-3 (vs. time and psi)

    :param Ti: ion temperature in eV

    :param Zeff: [optional if nis and Zis are provided] effective charge state of ions
        = sum_j(n_j (Z_j)^2)/sum_j(n_j Z_j)  where j is ion species (this is probably a sum over deuterium and carbon)

    :param nis: [optional if Zeff is provided] list of ion densities in m^-3

    :param Zis: [optional if Zeff is provided] ion charge states (list of scalars)

    :param Zdom: [might be optional] specify the charge number of the dominant ion species. Defaults to the one with the
        highest total number of particles (volume integral of ni). If using the estimation method where only Zeff is
        provided, then Zdom is assumed to be 1 if not provided.

    :param gEQDSK: an OMFITcollection of g-files or a single g-file as an instance of OMFITgeqdsk

    :param return_info_pack: Boolean: If true, returns a dictionary full of many intermediate variables from this
        calculation instead of just conductivity

    :param plot_slice: Set to the index of the timeslice to plot in order to plot one timeslice of the calculation,
        including input profiles and intermediate quantities. Set to None for no plot (default)

    :param charge_number_to_use_in_ion_collisionality: instruction for replacing single ion species charge number Z in
        nuistar equation when going to multi-ion species plasma.
        Options are: ['Koh', 'Dominant', 'Zeff', 'Zavg', 'Koh_avg']

        Dominant uses charge number of ion species which contributed the most electrons (recommended by Sauter 2002)
        Koh uses expression from Koh 2012 page 072505-11 evaluated for dominant ion species (recommended by Koh 2012)
        Koh_avg evaluates Koh for all ion species and then averages over species
        Zeff uses Z_eff   (No paper recommends using this but it appears to be used by ONETWO)
        Zavg uses ne/sum(ni) (Koh 2012 recommends using this except for collision frequency)

        Use Koh for best agreement with TRANSP

    :param charge_number_to_use_in_ion_lnLambda: instruction for replacing single ion species charge number Z in
        lnLambda equation when going to multi-ion species plasma.
        Options are: ['Koh', 'Dominant', 'Zeff', 'Zavg', 'Koh_avg']

        Use Koh for best agreement with TRANSP

    :return: neoclassical conductivity in (Ohm^-1 m^-1) as a function of time and input psi_N (after
        interpolation/extrapolation).
        If output with "return_info_pack", the return is a dictionary containing several intermediate variables which
        are used in the calculation (collisionality, lnLambda, etc.)
    """

    printd('Starting nclass_conductivity_from_gfile()...')

    def extract_gEQDSK(gEQDSK):
        # Pulls stuff out of a stack of EFIT g-files (or just one g-file)

        # Determine whether we got one G-file or a stack of G-files. If it's a stack, then all the keys will be
        # numbers. Otherwise, we should find CASE.
        if 'CASE' in list(gEQDSK.keys()):
            # Single g-file
            gtime = gEQDSK['CASE'][4].split('ms')[0].strip()
            gfiles = {gtime: gEQDSK}
        else:
            # Assume stack of g-files
            gfiles = gEQDSK
        keys = list(gfiles.keys())

        # Get out basic info
        nf = gfiles[keys[0]]['NW']  # Number of flux surfaces in the g-file
        nt = len(keys)  # Number of time slices in the stack of g-files
        psi_N_efit = gfiles[keys[0]]['fluxSurfaces']['levels']  # psi_N grid of the EFITs

        # Get q profile, geometry info, and trapped fraction
        q = np.zeros([nt, nf])
        R = np.zeros([nt, nf])
        fT = np.zeros([nt, nf])
        eps = np.zeros([nt, nf])
        volume = np.zeros([nt, nf])
        for j, t in enumerate(keys):
            q[j, :] = abs(gfiles[t]['QPSI']) * np.sign(gfiles[t]['CURRENT'] * gfiles[t]['fluxSurfaces']['BCENTR'])
            R[j, :] = gfiles[t]['fluxSurfaces']['geo']['R']
            eps[j, :] = gfiles[t]['fluxSurfaces']['geo']['a'] / R[j, :]  # Local inverse aspect ratio of the flux surface
            fc = gfiles[t]['fluxSurfaces']['avg']['fc']
            fT[j, :] = 1 - fc  # Fraction of trapped particles
            volume[j, :] = gfiles[t]['fluxSurfaces']['geo']['vol']  # Volume enclosed by each flux surface
        return psi_N_efit, R, eps, q, fT, volume, nt

    psi_N_efit, R, eps, q, fT, volume, nt = extract_gEQDSK(gEQDSK)  # Get EFIT info

    def reposition(x, y, newx):
        # Interpolates 2D stuff
        newy = np.zeros([nt, len(newx)])
        # printd('np.shape(x) = {:}, np.shape(y) = {:}'.format(np.shape(x),np.shape(y)))
        for t in range(nt):
            newy[t, :] = interp1e(x[t, :], y[t, :], bounds_error=False)(newx)
        return newy

    # Interpolate all the profiles
    if len(np.shape(psi_N)) == 1:
        psi_N = psi_N[np.newaxis, :] + Te * 0
    Te = reposition(psi_N, Te, psi_N_efit)
    ne = reposition(psi_N, ne, psi_N_efit)
    Ti = reposition(psi_N, Ti, psi_N_efit)
    if Zeff is not None:
        Zeff = reposition(psi_N, Zeff, psi_N_efit)
    if nis is not None:
        nis = [reposition(psi_N, ni, psi_N_efit) for ni in nis]

    # Call the real deal
    ret = nclass_conductivity(
        psi_N=psi_N_efit,
        Te=Te,
        ne=ne,
        Ti=Ti,
        q=q,
        eps=eps,
        R=R,
        fT=fT,
        volume=volume,
        Zeff=Zeff,
        nis=nis,
        Zis=Zis,
        Zdom=Zdom,
        return_info_pack=return_info_pack,
        plot_slice=plot_slice,
        charge_number_to_use_in_ion_collisionality=charge_number_to_use_in_ion_collisionality,
        charge_number_to_use_in_ion_lnLambda=charge_number_to_use_in_ion_lnLambda,
    )
    return ret


##############################################################
# Sauter's formula for flux surface averaged j_bootstrap * B #
##############################################################


@_available_to_user_fusion
def sauter_bootstrap(
    psi_N=None,
    Te=None,
    Ti=None,
    ne=None,
    p=None,
    nis=None,
    Zis=None,
    Zeff=None,
    gEQDSKs=None,
    R0=None,
    device='DIII-D',
    psi_N_efit=None,
    psiraw=None,
    R=None,
    eps=None,
    q=None,
    fT=None,
    I_psi=None,
    nt=None,
    version=jbs_versions[1],
    debug_plots=False,
    return_units=False,
    return_package=False,
    charge_number_to_use_in_ion_collisionality='Koh',
    charge_number_to_use_in_ion_lnLambda='Zavg',
    dT_e_dpsi=None,
    dT_i_dpsi=None,
    dn_e_dpsi=None,
    dnis_dpsi=None,
):
    """
    Sauter's formula for bootstrap current

    See: O. Sauter, et al., Phys. Plasmas 6, 2834 (1999); doi:10.1063/1.873240

    Other references:

    S Koh, et al., Phys. Plasmas 19, 072505 (2012); doi: 10.1063/1.4736953
        for dealing with ion charge number when there are multiple species
    T Osborne, "efit.py Kinetic EFIT Method", private communication (2013);
        this is a word file with a description of equations used to form the current profile constraint
    O Sauter, et al., Phys. Plasmas 9, 5140 (2002); doi:10.1063/1.1517052
        this has corrections for Sauter 1999 but it also has a note on what Z to use in which equations; it argues that ion equations should use the
        charge number of the main ions for Z instead of the ion effective charge number from Koh 2012
    `Sauter website <https://crppwww.epfl.ch/~sauter/neoclassical/>`_
        Accurate neoclassical resistivity, bootstrap current and other
        transport coefficients (Fortran 90 subroutines and matlab functions): has some code that was used to check
        the calculations in this script (BScoeff.m, nustar.m, sigmaneo.m, jdotB_BS.m)
    `GACODE NEO source <https://github.com/gafusion/gacode/blob/master/neo/src/neo_theory.f90>`_
        Calculations from NEO (E. A. Belli)
    Y R Lin-Liu, et al., "Zoo of j's", DIII-D physics memo (1996);
        got hardcopy from Sterling Smith & photocopied
    Update August 2021 : add new set of analytical formulae for the computation of the neoclassical condactivity from
        A.Redl, et al., Phys. Plasma 28, 022502 (2021) https://doi.org/10.1063/5.0012664  and all relevant variables are mentioned as neo_2021

    This function was initially written as part of the Kolemen Group Automatic Kinetic EFIT Project (auto_kEFIT).

    :param psi_N: normalized poloidal magnetic flux as a position coordinate for input profiles Te, Ti, ne, etc.

    :param Te: electron temperature in eV, first dimension: time, second dimension: psi_N

    :param Ti: ion temperature in eV, 2D with dimensions matching Te (time first)

    :param ne: electron density in m^-3, dimensions matching Te

    :param p: total pressure in Pa, dimensions matching Te

    :param Zeff: [optional if nis and Zis are provided] effective charge state of ions
        = sum_j(n_j (Z_j)^2)/sum_j(n_j Z_j)  where j is ion species (this is probably a sum over deuterium and carbon)

    :param nis: [optional if Zeff is provided] list of ion densities in m^-3

    :param Zis: [optional if Zeff is provided] ion charge states (list of scalars)

    :param R0: [optional if device is provided and recognized] The geometric center of the tokamak's vacuum vessel in m.
        (For DIII-D, this is 1.6955 m (Osborne, Lin-Liu))

    :param device: [used only if R0 is not provided] The name of a tokamak for the purpose of looking up R0

    :param gEQDSKs: a collection of g-files from which many parameters will be derived. The following quantities are
        taken from g-files if ANY of the required ones are missing:

        :param psi_N_efit: [optional] psi_N for the EFIT quantities if different from psi_N for kinetic profiles

        :param nt: [optional] number of time slices in equilibrium data (if you don't want to tell us, we will measure
            the shape of the array)

        :param psiraw: poloidal flux before normalization (psi_N is derived from this).

        :param R: major radius coordinate R of each flux surface's geometric center in m

        :param q: safety factor (inverse rotation transform)

        :param eps: inverse aspect ratio of each flux surface: a/R

        :param fT: trapped particle fraction on each flux surface

        :param I_psi: also known as F = R*Bt, averaged over each flux surface

    :param version: which quantity to return:
                    'jB_fsa' is the object directly from Sauter's paper: 2nd term on RHS of last equation in conclusion.
                    'osborne' is ``jB_fsa w/ |I_psi|`` replaced by R0. Motivated by memo from T. Osborne about kinetic EFITs
                    'jboot1' is 2nd in 1st equation of conclusion of Sauter 1999 w/ correction from Sauter 2002 erratum.
                    'jboot1BROKEN' is jboot1 without correction from Sauter 2002 (THIS IS FOR TESTING/COMPARISON ONLY)
                    'neo_2021' a new set of analytical coefficients from A.Redl, et al. (the new set of analytical formulae consists of the same analytical structure as the 'jboot1' and 'jboot1BROKEN' )

                    You should use jboot1 if you want ``<J.B>``
                    You should use osborne if you want J ******* Put this into current_to_efit_form() to make an EFIT
                    You should use jboot1 or jB_fsa to compare to Sauter's paper, equations 1 and 2 of the conclusion
                    You should use jboot1BROKEN to compare to Sauter 1999 without the 2002 correction

    :param debug_plots: plot internal quantities for debugging

    :param return_units: If False: returns just the current profiles in one 2D array. If True: returns a 3 element tuple
        containing the current profiles, a plain string containing the units, and a formatted string containing the
        units

    :param return_package: instead of just a current profile, return a dictionary containing the current profile as well
        as other information

    :param charge_number_to_use_in_ion_collisionality: instruction for replacing single ion species charge number Z in
        nuistar equation when going to multi-ion species plasma.
        Options are: ['Koh', 'Dominant', 'Zeff', 'Zavg', 'Koh_avg']

        Dominant uses charge number of ion species which contributed the most electrons (recommended by Sauter 2002)
        Koh uses expression from Koh 2012 page 072505-11 evaluated for dominant ion species (recommended by Koh 2012)
        Koh_avg evaluates Koh for all ion species and then averages over species
        Zeff uses Z_eff   (No paper recommends using this but it appears to be used by ONETWO)
        Zavg uses ne/sum(ni) (Koh 2012 recommends using this except for collision frequency)

        Use Koh for best agreement with TRANSP
        Use Zavg for best agreement with recommendations by Koh 2012

    :param charge_number_to_use_in_ion_lnLambda: instruction for replacing single ion species charge number Z in
        lnLambda equation when going to multi-ion species plasma.
        Options are: ['Koh', 'Dominant', 'Zeff', 'Zavg', 'Koh_avg']

        Use Koh for best agreement with TRANSP
        Use Koh for best agreement with recommendations by Koh 2012

    :return jB: flux surface averaged j_bootstrap * B with some modifications according to which version you select

    :return units: [only if return_units==True] a string with units like "A/m^2"

    :return units_format: [only if return_units==True] a TeX formatted string with units like "$A/m^2$"
        (can be included in plot labels directly)

    This is first equation in the conclusion of Sauter 1999 (which is equation 5 with stuff plugged in)
    (with correction from the erratum (Sauter 2002)::

        <j_par * B> = sigma_neo * <E_par * B> - I(psi) p_e *
                          [L_31 * p/p_e * d_psi(ln(p)) + L_32 * d_psi(ln(T_e))
                          + L_34 * alpha * (1-R_pe)/R_pe * d_psi(ln(T_i))]

    The second equation in the conclusion is nicer looking::

        <j_par * B> = sigma_new * <E_par * B> - I(psi) p *
                       [L_31 d_psi(ln(n_e)) + R_pe * (L_31 + L_32) * d_psi(ln(T_e))
                       + (1-R_pe)*(1+alpha*L_34/L_31)*L_31 * d_psi(ln(T_i))]

    In both equations, the first term is ohmic current and the second
    term is bootstrap current. The second equation uses some
    approximations which make the result much smoother. The first
    equation had an error in the original Sauter 1999 paper that was
    corrected in the 2002 erratum.

    * < > denotes a flux surface average (mentioned on page 2835)
    * j_par is the parallel current (parallel to the magnetic field B) (this is what we're trying to find)
    * B is the total magnetic field
    * sigma_neo is the neoclassical conductivity given by equation 7 on page 2835 or equation 13 on page 2837
      (this is mentioned as neoclassical resistivity on page 2836, but the form of the
      equation clearly shows that it is conductivity, the reciprocal of resistivity.
      Also the caption of figure 2 confirms that conductivity is what is meant.)
    * E_par is the parallel electric field
    * I(psi) = R * B_phi (page 2835)
    * p_e is the electron pressure
    * L_31, L_32, and L_34 are given by equations 8, 9, and 10 respectively (eqns on page 2835).
      Also they are given again by eqns 14-16 on pages 2837-2838
    * p is the total pressure
    * d_psi() is the derivative with respect to psi (not psi_N)
    * T_e is the electron temperature
    * alpha is given by equation 11 on page 2835 or by eqn 17a on page 2838
    * T_i is the ion temperature
    * R_pe = p_e/p
    * f_T the trapped particle fraction appears in many equations and is given by equation 12 on page 2835
      but also in equation 18b with nu_i* in equation 18c

    useful quantities are found in equation 18
    """

    printd('Starting sauter_bootstrap()...')

    if R0 is None:
        spec = device_specs(device)
        if 'R0' in list(spec.keys()) and spec['R0'] is not None:
            R0 = spec['R0']  # Nominal major radius: center of the vacuum vessel
        else:
            raise Exception('failed to look up R0 for device {:}! Please check your device settings!'.format(device))

    # Extract info from the g-files -----------------------------
    def extract_gEQDSK(gEQDSK):
        printi('  sauter_bootstrap: extracting data from gfiles...')
        # Pulls stuff out of a stack of EFIT g-files (or just one g-file)
        # Determine whether we got one G-file or a stack of G-files. If it's a stack, then all the keys will be
        # numbers. Otherwise, we should find CASE.
        if 'CASE' in list(gEQDSK.keys()):
            # Single g-file
            gtime = gEQDSK['CASE'][4].split('ms')[0].strip()
            gfiles = {gtime: gEQDSK}
        else:
            # Assume stack of g-files
            gfiles = gEQDSK
        keys = list(gfiles.keys())

        # Get out basic info
        nf = gfiles[keys[0]]['NW']  # Number of flux surfaces in the g-file
        nt = len(keys)  # Number of time slices in the stack of g-files
        psi_N_efit = gfiles[keys[0]]['fluxSurfaces']['levels']  # psi_N grid of the EFITs
        # Get q profile, geometry info, and trapped fraction
        q = np.zeros([nt, nf])
        R = np.zeros([nt, nf])
        fT = np.zeros([nt, nf])
        eps = np.zeros([nt, nf])
        I_psi = np.zeros([nt, nf])
        psiraw = np.zeros([nt, nf])
        for j, t in enumerate(keys):
            q[j, :] = abs(gfiles[t]['QPSI']) * np.sign(gfiles[t]['CURRENT'] * gfiles[t]['fluxSurfaces']['BCENTR'])

            R[j, :] = gfiles[t]['fluxSurfaces']['geo']['R']  # (m)

            eps[j, :] = gfiles[t]['fluxSurfaces']['geo']['a'] / R[j, :]  # Local inverse aspect ratio of the flux surface

            fc = gfiles[t]['fluxSurfaces']['avg']['fc']

            fT[j, :] = 1 - fc  # Fraction of trapped particles

            # <R*Bt> != <R>*<Bt> so we have to use I_psi = F instead of
            #   I_psi = gfile['fluxSurfaces']['avg']['Bt']*gfile['fluxSurfaces']['avg']['R']
            I_psi[j, :] = gfiles[t]['fluxSurfaces']['avg']['F']  # (T m) # this is the same as FPOL

            psiraw[j, :] = gfiles[t]['fluxSurfaces']['geo']['psi']

        return psi_N_efit, psiraw, R, eps, q, fT, I_psi, nt

    if psiraw is None or R is None or eps is None or q is None or fT is None or I_psi is None:
        # Some of the equilibrium data are missing, so we have to extract an EFIT
        psi_N_efit, psiraw, R, eps, q, fT, I_psi, nt = extract_gEQDSK(gEQDSKs)
    else:
        # We have enough equilibrium data to infer the rest
        if psi_N_efit is None:
            # If for some reason you have declined to put kinetic (ne, Te, etc) profiles on the same grid as the
            # equilibrium quantities, then please provide the psi_N grid for equilbrium quantities so that things can
            # be interpolated to the same grid. Otherwise, this happens.
            psi_N_efit = psi_N  # If psi_N_efit isn't provided, we'll assume it's the same as psi_N for kinetic profiles
        if nt is None:  # Number of timeslices
            if len(np.shape(psi_N)) == 2:
                nt = len(psi_N[:, 0])  # Count time slices in 2D data
            else:
                nt = 1  # 1D data must've come from a single timeslice

    # Interpolate profiles as needed ----------------------------
    def reposition(x, y, xnew):  # For interpolating 2d data on one axis
        nt = len(y[:, 0])
        ynew = np.zeros([nt, len(xnew)])
        for i in range(nt):
            if len(np.shape(x)) == 2:
                xx = x[i, :]
            else:
                xx = x
            printd('reposition np.shape(xx) = {:}, np.shape(y[i,:]) = {:}'.format(np.shape(xx), np.shape(y[i, :])))
            ynew[i, :] = interp1e(xx, y[i, :], bounds_error=False)(xnew)
        return ynew

    if np.array_equal(psi_N, psi_N_efit):
        pass  # No interpolation needed, they already match
    else:
        Te = reposition(psi_N, Te, psi_N_efit)
        Ti = reposition(psi_N, Ti, psi_N_efit)
        ne = reposition(psi_N, ne, psi_N_efit)
        p = reposition(psi_N, p, psi_N_efit)
        printd('repositioned Te,Ti,ne,p')
        if Zeff is not None:
            printd('repositioning Zeff')
            Zeff = reposition(psi_N, Zeff, psi_N_efit)
        if nis is not None:
            printd('repositioning nis')
            nis = [reposition(psi_N, ni, psi_N_efit) for ni in nis]

    # Get some of the quantities that are calculated along the way in the neoclassical conductivity calculation --------
    info = nclass_conductivity(
        psi_N=psi_N_efit,
        Te=Te,
        ne=ne,
        Ti=Ti,
        q=q,
        eps=eps,
        R=R,
        fT=fT,
        nis=nis,
        Zis=Zis,
        Zeff=Zeff,
        charge_number_to_use_in_ion_collisionality=charge_number_to_use_in_ion_collisionality,
        charge_number_to_use_in_ion_lnLambda=charge_number_to_use_in_ion_lnLambda,
        return_info_pack=True,
    )
    Zeff = info['Zeff']
    nuestar = info['electron_collisionality']
    nuistar = info['ion_collisionality']
    lnLambda_e = info['lnLambda_e']  # This isn't actually needed for the rest of the jboot calculations

    # Calculate more basic quantities -----------------------
    # pe
    pe = Te * ne * scipy.constants.e  # (Pa)
    # pe_err = np.sqrt(Te_err**2*ne**2+ne_err**2*Te**2)*scipy.constants.e  # (Pa)

    # R_pe
    R_pe = pe / p

    # d/dpsi
    if nt == 1:  # if there is only one timeslice, gradient() will complain about getting a 2d array
        gradpsi = np.atleast_2d(np.gradient(psiraw[0]))  # Gradient of un-normalized psi
    else:
        gradpsi = np.gradient(psiraw, axis=1)  # Gradient of un-normalized psi

    def d_psi(y):
        if is_uncertain(y):
            dy = np.gradient(nominal_values(y), axis=1)
            ye = std_devs(y)
            sigma = np.zeros_like(ye)
            sigma[:, 1:-1] = 0.5 * np.sqrt(ye[:, :-2] ** 2 + ye[:, 2:] ** 2)
            sigma[:, 0] = 0.5 * np.sqrt(ye[:, 0] ** 2 + ye[:, 1] ** 2)
            sigma[:, -1] = 0.5 * np.sqrt(ye[:, -2] ** 2 + ye[:, -1] ** 2)
            dy = unumpy.uarray(dy, sigma)
        else:
            dy = np.gradient(y, axis=1)
        return dy / gradpsi

    # Calculate Sauter coefficients ------------------------------------

    def F31(X):
        # Equation 14a (also used in equation 16a)
        if version == 'neo_2021':
            F31 = (
                (1 + 0.15 / (Zeff ** 1.2 - 0.71)) * X
                - 0.22 / (Zeff ** 1.2 - 0.71) * X ** 2
                + 0.01 / (Zeff ** 1.2 - 0.71) * X ** 3
                + 0.06 / (Zeff ** 1.2 - 0.71) * X ** 4
            )  # eq(10) from A.Redl, et al.
        else:
            F31 = (
                (1 + 1.4 / (Zeff + 1)) * X - 1.9 / (Zeff + 1) * X ** 2 + 0.3 / (Zeff + 1) * X ** 3 + 0.2 / (Zeff + 1) * X ** 4
            )  # Checked 20161228
        #                         F31 double checked against BScoeff.m 20170109, checked against neo_theory.f90 20170126
        return F31

    if version == 'neo_2021':
        f31teff = fT / (
            1
            + (0.67 * (1 - 0.7 * fT) * usqrt(nuestar)) / (0.56 + 0.44 * Zeff)
            + (0.52 + 0.086 * usqrt(nuestar)) * (1 + 0.87 * fT) * nuestar / (1 + 1.13 * (Zeff - 1) ** 0.5)
        )  # eq(11) from A.Redl, et al.
    else:
        f31teff = fT / (1.0 + (1.0 - 0.1 * fT) * usqrt(nuestar) + 0.5 * (1.0 - fT) * nuestar / Zeff)  # Equation 14b, checked 20161228

    # L31   from equation 14
    #                         eqn 14b double checked against BScoeff.m 20170109, checked against neo_theory.f90 20170126
    L_31 = F31(f31teff)  # Equation 14a  (or eq 10 from A.Redl, et al.)

    if version == 'neo_2021':
        f32eiteff = fT / (
            1
            + ((0.87 * (1 + 0.39 * fT) * usqrt(nuestar)) / (1 + 2.95 * (Zeff - 1) ** 2))
            + 1.53 * (1 - 0.37 * fT) * nuestar * (2 + 0.375 * (Zeff - 1))
        )  # eq(16) from A.Redl, et al.
    else:
        # L32   from equation 15
        # Corrected error in eqn 15e on 20161228 (sign of 0.6*fT was wrong)
        f32eiteff = fT / (
            1.0 + (1 + 0.6 * fT) * usqrt(nuestar) + 0.85 * (1.0 - 0.37 * fT) * nuestar * (1.0 + Zeff)
        )  # Equation 15e, corrected 20161228
    #                         eqn 15e double checked against BScoeff.m 20170109, checked against neo_theory.f90 20170126
    Y = f32eiteff  # Temporary shorter name for f32eiteff

    if version == 'neo_2021':
        F32ei = (
            -(0.4 + 1.93 * Zeff) / (Zeff * (0.8 + 0.6 * Zeff)) * (Y - Y ** 4)
            + 5.5 / (1.5 + 2 * Zeff) * (Y ** 2 - Y ** 4 - 0.8 * (Y ** 3 - Y ** 4))
            - 1.3 / (1 + 0.5 * Zeff) * Y ** 4
        )  # eq (15) from A.Redl, et al.

    else:
        F32ei = (
            -(0.56 + 1.93 * Zeff) / (Zeff * (1.0 + 0.44 * Zeff)) * (Y - Y ** 4)
            + 4.95 / (1 + 2.48 * Zeff) * (Y ** 2 - Y ** 4 - 0.55 * (Y ** 3 - Y ** 4))
            - 1.2 / (1.0 + 0.5 * Zeff) * Y ** 4
        )  # Equation 15c # checked 20161228, checked against neo_theory.f90 20170126
    #           Which Z should be used in F32ei? Neo uses the same "zeff" as elsewhere.
    if version == 'neo_2021':
        f32eeteff = fT / (
            1
            + (0.23 * (1 - 0.96 * fT) * usqrt(nuestar)) / Zeff ** 0.5
            + (0.13 * (1 - 0.38 * fT) * nuestar / Zeff ** 2)
            * (usqrt(1 + 2 * (Zeff - 1) ** 0.5) + fT ** 2 * usqrt((0.075 + 0.25 * (Zeff - 1) ** 2) * nuestar))
        )  # eq(14) from A.Redl, et al.

    else:

        f32eeteff = fT / (
            1.0 + 0.26 * (1.0 - fT) * usqrt(nuestar) + 0.18 * (1.0 - 0.37 * fT) * nuestar / usqrt(Zeff)
        )  # Equation 15d,checked 20161228
    #                         eqn 15d double checked against BScoeff.m 20170109, checked against neo_theory.f90 20170126
    X = f32eeteff  # Temporary shorter name for f32eeteff

    if version == 'neo_2021':
        F32ee = (0.1 + 0.6 * Zeff) / (Zeff * (0.77 + 0.63 * (1 + (Zeff - 1) ** 1.1))) * (X - X ** 4)
        (
            +0.7 / (1 + 0.2 * Zeff) * (X ** 2 - X ** 4 - 1.2 * (X ** 3 - X ** 4)) + 1.3 / (1 + 0.5 * Zeff) * X ** 4
        )  # eq(13) from A.Redl, et al.

    else:

        F32ee = (
            (0.05 + 0.62 * Zeff) / (Zeff * (1.0 + 0.44 * Zeff)) * (X - X ** 4)
            + 1.0 / (1.0 + 0.22 * Zeff) * (X ** 2 - X ** 4 - 1.2 * (X ** 3 - X ** 4))
            + 1.2 / (1.0 + 0.5 * Zeff) * X ** 4
        )  # Equation 15b, checked 20161228
    #                       eqn 15b double checked 20170109 against Sauter 1999, checked against neo_theory.f90 20170126
    L_32 = F32ee + F32ei  # Equation 15a # double checked against BScoeff.m 20170109 (or eq (12) from  from A.Redl, et al.)

    if version == 'neo_2021':
        f34teff = fT / (
            (1 + 0.25 * (1 - 0.7 * fT) * usqrt(nuestar) * (1 + 0.45 * (Zeff - 1) ** 0.5))
            + (0.61 * (1 - 0.41 * fT) * nuestar) / (Zeff ** 0.5)
        )  # eq(18) from from A.Redl, et al. ; which is actually f33teff
    else:

        # L34  from equation 16
        # eqn 16b is very similar to 14b but there is an extra factor of 0.5 in front of the last appearance of fT
        f34teff = fT / (1 + (1 - 0.1 * fT) * usqrt(nuestar) + 0.5 * (1 - 0.5 * fT) * nuestar / Zeff)  # Equation 16b, checked 20161228
    #                         eqn 16b double checked against BScoeff.m 20170109, checked against neo_theory.f90 20170126
    L_34 = F31(
        f34teff
    )  # Equation 16a # double checked against BScoeff.m 20170109, checked against neo_theory.f90 (or eq(19) from from A.Redl, et al.)

    if version == 'neo_2021':
        alpha0 = (
            -(0.62 + 0.055 * (Zeff - 1)) / (0.53 + 0.17 * (Zeff - 1)) * (1 - fT) / (1 - (0.31 - 0.065 * (Zeff - 1)) * fT - 0.25 * fT ** 2)
        )  # eq(20) from from A.Redl, et al.

    else:
        # alpha from equation 17
        alpha0 = -1.17 * (1.0 - fT) / (1.0 - 0.22 * fT - 0.19 * fT ** 2)  # Checked 20161228, double checked against BScoeff.m 20170109
    #       Double checked against neo_theory.f90 20170126

    if version == 'neo_2021':
        alpha = ((alpha0 + 0.7 * Zeff * fT ** 0.5 * usqrt(nuistar)) / (1 + 0.18 * usqrt(nuistar)) - 0.002 * nuistar ** 2 * fT ** 6) * (
            1 / (1 + 0.004 * nuistar ** 2 * fT ** 6)
        )  # eq (21) from A.Redl, et al.

    else:
        alpha = ((alpha0 + 0.25 * (1 - fT ** 2) * usqrt(nuistar)) / (1.0 + 0.5 * usqrt(nuistar)) + 0.315 * nuistar ** 2 * fT ** 6) / (
            1.0 + 0.15 * nuistar ** 2 * fT ** 6
        )  # equation 17a with correction from the erratum (Sauter 2002) #checked 20161228
    #                          eqn 17 double checked against BScoeff.m 20170109, checked against neo_theory.f90 20170126
    alphawrong = ((alpha0 + 0.25 * (1 - fT ** 2) * usqrt(nuistar)) / (1 + 0.5 * usqrt(nuistar)) - 0.315 * nuistar ** 2 * fT ** 6) / (
        1 + 0.15 * nuistar ** 2 * fT ** 6
    )  # equation 17a WITHOUT correction from the erratum (Sauter 2002)
    # This is what eqn17a looks like in sauter 1999; the difference is the sign of the second term (+ or - before 0.315)

    # Allow import of derivatives for better error propagation
    if dT_e_dpsi is None:
        dT_e_dpsi = d_psi(Te)

    if dT_i_dpsi is None:
        dT_i_dpsi = d_psi(Ti)

    if dn_e_dpsi is None:
        dn_e_dpsi = d_psi(ne)

    ni = np.sum(nis, axis=0)

    if dnis_dpsi is not None:
        dn_i_dpsi = np.sum(dnis_dpsi, axis=0)
        dp_dpsi = (ni * dT_i_dpsi + Ti * dn_i_dpsi + ne * dT_e_dpsi + Te * dn_e_dpsi) * scipy.constants.e  # (Pa / Weber)
    else:
        dp_dpsi = d_psi(p)

    # Inverse scale lengths (these are saved so they can be compared to NEO)
    dlnTedpsi = dT_e_dpsi / Te
    dlnTidpsi = dT_i_dpsi / Ti
    dlnpdpsi = dp_dpsi / p
    inv_scale_lengths = {'Te': dlnTedpsi, 'Ti': dlnTidpsi, 'p': dlnpdpsi}

    # Assemble the result ==========================================
    front = -I_psi * pe * np.sign(q)
    bra1 = L_31 * dp_dpsi / pe  # First term in the brackets
    bra2 = L_32 * dT_e_dpsi / Te  # Second term in the brackets
    bra3 = L_34 * alpha * (1 - R_pe) / R_pe * dT_i_dpsi / Ti  # Last term in the brackets
    bra3_broken = L_34 * alphawrong * dT_i_dpsi / Ti  # Last term in the brackets WITHOUT THE CORRECTION
    #                                             FROM THE ERRATUM (Sauter 2002) THIS IS JUST FOR TESTING/COMPARISON.
    #                                             IT IS WRONG!

    jboot1 = front * (bra1 + bra2 + bra3)  # This is the second term in the first equation of the conclusion of Sauter 1999
    #                                  with correction from Sauter 2002). It tends to be less smooth than the second
    #                                  equation, which is coming right up.
    #                                  The bootstrap current (times B) is the second term in equation for <j_par*B>,
    #                                  the first term is ohmic current (times B)

    jboot1BROKEN = front * (bra1 + bra2 + bra3_broken)  # THIS IS WRONG! THIS IS WHAT YOU WOULD GET IF YOU DID NOT HAVE THE
    #                                               CORRECTION FROM THE 2002 ERRATUM BY SAUTER

    # This definition of the bootstrap current assumes that
    #  d ln(n_e)     d ln(n_i)
    #  ---------  =  ---------
    #    d psi         d psi
    # or put another way, d_psi(ln(n_e))=d_psi(ln(n_i))  same inverse scale length for electrons and ions

    # This one (jB) is smoother than jboot1; it is the second equation in Sauter's conclusion. You are less likely to
    # get an ugly double peak if you have badly matched electron and ion density profiles, but the result doesn't agree
    # as nicely with TRANSP. jB has more assumptions in it than jboot1, so it is intrinsically worse if you trust your
    # profile fits. If your profile fits aren't great, it might actually improve matters by forcing some physics in.
    # Checked 20161228
    jB = (
        -I_psi
        * p
        * (L_31 * dn_e_dpsi / ne + R_pe * (L_31 + L_32) * dT_e_dpsi / Te + (1 - R_pe) * (L_31 + alpha * L_34) * dT_i_dpsi / Ti)
        * np.sign(q)
    )
    # Double checked jB against jdotB_BS.m 20170109

    # jB and jboot1 have units of N/m^3  =  T A/m^2  =  Pa/m
    units_jB = 'N/m^3'
    units_jB_format = '$N/m^3$'

    # Calculate different expressions
    # -------------------------------
    jB_osborne = jboot1 / abs(I_psi) * R0  # I_psi is just Bt * R. This replaces I_psi with just R0.
    # This change doesn't change the spatial variation much. I used abs(I_psi) so that it would go in the same direction
    # as all the other quantities.

    units_osb = 'A/m^2'
    units_osb_format = '$A/m^2$'

    if version == 'jB_fsa':
        # This is the basic one straight from the paper (second eqn) with no funny business
        printd(" selected second term in second equation of Sauter 1999 conclusion: jB")
        return_val = jB
        units = units_jB
        units_format = units_jB_format
    elif version == 'jboot1':
        # Also straight from the paper, but without some of the assumptions which make the result much smoother
        printd(
            " selected second term in FIRST equation of Sauter 1999 conclusion with correction from Sauter 2002: "
            "jboot1 (this could be noisier than the second eqn)"
        )
        return_val = jboot1
        units = units_jB
        units_format = units_jB_format
    elif version == 'jboot1BROKEN':
        # TESTING ONLY: this one has the error that was corrected in Sauter 2002
        printd(
            " selected second term in FIRST equation of Sauter 1999 conclusion WITHOUT CORRECTION "
            "(CONTAINS ERROR!!): jboot1BROKEN (this could be noisier than the second eqn)"
        )
        for i in range(3):
            printe(
                ' WARNING! You have selected a return value that contains a known error. '
                'This option is included for testing purposes only!'
            )
        return_val = jboot1BROKEN
        units = units_jB
        units_format = units_jB_format
    elif version == 'osborne':
        # This is an attempt to match the quantity that is used by EFIT.
        printd(" selected expression motivated by memo from Osborne: jB/I_psi*R0")
        return_val = jB_osborne
        units = units_osb
        units_format = units_osb_format
    elif version == 'neo_2021':
        # new set of analytical formulae for the computation of the neoclassical condactivity from
        # A.Redl, et al., Phys. Plasma 28, 022502 (2021)
        printd(
            " new new set of analytical formulae from A.Redl, et al., Phys. Plasma 28, 022502 (2021): "
            " the new set of analytical formulae consists of the same analytical structure as the 'jboot1'"
        )
        return_val = jboot1
        units = units_jB
        units_format = units_jB_format

    else:
        # Same as if version == 'jboot1'
        printd(" defaulted to sauter's thing: jboot1 (first equation in conclusion w/ correction from Sauter 2002)")
        return_val = jboot1
        units = units_jB
        units_format = units_jB_format

    if debug_plots:
        f, ax = pyplot.subplots(3)
        colors = ['b', 'r', 'k', 'g', 'y', 'm'] * 100
        for tt in range(nt):
            ax[0].plot(psi_N_efit, I_psi[tt, :], label='I(psi), timeslice # {:}'.format(tt), color=colors[tt])

            ax[1].plot(psi_N_efit, jB[tt, :], label='jB : <J*B> from 2nd eqn in concl', color=colors[tt])
            ax[1].plot(psi_N_efit, jB_osborne[tt, :], label='jB_osborne: jB*R0/|I_psi|', color=colors[tt], linestyle='--')
            ax[1].plot(psi_N_efit, jboot1[tt, :], label='jboot1 : <J*B> from 1st eqn in conclusion', color=colors[tt], linestyle='-.')

            ax[2].set_title('compare jboot1 with & without Sauter 2002 correction')
            ax[2].plot(psi_N_efit, jboot1[tt, :], label='<J*B>: first equation with 2002 correction', color=colors[tt])
            ax[2].plot(psi_N_efit, jboot1BROKEN[tt, :], label='BAD <J*B>: first equation WITH ERROR', color=colors[tt], linestyle='--')

        ax[2].legend(loc=0, no_duplicates=True).draggable()
        ax[1].legend(loc=0, no_duplicates=True).draggable()
        ax[0].legend(loc=0).draggable()
        ax[-1].set_xlabel(r'$\psi_N$')

    # Put it back to the input psi_N grid if profiles didn't already match EFIT grid
    if np.array_equal(psi_N, psi_N_efit):
        if return_package:
            return_val = {
                'bootstrap_current_result': return_val,
                'calculation_version': version,
                'term1': bra1,
                'term2': bra2,
                'term3': bra3,
                'front': front,
                'alpha': alpha,
                'alpha0': alpha0,
                'nuistar': nuistar,
                'lnLambda_e': lnLambda_e,
                'fT': fT,
                'inverse_scale_lengths': inv_scale_lengths,
            }
    else:
        printd(' repositioning return value (interp back to original psi_N)')
        if return_package:
            return_val = {
                'bootstrap_current_result': reposition(psi_N_efit, return_val, psi_N),
                'calculation_version': version,
                'term1': reposition(psi_N_efit, bra1, psi_N),
                'term2': reposition(psi_N_efit, bra2, psi_N),
                'term3': reposition(psi_N_efit, bra3, psi_N),
                'front': reposition(psi_N_efit, front, psi_N),
                'alpha': reposition(psi_N_efit, alpha, psi_N),
                'alpha0': reposition(psi_N_efit, alpha0, psi_N),
                'nuistar': reposition(psi_N_efit, nuistar, psi_N),
                'lnLambda_e': reposition(psi_N_efit, lnLambda_e, psi_N),
                'fT': reposition(psi_N_efit, fT, psi_N),
                'inverse_scale_lengths': {
                    'Te': reposition(psi_N_efit, inv_scale_lengths['Te'], psi_N),
                    'Ti': reposition(psi_N_efit, inv_scale_lengths['Ti'], psi_N),
                    'p': reposition(psi_N_efit, inv_scale_lengths['Tp'], psi_N),
                },
            }
        else:
            return_val = reposition(psi_N_efit, return_val, psi_N)

    if return_units:
        return return_val, units, units_format
    else:
        return return_val


#####################################################
# Convert current density to EFIT constraint format #
#####################################################
@_available_to_user_fusion
def current_to_efit_form(r0, inv_r, cross_sec, total_current, x):
    """
    Conversion of current density to EFIT constraint format. Adapted from currentConstraint.py by O. Meneghini
    :param r0: major radius of the geometric center of the vacuum vessel (1.6955 m for DIII-D) (scalar)

    :param inv_r: flux surface average (1/R); units should be reciprocal of r0 (function of position or
        function of position and time)

    :param cross_sec: cross sectional area of the plasma in m^2 (scalar or function of time

    :param total_current: total plasma current in A (scalar or function of time)

    :param x: input current density to be converted in A/m^2 (function of position or function of position and time)

    :return: x normalized to EFIT format (function of position or function of position and time)
    """

    r0_over_r = r0 * inv_r
    return x * 1.0 / r0_over_r / (total_current / cross_sec)  # Normalized to be unitless


##########################
# Estimate Ohmic current #
##########################
@_available_to_user_fusion
def estimate_ohmic_current_profile(cx_area, sigma, itot, jbs=None, ibs=None, jdriven=None, idriven=None):

    """
    Estimate the profile of ohmic current using total current, the profile of bootstrap and driven current, and
    neoclassical conductivity. The total Ohmic current profile is calculated by integrating bootstrap and driven current
    and subtracting this from the total current. The Ohmic current profile is assigned assuming flat loop voltage and
    the total is scaled to match the estimated total Ohmic current.

    All inputs should be on the same coordinate system with the same dimensions, except itot, ibs, and idriven should
    lack the position axis. If inputs have more than one dimension, position should be along the axis with index = 1
    (the second dimension).

    This function was initially written as part of the Kolemen Group Automatic Kinetic EFIT Project (auto_kEFIT).

    :param cx_area: Cross sectional area enclosed by each flux surface as a function of psin in m^2

    :param sigma: Neoclassical conductivity in Ohm^-1 m^-1

    :param itot: Total plasma current in A

    :param jbs: [optional if ibs is provided] Bootstrap current density profile in A/m^2. If this comes from
        sauter_bootstrap(), the recommended version is 'osborne'

    :param ibs: [optional if jbs is provided] Total bootstrap current in A

    :param jdriven: [optional if idriven is provided] Driven current density profile in A/m^2

    :param idriven: [optional if jdriven is provided] Total driven current in A

    :return: Ohmic current profile as a function of psin in A/m^2
    """

    # If total bootstrap and driven currents aren't provided, try to integrate bootstrap & driven current density.
    if ibs is None:
        ibs = np.trapz(jbs, cx_area, axis=-1)
    if idriven is None:
        idriven = np.trapz(jdriven, cx_area, axis=-1)

    iohm = itot - ibs - idriven

    printd('Total current: {:} A, bootstrap current: {:} A, driven current: {:} A'.format(itot, ibs, idriven))

    e0 = 1  # V/m  # The value doesn't matter because it normalizes out, but we put it here to keep track of units

    johm_raw = sigma * e0  # (V/m) / (Ohm m) = A/m^2
    iohm_raw = np.trapz(johm_raw, cx_area, axis=-1)
    iohm_raw_nz = copy.copy(iohm_raw)
    iohm_raw_nz[iohm_raw == 0] = 1
    norm = iohm / iohm_raw_nz
    norm[iohm_raw == 0] = 1

    johm = johm_raw * norm[:, np.newaxis]

    return johm


##################################################################
# Tim Stoltzfus-Dueck & Arash Ashourvan intrinsic rotation model #
##################################################################
@_available_to_user_fusion
def intrinsic_rotation(geo_a, geo_R, geo_Rx, R_mp, rho, I_p_sgn, Te, Ti, q, fc, B0, rho_ped, rho_sep=1.0, C_phi=1.0, d_c=1.0):
    """
    Tim Stoltzfus-Dueck & Arash Ashourvan intrinsic rotation model

    :param geo_a: [m] plasma minor radius evaluated at the midplane

    :param geo_R: [m] plasa major radius evaluated at the midplane

    :param geo_Rx: [m] radial position of the X point

    :param R_mp: [m] midplane radial coordinate from on-axis to the separatrix (LFS)

    :param rho: normalised sqrt(toroidal flux)

    :param I_p_sgn: sign of I_p to get the correct rotation direction, positive rotation is alway co-current

    :param Te: [eV] electron temperature profile

    :param Ti: [eV] ion temperature profile

    :param q: safety factor/q profile

    :param fc: Flux surface averaged passing particles fraction profile

    :param B0: [T] Magnetic field on axis

    :param rho_ped: rho value at pedestal top

    :param rho_sep: rho value at separatrix (/pedestal foot)

    :param C_phi: constant that translates Te scale length to turbulence scale length. default value = 1.75, range: [1.0,2.0]/[0.5,4]

    :param d_c: ballooning parameter for turbulence, where 0.0 is symmetric in ballooning angle, 2.0 is all at LFS. default value = 1.0, range: [0.0,2.0]

    :return omega_int: [rad/s] intrinsic plasma rotation at pedestal top
    """
    # Rx_bar in [-1,1]: normalised geometric quantity indicating X-point orietation,
    # where -1 is inboard, 0 centered, 1 outboard
    Rx_bar = (geo_Rx - geo_R) / geo_a

    # calculate L_Te
    # _ped indicates value at pedestal top, _sep indicates value at outer pedestal boundary
    Te_ped = uinterp1d(rho, Te, bounds_error=False)(rho_ped)
    Te_sep = uinterp1d(rho, Te, bounds_error=False)(rho_sep)
    R_ped = uinterp1d(rho, R_mp, bounds_error=False)(rho_ped)
    R_sep = uinterp1d(rho, R_mp, bounds_error=False)(rho_sep)
    grad_Te = (Te_ped - Te_sep) / (R_sep - R_ped)
    L_Te = 0.5 * (Te_ped + Te_sep) / grad_Te

    # Ti at the pedestal top
    Ti_ped = uinterp1d(rho, Ti, bounds_error=False)(rho_ped)

    # q, fc, Btot at the pedestal top
    q_ped = uinterp1d(rho, abs(q), bounds_error=False)(rho_ped)
    fc_ped = uinterp1d(rho, fc, bounds_error=False)(rho_ped)

    # Calculate L_phi from L_Te
    L_phi = C_phi * L_Te

    # Calculate v_int & omega_int
    v_int = 1.04 * fc_ped * (0.5 * d_c - Rx_bar) * q_ped * Ti_ped / (L_phi * B0)
    omega_int = np.sign(I_p_sgn) * v_int / R_ped
    return omega_int


def Hmode_profiles(edge=0.08, ped=0.4, core=2.5, rgrid=201, expin=1.5, expout=1.5, widthp=0.04, xphalf=None):
    """
     This function generates H-mode  density and temperature profiles evenly
     spaced in your favorite radial coordinate

    :param edge: (float) separatrix height

    :param ped: (float) pedestal height

    :param core: (float) on-axis profile height

    :param rgrid: (int) number of radial grid pointsx

    :param expin: (float) inner core exponent for H-mode pedestal profile

    :param expout (float) outer core exponent for H-mode pedestal profile

    :param width: (float) width of pedestal

    :param xphalf: (float) position of tanh
    """

    w_E1 = 0.5 * widthp  # width as defined in eped
    if xphalf is None:
        xphalf = 1.0 - w_E1

    xped = xphalf - w_E1

    pconst = 1.0 - np.tanh((1.0 - xphalf) / w_E1)
    a_t = 2.0 * (ped - edge) / (1.0 + np.tanh(1.0) - pconst)

    coretanh = 0.5 * a_t * (1.0 - np.tanh(-xphalf / w_E1) - pconst) + edge

    xpsi = np.linspace(0, 1, rgrid)
    ones = np.ones(rgrid)

    val = 0.5 * a_t * (1.0 - np.tanh((xpsi - xphalf) / w_E1) - pconst) + edge * ones

    xtoped = xpsi / xped
    for i in range(0, rgrid):
        if xtoped[i] ** expin < 1.0:
            val[i] = val[i] + (core - coretanh) * (1.0 - xtoped[i] ** expin) ** expout

    return val


def Lmode_profiles(edge=0.08, core=3.2, rgrid=201, peaking=6.0):
    """
    This function generates an evenly spaced radial L-mode profile
    Fixed at the edge and core value specified

    :param edge: (float) separatrix height

    :param core: (float) on-axis profile height

    :param rgrid: (int) number of radial grid points

    :param peaking: (float > 0.) small values give a broad profile, large values result in a peaked profile

    """
    # Reasonable profile defined on rho_tor_norm
    x_new = np.linspace(0, 1, 10 * rgrid)
    val = integz(x_new, peaking * x_new, x_new[-1], edge, x_new)

    # Make profiles more reasonable on psi grid
    x = np.linspace(0, 1, rgrid)
    val = np.interp(x, x_new ** 2, val)

    # scale profile
    val = (val - edge) * (core - edge) / (val[0] - val[-1]) + edge

    return val


###################################################
# USes scipy.optimize to find the h-mode pedestal #
###################################################
def pedestal_finder(profile, psi_norm=None, eped_definition=False, return_fit=False, doPlot=False, ngrid=201):
    from scipy import optimize, interpolate

    # param : plasma profile,  a 1D profile on a rho or psi grid (i.e. Te, P, ni)
    # param : return_fit, returns profile_fit_grid and profile_fit
    # param : doPlot, compares the fit to the data

    # if return_fit=False: return pedestal top, pedestal width
    # if return_fit=True:  return pedestal top, pedestal width, profile_fit_grid, profile_fit
    if isinstance(profile, int):
        printe('ERROR! ne input should be a 1D profile')

    def cost_function(c):
        if any(c < 0):
            return 1e10

        if eped_definition:
            nval = Hmode_profiles(
                rgrid=len(profile), xphalf=None, widthp=c[1], core=profile[0], ped=c[0], edge=profile[-1], expin=2.0, expout=2.0
            )
        else:
            nval = Hmode_profiles(
                rgrid=len(profile), xphalf=c[2], widthp=c[1], core=profile[0], ped=c[0], edge=profile[-1], expin=2.0, expout=2.0
            )

        cost = np.sqrt(sum(((profile - nval) ** 2 / profile[0] ** 2) * weight_func))
        return cost

    if psi_norm is None:
        psi_norm = np.linspace(0, 1, len(profile))

    profile = np.interp(fp=profile, xp=psi_norm, x=np.linspace(0, 1, ngrid))
    psi_norm = np.linspace(0, 1, ngrid)

    inversion_point = np.argmin(np.gradient(profile[int(ngrid / 2) :])) + int(ngrid / 2)
    inversion_point_margin = inversion_point - int(0.1 * ngrid)

    weight_func = np.zeros(ngrid)
    weight_func[inversion_point_margin:] += 1.0

    width0 = 1 - psi_norm[inversion_point]

    # eped definition sets xphalf to 1 - width
    # non eped definition optimizes over xphalf
    if eped_definition:
        c = [interpolate.interp1d(psi_norm, profile)([1 - 2 * width0])[0], width0]
        c = list(map(float, optimize.minimize(cost_function, c, method='Nelder-Mead', jac=False).x))
        nval_fit = Hmode_profiles(rgrid=ngrid, widthp=c[1], core=profile[0], ped=c[0], xphalf=None, edge=profile[-1], expin=2.0, expout=2.0)
    else:
        xphalf0 = 1 - width0 * 0.5
        c = [interpolate.interp1d(psi_norm, profile)([1 - 2 * width0])[0], width0, xphalf0]
        c = list(map(float, optimize.minimize(cost_function, c, method='Nelder-Mead', jac=False).x))
        nval_fit = Hmode_profiles(rgrid=ngrid, widthp=c[1], core=profile[0], ped=c[0], xphalf=c[2], edge=profile[-1], expin=2.0, expout=2.0)

    if doPlot:
        pyplot.figure()
        pyplot.plot(psi_norm, profile, label='raw')
        pyplot.plot(psi_norm, nval_fit, label='fit')
        pyplot.legend()

    if return_fit:
        return c[0], c[1], psi_norm, nval_fit  # pedestal top, pedestal width, profile_fit_grid, profile_fit
    return c[0], c[1]  # pedestal top, pedestal width


def blend_core_ped(psin, val, ped, widthp, edge, expin, expout, nml, blend_method='top=minimum gradient'):

    """
    This function returns core profile blended with desired pedestal width and height

    :param psin: (1d array) normalized psi

    :param val: (1d array) core profile to blend

    :param ped: (float) pedestal height

    :param widthp (flaot) pedestal width

    :param edge: (float) separatrix height

    :param expin: (float) inner core exponent for H-mode pedestal profile

    :param expout (float) outer core exponent for H-mode pedestal profile

    :param nml: (float) no mans land blending region

    :param blend_method: (str) method for determining the pedestal top
        options: 'top=minimum gradient', 'no mans land', 'EPED pedestal top'
    """

    # Generate H-mode pedestal profiles
    val_eped = Hmode_profiles(edge=edge, ped=ped, core=val[0], rgrid=len(psin), expin=expin, expout=expout, widthp=widthp)

    # Calculate inverse scale length
    z_0 = calcz(psin, val, consistent_reconstruction=False)
    z_1 = calcz(psin, val_eped, consistent_reconstruction=False)

    # Define linear interpolation point as local minimum of inverse scale length
    arg_nml = np.argmin((psin - nml) ** 2)
    if blend_method == 'top=minimum gradient':
        arg_top = np.argmin(z_1[arg_nml:]) + arg_nml
        top = psin[arg_top]
    elif blend_method == 'no mans land':
        top = nml = 1.0 - 2.5 * widthp
        arg_top = np.argmin(top ** 2)
        z_0[arg_nml:arg_top] = z_0[arg_nml]
    else:
        top = 1.0 - 2.5 * widthp

    # Blend inverse scale length profiles
    psin, z_new = mergez(psin, z_0, psin, z_1, 0.0, nml, top, psin)

    # Integrate blended z starting at psi_pedestal
    psi_bc = 1 - widthp * 2
    val_bc = interpolate.interp1d(psin, val_eped)(psi_bc)
    val_new = integz(psin, z_new, psi_bc, val_bc, psin)

    return val_new


def reactivity(Ti, model='D-T'):
    """
    Return value of fit to ['D-T', 'D-He3', 'D-DtoT', 'D-DtoHe3']  reactivity given ion temperature.
    This function is a direct translation to Python of what in is in TGYRO

    >> Ti = logspace(0, 10, 1000)
    >> pyplot.loglog(Ti, reactivity(Ti, 'D-T'), label='D-T')
    >> pyplot.loglog(Ti, reactivity(Ti, 'D-He3'), label='D-He3')
    >> pyplot.ylim([1E-28, 1E-21])

    :param Ti: thermal ion temperature in [eV]

    :param model: ['D-T', 'D-He3', 'D-DtoT', 'D-DtoHe3']

    :return: reactivity in [m^3/s]
    """
    Ti = Ti / 1e3  # from eV to keV

    if model == 'D-T':
        # Table VII of H.-S. Bosch and G.M. Hale, Nucl. Fusion 32 (1992) 611.
        c1 = 1.17302e-9
        c2 = 1.51361e-2
        c3 = 7.51886e-2
        c4 = 4.60643e-3
        c5 = 1.3500e-2
        c6 = -1.06750e-4
        c7 = 1.36600e-5
        bg = 34.3827
        er = 1.124656e6
    elif model == 'D-He3':
        bg = 68.7508
        mc2 = 1124572.0
        c1 = 5.51036e-10
        c2 = 6.41918e-3
        c3 = -2.02896e-3
        c4 = -1.91080e-5
        c5 = 1.35776e-4
        c6 = 0.0
        c7 = 0.0
        er = 18.3e6
    elif model == 'D-DtoT':
        bg = 31.3970
        mc2 = 937814.0
        c1 = 5.65718e-12
        c2 = 3.41267e-3
        c3 = 1.99167e-3
        c4 = 0.0
        c5 = 1.05060e-5
        c6 = 0.0
        c7 = 0.0
        er = 4.03e6
    elif model == 'D-DtoHe3':
        bg = 31.3970
        mc2 = 937814.0
        c1 = 5.43360e-12
        c2 = 5.85778e-3
        c3 = 7.68222e-3
        c4 = 0.0
        c5 = -2.96400e-6
        c6 = 0.0
        c7 = 0.0
        er = 0.82e6
    else:
        raise ValueError("Reactivity fits can be either ['D-T','D-He3','D-DtoT', 'D-DtoHe3']")

    # Eq. (12)
    r0 = Ti * (c2 + Ti * (c4 + Ti * c6)) / (1.0 + Ti * (c3 + Ti * (c5 + Ti * c7)))
    theta = Ti / (1.0 - r0)
    xi = (bg ** 2 / (4.0 * theta)) ** (1.0 / 3.0)

    sigv = c1 * theta * np.sqrt(xi / (er * Ti ** 3)) * np.exp(-3.0 * xi)

    return sigv / 1e6  # from cm^3/s to m^3/s


def fusion_power(n1, n2, Ti, model='D-T'):
    """
    Fusion heating power density for ['D-T', 'D-He3', 'D-DtoT', 'D-DtoHe3']
    This function is a direct translation to Python of what in is in TGYRO

    :param n1: density of first ion species in [m^-3]

    :param n2: density of second ion species in [m^-3]

    :param Ti: thermal ions temperature in [eV]

    :param model: ['D-T', 'D-He3', 'D-DtoT', 'D-DtoHe3']

    :return: fusion power [W/m^3]
    """
    if model == 'D-T':
        charged_particle_energy = 3.5e6  # eV
    elif model == 'D-He3':
        charged_particle_energy = 3.6e6 + 14.7e6  # eV
    elif model == 'D-DtoT':
        charged_particle_energy = 1.01e6 + 3.02e6  # eV
    elif model == 'D-DtoHe3':
        charged_particle_energy = 0.82e6  # eV

    charged_particle_energy_erg = charged_particle_energy * 1.6022e-12  # erg
    charged_particle_energy_joules = charged_particle_energy_erg * 1e-7  # Joules
    rate = n1 * n2 * reactivity(Ti, model)  # in 1/m^3/s
    power_watts = rate * charged_particle_energy_joules  # J/m^3/s = W/m^3
    return power_watts  # W/m^3


def sivukhin(x):
    """
    Compute a low-accuracy but fast approximation to the ion-alpha heating fraction.
    This function is a direct translation to Python of what in is in TGYRO.

                 x
              1  /     dy
      F(x) = --- | -----------
              x  /  1+y^(3/2)
                 0

    Here, F is the fraction of the alpha energy transferred
    to ions (at common temperature Ti) by collisions, and

                 x = E_alpha/E_crit

    Details are given in Stix, Plasma Phys. 14 (1972) 367.
    The function F is derived from Sivukhin's energy loss
    equation and so that is the rationale for the name.

    :param x: E_alpha/E_crit

    :return: ion-alpha heating fraction
    """

    def scalar_f(x, ngrid=201):
        y = np.linspace(0, 1, ngrid) * x
        f = np.trapz(1.0 / (1.0 + y ** 1.5), x=y)
        return f / x

    vector_f = np.vectorize(scalar_f)
    return vector_f(x)


def alpha_heating(ni, zi, mi, ne, te):
    """
    Alpha heating coefficients [Stix, Plasma Phys. 14 (1972) 367]
    See in particular Eqs. 15 and 17.
    This function is a direct translation to Python of what in is in TGYRO

    :param ni: list with thermal ions densities [m^-3]

    :param zi: list with thermal ions charges

    :param mi: list with thermal ions masses [AMU]

    :param ne: electron density [m^-3]

    :param te: electron temperature [eV]

    :return: frac_ai, alpha heating to the ions (electron alpha heating is (1-frac_ai)
    """

    malpha = constants.proton_mass * 4
    me = constants.electron_mass
    e_alpha = 3.5e6

    ni = np.atleast_2d(ni)
    mi = np.atleast_1d(mi)
    zi = np.atleast_1d(zi)

    c_a = ne * 0
    for k in range(ni.shape[0]):
        c_a += (ni[k] / ne) * zi[k] ** 2 * (mi[k] * constants.proton_mass / malpha)

    e_cross = te * (4.0 * np.sqrt(me / malpha) / (3.0 * np.sqrt(np.pi) * c_a)) ** (-2.0 / 3.0)

    x_a = e_alpha / e_cross
    frac_ai = sivukhin(x_a)
    # frac_ae = 1.0 - frac_ai
    return frac_ai


@_available_to_user_fusion
def standardize_gas_species_name(name, output_form='simple', on_fail='raise'):
    """
    Standardizes gas species names that could come from different/unknown sources.

    These include common impurity gas molecules, so nitrogen and deuterium translate
    to N2 and D2, since they form diatomic molecules.

    For example, N2, N$_2$, N_2, and nitrogen all mean the same thing. This function
    should accept any one of those and turn it into the format you request.

    Intended to handle exotic capitaliation; e.g. corrects NE or ne into Ne.

    :param name: str
        The name of the species

    :param output_form: str
        simple: the shortest, simplest, unambiguous and correct form. E.g.: N2
        latex: latex formatting for subscripts. E.g.: N$_2$
        name: the name of the species. E.g.: nitrogen
        markup: symbol with punctuation like _ to indicate underscores, but no $. E.g.: N_2
        atom: just the symbol for the atom without molecular information. E.g.: N
            This isn't recommended as an output format; it's here to simplify lookup in case
            someone indicates nitrogen gas by N instead of N2. Doesn't work for
            mixed-element molecules.

    :param on_fail: str
        Behavior on lookup failure.
            raise: raise OMFITexception
            print: print an error message and return None
            quiet: quietly return None

    :return: str
    """
    # Check inputs
    valid_output_forms = ['simple', 'latex', 'name', 'markup', 'atom']
    if output_form not in valid_output_forms:
        err_msg = f'Output format {output_form} is invalid. Please chose one of: {",".join(valid_output_forms)}.'
        if on_fail == 'raise':
            raise OMFITexception(err_msg)
        elif on_fail == 'print':
            printe(err_msg)
        else:
            printd(err_msg)
        printd('output_form will be changed to simple')
        output_form = 'simple'

    # Define known gas species
    names = dict(
        none=dict(latex='', name='no gas / empty', markup='', atom=''),
        H2=dict(latex='H$_2$', name='hydrogen', markup='H_2', atom='H'),
        D2=dict(latex='D$_2$', name='deuterium', markup='D_2', atom='D'),
        He=dict(latex='He', name='helium', markup='He', atom='He'),
        C2D2=dict(latex='C_2D_2', name='deuterated acetylene', markup='C_2D_2', atom=None),
        CD4=dict(latex='CD$_4$', name='deuterated methane', markup='CD_4', atom=None),
        N2=dict(latex='N$_2$', name='nitrogen', markup='N_2', atom='N'),
        Ne=dict(latex='Ne', name='neon', markup='Ne', atom='Ne'),
        Ar=dict(latex='Ar', name='argon', markup='Ar', atom='Ar'),
        Kr=dict(latex='Kr', name='krypton', markup='Kr', atom='Kr'),
    )

    # Step 1: identify which element we're talking about by finding its simple form
    namel = name.lower().strip()
    simple = None
    for k, v in names.items():
        nml = k.lower()
        if namel == nml:
            simple = k
            break
        elif namel in [vv.lower() if vv is not None else vv for vv in v.values()]:
            simple = k
            break

    # Deal with problems in step 1 before moving on
    if simple is None:
        err_msg = f'Did not recognize gas species {name}. Name translation failed.'
        if on_fail == 'raise':
            raise OMFITexception(err_msg)
        elif on_fail == 'print':
            printe(err_msg)
        else:
            printd(err_msg)
        return None

    # Step 2: convert to the desired output form
    if output_form == 'simple':
        if simple == 'none':
            return ''
        return simple
    else:
        return names[simple][output_form]


@_available_to_user_fusion
def lookup_d3d_gas_species(shot, valve=None, output_form=None):
    """
    Retrieves information on the gas species loaded into DIII-D gas injector(s)

    :param shot: int
        Shot to look up. The species loaded into each valve can change from shot to shot.

    :param valve: str [optional]
        Name of the gas valve or injector, like 'A' or 'PFX1'.
        'GASA' and 'A' are interchangeable. The valve name is not case sensitive.
        If provided, returns a string with the gas species for this valve, or raises OMFITexception on failure.
        If not provided, returns a dictionary of all the gas valves and species in the database.

    :param name_format: str [optional]
        Reformat the name of the gas species to conform to a preferred standard. Options (with examples) are:
            simple: N2
            latex: N$_2$
            name: nitrogen
            markup: N_2
        Set to None to get the string as written in the database.

    :return: str or dict
        Either the species of a specific valve, or a dictionary of all recorded valves and species.
        Either the return value itself or the dictionary values will be strings that are padded with spaces.
        If a valve is not in use, its gas species will be recorded as 'None '.
    """
    from omfit_classes.omfit_rdb import OMFITrdb

    shotgasvalve = OMFITrdb(query=f"select * from shotvalvegas where shot = {shot}", db='d3drdb', server='d3drdb', by_column=True)
    if valve is not None:
        if valve.lower().startswith('gas'):
            valve_ = valve[3:]
        else:
            valve_ = valve
        lowercasevalves = np.array([tmp.lower() for tmp in shotgasvalve['valve']])
        if valve_.lower() in lowercasevalves:
            result = shotgasvalve['gas'][lowercasevalves == valve_.lower()][0]
        elif valve.lower() in lowercasevalves:
            result = shotgasvalve['gas'][lowercasevalves == valve.lower()][0]
        else:
            raise OMFITexception(f'No record for gas valve {valve} for DIII-D#{shot}')

        if output_form is not None:
            return standardize_gas_species_name(result, output_form=output_form)
        else:
            return result

    else:
        result = {shotgasvalve['valve'][i]: shotgasvalve['gas'][i] for i in range(len(shotgasvalve['valve']))}
        if output_form is not None:
            return {k: standardize_gas_species_name(v, output_form=output_form) for k, v in result.items()}
        else:
            return result


@_available_to_user_fusion
def east_gas_injection(
    shot=None,
    valve=None,
    species=None,
    main_ion_species='D',
    server='EAST',
    tank_temperature=293.15,
    verbose=True,
    plot_total=False,
    plot_flow=False,
    tsmo=0.5,
    axs=None,
):
    """
    Calculates EAST gas injection amounts based on tank pressure

    Whereas DIII-D gas commands in V are often close to proportional to gas flows
    (because they're really inputs to an external flow controller built into the
    valve assembly), EAST gas commands are much more raw. An EAST command of 5 V
    is NOT roughly double a command of 2.5 V, for example. 2.5 V might not even
    open the valve, and there'd be no way to be sure from just the command. There
    is no flow sensor inside the EAST injectors like there is at DIII-D (the
    source of the gasb_cal measurement instead of the gascgasb command). Lastly,
    the EAST reservoirs behind the injectors are small and so the flow rate vs.
    voltage is probably not constant. The "tank" here isn't really a huge tank of
    gas, it's a length of pipe between the big tank of gas and the injector itself.
    So, letting out enough gas to control a shot really can affect it significantly.

    To get an actual measurement, we can turn to the pressure in the gas tank that
    feeds the injector and watch its decrease over time to get a flow rate. This
    script doesn't calculate a flow rate, it provides the integral of the flow rate.
    Since the data are noisy, some smoothing is recommended before differentiation
    to find the flow rate; we leave the choice of smoothing strength to the end user.

    Limitations:

    1. COOLING: We assumed constant temperature so far, but the gas tank clearly
    is cooled by letting gas out because the pressure very slowly rebounds after
    the shot, presumably from the tank warming up again. Remember the "tank" is
    actually just a little length of pipe behind the injector. To see how much
    error this causes, just look at how much tank pressure rebounds after seeding
    stops. The time history usually extends long after the shot. It seems like a
    small enough error that it hasn't been corrected yet.

    2. NEEDS POST-PROCESSING: most users are probably interested in flow rates
    and will have to take derivatives of the outputs of this function to get them,
    including smoothing to defeat noise in the signals.

    3. INCOMPLETE INFO: the electrons_per_molecule_puffed dictionary only lists a
    few species so far.

    :param shot: int
        EAST shot number, like 85293

    :param valve: str
        Like OU1. Also accepts names like OUPEV1 and VOUPEV1; PEV and leading V will be removed.
        There are different naming conventions in different contexts and this function tries to
        parse them all.

    :param species: str
        Species in the tank, like Ne.
        Diluted species are accepted; for example, "50% Ne" will be split at % and give 0.5 of the molecules as Ne
            and 0.5 of the molecules as the main ion species (probably D2).

    :param main_ion_species: str
        Species of main ions of the plasma, like D

    :param server: str
        MDSplus server to use as the source of the data. Intended to allow choice between 'EAST' and 'EAST_US'.

    :param tank_temperature: float
        Temperature of the gas in the tank in K

    :param verbose: bool
        Print information like gas totals

    :param plot_total: bool
        Plot total seeding amount vs time

    :param plot_flow: bool
        Plot flow rate (derivative of total seeding) vs time

    :param tsmo: float
        Smoothing timescale in seconds, used in plots only. Very important for viewing flow rate.

    :param axs: Axes instance or 1D array of Axes instances
        Axes used with plot_total or plot_flow. If none are provided, a new figure will be created.
        Number of Axes must be >= plot_flow+plot_total.

    :return: tuple of 1D arrays and a str
        1D array: time in s
        1D array: impurity electrons added
        1D array: fuel electrons added
        1D array: total molecules added
        str: primary species added
    """
    from omfit_classes.omfit_mds import OMFITmdsValue

    if shot is None:
        raise UtilsFusionBadInput('Must specify an EAST shot; e.g. 85266.')
    if valve is None:
        raise UtilsFusionBadInput(
            'Must specify the name of an EAST valve. Multiple conventions are tolerated. '
            'Examples: OU1, OUPEV1, VOUPEV1 are all valid and refer to the same valve.'
        )
    if species is None:
        raise UtilsFusionBadInput(
            'Must specify gas species in the tank. Mixtures like 50%Ne are accepted in the form '
            '<number>%<impurity species>. The rest of the mixture is assumed to be the main ion.'
        )
    if server not in ['EAST', 'EAST_US']:
        printw(f'This function is for EAST only. Server {server} was not recognized as an EAST MDSplus server.')

    def printv(*args):
        if verbose:
            print(*args)

    printv(f'  EAST#{shot} gas injection analysis: {species} via {valve} (plasma species: {main_ion_species})')
    electrons_per_molecule_puffed = dict(D=2, N=14, Ne=10, Ar=18)

    # Valve lengths as of 2020
    valve_lengths = dict(OU1=2.6e-2, OU2=2.6e-2, OU4=2.1e-2, OD=1.45e-2, CD=1.37e-2, HD=1.06e-2, JH=0.36e-2)  # m

    # Parse valve name into short form (there is more than one valid way to describe each valve in general)
    if valve not in valve_lengths and 'PEV' in valve:
        valve0 = valve
        valve = ''.join(valve0.split('PEV'))
        if 'OU' not in valve:
            valve = valve.rstrip(string.digits)
        if valve.startswith('V'):
            valve = valve[1:]
        printv(f'    simplified valve {valve0} to {valve}')

    # Determine relevant volume
    extra_volume = 291e-6  # m^3
    valve_diameter = 3.7e-2  # m
    valve_length = valve_lengths[valve]  # m
    valve_volume = np.pi * (valve_diameter / 2.0) ** 2 * valve_length  # m^3
    total_volume = valve_volume + extra_volume  # m^3

    # Look up which tank to use
    tanks = dict(OU1='OUG1', OU2='OUG1', OU4='OUG1')  # These valves are non-trivial mappings to their tank
    tank = tanks.get(valve, f'{valve}G1')  # Many valve-tank name mappings are trivial
    printv(f'    valve {valve}, tank {tank}, relevant volume {total_volume} m^3, assumed temperature {tank_temperature}')

    # Get tank pressure and inventory
    tank_pressure_mds = OMFITmdsValue(server, shot=shot, treename='EAST_1', TDI=rf'\{tank}')  # Pa
    if not tank_pressure_mds.check():
        raise OMFITexception(f'No data in {tank}')
    t = tank_pressure_mds.dim_of(0)  # s
    tank_pressure_raw = tank_pressure_mds.data()  # V
    # Calibrate gas pressure according to email from Kedong Li at ASIPP: P=(U-1)*2.5*10^4
    # U with unit of V and P with unit of Pa.
    tank_pressure = (tank_pressure_raw - 1) * 2.5e4  # Pa
    tank_inventory = tank_pressure * total_volume / (scipy.constants.Boltzmann * tank_temperature)  # molecules

    # Calculate seeding amounts and history (in molecules)
    initial_inventory = np.mean(tank_inventory[t < 0])
    molecules_seeded = initial_inventory - tank_inventory
    tmax = np.nanmax(t)
    final_inventory = np.mean(tank_inventory[t > (tmax - 5)])
    total_seeding = initial_inventory - final_inventory
    printv(
        f'    amount added: {total_seeding:0.3e} molecules; initial inventory: '
        f'{initial_inventory:0.3e} molecules, final: {final_inventory:0.3e}'
    )

    # Split molecules seeded into charges of each species seeded
    if '%' in species:
        percentage, primary_species = species.split('%')
        primary_species_fraction = float(percentage) / 100.0
        epmd = electrons_per_molecule_puffed[main_ion_species]
        epmi = electrons_per_molecule_puffed[primary_species.strip()]
        a = epmi * primary_species_fraction
        b = epmd * (1 - primary_species_fraction)
        impurity_electrons_seeded = a * molecules_seeded
        fuel_electrons_seeded = b * molecules_seeded
        impurity_total = a * total_seeding
        fuel_total = b * total_seeding
    else:
        if species == 'D':
            primary_species = 'D'
            fuel_electrons_seeded = electrons_per_molecule_puffed[species] * molecules_seeded
            impurity_electrons_seeded = 0 * t
            fuel_total = electrons_per_molecule_puffed[species] * total_seeding
            impurity_total = 0
        elif species == 'CD4':
            primary_species = 'C'
            fuel_electrons_seeded = molecules_seeded * 4
            impurity_electrons_seeded = molecules_seeded * 6
            fuel_total = total_seeding * 4
            impurity_total = total_seeding * 6
        else:
            primary_species = species
            impurity_electrons_seeded = electrons_per_molecule_puffed[species] * molecules_seeded
            fuel_electrons_seeded = 0 * t
            impurity_total = electrons_per_molecule_puffed[species] * total_seeding
            fuel_total = 0

    printv(f'    total {primary_species} added: {impurity_total:0.3e}, total {main_ion_species} added: {fuel_total:0.3e} electrons')

    # Plots (optional)
    if plot_flow or plot_total:
        from matplotlib import pyplot as plt
        from omfit_classes.utils_plot import cornernote

        # Figure/plot setup
        if axs is None:
            fig, axs = plt.subplots(plot_flow + plot_total, sharex='all')
        axs = np.atleast_1d(axs)
        ic = 'r'
        mc = 'b'
        factor = 1e-19
        unit_mod = '10$^{19}$ '
        cornernote(ax=axs[0], device='EAST', shot=shot, time='')
        axs[-1].set_xlabel('Time / s')

        # Process smoothing and derivatives
        imp_el_smo = butter_smooth(t, impurity_electrons_seeded, tsmo)
        main_el_smo = butter_smooth(t, fuel_electrons_seeded, tsmo)
        imp_flow = butter_smooth(t, deriv(t, imp_el_smo), tsmo)
        main_flow = butter_smooth(t, deriv(t, main_el_smo), tsmo)
        # Suppress artifacts at the edges of smoothing range
        bad = (t < (t[0] + tsmo * 2)) | (t > (t[-1] - tsmo * 2))
        imp_flow[bad] = np.NaN
        main_flow[bad] = np.NaN

        # Plot total gas added
        if plot_total:
            ax = axs[0]
            ax.axhline(0, color='k')
            ax.plot(t, impurity_electrons_seeded * factor, alpha=0.25, color=ic)
            ax.plot(t, fuel_electrons_seeded * factor, alpha=0.25, color=mc)
            ax.set_ylabel(f'Gas seeding / {unit_mod}el')
            ax.plot(t, imp_el_smo * factor, label=primary_species, color=ic)
            ax.plot(t, main_el_smo * factor, label='Main ion', color=mc)
            ax.legend(loc=0)

        # Plot flow rate
        if plot_flow:
            ax = axs[int(plot_total)]
            ax.axhline(0, color='k')
            ax.plot(t, imp_flow * factor, label=primary_species, color=ic)
            ax.plot(t, main_flow * factor, label='Main ion', color=mc)
            ax.set_ylabel(fr'$\Gamma$ / {unit_mod}el s$^{-1}$')
            ax.legend(loc=0)

    return t, impurity_electrons_seeded, fuel_electrons_seeded, molecules_seeded, primary_species


def _signal_description(signal):
    """
    Gives a tag or short description for a signal that could be specified by a tuple
    :param signal: str or iterable
        If iterable, it must contain one to four elements giving the following, in order:
        - pointname
        - treename
        - time unit conversion factor
        - operation
    :return: str
        A short string describing the signal
    """
    signal = tolist(signal)
    pt = signal[0]
    if len(signal) > 3:
        operation = signal[3]
    else:
        operation = None
    if operation is not None:
        tag = f'{operation}_{pt}'
    else:
        tag = pt
    return tag


def get_signals_common_timebase(device, shot, signals, timebase, default_values=None):
    """
    Gathers a list of signals and interpolates them onto a common timebase

    :param device: str

    :param shot: int

    :param signals: list of strings or list of iterables
        list of strings: (for use with DIII-D PTDATA) each element is a pointname
        list of iterables: (for use with MDSplus) each element should have one to four elements giving the
            - pointname
            - treename
            - time unit conversion factor (for use with a set of signals with mismatched timebases)
            - operation (like 'ddt' for derivative)

    :param timebase: 1D float array
        Desired final timebase for all signals in units matching the timebase of the source signals

    :param default_values: dict [optional]
        To add tolerance for missing data in the case where reasonable estimates are available, provide those
        estimates here. If retrieval from MDSplus/PTDATA fails, data from this dictionary will be interpolated
        onto the chosen timebase instead.
        To be useful, this dictionary must contain the following keys:
            time
            at least one other pointname that might be missing
        and in each case, the value should be a 1D float array matching the length of time

    :return: dictionary
        Keys are pointnames, values are 1D float arrays vs time. One element will be time.
    """
    from omfit_classes.omfit_mds import OMFITmdsValue

    data = {}
    for signal in signals:
        # Interpret signal info
        signal = tolist(signal)
        pt = signal[0]
        if len(signal) > 1:
            tree = signal[1]
        else:
            tree = None
        if len(signal) > 2:
            tf = signal[2]
        else:
            tf = 1
        if len(signal) > 3:
            operation = signal[3]
        else:
            operation = None
        tag = _signal_description(signal)

        # Check MDSplus
        mdspt = OMFITmdsValue(device, shot=shot, TDI=pt, treename=tree)
        if not mdspt.check():
            printw(f'WARNING! {pt} is missing')
            mdspt = None

        if mdspt is None:
            # Fallback plan: try to get default value or estimate for missing signal
            if default_values is not None and pt in default_values and 'time' in default_values:
                data[pt] = scipy.interpolate.interp1d(default_values['time'], default_values[pt])(timebase)
                printw(f'{pt} was estimated using the default value that was provided')
            else:
                printw(f'Unable to get estimate for {pt} from default_values')
                data[pt] = None
        else:
            dat = mdspt.data()
            if operation is None:
                pass
            elif operation == 'ddt':
                dat = deriv(mdspt.dim_of(0), dat)
            else:
                raise ValueError(f'Unrecognized operation ({operation}) requested')
            if np.array_equal(mdspt.dim_of(0), timebase):
                data[tag] = dat
            else:
                datt = mdspt.dim_of(0) * tf
                data[tag] = scipy.interpolate.interp1d(datt, dat, bounds_error=False, fill_value=np.NaN)(timebase)
    return data


@_available_to_user_fusion
def calc_h98_d3d(shot, calc_tau=False, calc_ptot=False, pinj_only=False, estimated_signals=None, data=None):
    """
    H98 confinement quality calcuation valid for DIII-D

    There are some other H98 calculations for DIII-D:

    h_thh98y2 is calcualted by the Transport code and is often regarded as
    pretty accurate, but it will turn itself off at the slightest hint of
    impurity seeding. If there's noise in one of the valves (GASB had an issue
    in 2021), this will be interpreted as seeding and the calculation will
    disable itself. So, it was pretty much always disabled because of this in
    years with noisy gas signals. The database that drives the 98y2 scaling goes
    up to Zeff=3, so a tiny bit of impurity seeding is tolerable. Even if Zeff
    is too high, it might still be interesting to see what H98 would be if it
    could be trustworthy.

    h98y2_aot is calculated from Automatic OneTwo runs and can overestimate H98.
    The AOT calculation is usually availble and doesn't fail because of impurity
    seeding, but it's probably less accurate than this calculation.

    :param shot: int

    :param calc_tau: bool
        Calculate tauth instead of gathering tauth. Might be useful if the
        confinement code stops early and doesn't write tauth.

    :param calc_ptot: bool
        Calculate total power instead of gathering it. Useful if ptot isn't
        written due to an error in another code

    :param pinj_only: bool
        Approximate ptot by pinj, ignoring ohmic and ECH power.
        This might be okay.

    :param estimated_signals: dict
        Data for estimating missing signals. Should contain a 'time' key whose
        value is a 1d float array. Should contain one additional key for each
        pointname that is being estimated, whose value is a 1d float array with
        length matching that of time.

    :param data: dict [optional]
        Pass in an empty dict and data used in the calculation will be written to
        it. Intermediate quantities may be captured for inspection in this way.

    :return: tuple containing two 1D float arrays
        Time in ms
        H98 as a function of time (unitless)
    """
    from omfit_classes.omfit_mds import OMFITmdsValue

    device = 'DIII-D'

    # Build list of required pointnames based on options
    input_pointnames = 'ip bt density r0 volume aminor'.split(' ')
    if calc_tau:
        input_pointnames += ['wmhd', ('wmhd', None, 1, 'ddt'), 'wfast']
    else:
        input_pointnames += ['tauth', 'wdot']
    if calc_ptot:
        input_pointnames += ['pinj']
        if not pinj_only:
            input_pointnames += ['poh', 'echpwrc']
    else:
        input_pointnames += ['ptot']

    # Establish timebase
    mdsdensity = OMFITmdsValue(device, shot=shot, TDI='density')
    t = mdsdensity.dim_of(0)

    # Gather input signals
    data_ = get_signals_common_timebase(device, shot, input_pointnames, t, default_values=estimated_signals)
    if data is None:
        data = data_
    else:
        data.update(data_)
    missing = [
        _signal_description(pt) for pt in input_pointnames if _signal_description(pt) not in data or data[_signal_description(pt)] is None
    ]
    if len(missing):
        data['error_message'] = f'Missing: {", ".join(missing)}'
        return None, None

    # Calculate intermediate quantities
    if calc_ptot:
        data['ptot'] = data['pinj'] * 1e3
        if not pinj_only:
            data['ptot'] += data['echpwrc'] + data['poh']
    if calc_tau:
        data['wdot'] = data['ddt_wmhd'] * 1000
    data['psol'] = data['ptot'] - data['wdot']
    if calc_tau:
        data['tauth'] = (data['wmhd'] - data['wfast']) / data['psol']
    data['volterm'] = data['volume'] / 19.74 / data['r0'] / data['aminor'] ** 2
    data['aspect'] = data['aminor'] / data['r0']
    data['main_ion_mass'] = 2.0

    # Final calculations
    factors = dict(ip=1e-6, density=1e-13, psol=1e-6)
    exponents = dict(ip=0.93, bt=0.15, density=0.41, psol=-0.69, r0=1.97, volterm=0.78, aspect=0.58, main_ion_mass=0.19)

    # taue_98y2 = 56.2e-3 * (ip/1e6)**0.93 * bt**0.15 * (density/1e-13)**0.41
    taue_98y2 = 56.2e-3
    for thing in 'ip density bt psol r0 volterm aspect main_ion_mass'.split(' '):
        print(f' * ({thing} * {factors.get(thing, 1)}) ** {exponents[thing]}')
        taue_98y2 *= abs(data[thing] * factors.get(thing, 1)) ** exponents[thing]
    data['taue_98y2'] = taue_98y2

    h98y2 = data['tauth'] / taue_98y2
    data['h98y2'] = h98y2
    data['time'] = t

    return t, h98y2


@_available_to_user_fusion
def available_efits_from_guess(scratch_area, device, shot, default_snap_list=None, format='{tree}', **kw):
    """
    Attempts to form a reasonable list of likely EFITs based on guesses

    :param scratch_area: dict
        Scratch area for storing results to reduce repeat calls. Mainly included to match
        call sigure of available_efits_from_rdb(), since OMFITmdsValue already has caching.

    :param device: str
        Device name

    :param shot: int
        Shot number

    :param default_snap_list: dict [optional]
        Default set of EFIT treenames. Newly discovered ones will be added to the list.

    :param **kw: quietly accepts and ignores other keywords for compatibility with other similar functions

    :return: (dict, str)
        Dictionary keys will be descriptions of the EFITs
            Dictionary values will be the formatted identifiers.
            For now, the only supported format is just the treename.
            If lookup fails, the dictionary will be {'': ''} or will only contain default results, if any.
        String will contain information about the discovered EFITs
    """
    printd(f'Trying to guess which EFITs might be available for device = {device}, shot = {shot}', topic='available_EFITs')
    if default_snap_list is None:
        default_snap_list = {'': ''}
    snap_list = copy.deepcopy(default_snap_list)
    scratch_area.setdefault('searched_in', [])
    scratch_area['searched_in'] += ['guess']

    if format != '{tree}':
        raise NotImplementedError(
            'Custom formatting of available EFIT results is not available when guessing '
            'which EFITs might be available. Please use format="{tree}" intead.'
        )
    if is_device(device, ['EAST', 'EAST_US']):
        trees = ['EFIT_EAST', 'EFITRT_EAST']
    elif is_device(device, 'DIII-D'):
        trees = ['EFIT01', 'EFIT02']
    elif is_device(device, ['KSTAR', 'NSTX']):
        trees = ['EFIT01']
    elif device == 'test_device_not_a_real_tokamak':
        trees = ['test1', 'test2', 'ffff_test!!_3']
    else:
        trees = []

    if len(trees) > 0:
        for tree in trees:
            snap_list[f"[{tree}]"] = tree
        help_info = f'EFIT trees were guessed for {device}#{shot}.'
    else:
        printd(f'  Failed to identify a basis for guessing which EFITs might be available for {device}#{shot}.', topic='available_EFITs')
        scratch_area['available_efits_from_guess_success'] = False
        help_info = 'No educated guesses were made; the only value(s) are defaults.'

    return snap_list, help_info


@_available_to_user_fusion
def available_EFITs(scratch_area, device, shot, allow_rdb=True, allow_mds=True, allow_guess=True, **kw):
    """
    Attempts to look up a list of available EFITs using various sources

    :param scratch_area: dict
        Scratch area for storing results to reduce repeat calls.

    :param device: str
        Device name

    :param shot: int
        Shot number

    :param allow_rdb: bool
        Allow connection to DIII-D RDB to gather EFIT information (only applicable for DIII-D)
        (First choice for DIII-D)

    :param allow_mds: bool
        Allow connection to MDSplus to gather EFIT information (only applicable to select devices)
        (First choice for non-DIII-D devices, second choice for DIII-D)

    :param allow_guess: bool
        Allow guesses based on common patterns of EFIT availability on specific devices
        (Last resort, only if other options fail)

    :param **kw: Keywords passed to specific functions. Can include:

        :param default_snap_list: dict [optional]
            Default set of EFIT treenames. Newly discovered ones will be added to the list.

        :param format: str
            Instructions for formatting data to make the EFIT tag name.
            Provided for compatibility with available_efits_from_rdb() because the only option is '{tree}'.

        :param no_empty: bool
            Use a second TDI command to check the number of nodes in each EFIT and
            filter out EFIT trees that are empty (0 nodes within them).
            Adds one MDSplus call.

        :param check_contents: bool
            Do a deeper check to make sure GEQDSK data are populated with at least one time.
            Adds one MDSplus call per EFIT that was found so far.

    :return: (dict, str)
        Dictionary keys will be descriptions of the EFITs
            Dictionary values will be the formatted identifiers.
            If lookup fails, the dictionary will be {'': ''} or will only contain default results, if any.
        String will contain information about the discovered EFITs
    """
    from omfit_classes.omfit_rdb import available_efits_from_rdb
    from omfit_classes.omfit_mds import available_efits_from_mds

    efit_list = copy.deepcopy(kw.get('default_snap_list', {'': ''}))
    help_info = 'No search methods were successful, so the list of EFIT trees is just the default set.'
    scratch_area['searched_in'] = []

    if is_device(device, ['DIII-D', 'NSTX', 'NSTX-U']) and allow_rdb:
        try:
            efit_list, help_info = available_efits_from_rdb(scratch_area, device, shot, **kw)
        except OMFITexception:
            printd(
                f'Failed to look up available EFITs from RDB for {device}#{shot}; '
                f'this could be because of failure to access the RDB server.',
                topic='available_EFITs',
            )
        else:
            if scratch_area.get('available_efits_from_rdb_success', None):
                return efit_list, help_info

    if allow_mds:
        efit_list, help_info = available_efits_from_mds(scratch_area, device, shot, **kw)
        if scratch_area.get('available_efits_from_mds_success', None):
            return efit_list, help_info

    if allow_guess:
        efit_list, help_info = available_efits_from_guess(scratch_area, device, shot, **kw)
        if scratch_area.get('available_efits_from_guess_success', None):
            return efit_list, help_info

    return efit_list, help_info

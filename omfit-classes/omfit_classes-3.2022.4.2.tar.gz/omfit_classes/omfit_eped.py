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

from omfit_classes.brainfusetf import btf_connect
from omfit_classes.brainfuse import activateNets
import numpy as np
from scipy import constants


__all__ = ['eped_nn_fann', 'eped_nn_tf', 'eped_nn']


def eped_nn_fann(a, betan, bt, delta, ip, kappa, m, neped, r, zeffped, z=1, zi=6, mi=12, solution=['H', 'superH'][0], model='multiroot'):
    """
    Routine that returns results of the EPED1-NN model

    :param a: scalar or array of minor radius [m]

    :param betan: scalar or array of beta_n

    :param bt: scalar or array of toroidal magnetic field [T]

    :param delta: scalar or array of triangularity

    :param ip: scalar or array of plasma current [MA]

    :param kappa: scalar or array of elongation

    :param m: scalar or array of ion mass (2 for D and 2.5 for DT)

    :param neped: scalar or array of density at pedestal [1E19 m^-3]

    :param r: scalar or array of major radius [m]

    :param zeffped: scalar or array of effective ion charge at pedestal

    :param z: scalar or array of ion charge (only used for calculating Te from pressure)

    :param mi: scalar or array of impurity ion mass (only used for calculating Te from pressure)

    :param Zi: scalar or array of impurity ion charge (only used for calculating Te from pressure)

    :param solution: 'H' or 'superH'

    :return: scalars or arrays of electron temperature in keV and pedestal width as fraction of psi
    """

    nets = OMFITsrc + f'/../modules/EPED/EPEDNN/{model}/*.net'

    dB = {}
    dB['a'] = a
    dB['betan'] = betan
    dB['bt'] = bt
    dB['delta'] = delta
    dB['ip'] = ip
    dB['kappa'] = kappa
    dB['m'] = m
    dB['neped'] = neped
    dB['r'] = r
    dB['zeffped'] = zeffped

    for k in dB:
        dB[k] = np.atleast_1d(dB[k])

    out, sut, targets, nets, out_ = activateNets(nets, dB)
    outputNames = nets[list(nets.keys())[0]].outputNames

    output_name = 'OUT_p_E1_%d' % ['H', 'meta', 'superH'].index(solution)

    z = np.atleast_1d(z)
    zi = np.atleast_1d(zi)
    mi = np.atleast_1d(mi)
    nival = neped * (zeffped - z) / (zi ** 2 - zi)
    nval = neped - zi * nival
    nsum = neped + nval + nival

    pped = out[:, outputNames.index(output_name)]
    Te = pped * 1e6 / (nsum * 1e19) / constants.e / 1e3
    wid = out[:, outputNames.index(output_name.replace('_p_', '_wid_'))]

    if len(Te) == 1:
        return Te[0], wid[0]
    else:
        return Te, wid


def eped_nn_tf(
    a,
    betan,
    bt,
    delta,
    ip,
    kappa,
    m,
    neped,
    r,
    zeffped,
    z=1,
    zi=6,
    mi=12,
    solution=['H', 'superH'][0],
    diamag=['GH', 'G', 'H'][0],
    model='eped1nn/models/EPED_mb_128_pow_norm_common_30x10.pb',
):
    """
    Routine that returns results of the EPED1-NN model

    :param a: scalar or array of minor radius [m]

    :param betan: scalar or array of beta_n

    :param bt: scalar or array of toroidal magnetic field [T]

    :param delta: scalar or array of triangularity

    :param ip: scalar or array of plasma current [MA]

    :param kappa: scalar or array of elongation

    :param m: scalar or array of ion mass (2 for D and 2.5 for DT)

    :param neped: scalar or array of density at pedestal [1E19 m^-3]

    :param r: scalar or array of major radius [m]

    :param zeffped: scalar or array of effective ion charge at pedestal

    :param z: scalar or array of ion charge (only used for calculating Te from pressure)

    :param mi: scalar or array of impurity ion mass (only used for calculating Te from pressure)

    :param Zi: scalar or array of impurity ion charge (only used for calculating Te from pressure)

    :param solution: 'H' or 'superH'

    :param diamag: diamagnetic stabilization model 'GH' or 'G' or 'H'

    :param model: string to select the EPED1NN model

    :return: scalars or arrays of electron temperature in keV and pedestal width as fraction of psi
    """

    output_name = f"OUT_p_E1_dmag{diamag}_sol{['H','meta','superH'].index(solution)}"

    a = np.atleast_1d(a)
    betan = np.atleast_1d(betan)
    bt = np.atleast_1d(bt)
    delta = np.atleast_1d(delta)
    ip = np.atleast_1d(ip)
    kappa = np.atleast_1d(kappa)
    m = np.atleast_1d(m)
    neped = np.atleast_1d(neped)
    r = np.atleast_1d(r)
    zeffped = np.atleast_1d(zeffped)

    input = [a, betan, bt, delta, ip, kappa, m, neped, r, zeffped]
    input = np.atleast_2d(input).T

    with btf_connect(path=model) as tf:
        input_names, output_names = tf.info()
    with btf_connect(path=model) as tf:
        output_list = tf.run(input=input)
    output = {}
    for k, oname in enumerate(output_names):
        output[oname] = output_list[:, k]

    z = np.atleast_1d(z)
    zi = np.atleast_1d(zi)
    mi = np.atleast_1d(mi)
    nival = neped * (zeffped - z) / (zi ** 2 - zi)
    nval = neped - zi * nival
    nsum = neped + nval + nival

    pped = output[output_name]
    Te = pped * 1e6 / (nsum * 1e19) / constants.e / 1e3
    wid = output[output_name.replace('_p_', '_wid_')]

    if len(Te) == 1:
        return Te[0], wid[0]
    else:
        return Te, wid


eped_nn = eped_nn_fann


############################################
if '__main__' == __name__:
    test_classes_main_header()
    print(eped_nn_fann(0.5, 1.0, 2.5, 0.6, 1.8, 1.9, 2.0, 3.6, 1.7, 2.0))
    print(
        eped_nn_fann([0.5, 0.5], [1.0, 1.0], [2.5, 2.5], [0.6, 0.6], [1.8, 1.8], [1.9, 1.9], [2.0, 2.0], [3.6, 3.6], [1.7, 1.7], [2.0, 2.0])
    )
    print(eped_nn_tf(0.5, 1.0, 2.5, 0.6, 1.8, 1.9, 2.0, 3.6, 1.7, 2.0))
    print(
        eped_nn_tf([0.5, 0.5], [1.0, 1.0], [2.5, 2.5], [0.6, 0.6], [1.8, 1.8], [1.9, 1.9], [2.0, 2.0], [3.6, 3.6], [1.7, 1.7], [2.0, 2.0])
    )

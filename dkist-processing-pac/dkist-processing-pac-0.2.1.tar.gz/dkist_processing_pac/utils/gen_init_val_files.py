import pkg_resources
import asdf
import numpy as np
from astropy.time import Time

def make_polcal_init_val_asdf(system_file: str,
                              minmax_frac: float = 0.02,
                              valid_time: str = 'now',
                              set_name: str = 'default') -> None:

    sys_wave, ret0h, ret045, ret0r, t_ret, t_pol, I_sys, x12, t12, x34, t34, x56, t56 = np.loadtxt(system_file,
                                                                                                   unpack=True,
                                                                                                   usecols=range(13))

    minmax_mult = np.array([-minmax_frac, 0, minmax_frac]) + 1.
    minmax_mult = minmax_mult[None, :]
    Q_in = (1 - x12**2) / (1 + x12**2)

    if valid_time == 'now':
        valid_time = Time.now().fits

    ## Just a dummy for now. We'll likely never use this, but it's included for backwards compatibility
    dummy_dret = np.zeros(sys_wave.shape) + 0.1 * np.pi / 180.
    dummy_QU = np.zeros((sys_wave.size, 3)) + np.array([-0.1, 0, 0.1])[None, :]
    dummy_Isys = np.zeros((sys_wave.size, 3)) + np.array([-0.1, 1, 0.1])[None, :]

    polcal_tree = {'gen_time': Time.now().fits,
                   'valid_time': valid_time,
                   'wave': sys_wave,
                   'params': {'ret0h': ret0h[:, None] * minmax_mult,
                              'dreth': dummy_dret[:, None] * minmax_mult,
                              'ret045': ret045[:, None] * minmax_mult,
                              'dret45': dummy_dret[:, None] * minmax_mult,
                              'ret0r': ret0r[:, None] * minmax_mult,
                              'dretr': dummy_dret[:, None] * minmax_mult,
                              'I_sys': dummy_Isys,
                              't_ret': t_ret[:, None] * minmax_mult,
                              't_pol': t_pol[:, None] * minmax_mult,
                              'Q_in': Q_in[:, None] * minmax_mult,
                              'U_in': dummy_QU,
                              'V_in': dummy_QU}
                   }

    initval_file = pkg_resources.resource_filename('dkist_processing_pac', 'data/init_values/polcal_{}.asdf'.format(set_name))
    af = asdf.AsdfFile(polcal_tree)
    af.write_to(initval_file)

    return

def make_groupcal_init_val_asdf(system_file: str,
                                minmax_frac: float = 0.02,
                                valid_time: str = 'now',
                                set_name: str = 'default') -> None:

    sys_wave, ret0h, ret045, ret0r, t_ret, t_pol, I_sys, x12, t12, x34, t34, x56, t56 = np.loadtxt(system_file,
                                                                                                   unpack=True,
                                                                                                   usecols=range(13))

    minmax_mult = np.array([-minmax_frac, 0, minmax_frac]) + 1.
    minmax_mult = minmax_mult[None, :]

    if valid_time == 'now':
        valid_time = Time.now().fits

    groupcal_tree = {'gen_time': Time.now().fits,
                     'valid_time': valid_time,
                     'wave': sys_wave,
                     'params': {'x34': x34[:, None] * minmax_mult,
                                't34': t34[:, None] * minmax_mult,
                                'x56': x56[:, None] * minmax_mult,
                                't56': t56[:, None] * minmax_mult}
                     }

    initval_file = pkg_resources.resource_filename('dkist_processing_pac', 'data/init_values/groupcal_{}.asdf'.format(set_name))
    af = asdf.AsdfFile(groupcal_tree)
    af.write_to(initval_file)

    return

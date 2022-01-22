import numpy as np
import SPMUtil
from SPMUtil.structures._structures import measurement_param, inflecion_point_param
from SPMUtil.filters import filter_1d


def frequency_shift_to_normalized_frequency_shift(delta_f, param: measurement_param) -> np.ndarray:
    """
     Large amplitudes A0>>d
    :param delta_f:
    :param param:
    :return:
    """
    return delta_f * param.k * (param.amp / 10) ** 1.5 / param.f0




def CalcForceCurveWithAutoFilter(df_curve, param: measurement_param, s_factor=0.3, diff_factor=-1e-8):
    x = np.linspace(0, param.max_z, param.data_count)
    y = df_curve
    F_y = CalcForceCurveSadar(filter_1d.average_smooth(y, 5), param)
    F_y_filtered = filter_1d.spline_smooth(x[2:-2], F_y, s=s_factor * (np.max(F_y) - np.min(F_y)), k=3)
    diff = np.diff(F_y_filtered, 1)
    c = 0
    for i in range(0, len(diff) - 1):
        if diff[i] * diff[i + 1] < 0 and diff[i] * diff[i + 1] < diff_factor:
            # print(diff[i] * diff[i+1], i)
            c += 1
    if c >= 3:
        return CalcForceCurveWithAutoFilter(df_curve, param, s_factor * 1.5, diff_factor)
    print("s_factor", s_factor)
    return x[2:-2], F_y_filtered



def CalcForceCurveSadar(df_curve, param: measurement_param) -> np.ndarray:
    """
    implement the Sader-Jarvis inversion

        References
    ----------
    .. [JS] John E. Sader, Takayuki Uchihashi, Michael J. Higgins,
    Alan Farrell, Yoshikazu Nakayama and Suzanne P. Jarvis
    "Quantitative force measurements using frequency modulation atomic force
    microscopy - theoretical foundations"
    Nanotechnology, 16 S94-S101 (2005)
    http://www.ampc.ms.unimelb.edu.au/afm/ref_files/Sader_NANO_2005.pdf

    .. [JW] Joachim Welker, Esther Illek, Franz J. Giessibl
    "Analysis of force-deconvolution methods in frequency-modulation
    atomic force microscopy"
    Beilstein J. Nanotechnol. 3, 238 (2012)
    http://www.beilstein-journals.org/bjnano/content/pdf/2190-4286-3-27.pdf
    """
    # get the spacing in z
    dh = param.dh / 10  # nm
    amp = param.amp / 10  # nm
    F = np.zeros(param.data_count)
    z = param.z / 10  # nm

    derivative = np.zeros(param.data_count)
    weights = np.array([1.0 / 12, -2.0 / 3, 0, 2.0 / 3, -1.0 / 12])

    for i in range(2, param.data_count - 2):
        derivative[i] = (np.dot(weights, df_curve[i - 2:i + 3]) / dh)

    for i in range(2, param.data_count - 2):
        t = z[i + 1:-2]
        df = df_curve[i + 1:-2]
        deriv = derivative[i + 1:-2]
        integrand = ((1 + (amp ** (1.0 / 2)) /
                      (8 * ((np.pi * (t - z[i])) ** (1 / 2.0)))) * df
                     - (((amp ** (3.0 / 2)) / (np.sqrt(2 * (t - z[i])))) * deriv))

        integral = np.trapz(integrand, t)
        # add some correction factors after [JS]
        corr_1 = df_curve[i + 2] * dh
        corr_2 = (2 * (np.sqrt(amp) / (8 * np.sqrt(np.pi)))
                  * df_curve[i + 2] * np.sqrt(dh))
        corr_3 = ((-2) * ((amp ** (3.0 / 2)) / np.sqrt(2))
                  * derivative[i + 2] * np.sqrt(dh))
        F[i - 2] = ((2 * param.k) / param.f0) * (
                integral + corr_1 + corr_2 + corr_3)
    return F[2:-2]



def CalcForceCurveMatrix(df_curve, param: measurement_param) -> np.ndarray:
    alpha = round(param.amp / param.dh)
    df_curve = np.flipud(df_curve)
    W = np.zeros(shape=(len(df_curve), len(df_curve)))
    for i in range(0, param.data_count):
        for j in range(0, param.data_count):
            if 0 <= i - j < 2 * alpha:
                W[i, j] = (param.f0 / param.k) * (np.pi / param.amp) \
                          * 2 / (2 * alpha + 1) * \
                          (np.sqrt((2 * alpha + 1) * (i - j + 1) - (i - j + 1) ** 2) - np.sqrt(
                              (2 * alpha + 1) * (i - j) - (i - j) ** 2))
    F = SPMUtil.formula.mldivide(W, df_curve)
    return np.flipud(F)



def inflection_point_test(x, F, Amp, z0) -> list:
    x = x - np.min(x)
    dx = x[1]-x[0]
    d1F = np.gradient(F) / dx
    d2F = np.gradient(d1F) / dx
    d3F = np.gradient(d2F) / dx

    # get inflection point in d2F
    point_list = []
    for i in range(0, z0):
        if d2F[i] * d2F[i+1] < 0:
            point_list.append(i)

    point_list = np.asarray(point_list)
    if len(point_list) < 0:
        return None

    param = []
    for i in point_list:
        p = inflecion_point_param(i)
        p.s_factor = x[i] * x[i] / 4 * d3F[i] / d1F[i]
        if p.is_well_posed:
            continue
        if x[i] / np.sqrt(-p.s_factor) / 2 <= Amp < x[i] / 2 and x[i] - 2*Amp > 0:
            p.wel_posed_boundary = x[i] - 2*Amp

    return param
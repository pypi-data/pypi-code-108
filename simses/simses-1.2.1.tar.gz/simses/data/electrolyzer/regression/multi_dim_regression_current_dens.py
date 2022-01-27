import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

TEMP_IDX = 0
P_A_IDX = 1
P_C_IDX = 2
POWER_DENS_IDX = 3
CURRENT_DENS_IDX = 4

IDEAL_GAS_CONST: float = 8.314462  # J/(mol K)
FARADAY_CONST: float = 96485.3321  # As/mol

LAMBDA = 25  # degree of humidification
MEM_THIKNESS = 200 * 10 ** (-4)  # cm
R_ele = 0.096  # Ohm cm²
P_O2_REF = 1  # bar
P_H2_REF = 1  # bar

EPS = np.finfo(float).eps

current_dens_lookup_data = pd.read_csv('cell_currentdensity_lookup.csv')
#current_dens_lookup_data = pd.read_csv('cell_currentdensity_lookup_no_current_influence_on_part_pressure.csv')

temperature = current_dens_lookup_data.iloc[:, TEMP_IDX]
p_anode = current_dens_lookup_data.iloc[:, P_A_IDX]
p_cathode = current_dens_lookup_data.iloc[:, P_C_IDX]
power_dens = current_dens_lookup_data.iloc[:, POWER_DENS_IDX]
current_dens = current_dens_lookup_data.iloc[:, CURRENT_DENS_IDX]

# parameters of curve fitting of activation powerdensity
p10 = -0.00705
p20 = 0.01346
p11 = -0.0001083

# data preparation
xdata = np.array([temperature, p_anode, p_cathode, power_dens])
ydata = np.array(current_dens)

def funk(x,q1, q3, q4, q5, q6, q7, q9, q10, q11, q12, q13, q14, q15, q17):
    temp = x[0, :]
    p_a = x[1, :]
    p_c = x[2, :]
    pow_dens = x[3, :]

    def alpha(temp) -> float:
        return 0.6627 * np.exp(-0.187 * temp) + 0.02934 * np.exp(-0.00454 * temp)  # V

    def i_0(temp) -> float:
        return 0.002159 * np.exp(-0.3179 * temp) + 1.149 * 10 ** (-7) * np.exp(-0.0205 * temp)  # A

    U_rev = 1 * 1.5184 - q3 * 1.5421 * 10 ** (-3) * (temp + 273.15) + q4 * 9.523 * 10 ** (-5) * (temp + 273.15) * \
            np.log(q5 * (temp + 273.15)) + q6 * 9.84 * 10 ** (-8) * (temp + 273.15) ** 2  # from "Hydrogen science and engeneering: Materials, processed, systems.."

    conduc_nafion = (0.005139 * LAMBDA - 0.00326) * \
                    np.exp(1268 * (1 / (303) - 1 / (temp + 273.15)))  # S/cm 0.14

    R_mem = MEM_THIKNESS / conduc_nafion  # Ohm cm2

    pressure_sat_h2o = q10 * 10 ** (- q11 * 2.1794 + q12 * 0.02953 * temp - q13 * 9.1837 * 10 ** (-5) * temp ** 2 +
                                    q14 * 1.4454 * 10 ** (-7) * temp ** 3)  # bar saturationpressure of water

    p_h2 = (1 + q15 * p_c) - pressure_sat_h2o  # without currentdensity dependency
    p_o2 = (1 + q9 * p_a) - pressure_sat_h2o  # without currentdensity dependency

    A = R_mem + R_ele + q1 * p20
    B = U_rev + q7 * IDEAL_GAS_CONST * (temp + 273.15) / (2 * FARADAY_CONST) * np.log(
        1 * (p_o2 / P_O2_REF) ** (1 / 2) * p_h2 / P_H2_REF) + 1 * p10 + q17 * p11 * temp - alpha(temp) * np.log(i_0(temp))
    C = - 1 * pow_dens
    return (-B + (B ** 2 - 4 * A * C) ** (1 / 2)) / (2 * A)

lb = - np.inf
ub = np.inf

lower_bounds = (lb, lb, lb, EPS, lb, lb, lb, lb, lb, lb, lb, lb, lb, lb)
#lower_bounds = lb
upper_bounds = ub

popt, pcov = curve_fit(funk, xdata, ydata, absolute_sigma=False, bounds=(lower_bounds, upper_bounds))

standart_deviation = np.sqrt(np.diag(pcov))
print(popt)
print(pcov)
print(standart_deviation)

current_ana_calc = funk(xdata, popt[0], popt[1], popt[2], popt[3], popt[4], popt[5], popt[6], popt[7], popt[8], popt[9],
                        popt[10], popt[11], popt[12], popt[13])

abs_err = current_dens - current_ana_calc

mean_abs_err = np.mean(abs(abs_err))

max_abs_err = max(abs(abs_err))

RMS = np.sqrt(sum((abs_err) ** 2) / len(abs_err))

relative_error = abs(abs_err / current_dens)

chisq = sum((abs_err) ** 2)

x1 = list(range(1, len(popt)+1))
y1 = popt
x2 = list(range(len(temperature)))
y21 = abs_err
y22 = relative_error

plt.subplot(311)
plt.ylabel('correction parameters')
plt.grid(True)
#plt.title('standart deviation of the parameters')
plt.plot(x1, y1, 'bo')
plt.xticks(x1, ('q1', 'q3', 'q4', 'q5', 'q6', 'q7', 'q9', 'q10', 'q11', 'q12', 'q13', 'q14', 'q15', 'q17'))

plt.subplot(312)
#plt.title('absolut error funktion vs look up table')
plt.ylabel('absolut error')
plt.grid(True)
plt.plot(x2, y21, 'rx')
plt.plot(x2, current_dens, 'bo')
plt.axis([-100, len(x2), min(abs_err), 0.009])

plt.subplot(313)
#plt.title('relative error funktion vs look up table')
plt.ylabel('relative error in %')
plt.grid(True)
plt.plot(x2, y22*100, 'gx')

#plt.subplot(414)
#plt.errorbar(x2, current_dens - funk(xdata, popt[0], popt[1], popt[2], popt[3], popt[4], popt[5], popt[6], popt[7], popt[8], popt[9], popt[10], popt[11], popt[12], popt[13], popt[14], popt[15], popt[16]
#                                , popt[17], popt[18], popt[19], popt[20], popt[21], popt[22], popt[23], popt[24], popt[25], popt[26], popt[27]), 0, fmt='b.')

plt.figtext(0.15, 0.8, "mean abs. error: %.6f"%mean_abs_err, fontweight="bold")
plt.figtext(0.15, 0.75, "RMS error: %.6f"%RMS, fontweight="bold")
plt.figtext(0.15, 0.7, "maximal absolut error: %.6f"%max_abs_err, fontweight="bold")
plt.grid(True)
plt.savefig('multidim current density fit - analysis')
plt.show()
#plt.savefig('multidim current density fit no curreninfluence on part pressure - standart deviation')


dict = {'parameters': popt}
df = pd.DataFrame(dict)
df.to_csv('parameters_multi_dim_current_dens_fit.csv', index=False)

# dict2 = {'temperatur':temperature, 'p anode':p_anode, 'p cathode':p_cathode, 'powerdensity':power_dens, 'currentdensity':current_dens, 'calc currentdensity':current_ana_calc, 'absolut error':abs_err}
# df2 = pd.DataFrame(dict2)
# df2.to_csv('restul best fit analytic equation currentedensity.csv', index=False)
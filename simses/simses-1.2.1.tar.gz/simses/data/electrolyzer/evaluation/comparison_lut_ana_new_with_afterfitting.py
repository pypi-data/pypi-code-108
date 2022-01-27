import math as m
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


TEMP_IDX = 0
P_A_IDX = 1
P_C_IDX = 2
POWER_DENS_IDX = 3
CURRENT_DENS_IDX = 4
ALPHA_IDX = 5
I_0_IDX = 6

# constants
IDEAL_GAS_CONST: float = 8.314462  # J/(mol K)
FARADAY_CONST: float = 96485.3321  # As/mol
A_CATHODE = 2.4  # bar cm²/A  -> angaben, Abhänigkeit von Dicke
A_ANODE = 2.8  # bar cm²/A
R_ele = 0.096  # Ohm cm²
LAMBDA = 25  # degree of humidification
THIKNESS_NAFION = 200  # um

# import of look up table
current_dens_lookup_data = pd.read_csv('cell_currentdensity_lookup_with_alpha.csv')
#current_dens_lookup_data = pd.read_csv('cell_currentdensity_lookup.csv')
temperature = current_dens_lookup_data.iloc[:, TEMP_IDX]
p_anode = current_dens_lookup_data.iloc[:, P_A_IDX]
p_cathode = current_dens_lookup_data.iloc[:, P_C_IDX]
power_dens = current_dens_lookup_data.iloc[:, POWER_DENS_IDX]
current_dens = current_dens_lookup_data.iloc[:, CURRENT_DENS_IDX]
alpha = current_dens_lookup_data.iloc[:, ALPHA_IDX]
i_0 = current_dens_lookup_data.iloc[:, I_0_IDX]

# parameters of curve fitting of activation powerdensity
p00 = 0
p10 = -0.007005
p01 = 0
p20 = 0.01346
p11 = -0.0001083
p02 = 0

current_dens_analytic = []

for i in range(len(temperature)):
    U_rev = 1.5184 - 1.5421 * 10 ** (-3) * (temperature[i] + 273.15) + 9.523 * 10 ** (-5) * (temperature[i]  + 273.15) * m.log(temperature[i]  + 273.15) \
                         + 9.84 * 10 ** (-8) * (temperature[i]  + 273.15) ** 2

    conductivity_nafion = (0.005139 * LAMBDA - 0.00326) * m.exp(1268 * (1 / 303 - 1 / (temperature[i]  + 273.15)))  # S/cm 0.14
    R_mem = THIKNESS_NAFION * 10 ** (-4) / conductivity_nafion  # Ohm cm2

    # calculate partial pressures of hydrogen and oxygen for calculation of Nernst-equation
    pressure_sat_h2o = 10 ** (-2.1794 + 0.02953 * temperature[i]  - 9.1837 * 10 ** (-5) * temperature[i]  ** 2 + 1.4454 * 10 ** (-7) * temperature[i] ** 3)
    p_h2 = (1 + p_cathode[i]) - pressure_sat_h2o  # without currentdensity dependency
    p_o2 = (1 + p_anode[i]) - pressure_sat_h2o  # without currentdensity dependency
    p_h2_ref = 1  # bar
    p_o2_ref = 1  # bar

    a = R_mem + R_ele + p20
    b = U_rev + IDEAL_GAS_CONST * (temperature[i]  + 273.15) / (2 * FARADAY_CONST) * m.log((p_o2 / p_o2_ref)**(1/2) * p_h2 / p_h2_ref) + p10 + p11 * temperature[i] - alpha[i] * m.log(i_0[i])
    c = p00 + p01 * temperature[i]  + p02 * temperature[i]  ** 2 - power_dens[i]

    current_dens_analytic.append((- b + (b ** 2 - 4 * a * c) ** (1/2)) / (2 * a))
    #i2 = (- b - (b ** 2 - 4 * a * c) ** (1/2)) / (2 * a)

abs_err = current_dens - current_dens_analytic

mean_abs_err = np.mean(abs(abs_err))

max_abs_err = max(abs(abs_err))

RMS = np.sqrt(sum((abs_err)**2)/len(abs_err))

x = list(range(len(temperature)))
y = abs_err
plt.ylabel('absolut error')
plt.title('error analytic calculated current vs. look up table')
plt.plot(x, y, 'rx')
plt.figtext(0.15, 0.25, "mean abs. error: %.6f"%mean_abs_err, fontweight="bold")
plt.figtext(0.15, 0.2, "RMS error: %.6f"%RMS, fontweight="bold")
plt.figtext(0.15, 0.15, "maximal absolut error: %.6f"%max_abs_err, fontweight="bold")
plt.grid(True)
#plt.savefig('error_of_analytic_currentdensity_calculation')
plt.savefig('error_of_analytic_currentdensity_calculation')
plt.show()



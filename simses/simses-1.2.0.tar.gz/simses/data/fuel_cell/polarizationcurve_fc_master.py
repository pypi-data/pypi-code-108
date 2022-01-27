import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import math as m
import pandas as pd
import csv

__TEMPERATURE_CELL_C: float = 80  # °C
__TEMPERATURE_CELL_K: float = 273.15 + __TEMPERATURE_CELL_C  # K
__TEMPERATURE_REF_K: float = 298.15  # K

__IDEAL_GAS_CONST: float = 8.314462  # J/(mol K)
__FARADAY_CONST: float = 96485.3321  # As/mol

__CONTACT_RESISTANCE = 1.25 * 10 ** -3  # Ohm * cm2

__AREA_CELL = 600  # cm2
__MAX_CURRENT_DENSITY = 1  # A/cm2
__REV_VOLTAGE_STC = 1.229  # V  reversible Zellspannung unter STC
__ALPHA_ANODE = 0.25
__ALPHA_CATHODE = 0.41
__REF_EX_CURRENT_DENS_ANODE = 171 * 10 ** -3  # A/cm2
__REF_EX_CURRENT_DENS_CATHODE = 2.8 * 10 ** -6  # A/cm2
__ACT_ENERGY_ANODE = 24359  # J/mol
__ACT_ENERGY_CATHODE = 40000  # J/mol
__LAMBDA = 22.5  # degree of humidification
__THIKNESS_NAFION = 50.8  # um
__CONDUCTIVITY_NAFION = (0.005139 * __LAMBDA - 0.00326) * m.exp(
    1268 * (1 / 303 - 1 / __TEMPERATURE_CELL_K))  # S/cm 0.14
__mem_resistance = __THIKNESS_NAFION * 10 ** -4 / __CONDUCTIVITY_NAFION  # Ohm * cm2

__ATM = 1.013  # bar

__PRESSURE_ANODE = 1.7  # bar   total pressure Anode
__PRESSURE_CATHODE = 1.7  # bar   total pressure Cathode

__pressure_sat_h2o = 10 ** (
        -2.1794 + 0.02953 * __TEMPERATURE_CELL_C - 9.1837e-5 * __TEMPERATURE_CELL_C ** 2 + 1.4454e-7 *
        __TEMPERATURE_CELL_C ** 3)

__pressure_h2 = (__PRESSURE_ANODE - __pressure_sat_h2o) / __ATM  # bar to atm
__pressure_o2 = (__PRESSURE_CATHODE - __pressure_sat_h2o) * 0.21 / __ATM  # bar to atm

__open_circuit_voltage = __REV_VOLTAGE_STC + (__IDEAL_GAS_CONST * __TEMPERATURE_CELL_K / (2 * __FARADAY_CONST)) \
                         * m.log(__pressure_h2 * __pressure_o2 ** 0.5) - 0.85 * 10 ** -3 * (__TEMPERATURE_CELL_K
                                                                                            - __TEMPERATURE_REF_K)

__current_density = np.linspace(0, 1000, 500) * 10 ** -3  # mA

__ex_current_dens_anode = __REF_EX_CURRENT_DENS_ANODE * m.exp((-__ACT_ENERGY_ANODE / __IDEAL_GAS_CONST) * \
                                                              (1 / __TEMPERATURE_CELL_K - 1 / 333))  # 1 / 333 sollte eventuell 1/298.1 sein??, da bezogen auf STC

__ex_current_dens_cathode = __REF_EX_CURRENT_DENS_CATHODE * m.exp((-__ACT_ENERGY_CATHODE / __IDEAL_GAS_CONST) * \
                                                              (1 / __TEMPERATURE_CELL_K - 1 / 298.15))

_cell_voltage = np.ones(len(__current_density))

_spec_cell_power = np.ones(len(__current_density))

for i in range(0, len(__current_density)):
    _cell_voltage[i] = __open_circuit_voltage - __IDEAL_GAS_CONST * __TEMPERATURE_CELL_K / \
                       (2 * __ALPHA_ANODE * __FARADAY_CONST) * m.asinh(__current_density[i] / __ex_current_dens_anode) - \
                       __IDEAL_GAS_CONST * __TEMPERATURE_CELL_K / \
                       (2 * __ALPHA_CATHODE * __FARADAY_CONST) * m.asinh(__current_density[i] /
                                                                     __ex_current_dens_cathode) - __CONTACT_RESISTANCE \
                      * __current_density[i] - __mem_resistance * __current_density[i]

for i in range(0, len(__current_density)):
    _spec_cell_power[i] = _cell_voltage[i] * __current_density[i]

x = __current_density
y1 = _cell_voltage
y2 = _spec_cell_power

ax1 = plt.subplot(211)
plt.plot(x, y1)

ax2 = plt.subplot(212)
plt.plot(x, y2)
plt.show()

dict = {'currentdensity': __current_density, 'cellvoltage at 1 bar': _cell_voltage}
dict2 = {'currentdenstiy': __current_density, 'cellpower at 1 bar': _spec_cell_power}

# df = pd.DataFrame(dict)
# df2 = pd.DataFrame(dict2)

# df.to_csv('polarizationcurve1bar.csv', index=False)
# df2.to_csv('powercurve1bar.csv', index=False)

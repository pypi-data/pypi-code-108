import math as m

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

__TEMPERATURE_CELL_C: float = 80  # °C
__TEMPERATURE_CELL_K: float = 273.15 + __TEMPERATURE_CELL_C  # K

__IDEAL_GAS_CONST: float = 8.314462  # J/(mol K)
__FARADAY_CONST: float = 96485.3321  # As/mol

__CONTACT_RESISTANCE = 25 * 10 ** -3  # Ohm * cm2

__AREA_CELL = 50  # cm2
__ALPHA_ANODE = 0.49
__ALPHA_CATHODE = 0.255
__RUGOSITY_ANODE = 600
__RUGOSITY_CATHODE = 240
__ACT_ENERGY_ANODE = 62836  # J/mol
__ACT_ENERGY_CATHODE = 24359  # J/mol
__K_0_ANODE = 4.63 * 10 ** (-3)  # mol/K/s/m²
__K_0_CATHODE = 1 * 10 ** (-2)  # mol/K/s/m²
__LAMBDA = 22.5  # degree of humidification
__THIKNESS_NAFION = 177.8  # um
__CONDUCTIVITY_NAFION = (0.005139 * __LAMBDA - 0.00326) * m.exp(1268 * (1 / 303 - 1 / __TEMPERATURE_CELL_K))  # S/cm 0.14
__mem_resistance = __THIKNESS_NAFION * 10 ** -4 / (__CONDUCTIVITY_NAFION)  # Ohm * cm2

__ATM = 1.013  # bar

__PRESSURE_ANODE = 1  # bar   total pressure Anode
__PRESSURE_CATHODE = 1  # bar   total pressure Cathode

__pressure_sat_h2o = 10 ** (-2.1794 + 0.02953 * __TEMPERATURE_CELL_C - 9.1837 * 10 ** -5 * __TEMPERATURE_CELL_C ** 2 + 1.4454 * 10 ** -7 *
                            __TEMPERATURE_CELL_C ** 3)

__pressure_h2 = (__PRESSURE_CATHODE - __pressure_sat_h2o) / __ATM  # bar to atm
__pressure_o2 = (__PRESSURE_ANODE - __pressure_sat_h2o) / __ATM  # bar to atm

__open_circuit_voltage = []

__open_circuit_voltage = __IDEAL_GAS_CONST * __TEMPERATURE_CELL_K / (2 * __FARADAY_CONST) * \
                         m.log(__pressure_h2 * __pressure_o2 ** 0.5) + (1.5241 - 1.2261 * 10 ** -3 * __TEMPERATURE_CELL_K +
                                                                        1.1858 * 10 ** -5 * __TEMPERATURE_CELL_K * m.log(
                        __TEMPERATURE_CELL_K) + 5.6692 * 10 ** -7 *
                                                                        __TEMPERATURE_CELL_K ** 2)  # V

__current_density = np.linspace(0, 5000, 500) * 10 ** -3  # mA

__ex_current_dens_anode = __RUGOSITY_ANODE * 2 * __FARADAY_CONST * __K_0_ANODE * __TEMPERATURE_CELL_K * m.exp(- __ACT_ENERGY_ANODE /  (__IDEAL_GAS_CONST * __TEMPERATURE_CELL_K)) / 10000 # A/cm² nach Formel aus schriftl. Ausarbeitung nicht 1737 sondern 893
__ex_current_dens_cathode = __RUGOSITY_CATHODE * 2 * __FARADAY_CONST * __K_0_CATHODE *__TEMPERATURE_CELL_K * m.exp(- __ACT_ENERGY_CATHODE / (__IDEAL_GAS_CONST * __TEMPERATURE_CELL_K)) / 10000  # A/cm²
_cell_voltage = np.ones(len(__current_density))

_spec_cell_power = np.ones(len(__current_density))

for i in range(0, len(__current_density)):
    _cell_voltage[i] = __open_circuit_voltage + __IDEAL_GAS_CONST * __TEMPERATURE_CELL_K / \
                       (2 * __ALPHA_ANODE * __FARADAY_CONST) * m.asinh(__current_density[i] / (__ex_current_dens_anode*2)) + \
                       __IDEAL_GAS_CONST * __TEMPERATURE_CELL_K / \
                       (2 * __ALPHA_CATHODE * __FARADAY_CONST) * m.asinh(__current_density[i] /
                                                                     (__ex_current_dens_cathode*2)) + __CONTACT_RESISTANCE \
                        * __current_density[i] + __mem_resistance * __current_density[i]

for i in range(0, len(__current_density)):
    _spec_cell_power[i] = _cell_voltage[i] * __current_density[i]  # (W/cm2)


x = __current_density  # A/cm2
y1 = _cell_voltage  # V
y2 = _spec_cell_power  # W/cm2

ax1 = plt.subplot(211)
plt.plot(x, y1)

ax2 = plt.subplot(212)
plt.plot(x, y2)
plt.show()

dict = {'currentdensity': __current_density, 'cellvoltage at 1 bar': _cell_voltage}
dict2 = {'currentdenstiy': __current_density, 'cellpower at 1 bar': _spec_cell_power}

df = pd.DataFrame(dict)
df2 = pd.DataFrame(dict2)

df.to_csv('polarizationcurve1bar.csv', index=False)
df2.to_csv('powercurve1bar.csv', index=False)

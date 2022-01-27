import math as m

import numpy as np
import pandas as pd

IDEAL_GAS_CONST: float = 8.314462  # J/(mol K)
FARADAY_CONST: float = 96485.3321  # As/mol

# constants
A_CATHODE = 2.4  # bar cm²/A  -> angaben, Abhänigkeit von Dicke
A_ANODE = 2.8  # bar cm²/A
R_ele = 0.096  # Ohm cm²
U_rev_STP = 1.23  # V
LAMBDA = 25  # degree of humidification
THIKNESS_NAFION = 200  # um

# parameters
ALPHA_array = np.array([0.02803, 0.02483, 0.02344, 0.02232, 0.02141, 0.02038])  # V
i_0_array = np.array([21.8, 5.71, 4.15, 3.36, 2.95, 1.97])* 10 **(-8)  # A/cm2
#R_mem_array = np.array([0.159, 0.140, 0.123, 0.109, 0.098, 0.088])  #  ohm cm²  direkte Parameter aus Q1

# input variables
T_array = [30.0, 40.0, 50.0, 60.0, 70.0, 80.0]  # °C
p_anode_array = np.linspace(0, 50, 13)  # barg  relative pressure compared to 1 bar ambient pressure
p_cathode_array = np.linspace(0, 50, 13)  # barg  relative pressure compared to 1 bar ambient pressure

U_rev_array = np.ones(len(T_array))
for i in range(len(T_array)):
    U_rev_array[i] = 1.5184 - 1.5421 * 10 ** (-3) * (T_array[i] + 273.15) + 9.523 * 10 ** (-5) * (T_array[i] + 273.15) * m.log(T_array[i] + 273.15) \
                     + 9.84 * 10 ** (-8) * (T_array[i] + 273.15) ** 2

# creating current density array with increasing step size to have more points in non linear area of the polariszation curve
current_density_array = []
current_density_array.append(0)
x = 0
i = 1
while x<3:
    x = x + 0.002*i**1.5
    current_density_array.append(x)
    i = i+1
current_density_array = np.array(current_density_array)
current_density_array[-1] = 3

pressure_sat_h2o_array = np.ones(len(T_array))  # bar
for i in range(len(T_array)):
    pressure_sat_h2o_array[i] = 10 ** (-2.1794 + 0.02953 * T_array[i] - 9.1837 * 10 ** -5 * T_array[i] ** 2 + 1.4454 * 10 ** -7 *
                            T_array[i] ** 3)

conductivity_nafion = np.ones(len(T_array))
for i in range(len(T_array)):
    conductivity_nafion[i] = (0.005139 * LAMBDA - 0.00326) * m.exp(1268 * (1 / 303 - 1 / (T_array[i]+273.15)))  # S/cm 0.14

R_mem_array = np.ones(len(T_array))
for i in range(len(T_array)):
    R_mem_array[i] = THIKNESS_NAFION * 10 ** (-4) / conductivity_nafion[i]  # Ohm cm2



temperature = []
p_anode = []
p_cathode = []
current_density = []
cell_voltage = []
alpha = []
i_0 = []

i=0

for i in range(0,len(T_array)):
    for j in range(0, len(p_anode_array)):
        for k in range(0, len(p_cathode_array)):
            for l in range(0, len(current_density_array)):
                # fill look-up-table with input values
                temperature.append(T_array[i])
                alpha.append(ALPHA_array[i])
                i_0.append(i_0_array[i])
                p_anode.append(p_anode_array[j])
                p_cathode.append(p_cathode_array[k])
                current_density.append(current_density_array[l])

                # calculate partial pressures of hydrogen and oxygen for calculation of Nernst-voltage without currentdependensy
                p_h2 = (1+p_cathode_array[k]) - pressure_sat_h2o_array[i]
                p_o2 = (1+p_anode_array[j]) - pressure_sat_h2o_array[i]
                p_h2_ref = 1  # bar
                p_o2_ref = 1  # bar

                # Nernst-voltage
                Nernst_Voltage = U_rev_array[i] + IDEAL_GAS_CONST * (T_array[i] + 273.15) / (2 * FARADAY_CONST) * \
                                 m.log((p_o2 / p_o2_ref)**(1/2) * p_h2 / p_h2_ref)
                #Nernst_Voltage = 1.23 + IDEAL_GAS_CONST * (T_array[i] + 273.15) / (2 * FARADAY_CONST) * \
                                 #m.log((p_o2 / p_o2_ref) ** (1 / 2) * p_h2 / p_h2_ref)

                # Activation-voltage
                if current_density_array[l] == 0:
                    Act_Voltage = 0
                else:
                    Act_Voltage = ALPHA_array[i] * m.log(current_density_array[l] / i_0_array[i])

                # ohmic voltage
                Ohm_Voltage = (R_mem_array[i] + R_ele) * current_density_array[l]

                # cell voltage
                cell_voltage.append(Nernst_Voltage + Act_Voltage + Ohm_Voltage)
                #cell_voltage.append(Nernst_Voltage)

temperature = np.array(temperature)
p_anode = np.array(p_anode)
p_cathode = np.array(p_cathode)
current_density = np.array(current_density)
cell_voltage = np.array(cell_voltage)
alpha = np.array(alpha)
i_0 = np.array(i_0)

# cell voltage lookup field - polariszation curve
cell_voltage_lookup_input = np.array([temperature, p_anode, p_cathode, current_density])
cell_voltage_lookup_output = np.array(cell_voltage)

dict1 = {'temperature in °C' : temperature, 'P anode in  bar' : p_anode, 'P cathode in bar' : p_cathode,
         'currentdensity in A/cm2' : current_density, 'cellvoltage in V' : cell_voltage}
df1 = pd.DataFrame(dict1)
df1.to_csv('cell_voltage_lookup_no_current_influence_on_part_pressure.csv', index=False)

# cell currentdensity lookup field - power curve
cell_power_density = cell_voltage * current_density

cell_current_density_lookup_input = np.array([temperature, p_anode, p_cathode, cell_power_density])
cell_current_density_lookup_output = current_density

dict2 = {'temperature in °C' : temperature, 'P anode in  bar' : p_anode, 'P cathode in bar' : p_cathode,
         'powerdensity in W/cm2' : cell_power_density, 'currentdensity in A/cm2' : current_density, 'alpha in V': alpha, 'i_0 in A/cm2': i_0}
df2 = pd.DataFrame(dict2)
df2.to_csv('cell_currentdensity_lookup_no_current_influence_on_part_pressure_with_alpha.csv', index=False)

# polarizationcurve_interpol = scipy.interpolate.LinearNDInterpolator(cell_voltage_lookup_input.T, cell_voltage_lookup_output)
# voltage1 = polarizationcurve_interpol(30.8,10.2,40.6,2.22)
# print(voltage1)

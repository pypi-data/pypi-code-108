import numpy as np
import matplotlib.pyplot as plt
import math as m
import pandas as pd


# physical constants  / physikalische Konstanten
IDEAL_GAS_CONST: float = 8.314462  # J/(mol K)
FARADAY_CONST: float = 96485.3321  # As/mol
ATM = 1.0  # bar

# fuel cell parameters / Brennstoffzellen Parameter
TEMPERATURE_REF_K: float = 298.15  # K
TEMPERATURE_C_in_K: float = 273.15  # K
RESISTANCE = 0.144787415  # Ohm*cm2

AREA_CELL = 150.0  # cm2
Max_CURRENT = 100.0  # A
Max_CURRENT_Density = Max_CURRENT/AREA_CELL  # A/cm2
REV_VOLTAGE_STC = 1.229  # V

PRESSURE_ANODE = 1.36  # pressure anode in bar
PRESSURE_CATHODE = 1.0  # pressure cathode in bar
PH2 = PRESSURE_ANODE / ATM  # bar to atm
PO2 = PRESSURE_CATHODE * 0.21 / ATM  # bar to atm

B = 0.044  # Konzentrationskoeffizient
N = 70  # Anzahl Zellen
alpha = 0.207900099  # Ladungsübertragungskoeffizient
i_0_ref = 1.89702*10**-4  # Austauschstomdichte [A/cm2] bei einer Referenztemperatur
E_A = 40000  # Aktivierungsenergie (wichtig für Austauschstromdichte [J/mol]
i_n = 0.0100310306  # internal current density [A/cm2]

# Auxiliary Arrays / Hilfs-Arrays
current_density = np.linspace(0, Max_CURRENT_Density, 1001)
cell_voltage = np.ones(len(current_density))
stack_voltage = np.ones(len(current_density))
cell_power = np.ones(len(current_density))
stack_power = np.ones(len(current_density))
cell_temperatur = np.ones(len(current_density))


def T_cell_Calc():
    """
    Calculate T_cell.
    :param i: cell current [A/cm2]
    :type i: float
    :return: T as float
    """
    try:
        result = (0.53 * current_density[i] * AREA_CELL + 26.01 + TEMPERATURE_C_in_K)
        return result
    except (TypeError, ZeroDivisionError):
        return None

def B1_Calc(n=2):
    """
    Calculate B (Constant in the mass transfer term).
    :param n: number of moles of electrons transferred in the balanced equation occurring in the fuel cell
    :type n: int
    :return: B1 as float
    """
    try:
        T = cell_temperatur[i]
        result = (IDEAL_GAS_CONST * T) / (n * FARADAY_CONST)
        return result
    except (TypeError, ZeroDivisionError):
        return None


# Nernst Voltage
def Enernst_Calc(PH2, PO2):
    """
    Calculate Enernst.
    :param PH2: partial pressure [atm]
    :type PH2 : float
    :param PO2: partial Pressure [atm]
    :type PO2: float
    :return: Enernst [V} as float
    """
    try:
        B1 = B1_Calc()  # (R * Tcell) / (2*F)
        T = cell_temperatur[i]

        result = REV_VOLTAGE_STC + B1 * m.log(PH2 * PO2 ** 0.5) - 0.85 * 10 ** -3 * (T - TEMPERATURE_REF_K)
        return result
    except (TypeError, OverflowError, ValueError):
        print(
            "[Error] Enernst Calculation Failed (PH2:%s, PO2:%s)" %
            (str(PH2), str(PO2)))


def i_0_Calc_from_temperature():
    """
    :param i_0_ref: Referenz Austauschstromdichte in [A/cm2]
    :type i_0_ref: float
    :param i: cell load current [A/cm2]
    :type i: float
    :return: i_0 Austauschstromdichte in Abhängigkeit der Temperatur  in [A/cm2]
    """
    Temperature = cell_temperatur[i]
    i_0 = i_0_ref * m.exp((-E_A/IDEAL_GAS_CONST)*((1/Temperature)-(1/TEMPERATURE_REF_K)))
    return i_0


def Eta_Conc_Calc(i, B, imax):
    """
    Calculate Eta concentration.
    :param i: cell load current [A/cm2]
    :type i :float
    :param imax: maximal cell current [A/cm2]
    :type imax: float
    :return: Eta concentration [V] as float
    """
    try:
        if i >= 0 and i + i_n < imax:
            result = - B * m.log(1 - ((i + i_n) / imax))
            return result

    except (TypeError, ZeroDivisionError, OverflowError, ValueError):
        print(
            "[Error] Eta Concentration Calculation Failed (i:%s, B1:%s, imax:%s)" %
            (str(i), str(B), str(imax)))


def Eta_Ohmic_Calc(R_total):
    """
    Calculate Eta ohmic.
    :param i: cell current [A/cm2]
    :type i: float
    :param R_total: Gesamtwiderstand einer Zelle [Ohm]
    :type R_total: float

    """
    try:
        if i != -i_n:
            result = (current_density[i] + i_n) * R_total
            return result
        return 0
    except (TypeError, ZeroDivisionError):
        print(
            "[Error] Eta Ohmic Calculation Failed (i:%s, R_total:%s)" %
            (str(i), str(R_total)))


def Eta_Act_Calc(i, alpha, i_n):
    """
    Calculate Eta activation.
    :param alpha: Ladungsübertragungskoeffizient
    :type alpha: float
    :param i: cell current [A/cm2]
    :type i: float
    :param i_n: interner Zellstrom [A/cm2]
    :type i_n: float
    :param i_0: Austauschstromdichte [A/cm2]
    :type i_0: float
    :return:  Eta activation [V] as float
    """
    try:
        i_0 = i_0_Calc_from_temperature()
        B1 = B1_Calc()  # (R * Tcell) / (2*F)

        result = (B1 / alpha) * (m.log((i + i_n) / i_0))
        return result

    except (TypeError, OverflowError, ValueError):
        print(
            "[Error] Eta Activation Calculation Failed (i:%s, alpha:%s, i_n:%s, i_0:%s)" %
            (str(i), str(alpha), str(i_n), str(i_0)))


def VStack_Calc(N, Vcell):
    """
    Calculate VStack.
    :param N: number of single cells
    :type N: int
    :param Vcell: cell voltage [V}
    :type Vcell: float
    :return: VStack [V] as float
    """
    try:
        result = N * Vcell
        return result
    except TypeError:
        print(
            "[Error] VStack Calculation Error (N:%s, Vcell:%s)" %
            (str(N), str(Vcell)))


def Loss_Calc(Eta_Act, Eta_Ohmic, Eta_Conc):
    """
    Calculate loss.
    :param Eta_Act: Eta activation [V]
    :type Eta_Act : float
    :param Eta_Ohmic: Eta ohmic [V]
    :type Eta_Ohmic : float
    :param Eta_Conc: Eta concentration [V]
    :type Eta_Conc : float
    :return: loss [V] as float
    """
    try:
        result = Eta_Act + Eta_Ohmic + Eta_Conc
        return result
    except TypeError:
        print(
            "[Error] Loss Calculation Error (Eta_Act:%s, Eta_Ohmic:%s, Eta_Conc:%s)" %
            (str(Eta_Act), str(Eta_Ohmic), str(Eta_Conc)))


def Vcell_Calc(Enernst, Loss):
    """
    Calculate cell voltage.
    :param Enernst:  Nernstvoltage [V}
    :type Enernst : float
    :param Loss:  loss [V]
    :type Loss : float
    :return:  cell voltage [V] as float
    """
    try:
        result = Enernst - Loss
        return result
    except TypeError:
        print(
            "[Error] Vcell Calculation Error (Enernst:%s, Loss:%s)" %
            (str(Enernst), str(Loss)))


def Power_Calc(Vcell, i):
    """
    Calculate power.
    :param Vcell: Vcell Voltage [V]
    :type Vcell : float
    :param i: cell current [A/cm2]
    :type i : float
    :return: cell power [W/cm2] as float
    """
    try:
        result = Vcell * i
        return result
    except TypeError:
        print(
            "[Error] Power Calculation Error (Vcell:%s, i:%s)" %
            (str(Vcell), str(i)))


def PowerStack_Calc(Power, N):
    """
    Calculate power_stack.
    :param Power: single cell power [W/cm2]
    :type Power : float
    :param N: number of single cells
    :type N : int
    :return: power stack [W] as float
    """
    try:
        result = N * Power * AREA_CELL
        return result
    except TypeError:
        print(
            "[Error] Power Stack Calculation Error (Power:%s, N:%s)" %
            (str(Power), str(N)))


for i in range(0, len(current_density)):
    a = current_density[i]
    cell_temperatur[i] = T_cell_Calc()
    Enernst = Enernst_Calc(PH2, PO2)
    Eta_Act = Eta_Act_Calc(a, alpha, i_n)
    Eta_Ohmic = Eta_Ohmic_Calc(RESISTANCE)
    Eta_Conc = Eta_Conc_Calc(a, B, Max_CURRENT_Density)
    Loss = Loss_Calc(Eta_Act, Eta_Ohmic, Eta_Conc)
    cell_voltage[i] = Vcell_Calc(Enernst, Loss)
    stack_voltage[i] = Vcell_Calc(N, cell_voltage[i])
    cell_power[i] = Power_Calc(cell_voltage[i], a)
    stack_power[i] = PowerStack_Calc(N, cell_power[i])

x = current_density * 150
y1 = cell_voltage * 70
y2 = cell_power * 150 * 70


#########################
#  Messungen dargestellt:
current_messung1 = (13.2, 16.08, 33.2, 53.2, 72.5, 76.7)  # neue Messungen scheinbar besser =)
voltage_messung1 = (57.09, 56.18, 52.27, 48.50, 44.65, 42.67)  # neue Messungen scheinbar besser =) --> siehe Excel File

current_messung2 = (12.29, 16.78, 33.68, 53.96, 73.52, 78.15)  # neue Messungen scheinbar besser =)
voltage_messung2 = (57.09, 56.18, 52.27, 48.43, 44.62, 42.68)  # neue Messungen scheinbar besser =) --> siehe Excel File

current_messung3 = (12.96, 18.13, 35.20, 55.81, 75.13, 79.94)  # neue Messungen scheinbar besser =)
voltage_messung3 = (57.07, 56.16, 52.20, 48.42, 44.62, 42.67)  # neue Messungen scheinbar besser =) --> siehe Excel File

#########################


fig, axs = plt.subplots(2, 1, constrained_layout=True)
axs[0].plot(x, y1)

#  Messungen plotten ######
axs[0].plot(current_messung1, voltage_messung1)
axs[0].plot(current_messung2, voltage_messung2)
axs[0].plot(current_messung3, voltage_messung3)
###########################

axs[0].set_title('U-I-Kennlinie')
axs[0].set_xlabel('Stromdichte (A/cm2)')
axs[0].set_ylabel('Zellspannung (V)')
fig.suptitle('Zellspannung und Zellleistung in Abhängigkeit der Stromdichte', fontsize=12)

axs[1].plot(x, y2)
axs[1].set_xlabel('Stromdichte (A/cm2)')
axs[1].set_title('P-I-Kennlinie')
axs[1].set_ylabel('Zellleistung (W/cm2)')

plt.show()

dict = {'currentdensity': current_density, 'cellvoltage at 1 bar': cell_voltage}
dict2 = {'currentdenstiy': current_density, 'cellpower at 1 bar': cell_power}

df = pd.DataFrame(dict)
df2 = pd.DataFrame(dict2)

#df.to_csv('polarizationcurve_jupiter.csv', index=False)
#df2.to_csv('powercurve_jupiter.csv', index=False)

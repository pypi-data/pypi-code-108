# Description: Process python data from the multiple runs of WANDA
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.patches import Rectangle
import numpy as np
from typing import List
import pywanda
import zipfile
from scipy.interpolate import interp1d
import math

WBIN = "c:\Program Files (x86)\Deltares\Wanda 4.6\Bin\\"
# Options
# Online path
FN_PATH = r"n:\Projects\11207000\11207361\B. Measurements and calculations\Optimization_folder"
# Local path
FN_PATH = r"c:\Users\meerkerk\OneDrive - Stichting Deltares\TemporaryProjects\11207361 - (2021) Texel windketel\B. Measurements and calculations\Optimization_folder_larger_volume"

FN_MODEL = os.path.join(FN_PATH, "models")
FN_FIGURE = os.path.join(FN_PATH, "figures")
# Options list
KEY_PROCESSED = "processed"
KEY_CVALUE = "AIRVvn A1 Initial C in P*V=C"
KEY_LAPLACE = "AIRVvn A1 Laplace coefficient"
KEY_LOCATION = ["pijp", "dekoog", "hogeberg"]
KEY_LOCATION_NAME = ["rest netwerk", "De Koog", "Hoge Berg"]
KEY_PUMP = "LCON L1 Logical value"
KEY_KETEL = "windketel Fluid level MIN"
KETEL_MIN = 3.4
# Append data from the models
KEY_SCENARIO = "Scenario Name  "
KEY_FLUID_START = "Fluid level initial"
KEY_FLUID_TIME = "time fluid level below Hmin"
KEY_FLUID_SERIES = "Fluid level series"
COMP_NAME = "AIRVvn A1"
PROP_NAME = "Fluid level"

# Parse data
def parse_data(fn: str):
    """ "Combine the data from both the XLS file and XLSX file"""
    # Read xlsx file
    df_data = pd.read_excel(os.path.join(FN_PATH, "{}.xlsx".format(fn)), index_col=0)
    return df_data


def str_list_contains(str_lst: List, cnt_list: List):
    """ "Check if a string list contains keywords enclosed in the cnt_list"""
    if any(
        isinstance(el, list) for el in cnt_list
    ):  # If cnt_list contains multiple lists with keywords:
        idx_list = []
        name_list = []
        sub_name_list = str_lst
        for idx_sub_list, sub_list in enumerate(cnt_list):
            idx_list.append(
                [
                    index
                    for index, name in enumerate(sub_name_list)
                    if any(substr in name for substr in sub_list)
                ]
            )
            if len(idx_list) > 1:
                sub_name_list = [str_lst[idx_list[-2][idx]] for idx in idx_list[-1]]
            else:
                sub_name_list = [str_lst[idx] for idx in idx_list[-1]]
            name_list.append(sub_name_list)
    else:
        idx_list = [
            index
            for index, name in enumerate(str_lst)
            if any(substr in name for substr in cnt_list)
        ]
        name_list = [str_lst[idx] for idx in idx_list]
    return idx_list, name_list


def list_remove(list_1, list_2):
    """Remove list_1 elements from list_2"""
    for element in list_1:
        if element in list_2:
            list_2.remove(element)
    return list_2


def fluid_level_wanda(df: object, model_name: str, fp_model: str = FN_MODEL):
    """Retrieve fluid level from Wanda
    :param df (object): Panda's Dataframe containing the rest of the information."""
    # Retrieve fluid level from Wanda
    # List all available wdi's in the case_files list.
    list_files = os.listdir(fp_model)
    case_files = [
        os.path.splitext(file)[0] for file in list_files if file.endswith(".wdi")
    ]
    case_files = [file for file in case_files if model_name in file]
    # select case files that correspond with case names in the df
    scenario_names = df[KEY_SCENARIO].to_list()
    case_files = [
        file for file in case_files if any(st in file for st in scenario_names)
    ]
    # Loop over the available models
    output = []
    df[KEY_FLUID_START] = np.ones([len(df), 1]) * np.nan
    df[KEY_FLUID_TIME] = np.ones([len(df), 1]) * np.nan
    # Loop over case files.
    for case in case_files:
        idx_name = [
            idx_file
            for idx_file, file in enumerate(scenario_names)
            if case.split("_")[-1] == file
        ][0]
        # Open model
        with zipfile.ZipFile(
            os.path.join(fp_model, "{}.zip".format(case)), "r"
        ) as zip_ref:
            zip_ref.extractall(fp_model)
        fn = os.path.join(fp_model, "{}.wdi".format(case))
        # Try to open model
        try:
            print("Processing {}".format(case))
            model = pywanda.WandaModel(fn, WBIN)
            # Reload output
            model.reload_output()
            comp = model.get_component(COMP_NAME)
            # Read component data
            val = comp.get_property(PROP_NAME).get_scalar_float()
            output.append([case.split("_")[-1], val])
            df.loc[idx_name, KEY_FLUID_START] = val
            # Determine time the value drops below specified height.
            Hlevel = np.array(comp.get_property(PROP_NAME).get_series()) - KETEL_MIN
            tlevel = np.array(model.get_time_steps())
            idx_time = np.where(Hlevel <= 0.0)[0]
            if len(idx_time) == 0:
                df.loc[idx_name, KEY_FLUID_TIME] = tlevel[-1]
            elif len(idx_time) == len(Hlevel):
                df.loc[idx_name, KEY_FLUID_TIME] = tlevel[0]
            else:
                idx_range = np.arange((idx_time[0] - 1), (idx_time[0] + 1))
                df.loc[idx_name, KEY_FLUID_TIME] = float(
                    interp1d(Hlevel[idx_range], tlevel[idx_range], kind="linear")(0)
                )
        except Exception as e:
            print(e)
            print("Skipping {}".format(case))
            output.append([case.split("_")[-1], np.NaN])
    return df


if __name__ == "__main__":
    scenario_list = {
        "Maximaal debiet": [
            "txl_db_max_case{}".format(idx) for idx in np.arange(30, 32 + 1)
        ],
        "Gemiddeld debiet": [
            "txl_db_avg_case{}".format(idx) for idx in np.arange(65, 68 + 1)
        ],
    }
    scenario_name = [r'Maximaal debiet $(566 \ \mathrm{m^3/h})$', r'Gemiddeld debiet $(360 \ \mathrm{m^3/h})$']
    case_marker = ["s", "o"]
    case_style = ["-", "--"]
    case_color = ["r", "b"]
    scenario_color = ["r", "b"]
    # Options
    H0 = 3.0  # minimal water level
    nstep = 41  # time steps
    Hmin = 0.4
    Hzuig = 1.0
    Hrange = [Hmin]

    # Figure config
    plt.rcParams.update({"font.size": 13})
    plt.figure(figsize=[15 / 2.54, 10 / 2.54])
    # Background curve
    # Calculate output pressure per case
    Prange = [200, 650]
    Hplot = [.4, 2.3]
    Hfit = [-0.5, 2.3]
    rho = 1000
    g = 9.81
    D0 = 0.4  # Inlet diameter
    dH = 5.0
    Patmos = 1.013E5
    Vketel = 18.7# Height difference between bottom and output pipe of airvessel
    # Ppipe
    Apipe = (math.pi / 4) * D0 ** 2
    Ppipe_inlet = rho * g * dH
    # Pketel
    Dketel = 2.84  # Diameter of the airvessel
    Aketel = (math.pi / 4) * Dketel ** 2
    Hcurve = np.linspace(Hfit[0], Hfit[1], 50)
    Pxtick = np.linspace(Prange[0] * 10 ** 3, Prange[1] * 10 ** 3, 50)
    Cest_list = [3_000_000, 5_000_000]
    Hwat = np.empty([len(Hcurve), 2])#3_500_000
    #TODO: Plot shaded region
    for idx_Cest, Cest in enumerate(Cest_list):
        Ptemp = rho*g*(dH + Hcurve) + Cest/(Vketel - Hcurve*Aketel) - Patmos
        Hwat[:, idx_Cest] = np.interp(Pxtick, Ptemp, Hcurve)
    # Shaded region
    plt.fill_between(Pxtick * 10 ** (-3), Hwat[:, 0], Hwat[:, 1], facecolor='green', linestyle='None', alpha=0.3)
    plt.plot(Pxtick*10**(-3), np.mean(Hwat, axis=1), color='black', label='druk tegenover waterniveau')
    plt.plot(Pxtick * 10 ** (-3), Hwat[:, 0], color='green', linestyle='--')
    plt.plot(Pxtick * 10 ** (-3), Hwat[:, 1], color='green', linestyle='--')
    Pxtick = Pxtick * 10 ** (-3)
    plt.plot([Pxtick[0], Pxtick[-1]], [1.65]*2, color='black', linestyle='--', label='Geadviseerd waterniveau')
    # Loop case
    for idx_scenario, scenario in enumerate(list(scenario_list.keys())):
        Toutput = np.zeros([len(scenario_list[scenario]), len(Hrange)])
        Coutput = np.zeros([len(scenario_list[scenario]), 1])
        H0output = np.zeros([len(scenario_list[scenario]), 1])
        P0output = np.zeros([len(scenario_list[scenario]), 1])
        Pmodel_output = np.zeros([len(scenario_list[scenario]), 1])
        for idx_case, case in enumerate(scenario_list[scenario]):
            print("Processing scenario {} for case: {}".format(scenario, case))
            # Open and reload model.
            fn = os.path.join(FN_MODEL, "{}.wdi".format(case))
            model = pywanda.WandaModel(fn, WBIN)
            model.reload_output()
            # Open component
            comp = model.get_component(COMP_NAME)
            # Retrieve properties from component
            tlevel = np.array(model.get_time_steps())
            Hlevel = np.array(comp.get_property(PROP_NAME).get_series()) - H0
            # Write out data
            H0output[idx_case] = Hlevel[0]
            Coutput[idx_case] = comp.get_property(
                "Initial C in P*V=C"
            ).get_scalar_float()
            Pmodel_output[idx_case] = comp.get_property('Pressure 1').get_series()[0]*10**-3
            # Wate rpressure
            Vwater = Aketel*Hlevel[0]
            Pwater_vessel = rho*g*Hlevel[0]
            # Pair
            C0 = Coutput[idx_case][0]
            Vair = Vketel - Vwater
            Pair = C0/Vair
            # Ptotal
            Ptotal = (Ppipe_inlet + Pwater_vessel + Pair - Patmos)*10**(-3)
            P0output[idx_case] = Ptotal
            print("Voor case {} is Hstart = {} m".format(case, Hlevel[0]))
            # Deteremine time below zero (i.e., where the waterheight-criterium is crossed)
            for idx_Hi, Hi in enumerate(Hrange):
                idx_t = np.where(Hlevel < Hi)[0]
                if len(idx_t) == 0:
                    Toutput[idx_case, idx_Hi] = max(tlevel)
                else:
                    try:
                        idx_range = np.arange(idx_t[0] - 1, idx_t[0] + 1)
                        Toutput[idx_case, idx_Hi] = float(
                            interp1d(
                                Hlevel[idx_range], tlevel[idx_range], kind="linear"
                            )(Hi)
                        )
                    except:
                        Toutput[idx_case, idx_Hi] = tlevel[idx_t[0]]
        test = 0
        for idx_Hi, Hi in enumerate(Hrange):
            plt.plot(
                Pmodel_output[:, 0],
                H0output[:, 0],
                linestyle=case_style[idx_Hi],
                color=scenario_color[idx_scenario],
                marker=case_marker[idx_scenario],
                label=scenario_name[idx_scenario],
                markerfacecolor=scenario_color[idx_scenario],
            )
            plt.text(P0output[0, 0] + 10, H0output[0, 0],
                     "C = {:04.0f} (kJ)".format(np.round(Coutput[0, 0]*10**(-3))),
                     color=scenario_color[idx_scenario])
            plt.text(P0output[-1, 0] + 10, H0output[-1, 0],
                     "C = {:04.0f} (kJ)".format(np.round(Coutput[-1, 0] * 10 ** (-3))),
                     color=scenario_color[idx_scenario])

    plt.legend(frameon=True, loc="lower right", fontsize="x-small", edgecolor='None')
    plt.grid()
    plt.xlim(Prange)
    plt.ylim(Hplot)
    plt.xlabel(r"$\mathrm{waterdruk \ P_{water}} \ \mathrm{(kPa)}$")
    plt.ylabel(r"$\mathrm{waterniveau \ ketel} \ \mathrm{(m)}$")
    plt.tight_layout()

    plt.savefig(os.path.join(FN_FIGURE, "Waterdruk_tegenover_waterniveau.png"))

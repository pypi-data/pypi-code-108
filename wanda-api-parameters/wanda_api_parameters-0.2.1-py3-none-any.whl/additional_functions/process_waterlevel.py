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
            idx_file for idx_file, file in enumerate(scenario_names) if case.split('_')[-1] == file
        ][0]
        # Open model
        with zipfile.ZipFile(os.path.join(fp_model, "{}.zip".format(case)), "r") as zip_ref:
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
            Hlevel = (np.array(comp.get_property(PROP_NAME).get_series())-KETEL_MIN)
            tlevel = np.array(model.get_time_steps())
            idx_time = np.where(Hlevel <= 0.0)[0]
            if len(idx_time) == 0:
                df.loc[idx_name, KEY_FLUID_TIME] = tlevel[-1]
            elif len(idx_time) == len(Hlevel):
                df.loc[idx_name, KEY_FLUID_TIME] = tlevel[0]
            else:
                idx_range = np.arange((idx_time[0]-1),(idx_time[0]+1))
                df.loc[idx_name, KEY_FLUID_TIME] = float(interp1d(Hlevel[idx_range], tlevel[idx_range], kind='linear')(0))
        except Exception as e:
            print(e)
            print("Skipping {}".format(case))
            output.append([case.split("_")[-1], np.NaN])
    return df


if __name__ == "__main__":
    case_list = ['txl_db_max_case30',  'txl_db_max_case33',
                 ]
    case_list = ['txl_db_avg_case65', 'txl_db_avg_case68',
                 ]
    case_label = ['Maximaal debiet C = 3,000 kJ',  'Maximaal debiet C = 5,000 kJ',
                  ]
    case_label = ['Gemiddeld debiet C = 2,000 kJ', 'Gemiddeld debiet C = 5,000 kJ',
                  ]
    case_marker = ['None', 'None', 'None', 'None', 'None', 'None']
    case_style = ['-','--']*2
    case_color = ['r','r','b','b']
    # Options
    H0 = 3.0    # minimal water level
    nstep = 41  # time steps
    Hlevel = np.empty([nstep, len(case_list)])

    # Figure config
    plt.rcParams.update({"font.size": 13})
    plt.figure(figsize=[15 / 2.54, 10 / 2.54])
    plt.plot([0, 400], [0.4] * 2, color='gray', linestyle='--')
    plt.text(10, 0.35, "minimum hoogte", fontsize='x-small', verticalalignment='top', horizontalalignment='left')
    plt.plot([0, 400], [1.0] * 2, color='gray', linestyle='--')
    plt.text(20, 1.0, "minimum hoogte verversingsleiding", fontsize='x-small', verticalalignment='bottom',
             horizontalalignment='left')
    # Loop case
    for idx_case, case in enumerate(case_list):
        print('Processing case: {}'.format(case))
        # Open and reload model.
        fn = os.path.join(FN_MODEL, "{}.wdi".format(case))
        model = pywanda.WandaModel(fn, WBIN)
        model.reload_output()
        # Open component
        comp = model.get_component(COMP_NAME)
        tlevel = np.array(model.get_time_steps())
        Hlevel[:, idx_case] = np.array(comp.get_property(PROP_NAME).get_series()) - H0
        print("Voor case {} is Hstart = {} m".format(case, Hlevel[0, idx_case]))
        # Plot case
        if case_label[idx_case] is not None:
            plt.plot(tlevel, Hlevel[:, idx_case],
                     marker=case_marker[idx_case],
                     linestyle=case_style[idx_case],
                     color=case_color[idx_case],
                     label=case_label[idx_case])
        else:
            plt.plot(tlevel, Hlevel[:, idx_case],
                     marker=case_marker[idx_case],
                     linestyle=case_style[idx_case],
                     color=case_color[idx_case],
                     )
    plt.legend(frameon=False, loc='upper right')
    plt.xlim([0, 400])
    plt.ylim([0, 3])
    plt.xlabel(r'$\mathrm{tijd} \ \mathrm{(s)}$')
    plt.ylabel(r'$waterniveau ketel \ \mathrm{(m)}$')
    plt.tight_layout()

    plt.savefig(
        os.path.join(FN_FIGURE, "waterlevel_over_time_no_restart_gem.png")
    )

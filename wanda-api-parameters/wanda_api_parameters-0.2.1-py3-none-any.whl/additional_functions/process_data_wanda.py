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
FN_PATH = r"c:\Users\meerkerk\OneDrive - Stichting Deltares\TemporaryProjects\Texel_waterslag\B. Measurements and calculations\Optimization_folder_larger_volume"

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
KEY_SCENARIO = "Scenario Name "
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
    fn_list = ["txl_db_max", "txl_db_avg"]
    marker_level = ['s', 'o']
    color_level = ['r', 'b']
    update_file = False

    plt.rcParams.update({"font.size": 16})
    fig_level = plt.figure(figsize=[15 / 2.54, 10 / 2.54])
    ax_level = fig_level.gca()
    for index_fn, fn in enumerate(fn_list):
        if fn == "txl_db_avg":
            title_label = "Gemiddeld debiet"
        elif fn == "txl_db_max":
            title_label = "Maximaal debiet"
        else:
            title_label = "Unknown"
        # Read in the excel file with data
        if os.path.isfile(os.path.join(FN_PATH, "{}_{}.xlsx".format(fn, KEY_PROCESSED))) and not update_file:
            df = parse_data(fn="{}_{}".format(fn, KEY_PROCESSED))
        else:
            df = parse_data(fn=fn)
            # Parse the initial fluid levels from the model.
            df = fluid_level_wanda(df=df, model_name=fn)
            # Write to processed folder
            df.to_excel(os.path.join(FN_PATH, "{}_{}.xlsx".format(fn, KEY_PROCESSED)))
        names = list(df.columns)
        # Check name list for specified names
        name_list = [[*KEY_LOCATION, KEY_CVALUE, KEY_LAPLACE], ["MAX"]]
        idx_name, name_sub_list = str_list_contains(str_lst=names, cnt_list=name_list)
        name_sub = list_remove(list_1=name_sub_list[1], list_2=name_sub_list[0])
        # Map data values to configuration
        sub_sets = []
        len_set = len(np.unique(df[KEY_CVALUE]))
        for ii in range(int(len(df) / len_set)):
            sub_sets.append(np.arange(ii * len_set, (ii + 1) * len_set, 1))
        for indx_sub_set, sub_set in enumerate(sub_sets):
            df_sub = df.loc[sub_set]
            # Plot width
            Crange = 10_000
            # Plot data
            plt.rcParams.update({"font.size": 16})
            plt.figure(figsize=[15 / 2.54, 12.5 / 2.54])
            ax = plt.gca()
            hatches = ["/", "\\", "|", "-", "+", "x", "o", "O", ".", "*"]
            # Define pressure patch
            rect_pressure = Rectangle(
                xy=[0, -2],
                width=Crange,
                height=2,
                edgecolor="black",
                facecolor="black",
                alpha=0.1,
            )
            # Define fluid level patch
            idx_Cmax = np.where(df_sub[KEY_KETEL] > KETEL_MIN)[0][-1]
            Cmax = df_sub.iloc[idx_Cmax][KEY_CVALUE]
            # Define minimum C value
            location_name = [name for name in name_sub if "Pressure" in name]
            idx_Cmin = np.where(np.prod((df_sub[location_name].values >= 0), axis=1))[0]
            # Set herstart
            if df_sub[KEY_PUMP].unique()[0] == 2:
                label_herstart = "en herstart"
            elif df_sub[KEY_PUMP].unique()[0] == 1:
                label_herstart = "zonder herstart"
            else:
                label_herstart = ""

            print("{} {} met een Laplace coefficient van {:.1f}".format(
                    title_label, label_herstart, df_sub[KEY_LAPLACE].unique()[0]
                ))
            if len(idx_Cmin) > 0:
                idx_Cmin = idx_Cmin[0]
                Cmin = df_sub.iloc[idx_Cmin][KEY_CVALUE]
                trange = [df_sub.iloc[idx_Cmin][KEY_FLUID_TIME], df_sub.iloc[idx_Cmax][KEY_FLUID_TIME]]
                print("For {} <C< {} (kJ) the drainage time is between {} <t< {} (s)".format(Cmin, Cmax, trange[0],
                                                                                             trange[1]))
            else:
                Cmin = np.nan
                trange = [np.nan]*2
            if Cmax == 1_000:
                Cmax = 0
            rect_level = Rectangle(
                xy=[Cmax, 0],
                width=Crange,
                height=3,
                edgecolor="black",
                facecolor="blue",
                alpha=0.25,
                fill=False,
                hatch="//",
            )
            # Patch plot
            ax.add_patch(rect_pressure)
            ax.add_patch(rect_level)
            plt.plot([0, Crange], [0, 0], linewidth=2, linestyle="--", color="black")
            plt.text(
                Crange-250,
                0 - 0.1,
                "Onderdruk gebied",
                horizontalalignment="right",
                verticalalignment="top",
                fontsize="x-small",
                )
            plt.plot([Cmax, Cmax], [-2, 2], linewidth=2, linestyle="--", color="black")
            plt.text(
                Cmax + 250,
                -2 + 0.1,
                "Minimaal waterniveau",
                horizontalalignment="left",
                verticalalignment="bottom",
                rotation="vertical",
                fontsize="x-small",
                )
            marker_list = ["o", "^", "s"]
            for idx_location, location in enumerate(KEY_LOCATION):
                location_name = [name for name in name_sub if location in name]
                plt.plot(
                    df_sub[KEY_CVALUE],
                    df_sub[location_name],
                    label=KEY_LOCATION_NAME[idx_location],
                    marker=marker_list[idx_location],
                )
            plt.legend(frameon=False, loc="lower left", fontsize='x-small')
            plt.xlabel(r"$C = P_{lucht} \times V_{lucht} \ (kJ)$")
            plt.ylabel(r"$P \ (barg)$")

            plt.title(
                "{} {} \n met een Laplace coefficient van {:.1f} \n".format(
                    title_label, label_herstart, df_sub[KEY_LAPLACE].unique()[0]
                )
            )
            plt.xlim([0, Crange])
            plt.ylim([-2, 2])
            plt.grid(False)
            plt.tight_layout()
            plt.savefig(
                os.path.join(FN_FIGURE, "{}_{:2.0f}.svg".format(fn, indx_sub_set)),
                format="svg"
            )

        Hbottom = 3.0
        Hmin = 0.4
        Hsuction = 1.0

        # Plot a single sub set as all subsets are similar (i.e., similar initial conditions)
        sub_set = sub_sets[0]
        df_sub = df.loc[sub_set]
        # Create figure to show water level vs C
        Csetpoints = [3_000, 5_000]
        yvalues = df_sub[KEY_FLUID_START].values - Hbottom
        for Cset in Csetpoints:
            idx_c = np.where(df_sub[KEY_CVALUE].values==Cset)[0][0]
            print("{} bij {} kJ is H = {} m".format(title_label, Cset, yvalues[idx_c]))

        ax_level.plot(df_sub[KEY_CVALUE].values,
                      yvalues,
                      color=color_level[index_fn],
                      marker=marker_level[index_fn],
                      markerfacecolor=color_level[index_fn],
                      label="{}".format(
                          title_label
                      )
                      )
plt.figure(fig_level)
ax_level.plot([0, Crange], [Hmin]*2, color='k', marker='None', linestyle='--')#,label=r'minimum hoogte $(m)$')
ax_level.plot([0, Crange], [Hsuction] * 2, color='k', marker='None', linestyle=':')#,label=r'minimum hoogte zuigleiding $(m)$')
plt.text(
    250,
    Hmin-0.05,
    "minimum hoogte",
    horizontalalignment="left",
    verticalalignment="top",
    fontsize="x-small",
    )
plt.text(
    250,
    Hsuction-0.05,
    "minimum hoogte verversingsleiding",
    horizontalalignment="left",
    verticalalignment="top",
    fontsize="x-small",
    )
ax =plt.gca()
ax.set_xlim([0, Crange])
ax.set_ylim([0, 3])
plt.legend(frameon=False, fontsize='x-small', loc='upper right')
plt.xlabel(r"$C = P_{lucht} \times V_{lucht} \ (kJ)$")
plt.ylabel(r"$waterniveau ketel \ (m)$")
plt.tight_layout()
plt.savefig(
    os.path.join(FN_FIGURE, "waterlevel_vs_cvalue.png")
)
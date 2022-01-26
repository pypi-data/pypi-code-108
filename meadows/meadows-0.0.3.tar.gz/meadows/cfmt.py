from __future__ import annotations
from typing import TYPE_CHECKING, Tuple
if TYPE_CHECKING:
    from pandas.core.frame import DataFrame


def score_cfmt(annotations: DataFrame) -> Tuple[int, DataFrame]:
    """Determine total score and mark correct responses

    Args:
        annotations (DataFrame): Annotations

    Returns:
        Tuple[int, DataFrame]: First element is the total score,
            second a copy of the dataframe with a new "correct" column
    """
    scored = annotations.copy()
    scored = scored.loc[~scored.stim1_name.str.contains('pract')]
    def isCorrect(row):
        return KEY[row.stim1_name] == int(row.label)
    scored['correct'] = scored.apply(isCorrect, axis=1)
    return (scored.correct.values.sum(), scored)


KEY = dict(
    pract_00_X_01_13_l_li=1,
    pract_00_X_02_00_f_li=2,
    pract_00_X_03_13_r_li=2,
    intro_00_B_01_13_l_li=2,
    intro_00_B_02_00_f_li=3,
    intro_00_B_03_13_r_li=3,
    intro_01_D_01_13_l_li=2,
    intro_01_D_02_00_f_li=3,
    intro_01_D_03_13_r_li=3,
    intro_02_J_01_13_l_li=3,
    intro_02_J_02_00_f_li=3,
    intro_02_J_03_13_r_li=1,
    intro_03_M_01_13_l_li=2,
    intro_03_M_02_00_f_li=3,
    intro_03_M_03_13_r_li=1,
    intro_04_N_01_13_l_li=3,
    intro_04_N_02_00_f_li=1,
    intro_04_N_03_13_r_li=3,
    intro_05_Z_01_13_l_li=1,
    intro_05_Z_02_00_f_li=3,
    intro_05_Z_03_13_r_li=1,
    novel_00_M_05_00_f_hl=1,
    novel_01_N_08_13_r_dk=2,
    novel_02_Z_06_23_l_li=1,
    novel_03_D_05_00_f_hl=3,
    novel_04_B_07_00_f_bl=3,
    novel_05_J_06_23_l_li=2,
    novel_06_D_07_00_f_bl=1,
    novel_07_Z_05_00_f_hl=3,
    novel_08_M_06_23_l_li=2,
    novel_09_J_07_00_f_bl=3,
    novel_10_N_04_23_r_li=2,
    novel_11_M_08_13_r_dk=3,
    novel_12_J_05_00_f_hl=2,
    novel_13_N_07_00_f_bl=1,
    novel_14_Z_04_23_r_li=2,
    novel_15_D_08_13_r_li=2,
    novel_16_M_07_00_f_bl=2,
    novel_17_B_04_23_r_li=2,
    novel_18_D_06_23_l_li=1,
    novel_19_N_05_00_f_hl=3,
    novel_20_B_06_23_l_li=1,
    novel_21_Z_08_13_r_dk=2,
    novel_22_J_04_23_r_li=2,
    novel_23_B_08_13_r_hs=1,
    novel_24_M_04_23_r_li=3,
    novel_25_J_08_13_r_dk=1,
    novel_26_Z_07_00_f_bl=2,
    novel_27_D_04_23_r_li=1,
    novel_28_N_06_23_l_li=1,
    novel_29_B_05_00_f_hl=3,
    noise_00_Z_12_00_f_li=2,
    noise_01_M_11_23_r_li=3,
    noise_02_D_10_13_l_li=1,
    noise_03_J_12_00_f_hs=1,
    noise_04_J_11_23_r_li=3,
    noise_05_N_09_00_f_ls=1,
    noise_06_B_12_00_f_hs=2,
    noise_07_M_12_00_f_hs=1,
    noise_08_D_12_00_f_hs=2,
    noise_09_Z_11_23_r_li=2,
    noise_10_N_10_13_l_dk=2,
    noise_11_B_09_00_f_ls=2,
    noise_12_M_09_00_f_ls=1,
    noise_13_J_09_00_f_li=2,
    noise_14_N_12_00_f_li=1,
    noise_15_B_10_13_l_li=2,
    noise_16_N_11_23_r_li=3,
    noise_17_J_10_13_l_li=1,
    noise_18_Z_09_00_f_li=3,
    noise_19_D_09_00_f_ls=1,
    noise_20_M_10_13_l_dk=1,
    noise_21_Z_10_13_l_li=1,
    noise_22_B_11_23_r_li=1,
    noise_23_D_11_23_r_li=3
)

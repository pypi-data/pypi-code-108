import os.path
import numpy as np
from typing import List
import pandas
from pandas import DataFrame
from logging import info


def threshold_confidence(h5s: List[str], min_likelihood: float, save_csv=False) -> List[str]:
    """
    Thresholds the dlc analysis for a minimum likelihood values less than min_likelihood will be changed to np.nan
    :param h5s: the paths to the h5 files
    :param min_likelihood: the likelihood cutoff all points
    :param save_csv: set true to save a csv file in addition to the hdf5
    :return: a list to the path of thresholded hdf5s
    """
    ret_h5s = []
    for h5_path in h5s:
        if not os.path.isfile(h5_path):
            raise FileNotFoundError
        out_path = os.path.splitext(h5_path)[0] + "_threshold.h5"
        ret_h5s.append(out_path)
        if not os.path.isfile(out_path):
            df = pandas.read_hdf(h5_path)
            assert type(df) == DataFrame
            dlc_scorer = df.columns.levels[0].to_list()[0]
            bps = df.columns.levels[1].to_list()
            __threshold_bp(df, dlc_scorer, min_likelihood, bps)
            df.to_hdf(out_path, key="scorer", mode="w")
            if save_csv:
                df.to_csv(out_path.replace(".h5", ".csv"), mode="w")
        else:
            info(f"{h5_path} was already thresholded, skipping")
    return ret_h5s


def __threshold_bp(df: DataFrame, dlc_scorer, cutoff: float, bps: List[str]):
    for i, bp in enumerate(bps):
        prob = df[dlc_scorer, bp, "likelihood"].values.squeeze()
        mask_ = prob < cutoff
        x = np.ma.array(df[dlc_scorer, bp, "x"].values, mask=mask_).filled(np.nan).squeeze()
        y = np.ma.array(df[dlc_scorer, bp, "y"].values, mask=mask_).filled(np.nan).squeeze()
        df[dlc_scorer, bp, "x"] = x
        df[dlc_scorer, bp, "y"] = y

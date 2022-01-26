from enum import Enum

import numpy as np
import pandas as pd
from pyridy.file import RDYFile
from pyridy.utils import GPSSeries, LinearAccelerationSeries, WzSeries


class ConditionProcessor:
    def __init__(self, thres_lo: float = 0, thres_hi: float = 0, v_thres: float = 1.0, sampling_period: str = "1000ms"):
        """
        Class representing the Track condition based on a RDYFile containing measurements of a track
        :param thres_lo:
        :param thres_hi:
        """
        self.thres_lo: float = thres_lo
        self.thres_hi: float = thres_hi
        self.v_thres: float = v_thres
        self.sampling_period: str = sampling_period

        pass

    # Use properties to automatically update track condition when values are changed
    # @property
    # def thres_lo(self):
    #     return self._thres_lo
    #
    # @thres_lo.setter
    # def thres_lo(self, value):
    #     self._thres_lo = value
    #     self._evaluate_track_condition()
    #
    # @property
    # def thres_hi(self):
    #     return self._thres_hi
    #
    # @thres_hi.setter
    # def thres_hi(self, value):
    #     self._thres_hi = value
    #     self._evaluate_track_condition()

    def process_file(self, file: RDYFile, method="acc") -> pd.DataFrame:
        if method not in ["acc", "velocity", "comfort"]:
            raise ValueError("Method must be either 'acc', 'velocity' or 'comfort'")

        gps_df = file.measurements[GPSSeries].to_df()
        lin_acc_df = file.measurements[LinearAccelerationSeries].to_df()
        wz_df = file.measurements[WzSeries].to_df()

        if method == "acc" or method == "velocity":
            if not gps_df.empty and not lin_acc_df.empty:
                # Concatenate dataframes and resort them ascending
                df_merged = pd.concat([lin_acc_df, gps_df]).sort_index()

                # Merge identical indices by taking mean of column values and then interpolate NaN values
                df_merged = df_merged.groupby(level=0).mean().interpolate()

                # Resample to 1 Hz
                df_merged = df_merged.resample(self.sampling_period).mean()

                if method == "acc":
                    conditions = [
                        (df_merged['lin_acc_z'].abs() <= self.thres_lo),
                        (df_merged['lin_acc_z'].abs() > self.thres_lo) & (df_merged['lin_acc_z'].abs() <= self.thres_hi),
                        (df_merged['lin_acc_z'].abs() > self.thres_hi)
                    ]
                elif method == "velocity":
                    conditions = [
                        ((df_merged['lin_acc_z'].abs() / (df_merged['speed']**2).abs()) <= self.thres_lo),
                        ((df_merged['lin_acc_z'].abs() / (df_merged['speed']**2).abs()) > self.thres_lo) & ((df_merged['lin_acc_z'].abs() / (df_merged['speed']**2).abs()) <= self.thres_hi),
                        ((df_merged['lin_acc_z'].abs() / (df_merged['speed']**2).abs()) > self.thres_hi)
                    ]
                else:
                    raise ValueError("Method must be either 'acc', 'velocity' or 'comfort'")

                values = [TrackCondition.GOOD.name, TrackCondition.SATISFACTORY.name, TrackCondition.INSUFFICIENT.name]

                df_merged['condition'] = np.select(conditions, values)
                df_merged = df_merged.drop(df_merged[df_merged.condition == '0'].index).reset_index()
                df_merged = df_merged[df_merged['speed'] >= self.v_thres]
                df_merged = df_merged[['lat', 'lon', 'condition']]
            else:
                df_merged = pd.DataFrame({"lat": [], "lon": [], "condition": []})
        elif method == "comfort":
            if not gps_df.empty and not wz_df.empty:
                # Concatenate dataframes and resort them ascending
                df_merged = pd.concat([wz_df, gps_df]).sort_index()

                # Merge identical indices by taking mean of column values and then interpolate NaN values
                df_merged = df_merged.groupby(level=0).mean().interpolate()

                # Resample to 1 Hz
                df_merged = df_merged.resample(self.sampling_period).mean()
                conditions = [
                    (df_merged['wz_z'].abs() <= self.thres_lo),
                    (df_merged['wz_z'].abs() > self.thres_lo) & (df_merged['wz_z'].abs() <= self.thres_hi),
                    (df_merged['wz_z'].abs() > self.thres_hi)
                ]

                values = [TrackCondition.GOOD.name, TrackCondition.SATISFACTORY.name, TrackCondition.INSUFFICIENT.name]

                df_merged['condition'] = np.select(conditions, values)
                df_merged = df_merged.drop(df_merged[df_merged.condition == '0'].index).reset_index()
                df_merged = df_merged[df_merged['speed'] >= self.v_thres]
                df_merged = df_merged[['lat', 'lon', 'condition']]
            else:
                df_merged = pd.DataFrame({"lat": [], "lon": [], "condition": []})
            pass
        else:
            raise ValueError("Method must be either 'acc', 'velocity' or 'comfort'")

        return df_merged


class TrackCondition(Enum):
    GOOD = "#57AB27"  # (RWTHGrün100)
    SATISFACTORY = "#F6A800"  # (RWTHOrange100)
    INSUFFICIENT = "#CC071E"  # (RWTHRot100)

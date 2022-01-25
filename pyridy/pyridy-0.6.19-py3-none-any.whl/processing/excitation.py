import logging
from datetime import timedelta
from typing import Union

import numpy as np
import pandas as pd
from scipy import signal, integrate
from tqdm.auto import tqdm

from pyridy import Campaign
from pyridy.processing import PostProcessor
from pyridy.utils import LinearAccelerationSeries, GPSSeries

logger = logging.getLogger(__name__)


class ExcitationProcessor(PostProcessor):
    def __init__(self, campaign: Campaign, f_s: int = 200, f_c: float = 0.1, order: int = 4):
        """ The ExcitationProcessor performs a double integration of the acceleration data to calculate
        excitations. High-Pass Filters are applied to remove static offset and drift. Hence, the resulting
        excitations only represent high-frequent excitations but no quasi-static movements

        Parameters
        ----------
        campaign: Campaign
            The measurement campaign on which the ExcitationProcessor should be applied. Results are saved directly
            in the campaign.
        f_s: int, default: 200
            Sampling frequency to be used.
        f_c: float, default: 0.1
            Cut-Off frequency for the high-pass filter
        order: int, default: 4
            Order of the high-pass filter
        """
        super(ExcitationProcessor, self).__init__(campaign)
        self.f_s = f_s
        self.f_c = f_c
        self.order = order

        self.b, self.a = signal.butter(self.order, 2 * self.f_c / self.f_s, 'high')  # High Pass (2*f_c/f_s)

    def execute(self, axes: Union[str, list] = "z", intp_gps: bool = True):
        """ Executes the processor on the given axes

        Parameters
        ----------
        intp_gps: bool, default: True
            If true interpolates the GPS measurements onto the results
        axes: str or list, default: "z"
            Axes to which processor should be applied to. Can be a single axis or a list of axes
        """
        if type(axes) == str:
            if axes not in ["x", "y", "z"]:
                raise ValueError("axes must be 'x', 'y' or 'z', or list of these values")
            else:
                axes = [axes]
        elif type(axes) == list:
            for ax in axes:
                if ax not in ["x", "y", "z"]:
                    raise ValueError("axes must be 'x', 'y' or 'z', or list of these values")
        else:
            raise ValueError("axes must be list or str")

        for f in tqdm(self.campaign):
            if len(f.measurements[LinearAccelerationSeries]) == 0:
                logger.warning("(%s) LinearAccelerationSeries is empty, can't execute ExcitationProcessor on this file"
                               % f.name)
                continue
            else:
                lin_acc_df = f.measurements[LinearAccelerationSeries].to_df()

                if len(f.measurements[GPSSeries]) > 0:
                    gps_df = f.measurements[GPSSeries].to_df()
                    df = pd.concat([lin_acc_df, gps_df]).sort_index()
                else:
                    logger.warning(
                        "(%s) GPSSeries is empty, can't interpolate GPS values onto results" % f.name)
                    df = lin_acc_df

                df = df.resample(timedelta(seconds=1 / self.f_s)).mean().interpolate()
                t = (df.index.values - df.index.values[0]) / np.timedelta64(1, "s")

                for ax in axes:
                    if ax == "x":
                        lin_acc = df.lin_acc_x
                    elif ax == "y":
                        lin_acc = df.lin_acc_y
                    elif ax == "z":
                        lin_acc = df.lin_acc_x
                    else:
                        raise ValueError("axes must be 'x', 'y' or 'z', or list of these values")

                    # High pass filter first to remove static offset
                    lin_acc_hp = signal.filtfilt(self.b, self.a, lin_acc, padlen=150)

                    # Integrate and High-Pass Filter
                    lin_v = integrate.cumtrapz(lin_acc_hp, t, initial=0)
                    lin_v_hp = signal.filtfilt(self.b, self.a, lin_v, padlen=150)
                    df["lin_v_" + ax] = lin_v_hp

                    lin_s = integrate.cumtrapz(lin_v_hp, t, initial=0)
                    lin_s_hp = signal.filtfilt(self.b, self.a, lin_s, padlen=150)
                    df["lin_s_" + ax] = lin_s_hp

                if ExcitationProcessor not in self.campaign.results:
                    self.campaign.results[ExcitationProcessor] = {f.name: df}
                else:
                    self.campaign.results[ExcitationProcessor][f.name] = df

        params = self.__dict__.copy()
        params.pop("campaign")
        if ExcitationProcessor not in self.campaign.results:
            self.campaign.results[ExcitationProcessor] = {"params": params}
        else:
            self.campaign.results[ExcitationProcessor]["params"] = params
        pass

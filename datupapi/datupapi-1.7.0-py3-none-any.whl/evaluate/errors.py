import boto3
import numpy as np
import os
import pandas as pd

from datupapi.configure.config import Config


class Errors(Config):

    def __init__(self, config_file, logfile, log_path, *args, **kwargs):
        Config.__init__(self, config_file=config_file, logfile=logfile)
        self.log_path = log_path


    def compute_mape(self, target=None, forecast=None):
        """
        Return the Mean Absolute Percentage Error between target and forecast points.

        :param target: List of target values
        :param forecast: List of forecast values
        :return mape: Mean Absolute Percentage Error value

        >>> mape = compute_mape(target=mytarget, forecast=myforecast)
        >>> mape = 12.34
        """
        try:
            target = np.array(target, dtype=float)
            forecast = np.array(forecast, dtype=float)
            if np.all((target == 0)):
                mape = 0
            else:
                e = target - forecast
                mape = 100*(abs(e)/target).mean()
        except ZeroDivisionError as err:
            self.logger.exception(f'Division by zero. Error set to 0 by default: {err}')
            mape = 0
        return mape


    def compute_mape_jet(self, target=None, forecast=None):
        """
        Return the CNCH's Mean Absolute Percentage Error between target and forecast points.

        :param target: List of target values
        :param forecast: List of forecast values
        :return mape: Mean Absolute Percentage Error value

        >>> mape = compute_mape_jet(target=mytarget, forecast=myforecast)
        >>> mape = 12.34
        """
        try:
            target = np.array(target, dtype=float)
            forecast = np.array(forecast, dtype=float)
            if np.all((forecast == 0)):
                cmape = 100
            else:
                e = target - forecast
                cmape = 100*(np.divide(abs(e), abs(forecast), out=np.ones_like(forecast), where=forecast!=0)).mean()
        except ZeroDivisionError as err:
            self.logger.exception(f'Division by zero. Error set to 0 by default: {err}')
            cmape = 0
        return cmape


    def compute_mase(self, target=None, forecast=None):
        """
        Return the Mean Absolute Scaled Error between target and forecast points.

        :param target: List of target values
        :param forecast: List of forecast values
        :return mase: Weighted Mean Absolute Percentage Error value

        >>> mase = compute_mase(target=mytarget, forecast=myforecast)
        >>> mase = 12.34
        """
        try:
            target = pd.Series(target, dtype=float)
            forecast = pd.Series(forecast, dtype=float)
            e = target - forecast
            denominator = (1/(len(target)-1))*sum(abs((target-target.shift(1)).fillna(0)))
            if denominator == 0:
                mase = 0
            else:
                mase = abs(e/denominator).mean()
        except ZeroDivisionError as err:
            self.logger.exception(f'Division by zero. Error set to 0 by default: {err}')
            mase = 0
        return mase


    def compute_rmse(self, target=None, forecast=None):
        """
        Return the Root Mean Square Error between target and forecast points.

        :param target: List of target values
        :param forecast: List of forecast values
        :return rmse: Root Mean Square Error value

        >>> rmse = compute_rmse(target=mytarget, forecast=myforecast)
        >>> rmse = 12.34
        """
        try:
            target = np.array(target, dtype=float)
            forecast = np.array(forecast, dtype=float)
            e = target - forecast
            rmse = np.sqrt((e**2).mean())
        except ValueError as err:
            self.logger.exception(f'Invalid values. Please check values and data type: {err}')
        return rmse


    def compute_smape(self, target=None, forecast=None):
        """
        Return the symmetric Mean Absolute Percentage Error between target and forecast points.

        :param target: List of target values
        :param forecast: List of forecast values
        :return smape: symmetric Mean Absolute Percentage Error value

        >>> smape = compute_smape(target=mytarget, forecast=myforecast)
        >>> smape = 12.34
        """
        try:
            target = np.array(target, dtype=float)
            forecast = np.array(forecast, dtype=float)
            if np.all((target == 0)) and np.all((forecast == 0)):
                smape = 0
            else:
                e = target - forecast
                denominator = np.abs(target) + np.abs(forecast)
                smape = 2*100*(np.divide(np.abs(e), denominator, out=np.ones_like(forecast), where=denominator!=0)).mean()
        except ZeroDivisionError as err:
            self.logger.exception(f'Division by zero. Error set to 0 by default: {err}')
            smape = 0
        return smape


    def compute_wape(self, target=None, forecast=None):
        """
        Return the Weighted Absolute Percentage Error between target and forecast points.

        :param target: List of target values
        :param forecast: List of forecast values
        :return wape: Weighted Mean Absolute Percentage Error value

        >>> wape = compute_wape(target=mytarget, forecast=myforecast)
        >>> wape = 12.34
        """
        try:
            target = np.array(target, dtype=float)
            forecast = np.array(forecast, dtype=float)
            if np.all((target == 0)):
                wape = 0
            else:
                e = target - forecast
                wape = 100*((abs(e)).sum()/abs(target).sum())
        except ZeroDivisionError as err:
            self.logger.exception(f'Division by zero. Error set to 0 by default: {err}')
            wape = 0
        return wape


    def compute_wmape(self, target=None, forecast=None):
        """
        Return the Weighted Mean Absolute Percentage Error between target and forecast points.

        :param target: List of target values
        :param forecast: List of forecast values
        :return rmse: Weighted Mean Absolute Percentage Error value

        >>> wmape = compute_wmape(target=mytarget, forecast=myforecast)
        >>> wmape = 12.34
        """
        try:
            target = np.array(target, dtype=float)
            forecast = np.array(forecast, dtype=float)

            if np.all((target == 0)):
                wmape = 0
            else:
                e = target - forecast
                wmape = 100 * (target * np.divide(abs(e), abs(target),
                                                  out=np.ones_like(target),
                                                  where=target != 0)).sum() / target.sum()
        except ZeroDivisionError as err:
            self.logger.exception(f'Division by zero. Error set to 0 by default: {err}')
            wmape = 0
        return wmape






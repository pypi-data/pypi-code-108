import numpy as np

def mape(forecast, actuals):
    return (np.abs((actuals - forecast)/actuals).sum()) / len(forecast)

def smape(forecast, actuals):
    return (np.abs(actuals - forecast) / ((np.abs(actuals) + np.abs(forecast)) / 2) ).sum() / len(forecast)

def mda(forecast, actuals):
    return (((forecast < forecast.shift(-1)).iloc[:-1] == (actuals < actuals.shift(-1)).iloc[:-1]) * 1).sum() / (len(forecast) - 1)

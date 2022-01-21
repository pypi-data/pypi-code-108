import clarus.services

def computeeffectiverates(output=None, **params):
    return clarus.services.api_request('Market', 'ComputeEffectiveRates', output=output, **params)

def curvebuild(output=None, **params):
    return clarus.services.api_request('Market', 'CurveBuild', output=output, **params)

def curvebuildconfig(output=None, **params):
    return clarus.services.api_request('Market', 'CurveBuildConfig', output=output, **params)

def curveusage(output=None, **params):
    return clarus.services.api_request('Market', 'CurveUsage', output=output, **params)

def df(output=None, **params):
    return clarus.services.api_request('Market', 'DF', output=output, **params)

def directforwards(output=None, **params):
    return clarus.services.api_request('Market', 'DirectForwards', output=output, **params)

def fixingcodemapping(output=None, **params):
    return clarus.services.api_request('Market', 'FixingCodeMapping', output=output, **params)

def fixings(output=None, **params):
    return clarus.services.api_request('Market', 'Fixings', output=output, **params)

def futures(output=None, **params):
    return clarus.services.api_request('Market', 'Futures', output=output, **params)

def fxrates(output=None, **params):
    return clarus.services.api_request('Market', 'FXRates', output=output, **params)

def fxvolsurface(output=None, **params):
    return clarus.services.api_request('Market', 'FXVolSurface', output=output, **params)

def inflationrates(output=None, **params):
    return clarus.services.api_request('Market', 'InflationRates', output=output, **params)

def instantaneousforwards(output=None, **params):
    return clarus.services.api_request('Market', 'InstantaneousForwards', output=output, **params)

def intradayquotes(output=None, **params):
    return clarus.services.api_request('Market', 'IntradayQuotes', output=output, **params)

def ladders(output=None, **params):
    return clarus.services.api_request('Market', 'Ladders', output=output, **params)

def pardv01(output=None, **params):
    return clarus.services.api_request('Market', 'ParDV01', output=output, **params)

def parrates(output=None, **params):
    return clarus.services.api_request('Market', 'ParRates', output=output, **params)

def pricinggrid(output=None, **params):
    return clarus.services.api_request('Market', 'PricingGrid', output=output, **params)

def quotecodemapping(output=None, **params):
    return clarus.services.api_request('Market', 'QuoteCodeMapping', output=output, **params)

def riskfreerates(output=None, **params):
    return clarus.services.api_request('Market', 'RiskFreeRates', output=output, **params)

def seasonality(output=None, **params):
    return clarus.services.api_request('Market', 'Seasonality', output=output, **params)

def shiftsetgenerator(output=None, **params):
    return clarus.services.api_request('Market', 'ShiftSetGenerator', output=output, **params)

def surfacebuildconfig(output=None, **params):
    return clarus.services.api_request('Market', 'SurfaceBuildConfig', output=output, **params)

def surfaceusage(output=None, **params):
    return clarus.services.api_request('Market', 'SurfaceUsage', output=output, **params)

def swaptionvolsurface(output=None, **params):
    return clarus.services.api_request('Market', 'SwaptionVolSurface', output=output, **params)

def zerorates(output=None, **params):
    return clarus.services.api_request('Market', 'ZeroRates', output=output, **params)


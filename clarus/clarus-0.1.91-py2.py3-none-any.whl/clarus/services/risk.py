import clarus.services

def dv01(output=None, **params):
    return clarus.services.api_request('Risk', 'DV01', output=output, **params)

def fxdelta(output=None, **params):
    return clarus.services.api_request('Risk', 'FXDelta', output=output, **params)

def fxvega(output=None, **params):
    return clarus.services.api_request('Risk', 'FXVega', output=output, **params)

def grossdv01(output=None, **params):
    return clarus.services.api_request('Risk', 'GrossDV01', output=output, **params)

def irdelta(output=None, **params):
    return clarus.services.api_request('Risk', 'IRDelta', output=output, **params)

def irgamma(output=None, **params):
    return clarus.services.api_request('Risk', 'IRGamma', output=output, **params)

def irvega(output=None, **params):
    return clarus.services.api_request('Risk', 'IRVega', output=output, **params)

def stress(output=None, **params):
    return clarus.services.api_request('Risk', 'Stress', output=output, **params)

def theta(output=None, **params):
    return clarus.services.api_request('Risk', 'Theta', output=output, **params)

def var(output=None, **params):
    return clarus.services.api_request('Risk', 'VaR', output=output, **params)

def varattribution(output=None, **params):
    return clarus.services.api_request('Risk', 'VaRAttribution', output=output, **params)

def varvectors(output=None, **params):
    return clarus.services.api_request('Risk', 'VaRVectors', output=output, **params)


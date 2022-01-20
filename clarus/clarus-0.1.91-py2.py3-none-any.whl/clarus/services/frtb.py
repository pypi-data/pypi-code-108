import clarus.services

def ima(output=None, **params):
    return clarus.services.api_request('FRTB', 'IMA', output=output, **params)

def imaimpact(output=None, **params):
    return clarus.services.api_request('FRTB', 'IMAImpact', output=output, **params)

def modellablerf(output=None, **params):
    return clarus.services.api_request('FRTB', 'ModellableRF', output=output, **params)

def modellablerftrades(output=None, **params):
    return clarus.services.api_request('FRTB', 'ModellableRFTrades', output=output, **params)

def plvectors(output=None, **params):
    return clarus.services.api_request('FRTB', 'PLVectors', output=output, **params)

def sa(output=None, **params):
    return clarus.services.api_request('FRTB', 'SA', output=output, **params)

def saimpact(output=None, **params):
    return clarus.services.api_request('FRTB', 'SAImpact', output=output, **params)


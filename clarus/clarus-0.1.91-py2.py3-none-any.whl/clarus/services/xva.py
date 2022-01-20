import clarus.services

def fva(output=None, **params):
    return clarus.services.api_request('XVA', 'FVA', output=output, **params)

def mva(output=None, **params):
    return clarus.services.api_request('XVA', 'MVA', output=output, **params)

def mvaattribution(output=None, **params):
    return clarus.services.api_request('XVA', 'MVAAttribution', output=output, **params)

def sensitivity(output=None, **params):
    return clarus.services.api_request('XVA', 'Sensitivity', output=output, **params)


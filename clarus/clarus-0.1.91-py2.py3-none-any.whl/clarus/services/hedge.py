import clarus.services

def equivalents(output=None, **params):
    return clarus.services.api_request('Hedge', 'Equivalents', output=output, **params)

def equivalents01(output=None, **params):
    return clarus.services.api_request('Hedge', 'Equivalents01', output=output, **params)


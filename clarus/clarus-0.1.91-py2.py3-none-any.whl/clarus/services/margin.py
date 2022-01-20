import clarus.services

def attribution(output=None, **params):
    return clarus.services.api_request('Margin', 'Attribution', output=output, **params)

def core(output=None, **params):
    return clarus.services.api_request('Margin', 'CORE', output=output, **params)

def im(output=None, **params):
    return clarus.services.api_request('Margin', 'IM', output=output, **params)

def impact(output=None, **params):
    return clarus.services.api_request('Margin', 'Impact', output=output, **params)

def optimiser(output=None, **params):
    return clarus.services.api_request('Margin', 'Optimiser', output=output, **params)

def parswapsim(output=None, **params):
    return clarus.services.api_request('Margin', 'ParSwapsIM', output=output, **params)

def plvectors(output=None, **params):
    return clarus.services.api_request('Margin', 'PLVectors', output=output, **params)

def sensitivity(output=None, **params):
    return clarus.services.api_request('Margin', 'Sensitivity', output=output, **params)

def vm(output=None, **params):
    return clarus.services.api_request('Margin', 'VM', output=output, **params)

def vmbuffer(output=None, **params):
    return clarus.services.api_request('Margin', 'VMBuffer', output=output, **params)

def vmlsoc(output=None, **params):
    return clarus.services.api_request('Margin', 'VMLSOC', output=output, **params)


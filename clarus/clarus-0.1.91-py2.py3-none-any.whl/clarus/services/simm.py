import clarus.services

def history(output=None, **params):
    return clarus.services.api_request('SIMM', 'History', output=output, **params)

def impact(output=None, **params):
    return clarus.services.api_request('SIMM', 'Impact', output=output, **params)

def margin(output=None, **params):
    return clarus.services.api_request('SIMM', 'Margin', output=output, **params)

def sensitivity(output=None, **params):
    return clarus.services.api_request('SIMM', 'Sensitivity', output=output, **params)


import clarus.services

def saccr(output=None, **params):
    return clarus.services.api_request('Credit', 'SACCR', output=output, **params)


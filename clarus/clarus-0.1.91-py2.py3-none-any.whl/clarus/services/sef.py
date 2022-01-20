import clarus.services

def volume(output=None, **params):
    return clarus.services.api_request('SEF', 'Volume', output=output, **params)


import clarus.services

def ladder(output=None, **params):
    return clarus.services.api_request('Load', 'Ladder', output=output, **params)

def market(output=None, **params):
    return clarus.services.api_request('Load', 'Market', output=output, **params)

def portfolio(output=None, **params):
    return clarus.services.api_request('Load', 'Portfolio', output=output, **params)

def scenario(output=None, **params):
    return clarus.services.api_request('Load', 'Scenario', output=output, **params)


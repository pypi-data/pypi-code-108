import clarus.services

def disclosures(output=None, **params):
    return clarus.services.api_request('CCPQD', 'Disclosures', output=output, **params)

def ratios(output=None, **params):
    return clarus.services.api_request('CCPQD', 'Ratios', output=output, **params)

def reference(output=None, **params):
    return clarus.services.api_request('CCPQD', 'Reference', output=output, **params)


import clarus.services

def clearingeligible(output=None, **params):
    return clarus.services.api_request('Compliance', 'ClearingEligible', output=output, **params)

def clearingmandatory(output=None, **params):
    return clarus.services.api_request('Compliance', 'ClearingMandatory', output=output, **params)

def sefmandatory(output=None, **params):
    return clarus.services.api_request('Compliance', 'SEFMandatory', output=output, **params)


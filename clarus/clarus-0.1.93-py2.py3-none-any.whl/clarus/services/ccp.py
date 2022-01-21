import clarus.services

def collateralacceptable(output=None, **params):
    return clarus.services.api_request('CCP', 'CollateralAcceptable', output=output, **params)

def collateralspreads(output=None, **params):
    return clarus.services.api_request('CCP', 'CollateralSpreads', output=output, **params)

def defaultresources(output=None, **params):
    return clarus.services.api_request('CCP', 'DefaultResources', output=output, **params)

def rfrvolume(output=None, **params):
    return clarus.services.api_request('CCP', 'RFRVolume', output=output, **params)

def volume(output=None, **params):
    return clarus.services.api_request('CCP', 'Volume', output=output, **params)


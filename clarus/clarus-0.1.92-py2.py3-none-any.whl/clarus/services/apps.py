import clarus.services

def collateralbalances(output=None, **params):
    return clarus.services.api_request('Apps', 'CollateralBalances', output=output, **params)

def jbdraxmtm(output=None, **params):
    return clarus.services.api_request('Apps', 'JBDraxMTM', output=output, **params)


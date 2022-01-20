import clarus.services

def dsb(output=None, **params):
    return clarus.services.api_request('MIFID', 'DSB', output=output, **params)

def firds(output=None, **params):
    return clarus.services.api_request('MIFID', 'FIRDS', output=output, **params)

def lastprice(output=None, **params):
    return clarus.services.api_request('MIFID', 'LastPrice', output=output, **params)

def lasttrade(output=None, **params):
    return clarus.services.api_request('MIFID', 'LastTrade', output=output, **params)

def tradefilter(output=None, **params):
    return clarus.services.api_request('MIFID', 'TradeFilter', output=output, **params)

def volume(output=None, **params):
    return clarus.services.api_request('MIFID', 'Volume', output=output, **params)

def volumeadv(output=None, **params):
    return clarus.services.api_request('MIFID', 'VolumeADV', output=output, **params)


import clarus.services

def lastprice(output=None, **params):
    return clarus.services.api_request('SDR', 'LastPrice', output=output, **params)

def lasttrade(output=None, **params):
    return clarus.services.api_request('SDR', 'LastTrade', output=output, **params)

def ohlc(output=None, **params):
    return clarus.services.api_request('SDR', 'OHLC', output=output, **params)

def tradefilter(output=None, **params):
    return clarus.services.api_request('SDR', 'TradeFilter', output=output, **params)

def trades(output=None, **params):
    return clarus.services.api_request('SDR', 'Trades', output=output, **params)

def volume(output=None, **params):
    return clarus.services.api_request('SDR', 'Volume', output=output, **params)

def volumeadv(output=None, **params):
    return clarus.services.api_request('SDR', 'VolumeADV', output=output, **params)


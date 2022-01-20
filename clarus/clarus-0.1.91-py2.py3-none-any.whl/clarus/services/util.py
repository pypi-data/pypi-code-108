import clarus.services

def activity(output=None, **params):
    return clarus.services.api_request('Util', 'Activity', output=output, **params)

def assetpricedefinition(output=None, **params):
    return clarus.services.api_request('Util', 'AssetPriceDefinition', output=output, **params)

def batch(output=None, **params):
    return clarus.services.api_request('Util', 'Batch', output=output, **params)

def dataframetransform(output=None, **params):
    return clarus.services.api_request('Util', 'DataframeTransform', output=output, **params)

def discovery(output=None, **params):
    return clarus.services.api_request('Util', 'Discovery', output=output, **params)

def domain(output=None, **params):
    return clarus.services.api_request('Util', 'Domain', output=output, **params)

def equityindexdefinition(output=None, **params):
    return clarus.services.api_request('Util', 'EquityIndexDefinition', output=output, **params)

def financialcenters(output=None, **params):
    return clarus.services.api_request('Util', 'FinancialCenters', output=output, **params)

def fuzzyrequest(output=None, **params):
    return clarus.services.api_request('Util', 'FuzzyRequest', output=output, **params)

def generatetradex(output=None, **params):
    return clarus.services.api_request('Util', 'GenerateTradeX', output=output, **params)

def grid(output=None, **params):
    return clarus.services.api_request('Util', 'Grid', output=output, **params)

def periodlength(output=None, **params):
    return clarus.services.api_request('Util', 'PeriodLength', output=output, **params)

def quotecodedefinition(output=None, **params):
    return clarus.services.api_request('Util', 'QuoteCodeDefinition', output=output, **params)

def report(output=None, **params):
    return clarus.services.api_request('Util', 'Report', output=output, **params)

def shiftsetgenerator(output=None, **params):
    return clarus.services.api_request('Util', 'ShiftSetGenerator', output=output, **params)

def simmcrifquotes(output=None, **params):
    return clarus.services.api_request('Util', 'SimmCrifQuotes', output=output, **params)

def sourcedata(output=None, **params):
    return clarus.services.api_request('Util', 'SourceData', output=output, **params)

def tickers(output=None, **params):
    return clarus.services.api_request('Util', 'Tickers', output=output, **params)

